# Databricks notebook source
# MAGIC %md
# MAGIC # ads_abf_3_v6 — CUPED variance-reduced significance
# MAGIC ABF1 (Control) vs ABF3 (Test). For TVT / unbudgeted_revenue / unbudgeted_impressions,
# MAGIC report RAW and **CUPED**-adjusted lift + 95% CI + variance-reduction %.
# MAGIC Matrix: {ITT, ToT} × {all-titles, ABF3-titles-only}.
# MAGIC
# MAGIC CUPED: Y_adj = Y - θ(X - X̄), θ = cov(Y,X)/var(X) pooled across arms.
# MAGIC Covariate X = device's PRE-PERIOD (2026-05-15..05-28) value of the SAME metric
# MAGIC (measured over all titles the device watched pre-launch). Pre-period ends before
# MAGIC launch (2026-05-29) so there is no leakage.

# COMMAND ----------

from pyspark.sql import functions as F
import scipy.stats as st, math, json
import pandas as pd

dbutils.widgets.text('EXP', 'ads_abf_3_v8')
dbutils.widgets.text('START_DS', '2026-07-23')
dbutils.widgets.text('END_DS', '2026-08-10')
dbutils.widgets.text('PRE_START', '2026-07-09')
dbutils.widgets.text('PRE_END', '2026-07-22')
dbutils.widgets.text('TITLES', 'core_dev.dsa.temp_bp_abf_v8_titles')
dbutils.widgets.text('POPULATIONS', 'ITT,ToT')
dbutils.widgets.text('FIRST_EXP_MIN', '')   # if set, keep only devices first exposed >= this ts (fresh cohort)
dbutils.widgets.text('ACTIVE_FROM', '')      # start ds for the Active filter; defaults to START_DS. Set to launch ds so Active = watched since exposure (treatment-independent)
EXP = dbutils.widgets.get('EXP')
START_DS = dbutils.widgets.get('START_DS')
END_DS = dbutils.widgets.get('END_DS')   # cap at last complete day
PRE_START = dbutils.widgets.get('PRE_START')
PRE_END = dbutils.widgets.get('PRE_END')
TITLES = dbutils.widgets.get('TITLES')
POPULATIONS = [p.strip() for p in dbutils.widgets.get('POPULATIONS').split(',')]
FIRST_EXP_MIN = dbutils.widgets.get('FIRST_EXP_MIN').strip()
ACTIVE_FROM = dbutils.widgets.get('ACTIVE_FROM').strip() or START_DS
print(f"EXP={EXP}  window={START_DS}..{END_DS}  pre={PRE_START}..{PRE_END}")
ADV_EXCL = "1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452"
METRICS = ['tvt', 'rev', 'imps']

# COMMAND ----------

# ---- exposures (assignment) ----
spark.sql(f"""
  CREATE OR REPLACE TEMP VIEW exp AS
  SELECT device_id, group_name AS variant, MIN(timestamp) AS first_exposure_ts
  FROM core_dev.statsig.exposures WHERE experiment_id = '{EXP}'
  GROUP BY device_id, group_name
  {"HAVING MIN(timestamp) >= '" + FIRST_EXP_MIN + "'" if FIRST_EXP_MIN else ""}
""")

# ---- PRE-PERIOD covariate per device (all titles, before launch) ----
spark.sql(f"""
  CREATE OR REPLACE TEMP VIEW pre AS
  WITH vs AS (
    SELECT e.device_id, SUM(v.tvt_millisec/1000.0/60.0) AS x_tvt
    FROM exp e JOIN core_prod.tubidw.video_session v ON e.device_id = v.device_id
    WHERE v.ds >= '{PRE_START}' AND v.ds <= '{PRE_END}'
    GROUP BY e.device_id
  ),
  im AS (
    SELECT e.device_id,
      SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
               AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS x_rev,
      SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
               AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN 1 ELSE 0 END) AS x_imps
    FROM exp e JOIN core_prod.ads.impressions i ON e.device_id = i.device_id
    JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
    WHERE i.date >= '{PRE_START}' AND i.date <= '{PRE_END}' AND i.unbillable = 'f'
    GROUP BY e.device_id
  )
  SELECT e.device_id,
         COALESCE(vs.x_tvt,0) AS x_tvt,
         COALESCE(im.x_rev,0) AS x_rev,
         COALESCE(im.x_imps,0) AS x_imps
  FROM exp e LEFT JOIN vs ON e.device_id=vs.device_id LEFT JOIN im ON e.device_id=im.device_id
""")

# COMMAND ----------

# ---- experiment-period outcome per device, parameterized by scope ----
def build_outcome(scope):
    abf3_vs = "AND v.content_id IN (SELECT content_id FROM %s)" % TITLES if scope=='abf3' else ""
    abf3_im = "AND i.content_id IN (SELECT CAST(content_id AS STRING) FROM %s)" % TITLES if scope=='abf3' else ""
    spark.sql(f"""
      CREATE OR REPLACE TEMP VIEW outc_{scope} AS
      WITH vs AS (
        SELECT e.device_id, SUM(v.tvt_millisec/1000.0/60.0) AS y_tvt
        FROM exp e JOIN core_prod.tubidw.video_session v
          ON e.device_id=v.device_id AND v.start_ts>=e.first_exposure_ts AND v.ds>='{START_DS}' AND v.ds<='{END_DS}'
        WHERE 1=1 {abf3_vs}
        GROUP BY e.device_id
      ),
      im AS (
        SELECT e.device_id,
          SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                   AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS y_rev,
          SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                   AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN 1 ELSE 0 END) AS y_imps
        FROM exp e JOIN core_prod.ads.impressions i
          ON e.device_id=i.device_id AND i.ts>=e.first_exposure_ts
        JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id=c.id
        WHERE i.date>='{START_DS}' AND i.date<='{END_DS}' AND i.unbillable='f' {abf3_im}
        GROUP BY e.device_id
      )
      SELECT e.device_id, e.variant,
             COALESCE(vs.y_tvt,0) AS y_tvt,
             COALESCE(im.y_rev,0) AS y_rev,
             COALESCE(im.y_imps,0) AS y_imps
      FROM exp e LEFT JOIN vs ON e.device_id=vs.device_id LEFT JOIN im ON e.device_id=im.device_id
    """)

# ---- ToT device set: watched >=1 ABF3 title (tvt>0 on experiment titles) ----
spark.sql(f"""
  CREATE OR REPLACE TEMP VIEW tot_dev AS
  SELECT DISTINCT e.device_id
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id=v.device_id AND v.start_ts>=e.first_exposure_ts AND v.ds>='{START_DS}' AND v.ds<='{END_DS}'
  WHERE v.content_id IN (SELECT content_id FROM {TITLES})
""")

# ---- Active device set: watched >=1 session on ANY title post-exposure ----
spark.sql(f"""
  CREATE OR REPLACE TEMP VIEW active_dev AS
  SELECT DISTINCT e.device_id
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id=v.device_id AND v.start_ts>=e.first_exposure_ts AND v.ds>='{ACTIVE_FROM}' AND v.ds<='{END_DS}'
""")

# COMMAND ----------

# Compute raw + CUPED stats for one (scope, population). Returns list of metric dicts.
def analyze(scope, population):
    build_outcome(scope)
    pop_filter = {'ToT': "JOIN tot_dev td ON o.device_id = td.device_id",
                  'Active': "JOIN active_dev ad ON o.device_id = ad.device_id",
                  'ITT': ""}[population]
    # join outcome + covariate at device level
    df = spark.sql(f"""
      SELECT o.variant,
             o.y_tvt, o.y_rev, o.y_imps,
             p.x_tvt, p.x_rev, p.x_imps
      FROM outc_{scope} o
      JOIN pre p ON o.device_id = p.device_id
      {pop_filter}
    """)
    df.createOrReplaceTempView('joined')

    # pooled theta per metric = cov(Y,X)/var(X) over ALL devices (both arms)
    cov = spark.sql("""
      SELECT
        covar_samp(y_tvt,x_tvt) AS c_tvt, var_samp(x_tvt) AS vx_tvt,
        covar_samp(y_rev,x_rev) AS c_rev, var_samp(x_rev) AS vx_rev,
        covar_samp(y_imps,x_imps) AS c_imps, var_samp(x_imps) AS vx_imps,
        avg(x_tvt) AS mx_tvt, avg(x_rev) AS mx_rev, avg(x_imps) AS mx_imps
      FROM joined
    """).collect()[0]
    theta = {}
    xbar = {}
    for m in METRICS:
        vx = float(cov['vx_'+m]); theta[m] = float(cov['c_'+m])/vx if vx>0 else 0.0
        xbar[m] = float(cov['mx_'+m])

    # per-arm moments of Y (raw) and Y_adj = Y - theta*(X - xbar)
    agg = spark.sql(f"""
      SELECT variant,
        COUNT(*) AS n,
        avg(y_tvt) m_tvt, var_samp(y_tvt) v_tvt,
        avg(y_rev) m_rev, var_samp(y_rev) v_rev,
        avg(y_imps) m_imps, var_samp(y_imps) v_imps,
        avg(y_tvt - {theta['tvt']}*(x_tvt - {xbar['tvt']})) ma_tvt, var_samp(y_tvt - {theta['tvt']}*(x_tvt - {xbar['tvt']})) va_tvt,
        avg(y_rev - {theta['rev']}*(x_rev - {xbar['rev']})) ma_rev, var_samp(y_rev - {theta['rev']}*(x_rev - {xbar['rev']})) va_rev,
        avg(y_imps - {theta['imps']}*(x_imps - {xbar['imps']})) ma_imps, var_samp(y_imps - {theta['imps']}*(x_imps - {xbar['imps']})) va_imps
      FROM joined GROUP BY variant
    """).toPandas()
    for c in agg.columns:
        if c != 'variant': agg[c] = pd.to_numeric(agg[c]).astype(float)
    t = agg[agg.variant=='Test'].iloc[0]; c = agg[agg.variant=='Control'].iloc[0]

    def welch(m1,v1,n1,m0,v0,n0):
        se=math.sqrt(v1/n1+v0/n0); diff=m1-m0
        dfree=(v1/n1+v0/n0)**2/((v1/n1)**2/(n1-1)+(v0/n0)**2/(n0-1))
        tcrit=st.t.ppf(0.975,dfree)
        return dict(lift_pct=diff/m0*100, ci_lo=(diff-tcrit*se)/m0*100, ci_hi=(diff+tcrit*se)/m0*100,
                    p=2*st.t.sf(abs(diff/se),dfree), se=se)

    out=[]
    n1=int(t['n']); n0=int(c['n'])
    for m in METRICS:
        raw = welch(t['m_'+m],t['v_'+m],n1,c['m_'+m],c['v_'+m],n0)
        cup = welch(t['ma_'+m],t['va_'+m],n1,c['ma_'+m],c['va_'+m],n0)
        # variance reduction: 1 - var_adj/var_raw (pooled avg of arm variances)
        vr = 1 - ((t['va_'+m]+c['va_'+m])/2.0)/((t['v_'+m]+c['v_'+m])/2.0) if (t['v_'+m]+c['v_'+m])>0 else 0.0
        out.append(dict(scope=scope, population=population, metric=m, theta=round(theta[m],5),
                        n_test=n1, n_control=n0,
                        raw_lift=round(raw['lift_pct'],3), raw_ci=[round(raw['ci_lo'],3),round(raw['ci_hi'],3)], raw_p=raw['p'],
                        cuped_lift=round(cup['lift_pct'],3), cuped_ci=[round(cup['ci_lo'],3),round(cup['ci_hi'],3)], cuped_p=cup['p'],
                        var_reduction_pct=round(vr*100,2),
                        ci_width_raw=round(raw['ci_hi']-raw['ci_lo'],3), ci_width_cuped=round(cup['ci_hi']-cup['ci_lo'],3)))
    return out

# COMMAND ----------

results=[]
for population in POPULATIONS:
    for scope in ['all','abf3']:
        results += analyze(scope, population)

pdf = pd.DataFrame(results)
print(pdf[['population','scope','metric','raw_lift','cuped_lift','var_reduction_pct','ci_width_raw','ci_width_cuped','cuped_p']].to_string(index=False))

# COMMAND ----------

dbutils.notebook.exit(json.dumps(results, default=str))
