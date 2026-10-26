# Databricks notebook source
# MAGIC %md
# MAGIC # Revenue-weighted title-clustered CI (consistency fix)
# MAGIC `title_generalization` computes the title bootstrap TVT-weighted, but the topline
# MAGIC revenue projection is REVENUE-weighted. This recomputes the title-clustered CI with
# MAGIC weight = pre-launch REVENUE per title, so the CI belongs to the same revenue estimand
# MAGIC as the +3.68%/+1.36% topline. Also reports a poststratified-INSIDE-bootstrap variant
# MAGIC (reweight per-decile to the universe revenue mix on every resample) so the CI is a
# MAGIC proper interval for the projected lift. Basis: ToT / ABF3-titles-only / unbudgeted_revenue.

# COMMAND ----------

from pyspark.sql import functions as F
import numpy as np, json
import pandas as pd

dbutils.widgets.text('EXP', 'ads_abf_3_v7')
dbutils.widgets.text('START_DS', '2026-06-17')
dbutils.widgets.text('END_DS', '2026-06-22')
dbutils.widgets.text('WIN_START', '2026-05-07')   # pre-launch window for weights/shares
dbutils.widgets.text('WIN_END', '2026-05-20')
dbutils.widgets.text('PLATFORM_TYPE', 'ALL')
EXP = dbutils.widgets.get('EXP')
START_DS = dbutils.widgets.get('START_DS')
END_DS = dbutils.widgets.get('END_DS')
WIN_START = dbutils.widgets.get('WIN_START')
WIN_END = dbutils.widgets.get('WIN_END')
PLATFORM_TYPE = dbutils.widgets.get('PLATFORM_TYPE')
TITLES = 'core_dev.dsa.temp_bp_abf_v6_exp_titles'
UNIVERSE = 'core_dev.dsa.temp_bp_abf1_universe'
ADV_EXCL = "1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452"
IMP_PLAT_FILTER = "" if PLATFORM_TYPE == 'ALL' else ""  # OTT==ALL; impressions plat filter only needed for mobile/web
N_BOOT = 2000
SEED = 12345
print(f"EXP={EXP}  window={START_DS}..{END_DS}  pre={WIN_START}..{WIN_END}  platform={PLATFORM_TYPE}")

# COMMAND ----------

# per-title, per-arm mean device revenue on experiment titles (ToT, ABF3 titles only)
title_arm = spark.sql(f"""
WITH exp AS (
  SELECT device_id, group_name AS variant, MIN(timestamp) AS first_exposure_ts
  FROM core_dev.statsig.exposures WHERE experiment_id = '{EXP}'
  GROUP BY device_id, group_name
),
vs AS (
  SELECT e.device_id, e.variant, v.content_id,
         SUM(v.tvt_millisec/1000.0/60.0) AS tvt_mins
  FROM exp e
  JOIN core_prod.tubidw.video_session v
    ON e.device_id = v.device_id AND v.start_ts >= e.first_exposure_ts AND v.ds >= '{START_DS}' AND v.ds <= '{END_DS}'
  WHERE v.content_id IN (SELECT content_id FROM {TITLES})
  GROUP BY e.device_id, e.variant, v.content_id
),
imp AS (
  SELECT i.device_id, i.content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS rev
  FROM core_prod.ads.impressions i
  JOIN exp e ON i.device_id = e.device_id AND i.ts >= e.first_exposure_ts
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '{START_DS}' AND i.date <= '{END_DS}' AND i.unbillable = 'f'
    AND i.content_id IN (SELECT CAST(content_id AS STRING) FROM {TITLES})
  GROUP BY i.device_id, i.content_id
),
devtitle AS (
  SELECT vs.content_id, vs.variant, vs.device_id, COALESCE(imp.rev,0) AS rev
  FROM vs LEFT JOIN imp ON vs.device_id = imp.device_id AND CAST(vs.content_id AS STRING) = imp.content_id
)
SELECT content_id, variant, COUNT(*) AS n_dev, AVG(rev) AS mean_rev
FROM devtitle GROUP BY content_id, variant
""").toPandas()

# pre-launch per-title REVENUE (the new weight) + density
rev_wt = spark.sql(f"""
  SELECT CAST(i.content_id AS INT) AS content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS rev_pre
  FROM core_prod.ads.impressions i
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '{WIN_START}' AND i.date <= '{WIN_END}' AND i.unbillable = 'f'
  GROUP BY CAST(i.content_id AS INT)
""").toPandas()
dens = spark.sql(f"SELECT content_id, abf1_cue_points FROM {UNIVERSE}").toPandas()

# COMMAND ----------

p = title_arm.pivot_table(index='content_id', columns='variant', values=['mean_rev','n_dev'], aggfunc='first')
p.columns = [f"{a}_{b}" for a,b in p.columns]
p = p.reset_index().merge(rev_wt, on='content_id', how='left').merge(dens, on='content_id', how='left')
p = p.fillna({'rev_pre': 0.0})
for col in ['mean_rev_Test','mean_rev_Control','n_dev_Test','n_dev_Control','rev_pre','abf1_cue_points']:
    if col in p.columns:
        p[col] = pd.to_numeric(p[col], errors='coerce').astype(float)
p = p.dropna(subset=['mean_rev_Test','mean_rev_Control'])
p = p[p['mean_rev_Control'] > 0].copy()
print(f"titles with defined per-title lift: {len(p)} / 1084")
print(f"titles with rev_pre>0: {(p['rev_pre']>0).sum()}  (rev-weight nonzero)")

# COMMAND ----------

def agg_lift(mt, mc, w):
    num = np.sum(w*mt) - np.sum(w*mc); den = np.sum(w*mc)
    return num/den if den != 0 else np.nan

mt = p['mean_rev_Test'].values; mc = p['mean_rev_Control'].values
w_rev = p['rev_pre'].values

point_rev = agg_lift(mt, mc, w_rev) * 100
print(f"REVENUE-weighted aggregate revenue lift (point): {point_rev:+.3f}%")

# --- (1) simple revenue-weighted title bootstrap ---
rng = np.random.default_rng(SEED)
idx = np.arange(len(p)); n = len(p)
boots = np.empty(N_BOOT)
for b in range(N_BOOT):
    s = rng.choice(idx, size=n, replace=True)
    boots[b] = agg_lift(mt[s], mc[s], w_rev[s])
boots = boots[~np.isnan(boots)] * 100
lo, hi = np.percentile(boots, [2.5, 97.5])
print(f"REV-weighted title-clustered 95% CI: [{lo:+.3f}%, {hi:+.3f}%]  (mean {boots.mean():+.3f}, sd {boots.std():.3f}, n={len(boots)})")

# COMMAND ----------

# --- (2) poststratify-INSIDE-bootstrap: reweight per-decile to UNIVERSE revenue mix every resample ---
# decile edges from experiment titles (same basis as global notebook)
edges = pd.qcut(p['abf1_cue_points'], 10, retbins=True, duplicates='drop')[1]
cuts = list(edges)[1:-1]
def assign_dec(x):
    for i,c in enumerate(cuts):
        if x <= c: return i
    return len(cuts)
p['decile'] = p['abf1_cue_points'].apply(assign_dec)

# universe revenue per decile (the poststrat target weights)
uni = dens.merge(rev_wt, on='content_id', how='left').fillna({'rev_pre':0.0})
uni['abf1_cue_points'] = pd.to_numeric(uni['abf1_cue_points'], errors='coerce').astype(float)
uni['rev_pre'] = pd.to_numeric(uni['rev_pre'], errors='coerce').fillna(0.0).astype(float)
uni['decile'] = uni['abf1_cue_points'].apply(assign_dec)
uni_rev_dec = uni.groupby('decile')['rev_pre'].sum()
uni_share = (uni_rev_dec / uni_rev_dec.sum()).to_dict()

deciles = p['decile'].values
uniq_dec = sorted(p['decile'].unique())
target_w = np.array([uni_share.get(d,0.0) for d in uniq_dec])
target_w = target_w / target_w.sum()

def poststrat_lift(mt_, mc_, wrev_, dec_):
    # within-decile revenue-weighted lift, then combine by universe revenue share
    out = 0.0; wsum = 0.0
    for k,d in enumerate(uniq_dec):
        m = dec_ == d
        if not m.any(): continue
        den = np.sum(wrev_[m]*mc_[m])
        if den == 0: continue
        dl = (np.sum(wrev_[m]*mt_[m]) - den)/den
        out += dl * target_w[k]; wsum += target_w[k]
    return out/wsum if wsum>0 else np.nan

point_ps = poststrat_lift(mt, mc, w_rev, deciles) * 100
boots_ps = np.empty(N_BOOT)
for b in range(N_BOOT):
    s = rng.choice(idx, size=n, replace=True)
    boots_ps[b] = poststrat_lift(mt[s], mc[s], w_rev[s], deciles[s])
boots_ps = boots_ps[~np.isnan(boots_ps)] * 100
lo2, hi2 = np.percentile(boots_ps, [2.5, 97.5])
print(f"Poststratified (rev-wt, universe rev mix) point: {point_ps:+.3f}%")
print(f"Poststratify-inside-bootstrap 95% CI: [{lo2:+.3f}%, {hi2:+.3f}%]  (sd {boots_ps.std():.3f}, n={len(boots_ps)})")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    'exp': EXP, 'window': [START_DS, END_DS],
    'n_titles_defined': int(len(p)),
    'rev_weighted_point_pct': round(point_rev,3),
    'rev_weighted_title_ci': [round(lo,3), round(hi,3)],
    'rev_weighted_boot_sd': round(float(boots.std()),3),
    'poststrat_inside_point_pct': round(point_ps,3),
    'poststrat_inside_ci': [round(lo2,3), round(hi2,3)],
    'poststrat_inside_boot_sd': round(float(boots_ps.std()),3),
}, default=str))
