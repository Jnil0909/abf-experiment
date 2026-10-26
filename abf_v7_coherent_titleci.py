# Databricks notebook source
# MAGIC %md
# MAGIC # Coherent title-clustered CI for the TOPLINE estimator
# MAGIC The topline ABF1-wide rev lift (+3.68%) = Σ_decile( device-POOLED decile lift ×
# MAGIC universe-revenue share of decile ). To get a title-clustered CI that genuinely belongs
# MAGIC to THAT number, bootstrap the titles and on each resample recompute the device-pooled
# MAGIC decile lifts, then re-aggregate with the SAME (fixed) universe-revenue decile weights.
# MAGIC Device-pooling means weight=in-experiment device count, so near-empty titles (the
# MAGIC pre-launch-heavy/in-experiment-empty −100% junk that broke the per-title rev-weighted
# MAGIC bootstrap) contribute ~0 weight automatically — no filter hack needed. Also report a
# MAGIC version with a min-exposure filter for robustness. v7 + v6 OTT.

# COMMAND ----------

import numpy as np, json
import pandas as pd

dbutils.widgets.text('EXP','ads_abf_3_v7')
dbutils.widgets.text('START_DS','2026-06-17'); dbutils.widgets.text('END_DS','2026-06-22')
dbutils.widgets.text('WIN_START','2026-05-07'); dbutils.widgets.text('WIN_END','2026-05-20')
dbutils.widgets.text('PLATFORM_TYPE','ALL')   # ALL(OTT) | MOBILE | WEB — scopes universe-revenue weights
EXP=dbutils.widgets.get('EXP'); START_DS=dbutils.widgets.get('START_DS'); END_DS=dbutils.widgets.get('END_DS')
WIN_START=dbutils.widgets.get('WIN_START'); WIN_END=dbutils.widgets.get('WIN_END')
PLATFORM_TYPE=dbutils.widgets.get('PLATFORM_TYPE')
TITLES='core_dev.dsa.temp_bp_abf_v6_exp_titles'; UNIVERSE='core_dev.dsa.temp_bp_abf1_universe'
ADV_EXCL="1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452"
_PLAT_MAP={'MOBILE':['android','iphone','ipad','firetablet','android_samsung'],'WEB':['web']}
if PLATFORM_TYPE=='ALL':
    IMP_PLAT_FILTER=""
else:
    _names=",".join(f"'{x}'" for x in _PLAT_MAP[PLATFORM_TYPE])
    IMP_PLAT_FILTER=f"AND lower(i.platform) IN ({_names})"
N_BOOT=2000; SEED=12345
print(f"{EXP} {START_DS}..{END_DS} pre {WIN_START}..{WIN_END} platform={PLATFORM_TYPE}")

# COMMAND ----------

# per-title per-arm: device count + total in-experiment revenue (sum, for pooling)
title_arm = spark.sql(f"""
WITH exp AS (
  SELECT device_id, group_name AS variant, MIN(timestamp) AS first_exposure_ts
  FROM core_dev.statsig.exposures WHERE experiment_id='{EXP}' GROUP BY device_id, group_name
),
vs AS (
  SELECT e.device_id, e.variant, v.content_id, SUM(v.tvt_millisec/1000.0/60.0) AS tvt_mins
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id=v.device_id AND v.start_ts>=e.first_exposure_ts AND v.ds>='{START_DS}' AND v.ds<='{END_DS}'
  WHERE v.content_id IN (SELECT content_id FROM {TITLES})
  GROUP BY e.device_id, e.variant, v.content_id
),
imp AS (
  SELECT i.device_id, i.content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS rev
  FROM core_prod.ads.impressions i
  JOIN exp e ON i.device_id=e.device_id AND i.ts>=e.first_exposure_ts
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id=c.id
  WHERE i.date>='{START_DS}' AND i.date<='{END_DS}' AND i.unbillable='f'
    AND i.content_id IN (SELECT CAST(content_id AS STRING) FROM {TITLES})
  GROUP BY i.device_id, i.content_id
),
devtitle AS (
  SELECT vs.content_id, vs.variant, vs.device_id, COALESCE(imp.rev,0) AS rev
  FROM vs LEFT JOIN imp ON vs.device_id=imp.device_id AND CAST(vs.content_id AS STRING)=imp.content_id
)
SELECT content_id, variant, COUNT(*) AS n_dev, SUM(rev) AS sum_rev
FROM devtitle GROUP BY content_id, variant
""").toPandas()
dens = spark.sql(f"SELECT content_id, abf1_cue_points FROM {UNIVERSE}").toPandas()

# universe revenue per decile (fixed poststrat weights), pre-launch window
uni_rev = spark.sql(f"""
WITH imp AS (
  SELECT CAST(i.content_id AS INT) AS content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS rev
  FROM core_prod.ads.impressions i JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id=c.id
  WHERE i.date>='{WIN_START}' AND i.date<='{WIN_END}' AND i.unbillable='f' {IMP_PLAT_FILTER} GROUP BY CAST(i.content_id AS INT)
)
SELECT u.content_id, u.abf1_cue_points, COALESCE(imp.rev,0) AS uni_rev
FROM {UNIVERSE} u LEFT JOIN imp ON u.content_id=imp.content_id
""").toPandas()

# COMMAND ----------

p = title_arm.pivot_table(index='content_id', columns='variant', values=['n_dev','sum_rev'], aggfunc='first')
p.columns=[f"{a}_{b}" for a,b in p.columns]
p=p.reset_index().merge(dens,on='content_id',how='left')
for c0 in ['n_dev_Test','n_dev_Control','sum_rev_Test','sum_rev_Control','abf1_cue_points']:
    p[c0]=pd.to_numeric(p[c0],errors='coerce')
p=p.dropna(subset=['n_dev_Test','n_dev_Control','abf1_cue_points']).fillna({'sum_rev_Test':0.0,'sum_rev_Control':0.0})
p['abf1_cue_points']=p['abf1_cue_points'].astype(float)

# decile edges (same qcut basis as global notebook) + universe revenue share per decile
edges=pd.qcut(p['abf1_cue_points'],10,retbins=True,duplicates='drop')[1]
cuts=list(edges)[1:-1]
def adec(x):
    for i,c in enumerate(cuts):
        if x<=c: return i
    return len(cuts)
p['decile']=p['abf1_cue_points'].apply(adec)
uni_rev['abf1_cue_points']=pd.to_numeric(uni_rev['abf1_cue_points'],errors='coerce').astype(float)
uni_rev['uni_rev']=pd.to_numeric(uni_rev['uni_rev'],errors='coerce').fillna(0.0)
uni_rev['decile']=uni_rev['abf1_cue_points'].apply(adec)
uni_share=uni_rev.groupby('decile')['uni_rev'].sum()
uni_share=(uni_share/uni_share.sum())
uniq=sorted(p['decile'].unique())
W=np.array([uni_share.get(d,0.0) for d in uniq]); W=W/W.sum()
print(f"n titles {len(p)}; deciles {uniq}")

# COMMAND ----------

dec_arr=p['decile'].values
nt=p['n_dev_Test'].values; nc=p['n_dev_Control'].values
st_=p['sum_rev_Test'].values; sc=p['sum_rev_Control'].values

def abf1wide(idx):
    # device-pooled decile lift, then universe-revenue-weighted across deciles
    out=0.0; wsum=0.0
    for k,d in enumerate(uniq):
        m=dec_arr[idx]==d
        if not m.any(): continue
        NT=nt[idx][m].sum(); NC=nc[idx][m].sum()
        if NT==0 or NC==0: continue
        mt=st_[idx][m].sum()/NT; mc=sc[idx][m].sum()/NC
        if mc==0: continue
        out+=((mt-mc)/mc)*W[k]; wsum+=W[k]
    return out/wsum if wsum>0 else np.nan

allidx=np.arange(len(p))
point=abf1wide(allidx)*100
print(f"Coherent ABF1-wide rev lift (device-pooled decile, univ-rev wt): {point:+.3f}%  (cf global notebook +3.68% v7 / +6.02% v6)")

rng=np.random.default_rng(SEED); n=len(p)
boots=np.empty(N_BOOT)
for b in range(N_BOOT):
    s=rng.choice(allidx,size=n,replace=True)
    boots[b]=abf1wide(s)
boots=boots[~np.isnan(boots)]*100
lo,hi=np.percentile(boots,[2.5,97.5])
print(f"Coherent title-clustered 95% CI: [{lo:+.3f}%, {hi:+.3f}%]  (sd {boots.std():.3f}, n {len(boots)})")

# COMMAND ----------

# robustness: min-exposure filter (>=100 devices/arm) on the per-title rev-weighted bootstrap,
# to show the junk-title fix also works the simpler way
q=p[(p['n_dev_Test']>=100)&(p['n_dev_Control']>=100)&(p['sum_rev_Control']>0)].copy()
mt_q=(q['sum_rev_Test']/q['n_dev_Test']).values; mc_q=(q['sum_rev_Control']/q['n_dev_Control']).values
# weight by in-experiment control revenue (window-matched to signal)
wq=q['sum_rev_Control'].values
def agg(mt,mc,w):
    den=np.sum(w*mc); return (np.sum(w*mt)-den)/den if den else np.nan
pt_q=agg(mt_q,mc_q,wq)*100
bq=np.empty(N_BOOT); idxq=np.arange(len(q))
for b in range(N_BOOT):
    s=rng.choice(idxq,size=len(q),replace=True); bq[b]=agg(mt_q[s],mc_q[s],wq[s])
bq=bq[~np.isnan(bq)]*100
loq,hiq=np.percentile(bq,[2.5,97.5])
print(f"\nRobustness (>=100 dev/arm, n={len(q)}, weight=in-exp control rev):")
print(f"  point {pt_q:+.3f}%  CI [{loq:+.3f}%, {hiq:+.3f}%]")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    'exp':EXP,'n_titles':int(len(p)),
    'coherent_abf1wide_point_pct':round(float(point),3),
    'coherent_title_ci':[round(float(lo),3),round(float(hi),3)],
    'coherent_boot_sd':round(float(boots.std()),3),
    'robust_n':int(len(q)),'robust_point_pct':round(float(pt_q),3),
    'robust_ci':[round(float(loq),3),round(float(hiq),3)],
}, default=str))
