# Databricks notebook source
# MAGIC %md
# MAGIC # v8 — NPV_TVT (non-power-viewer TVT), Statsig-faithful definition
# MAGIC Power viewer (per Statsig): latest `device_okr_daily` snapshot in [RUN_START−7, first_exposure_ds]
# MAGIC has visit_days_last28d_count ≥ 8 AND (tvt_sec_last28+linear_tvt_sec_last28)/3600/visit_days > 4.
# MAGIC NPV_TVT = per-device TVT from `statsig_video_session_metrics_daily` over the analysis window,
# MAGIC restricted to non-power-viewer devices (flag is pre-exposure → valid population cut).
# MAGIC Outputs raw + CUPED Welch lift, CI, p for NPV and (context) PV subpopulations + flag balance by arm.

# COMMAND ----------

from pyspark.sql import functions as F
import scipy.stats as st, math, json
import pandas as pd

dbutils.widgets.text('EXP', 'ads_abf_3_v8')
dbutils.widgets.text('RUN_START', '2026-07-23')   # experiment start (flag anchor + exposure window start)
dbutils.widgets.text('START_DS', '2026-08-12')    # analysis window
dbutils.widgets.text('END_DS', '2026-08-20')
dbutils.widgets.text('PRE_START', '2026-07-09')   # CUPED covariate window
dbutils.widgets.text('PRE_END', '2026-07-22')
EXP = dbutils.widgets.get('EXP'); RUN_START = dbutils.widgets.get('RUN_START')
START_DS = dbutils.widgets.get('START_DS'); END_DS = dbutils.widgets.get('END_DS')
PRE_START = dbutils.widgets.get('PRE_START'); PRE_END = dbutils.widgets.get('PRE_END')
print(f"EXP={EXP} run_start={RUN_START} window={START_DS}..{END_DS} pre={PRE_START}..{PRE_END}")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TEMP VIEW exp AS
SELECT device_id, MIN(group_name) AS variant,
       MIN(timestamp) AS first_exposure_ts, MIN(DATE(timestamp)) AS first_exposure_ds
FROM core_dev.statsig.exposures
WHERE experiment_id = '{EXP}' AND DATE(timestamp) BETWEEN '{RUN_START}' AND '{END_DS}'
GROUP BY device_id
HAVING COUNT(DISTINCT group_name) = 1
""")

spark.sql(f"""
CREATE OR REPLACE TEMP VIEW flags AS
SELECT e.device_id, e.variant, e.first_exposure_ts,
  COALESCE(
    MAX_BY(
      CASE WHEN okr.visit_days_last28d_count >= 8
            AND (okr.tvt_sec_last28 + okr.linear_tvt_sec_last28) / 3600.0
                / NULLIF(okr.visit_days_last28d_count, 0) > 4
           THEN TRUE ELSE FALSE END,
      okr.ds), FALSE) AS power_viewer_flag
FROM exp e
LEFT JOIN core_prod.tubidw.device_okr_daily okr
  ON e.device_id = okr.device_id
 AND okr.ds BETWEEN date_add('{RUN_START}', -7) AND e.first_exposure_ds
GROUP BY e.device_id, e.variant, e.first_exposure_ts
""")

bal = spark.sql("""
SELECT variant, COUNT(*) n, AVG(CASE WHEN power_viewer_flag THEN 1.0 ELSE 0.0 END) pv_share
FROM flags GROUP BY variant ORDER BY variant
""").toPandas()
print(bal.to_string(index=False))

# COMMAND ----------

# outcome + CUPED covariate per device (Statsig TVT source)
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW dev AS
WITH y AS (
  SELECT f.device_id, SUM(vs.tvt) AS y_tvt
  FROM flags f JOIN core_prod.tubidw.statsig_video_session_metrics_daily vs
    ON f.device_id = vs.device_id
  WHERE vs.ds BETWEEN '{START_DS}' AND '{END_DS}' AND vs.ds >= DATE(f.first_exposure_ts)
  GROUP BY f.device_id
),
x AS (
  SELECT f.device_id, SUM(vs.tvt) AS x_tvt
  FROM flags f JOIN core_prod.tubidw.statsig_video_session_metrics_daily vs
    ON f.device_id = vs.device_id
  WHERE vs.ds BETWEEN '{PRE_START}' AND '{PRE_END}'
  GROUP BY f.device_id
)
SELECT f.variant, f.power_viewer_flag,
       COALESCE(y.y_tvt, 0) AS y_tvt, COALESCE(x.x_tvt, 0) AS x_tvt
FROM flags f
LEFT JOIN y ON f.device_id = y.device_id
LEFT JOIN x ON f.device_id = x.device_id
""")

def welch(m1,v1,n1,m0,v0,n0):
    se = math.sqrt(v1/n1+v0/n0); diff = m1-m0
    dfree = (v1/n1+v0/n0)**2/((v1/n1)**2/(n1-1)+(v0/n0)**2/(n0-1))
    tc = st.t.ppf(0.975, dfree)
    return dict(lift_pct=round(diff/m0*100,3), ci=[round((diff-tc*se)/m0*100,3), round((diff+tc*se)/m0*100,3)],
                p=2*st.t.sf(abs(diff/se), dfree))

results = []
for label, flag in [('NPV', 'NOT power_viewer_flag'), ('PV', 'power_viewer_flag')]:
    cov = spark.sql(f"SELECT covar_samp(y_tvt,x_tvt) c, var_samp(x_tvt) vx, avg(x_tvt) mx FROM dev WHERE {flag}").collect()[0]
    theta = float(cov['c'])/float(cov['vx']) if cov['vx'] and float(cov['vx'])>0 else 0.0
    mx = float(cov['mx'] or 0)
    agg = spark.sql(f"""
      SELECT variant, COUNT(*) n,
        avg(y_tvt) m, var_samp(y_tvt) v,
        avg(y_tvt - {theta}*(x_tvt - {mx})) ma, var_samp(y_tvt - {theta}*(x_tvt - {mx})) va
      FROM dev WHERE {flag} GROUP BY variant
    """).toPandas()
    for c0 in ['m','v','ma','va']: agg[c0] = pd.to_numeric(agg[c0]).astype(float)
    t = agg[agg.variant=='Test'].iloc[0]; c = agg[agg.variant=='Control'].iloc[0]
    raw = welch(t['m'],t['v'],int(t['n']),c['m'],c['v'],int(c['n']))
    cup = welch(t['ma'],t['va'],int(t['n']),c['ma'],c['va'],int(c['n']))
    results.append(dict(subpop=label, n_test=int(t['n']), n_control=int(c['n']), theta=round(theta,4),
                        raw_lift=raw['lift_pct'], raw_ci=raw['ci'], raw_p=raw['p'],
                        cuped_lift=cup['lift_pct'], cuped_ci=cup['ci'], cuped_p=cup['p']))
    print(label, results[-1])

# COMMAND ----------

dbutils.notebook.exit(json.dumps(dict(
    exp=EXP, window=[START_DS, END_DS],
    balance=bal.to_dict('records'),
    results=results), default=str))
