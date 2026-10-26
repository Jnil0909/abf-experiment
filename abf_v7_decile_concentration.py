# Databricks notebook source
# MAGIC %md
# MAGIC # v7 OTT — per-decile contribution to global revenue lift (concentration check)
# MAGIC For each ABF1-density decile: experiment rev lift, the decile's revenue weight in the
# MAGIC full ABF1 universe, and the contribution `lift_d × rev_d` to the global lift.
# MAGIC Reproduces blocks (A) and (B) of `ads_abf_3_v7__global_graduation_projection`
# MAGIC (OTT params) and reports how concentrated the +1.36% global lift is.

# COMMAND ----------

from pyspark.sql import functions as F
import numpy as np, math, json
import pandas as pd
import scipy.stats as st

# params (default v7 OTT; widgets allow v6 too)
dbutils.widgets.text('EXP', 'ads_abf_3_v7')
dbutils.widgets.text('START_DS', '2026-06-17')
dbutils.widgets.text('END_DS', '2026-06-22')
dbutils.widgets.text('WIN_START', '2026-05-07')
dbutils.widgets.text('WIN_END', '2026-05-20')
EXP = dbutils.widgets.get('EXP')
START_DS = dbutils.widgets.get('START_DS')
END_DS = dbutils.widgets.get('END_DS')
WIN_START = dbutils.widgets.get('WIN_START')
WIN_END = dbutils.widgets.get('WIN_END')
PLATFORM_TYPE = 'ALL'      # OTT == ALL (matches v6)
TITLES = 'core_dev.dsa.temp_bp_abf_v6_exp_titles'
UNIVERSE = 'core_dev.dsa.temp_bp_abf1_universe'
ADV_EXCL = "1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452"
IMP_PLAT_FILTER = ""
print(f"EXP={EXP}  window={START_DS}..{END_DS}  baseline={WIN_START}..{WIN_END}")

# COMMAND ----------

# decile edges from experiment-title density
exp_dens = spark.sql(f"SELECT u.abf1_cue_points FROM {UNIVERSE} u WHERE u.in_experiment = 1").toPandas()
exp_dens['abf1_cue_points'] = pd.to_numeric(exp_dens['abf1_cue_points']).astype(float)
edges = pd.qcut(exp_dens['abf1_cue_points'], 10, retbins=True, duplicates='drop')[1]
cuts = list(edges)[1:-1]
n_dec = len(cuts) + 1
def decile_case(col):
    whens = " ".join(f"WHEN {col} <= {c} THEN {i}" for i, c in enumerate(cuts))
    return f"CASE {whens} ELSE {len(cuts)} END"
print(f"n_deciles={n_dec}; interior cuts={cuts}")

# COMMAND ----------

# (A) experiment per-decile revenue lift (device-level ToT, ABF3 titles only)
DCASE = decile_case('u.abf1_cue_points')
lift_df = spark.sql(f"""
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
  SELECT vs.device_id, vs.variant, vs.content_id, vs.tvt_mins, COALESCE(imp.rev, 0) AS rev
  FROM vs LEFT JOIN imp ON vs.device_id = imp.device_id AND CAST(vs.content_id AS STRING) = imp.content_id
),
tagged AS (
  SELECT dt.device_id, dt.variant, {DCASE} AS decile, dt.tvt_mins, dt.rev
  FROM devtitle dt JOIN {UNIVERSE} u ON dt.content_id = u.content_id
),
dev AS (
  SELECT decile, variant, device_id, SUM(rev) AS rev, SUM(tvt_mins) AS tvt
  FROM tagged GROUP BY decile, variant, device_id
)
SELECT decile, variant, AVG(rev) AS m_rev, var_samp(rev) AS v_rev,
       AVG(tvt) AS m_tvt, var_samp(tvt) AS v_tvt, COUNT(*) AS n
FROM dev GROUP BY decile, variant
""").toPandas()
for col in ['m_rev','v_rev','m_tvt','v_tvt']:
    lift_df[col] = pd.to_numeric(lift_df[col]).astype(float)

def lift_ci(t, c, mp, vp):
    m1,v1,n1 = float(t[mp]),float(t[vp]),int(t['n'])
    m0,v0,n0 = float(c[mp]),float(c[vp]),int(c['n'])
    se = math.sqrt(v1/n1+v0/n0); diff=m1-m0
    df = (v1/n1+v0/n0)**2 / ((v1/n1)**2/(n1-1) + (v0/n0)**2/(n0-1))
    tcrit = st.t.ppf(0.975, df)
    return diff/m0, (diff-tcrit*se)/m0, (diff+tcrit*se)/m0

lifts = {}
for d in sorted(lift_df['decile'].unique()):
    t = lift_df[(lift_df.decile==d)&(lift_df.variant=='Test')]
    c = lift_df[(lift_df.decile==d)&(lift_df.variant=='Control')]
    if t.empty or c.empty: continue
    t=t.iloc[0]; c=c.iloc[0]
    rl, rlo, rhi = lift_ci(t,c,'m_rev','v_rev')
    tl, tlo, thi = lift_ci(t,c,'m_tvt','v_tvt')
    lifts[int(d)] = dict(rev_lift=rl, rev_lo=rlo, rev_hi=rhi, tvt_lift=tl,
                         n_test=int(t['n']), n_ctrl=int(c['n']))

# COMMAND ----------

# (B) ABF1-universe per-decile revenue weight (baseline window)
UCASE = decile_case('abf1_cue_points')
rev_share = spark.sql(f"""
WITH uni_dec AS (SELECT content_id, {UCASE} AS decile FROM {UNIVERSE}),
imp AS (
  SELECT CAST(i.content_id AS INT) AS content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS rev
  FROM core_prod.ads.impressions i
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '{WIN_START}' AND i.date <= '{WIN_END}' AND i.unbillable = 'f' {IMP_PLAT_FILTER}
  GROUP BY CAST(i.content_id AS INT)
)
SELECT COALESCE(CAST(d.decile AS INT), -1) AS decile, SUM(imp.rev) AS rev
FROM imp LEFT JOIN uni_dec d ON imp.content_id = d.content_id
GROUP BY COALESCE(CAST(d.decile AS INT), -1)
""").toPandas()
rev_share['rev'] = pd.to_numeric(rev_share['rev']).astype(float)
rev_share['decile'] = rev_share['decile'].astype(int)

total_rev_all = rev_share['rev'].sum()
abf1_rev = rev_share[rev_share.decile >= 0]['rev'].sum()
abf1_rev_share = abf1_rev / total_rev_all

# COMMAND ----------

# (B2) within-decile coverage: # experiment titles per decile, and exp-title revenue
#      as a share of that decile's FULL universe revenue (the within-decile representativeness)
cov = spark.sql(f"""
WITH uni_dec AS (SELECT content_id, in_experiment, {UCASE} AS decile FROM {UNIVERSE}),
imp AS (
  SELECT CAST(i.content_id AS INT) AS content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS rev
  FROM core_prod.ads.impressions i
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '{WIN_START}' AND i.date <= '{WIN_END}' AND i.unbillable = 'f'
  GROUP BY CAST(i.content_id AS INT)
)
SELECT d.decile,
       COUNT(*) AS n_titles_universe,
       SUM(d.in_experiment) AS n_titles_exp,
       SUM(imp.rev) AS rev_universe,
       SUM(CASE WHEN d.in_experiment=1 THEN imp.rev ELSE 0 END) AS rev_exp
FROM uni_dec d JOIN imp ON d.content_id = imp.content_id
GROUP BY d.decile ORDER BY d.decile
""").toPandas()
for c0 in ['n_titles_universe','n_titles_exp','rev_universe','rev_exp']:
    cov[c0] = pd.to_numeric(cov[c0]).astype(float)
cov['decile'] = cov['decile'].astype(int)
cov['exp_title_frac'] = cov['n_titles_exp'] / cov['n_titles_universe']
cov['exp_rev_coverage'] = cov['rev_exp'] / cov['rev_universe']   # how much of decile's universe rev is exp titles
print("within-decile coverage (how representative is the exp sample inside each decile):")
print(cov[['decile','n_titles_universe','n_titles_exp','exp_title_frac','exp_rev_coverage']].to_string(index=False))

# COMMAND ----------

# (C) per-decile contribution table
rev_map = rev_share[rev_share.decile >= 0].set_index('decile')['rev'].to_dict()
rows = []
num_rev = wsum = 0.0
for d in sorted(rev_map):
    if d not in lifts: continue
    rev_d = rev_map[d]
    L = lifts[d]
    contrib_abf1wide = L['rev_lift'] * rev_d          # numerator term for ABF1-wide
    num_rev += contrib_abf1wide
    wsum += rev_d
    rows.append(dict(decile=d, rev_lift_pct=L['rev_lift']*100,
                     rev_lo_pct=L['rev_lo']*100, rev_hi_pct=L['rev_hi']*100,
                     tvt_lift_pct=L['tvt_lift']*100,
                     abf1_rev_weight=rev_d, abf1_rev_weight_share=rev_d/abf1_rev,
                     contrib_term=contrib_abf1wide, n_test=L['n_test'], n_ctrl=L['n_ctrl']))
abf1_wide_rev_lift = num_rev / wsum
global_rev_lift = num_rev / total_rev_all

df = pd.DataFrame(rows).sort_values('decile')
# each decile's share of the ABF1-wide lift numerator (the concentration metric)
df['contrib_share_of_liftnum'] = df['contrib_term'] / num_rev
df['decile_global_contrib_pp'] = df['contrib_term'] / total_rev_all * 100  # this decile's pp toward global lift

pd.set_option('display.width', 200); pd.set_option('display.max_columns', 30)
print(df[['decile','rev_lift_pct','rev_lo_pct','rev_hi_pct','tvt_lift_pct',
          'abf1_rev_weight_share','contrib_share_of_liftnum','decile_global_contrib_pp','n_test']].to_string(index=False))
print("-"*80)
print(f"ABF1 rev share of total:        {abf1_rev_share*100:.2f}%")
print(f"ABF1-wide rev lift (rev-wtd):   {abf1_wide_rev_lift*100:+.3f}%")
print(f"GLOBAL rev lift:                {global_rev_lift*100:+.3f}%")
print(f"# positive-lift deciles:        {(df.rev_lift_pct>0).sum()}/{len(df)}")
print(f"# deciles whose CI excludes 0:  {((df.rev_lo_pct>0)|(df.rev_hi_pct<0)).sum()}/{len(df)}")
# concentration summary
top = df.reindex(df.contrib_share_of_liftnum.abs().sort_values(ascending=False).index)
print(f"Top-1 decile share of lift:     {top.iloc[0].contrib_share_of_liftnum*100:.1f}% (decile {int(top.iloc[0].decile)})")
print(f"Top-2 deciles share of lift:    {top.iloc[:2].contrib_share_of_liftnum.sum()*100:.1f}%")
print(f"Top-3 deciles share of lift:    {top.iloc[:3].contrib_share_of_liftnum.sum()*100:.1f}%")
print(f"Negative-contribution deciles:  {df[df.contrib_term<0].decile.tolist()}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    'abf1_rev_share_pct': round(abf1_rev_share*100,3),
    'abf1_wide_rev_lift_pct': round(abf1_wide_rev_lift*100,3),
    'global_rev_lift_pct': round(global_rev_lift*100,3),
    'n_deciles': int(len(df)),
    'n_positive': int((df.rev_lift_pct>0).sum()),
    'per_decile': df.round(5).to_dict('records'),
    'coverage': cov.round(5).to_dict('records'),
}, default=str))
