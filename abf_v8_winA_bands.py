# Databricks notebook source
# MAGIC %md
# MAGIC # v8 Window A — per-ABF1-band on-title lift + dense-band over-prune read
# MAGIC Window A = launch (2026-07-23) → last complete pre-top-up day (2026-08-10).
# MAGIC Titles = v8-treated ∩ June ABF1 universe (~141K), banded by ABF1 control cue points
# MAGIC (1–3 / 4–6 / 7–9 / 10–12 / 13+, plus 0). Device-level ToT-per-band Welch lifts
# MAGIC (same estimator as `abf_v7_decile_concentration` block A).
# MAGIC (C) splits the dense bands by v8-below-control (n_cue_points < abf1_cue_points) —
# MAGIC the direct test of the v7-decile-8 over-prune recurrence.
# MAGIC (B) baseline-window revenue weights → measured treated-wide + global contribution.

# COMMAND ----------

from pyspark.sql import functions as F
import math, json
import pandas as pd
import scipy.stats as st

dbutils.widgets.text('EXP', 'ads_abf_3_v8')
dbutils.widgets.text('START_DS', '2026-07-23')
dbutils.widgets.text('END_DS', '2026-08-10')
dbutils.widgets.text('WIN_START', '2026-07-09')   # baseline (pre-launch) for weights
dbutils.widgets.text('WIN_END', '2026-07-22')
dbutils.widgets.text('TITLES_TABLE', 'core_dev.dsa.temp_bp_abf_v8_titles')
dbutils.widgets.text('IMP_PLAT_FILTER', '')   # e.g. "AND i.platform = 'web'" — scopes the (B) revenue-share denominator to the platform
EXP = dbutils.widgets.get('EXP')
START_DS = dbutils.widgets.get('START_DS')
END_DS = dbutils.widgets.get('END_DS')
WIN_START = dbutils.widgets.get('WIN_START')
WIN_END = dbutils.widgets.get('WIN_END')
V8 = dbutils.widgets.get('TITLES_TABLE')
IMP_PLAT_FILTER = dbutils.widgets.get('IMP_PLAT_FILTER')
UNIVERSE = 'core_dev.dsa.temp_bp_abf1_universe'
ADV_EXCL = "1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452"
print(f"EXP={EXP}  window={START_DS}..{END_DS}  baseline={WIN_START}..{WIN_END}")

# COMMAND ----------

# banded title set: v8-treated ∩ June universe, with below-control flag
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW bands AS
SELECT u.content_id,
  CASE WHEN u.abf1_cue_points <= 0 THEN '0'
       WHEN u.abf1_cue_points <= 3 THEN '1-3'
       WHEN u.abf1_cue_points <= 6 THEN '4-6'
       WHEN u.abf1_cue_points <= 9 THEN '7-9'
       WHEN u.abf1_cue_points <= 12 THEN '10-12'
       ELSE '13+' END AS band,
  CASE WHEN t.n_cue_points < u.abf1_cue_points THEN 1 ELSE 0 END AS below_ctrl,
  COALESCE(u.content_type, 'UNKNOWN') AS content_type
FROM {UNIVERSE} u JOIN {V8} t ON u.content_id = t.content_id
""")
print(spark.sql("SELECT band, below_ctrl, COUNT(*) n FROM bands GROUP BY 1,2 ORDER BY 1,2").toPandas().to_string(index=False))

# COMMAND ----------

# device×title outcomes on banded titles, Window A
spark.sql(f"""
CREATE OR REPLACE TEMP VIEW devtitle AS
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
  WHERE v.content_id IN (SELECT content_id FROM bands)
  GROUP BY e.device_id, e.variant, v.content_id
),
imp AS (
  SELECT i.device_id, CAST(i.content_id AS INT) AS content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS rev
  FROM core_prod.ads.impressions i
  JOIN (SELECT device_id, MIN(timestamp) AS first_exposure_ts FROM core_dev.statsig.exposures
        WHERE experiment_id = '{EXP}' GROUP BY device_id) e
    ON i.device_id = e.device_id AND i.ts >= e.first_exposure_ts
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '{START_DS}' AND i.date <= '{END_DS}' AND i.unbillable = 'f'
    AND i.content_id IN (SELECT CAST(content_id AS STRING) FROM bands)
  GROUP BY i.device_id, CAST(i.content_id AS INT)
)
SELECT vs.device_id, vs.variant, vs.content_id, b.band, b.below_ctrl, b.content_type,
       vs.tvt_mins, COALESCE(imp.rev, 0) AS rev
FROM vs JOIN bands b ON vs.content_id = b.content_id
LEFT JOIN imp ON vs.device_id = imp.device_id AND vs.content_id = imp.content_id
""")

# COMMAND ----------

def welch_lifts(group_expr, where=""):
    df = spark.sql(f"""
      WITH dev AS (
        SELECT {group_expr} AS grp, variant, device_id, SUM(rev) AS rev, SUM(tvt_mins) AS tvt
        FROM devtitle {where} GROUP BY {group_expr}, variant, device_id
      )
      SELECT grp, variant, AVG(rev) m_rev, var_samp(rev) v_rev,
             AVG(tvt) m_tvt, var_samp(tvt) v_tvt, COUNT(*) n
      FROM dev GROUP BY grp, variant
    """).toPandas()
    for c0 in ['m_rev','v_rev','m_tvt','v_tvt']:
        df[c0] = pd.to_numeric(df[c0]).astype(float)
    def ci(t, c, mp, vp):
        m1,v1,n1 = float(t[mp]),float(t[vp]),int(t['n'])
        m0,v0,n0 = float(c[mp]),float(c[vp]),int(c['n'])
        if m0 <= 0 or v1/n1 + v0/n0 <= 0:
            return None, None, None, None
        se = math.sqrt(v1/n1+v0/n0); diff = m1-m0
        dfree = (v1/n1+v0/n0)**2 / ((v1/n1)**2/(n1-1) + (v0/n0)**2/(n0-1))
        tc = st.t.ppf(0.975, dfree)
        p = 2*st.t.sf(abs(diff/se), dfree)
        return diff/m0, (diff-tc*se)/m0, (diff+tc*se)/m0, p
    out = []
    for g in sorted(df['grp'].unique()):
        t = df[(df.grp==g)&(df.variant=='Test')]; c = df[(df.grp==g)&(df.variant=='Control')]
        if t.empty or c.empty: continue
        t=t.iloc[0]; c=c.iloc[0]
        rl,rlo,rhi,rp = ci(t,c,'m_rev','v_rev')
        tl,tlo,thi,tp = ci(t,c,'m_tvt','v_tvt')
        if rl is None and tl is None:
            continue
        rl,rlo,rhi = (x if x is not None else float('nan') for x in (rl,rlo,rhi))
        tl,tlo,thi = (x if x is not None else float('nan') for x in (tl,tlo,thi))
        out.append(dict(grp=g, rev_lift_pct=rl*100, rev_lo=rlo*100, rev_hi=rhi*100, rev_p=rp,
                        tvt_lift_pct=tl*100, tvt_lo=tlo*100, tvt_hi=thi*100, tvt_p=tp,
                        n_test=int(t['n']), n_ctrl=int(c['n'])))
    return pd.DataFrame(out)

# (A) per-band lifts
band_lifts = welch_lifts("band")
print("(A) per-ABF1-band on-title lifts (device-level ToT-per-band, Window A):")
print(band_lifts.round(3).to_string(index=False))

# COMMAND ----------

# (A2) per band x content_type (tests the sparse-band gating hypothesis)
band_type = welch_lifts("CONCAT(band, '|', content_type)")
print("(A2) per band x content_type:")
print(band_type.round(3).to_string(index=False))

# COMMAND ----------

# (C) dense bands split by below-control (the over-prune read)
dense_split = welch_lifts("CONCAT(band, '|below=', below_ctrl)", "WHERE band IN ('10-12','13+')")
print("(C) dense bands split by v8-below-control:")
print(dense_split.round(3).to_string(index=False))

# COMMAND ----------

# (B) baseline-window revenue weights per band (+ total business revenue)
rev_share = spark.sql(f"""
WITH imp AS (
  SELECT CAST(i.content_id AS INT) AS content_id,
         SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                  AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS rev
  FROM core_prod.ads.impressions i
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '{WIN_START}' AND i.date <= '{WIN_END}' AND i.unbillable = 'f' {IMP_PLAT_FILTER}
  GROUP BY CAST(i.content_id AS INT)
)
SELECT COALESCE(b.band, '_not_banded') AS band, SUM(imp.rev) AS rev
FROM imp LEFT JOIN bands b ON imp.content_id = b.content_id
GROUP BY COALESCE(b.band, '_not_banded')
""").toPandas()
rev_share['rev'] = pd.to_numeric(rev_share['rev']).astype(float)
total_rev = rev_share['rev'].sum()
banded_rev = rev_share[rev_share.band != '_not_banded']['rev'].sum()
print("(B) baseline rev by band:")
print(rev_share.to_string(index=False))
print(f"banded (v8∩universe) rev share of total: {banded_rev/total_rev*100:.2f}%")

# COMMAND ----------

# (D) aggregate: treated-wide (rev-weighted band lifts) + global contribution
rmap = rev_share.set_index('band')['rev'].to_dict()
num = wsum = 0.0
rows = []
for _, r in band_lifts.iterrows():
    w = rmap.get(r['grp'], 0.0)
    num += r['rev_lift_pct']/100 * w; wsum += w
    rows.append(dict(band=r['grp'], rev_lift_pct=round(r['rev_lift_pct'],3),
                     rev_weight_share=round(w/banded_rev,4),
                     global_contrib_pp=round(r['rev_lift_pct']/100 * w / total_rev * 100, 4)))
treated_wide = num/wsum*100
global_pp = num/total_rev*100
print(pd.DataFrame(rows).to_string(index=False))
print(f"treated-wide rev lift (rev-wtd bands): {treated_wide:+.3f}%")
print(f"global contribution (÷ total rev):     {global_pp:+.3f}pp")
print(f"[compare: v7 ABF1-wide +3.68% → global +1.36% @37.03% share; v6 +6.02% → +2.2%]")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    'band_lifts': band_lifts.round(5).to_dict('records'),
    'band_type_lifts': band_type.round(5).to_dict('records'),
    'dense_split': dense_split.round(5).to_dict('records'),
    'rev_share': rev_share.round(2).to_dict('records'),
    'banded_rev_share_pct': round(banded_rev/total_rev*100, 3),
    'treated_wide_rev_lift_pct': round(treated_wide, 3),
    'global_contrib_pp': round(global_pp, 4),
}, default=str))
