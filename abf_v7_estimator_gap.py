# Databricks notebook source
# MAGIC %md
# MAGIC # Reconcile +3.68% (decile-pooled) vs +1.17% (title-level rev-weighted) ABF1-wide lift
# MAGIC Pull per-title: pre-launch revenue weight, in-experiment per-title lift, density decile.
# MAGIC Then show how concentrated the title-level revenue-weighted estimate is, and whether a
# MAGIC few high-revenue dense/negative titles drive the gap to the decile-smoothed +3.68%.
# MAGIC v7 OTT.

# COMMAND ----------

import numpy as np, json
import pandas as pd

EXP='ads_abf_3_v7'; START_DS='2026-06-17'; END_DS='2026-06-22'
WIN_START='2026-05-07'; WIN_END='2026-05-20'
TITLES='core_dev.dsa.temp_bp_abf_v6_exp_titles'; UNIVERSE='core_dev.dsa.temp_bp_abf1_universe'
ADV_EXCL="1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452"

# COMMAND ----------

# per-title test/control mean device revenue + device counts (ToT, ABF3 titles only)
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
SELECT content_id, variant, COUNT(*) n_dev, AVG(rev) mean_rev, SUM(rev) sum_rev
FROM devtitle GROUP BY content_id, variant
""").toPandas()

rev_wt = spark.sql(f"""
  SELECT CAST(i.content_id AS INT) content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) rev_pre
  FROM core_prod.ads.impressions i JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id=c.id
  WHERE i.date>='{WIN_START}' AND i.date<='{WIN_END}' AND i.unbillable='f'
  GROUP BY CAST(i.content_id AS INT)
""").toPandas()
dens = spark.sql(f"SELECT content_id, abf1_cue_points FROM {UNIVERSE}").toPandas()

# COMMAND ----------

p = title_arm.pivot_table(index='content_id', columns='variant', values=['mean_rev','sum_rev','n_dev'], aggfunc='first')
p.columns=[f"{a}_{b}" for a,b in p.columns]
p=p.reset_index().merge(rev_wt,on='content_id',how='left').merge(dens,on='content_id',how='left').fillna({'rev_pre':0.0})
for c0 in ['mean_rev_Test','mean_rev_Control','sum_rev_Test','sum_rev_Control','n_dev_Test','n_dev_Control','rev_pre','abf1_cue_points']:
    p[c0]=pd.to_numeric(p[c0],errors='coerce')
p=p.dropna(subset=['mean_rev_Test','mean_rev_Control'])
p=p[p['mean_rev_Control']>0].copy()
p['abf1_cue_points']=p['abf1_cue_points'].astype(float)
p['title_lift']=(p['mean_rev_Test']-p['mean_rev_Control'])/p['mean_rev_Control']   # per-title % lift
p['rev_wt_share']=p['rev_pre']/p['rev_pre'].sum()
# each title's contribution to the rev-weighted aggregate-lift numerator: w*(mt-mc); denom sum w*mc
num_i = p['rev_pre']*(p['mean_rev_Test']-p['mean_rev_Control'])
den = (p['rev_pre']*p['mean_rev_Control']).sum()
p['contrib_to_aggnum'] = num_i
p['contrib_share'] = num_i / num_i.sum()
agg = num_i.sum()/den*100
print(f"n titles {len(p)}; title-level rev-weighted aggregate lift = {agg:+.3f}%")

# COMMAND ----------

# decile assignment (same qcut basis)
edges=pd.qcut(p['abf1_cue_points'],10,retbins=True,duplicates='drop')[1]
cuts=list(edges)[1:-1]
def adec(x):
    for i,c in enumerate(cuts):
        if x<=c: return i
    return len(cuts)
p['decile']=p['abf1_cue_points'].apply(adec)

# COMMAND ----------

# TOP-20 titles by pre-launch revenue weight: their lift, decile, contribution
top=p.sort_values('rev_pre',ascending=False).head(20)
print("TOP 20 titles by pre-launch revenue weight:")
print(top[['content_id','abf1_cue_points','decile','rev_pre','rev_wt_share','title_lift','contrib_share','n_dev_Test']]
      .assign(title_lift=lambda d:(d.title_lift*100).round(2), rev_wt_share=lambda d:(d.rev_wt_share*100).round(2),
              contrib_share=lambda d:(d.contrib_share*100).round(2)).to_string(index=False))

# how much of the rev-weight is in the top titles
ps=p.sort_values('rev_pre',ascending=False)
for k in [10,20,50,100]:
    print(f"top {k} titles = {ps.head(k)['rev_wt_share'].sum()*100:.1f}% of rev-weight, "
          f"{ps.head(k)['contrib_share'].sum()*100:+.1f}% of agg-lift numerator")

# COMMAND ----------

# negative-lift high-revenue titles
neg = p[p['title_lift']<0].sort_values('rev_pre',ascending=False)
print(f"\n# titles with negative per-title lift: {len(neg)}/{len(p)}; "
      f"they hold {neg['rev_wt_share'].sum()*100:.1f}% of rev-weight, "
      f"{neg['contrib_share'].sum()*100:+.1f}% of agg numerator")
print("Top 15 negative-lift titles by rev weight:")
print(neg.head(15)[['content_id','abf1_cue_points','decile','rev_pre','rev_wt_share','title_lift','contrib_share']]
      .assign(title_lift=lambda d:(d.title_lift*100).round(2), rev_wt_share=lambda d:(d.rev_wt_share*100).round(2),
              contrib_share=lambda d:(d.contrib_share*100).round(2)).to_string(index=False))

# COMMAND ----------

# Why decile-pooled differs: pooled lift per decile = sum_rev diff / sum_rev control (device-pooled),
# vs title-level rev-weighted within decile. Show both per decile.
rows=[]
for d,g in p.groupby('decile'):
    # device-pooled (like global notebook): uses sum over devices
    pooled = (g['sum_rev_Test'].sum()-g['sum_rev_Control'].sum())  # NOTE approximate; pooled uses mean*n
    # better pooled: total test rev / n_test  minus total control / n_control, relative
    mt_pool=(g['mean_rev_Test']*g['n_dev_Test']).sum()/g['n_dev_Test'].sum()
    mc_pool=(g['mean_rev_Control']*g['n_dev_Control']).sum()/g['n_dev_Control'].sum()
    pooled_lift=(mt_pool-mc_pool)/mc_pool*100
    # title rev-weighted within decile
    num=(g['rev_pre']*(g['mean_rev_Test']-g['mean_rev_Control'])).sum()
    den2=(g['rev_pre']*g['mean_rev_Control']).sum()
    tlift=num/den2*100 if den2 else np.nan
    rows.append(dict(decile=int(d), n=len(g), pooled_lift_pct=round(pooled_lift,2),
                     title_revwt_lift_pct=round(tlift,2), rev_wt=round(g['rev_pre'].sum(),0)))
dec=pd.DataFrame(rows).sort_values('decile')
print("\nPer-decile: device-pooled lift (global-notebook style) vs title-rev-weighted lift:")
print(dec.to_string(index=False))

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    'n_titles': int(len(p)),
    'title_revwt_agg_lift_pct': round(float(agg),3),
    'n_negative': int(len(neg)),
    'neg_revwt_share_pct': round(float(neg['rev_wt_share'].sum()*100),2),
    'neg_contrib_share_pct': round(float(neg['contrib_share'].sum()*100),2),
    'top10_revwt_share_pct': round(float(ps.head(10)['rev_wt_share'].sum()*100),2),
    'top20_revwt_share_pct': round(float(ps.head(20)['rev_wt_share'].sum()*100),2),
    'per_decile_pooled_vs_titlerevwt': dec.to_dict('records'),
    'top20_titles': top[['content_id','decile','rev_pre','title_lift','contrib_share']].round(5).to_dict('records'),
}, default=str))
