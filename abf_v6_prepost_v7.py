# Databricks notebook source
# MAGIC %md
# MAGIC # ABF3 v6 (OTT) — pre/post-V7 clean-window analysis
# MAGIC
# MAGIC V7 (`dynamic_ads_tolerance_mtml_device_xgboost_session`) had a hard stop on **2026-06-02**.
# MAGIC ABF3 v6 OTT (`ads_abf_3_v6`) is still running. So **2026-06-03 onward is a clean, V7-free window**
# MAGIC measured on the full OTT population with ABF3 randomization intact.
# MAGIC
# MAGIC **Question:** Does ABF3 carry a standalone TVT cost when V7 is absent? If the −0.33% headline (measured
# MAGIC mostly on V7-active days) shrinks toward flat post-V7, that corroborates the V7-compounding story with
# MAGIC real power. If it stays ~−0.33%, ABF3 has a genuine standalone cost.
# MAGIC
# MAGIC **Design:**
# MAGIC - **P1_withV7** = 2026-05-29..06-02 (V7 live).  **P2_postV7** = 2026-06-03..06-10 (V7 off).
# MAGIC - Each period: ABF3 Test-vs-Control, on-title ToT, device-level, CUPED (clean pre 05-07..05-20, before any launch).
# MAGIC - Periods defined INDEPENDENTLY (a device may appear in both — assignment is fixed by randomization, so each
# MAGIC   within-period contrast is a clean RCT; we do NOT cohort on first-exposure timing, which would condition on a
# MAGIC   post-randomization outcome).
# MAGIC - **Platform cuts as a falsification test** (device_id is platform-specific → Roku & non-Roku are disjoint):
# MAGIC   - **non-Roku** = where V7 operated → expect the ABF3 TVT hit to SHRINK P1→P2 if V7 was contributing.
# MAGIC   - **Roku (placebo)** = V7 never present in either period → expect ABF3 effect STABLE P1→P2. If Roku also shrinks,
# MAGIC     the change is time/novelty drift, not V7.
# MAGIC   - **all-OTT** = production-relevant standalone number.
# MAGIC - Also reports all-titles ITT (full-OTT) per period for power.
# MAGIC
# MAGIC **Caveat:** `ads_world_cup_ad_config_v1` (an ad-config exp) turned on 06-04 — but it's WC-specific (ABF3 v6 on-title
# MAGIC set is 1,084 non-WC ABF1 titles) and independently randomized (balanced across ABF3 arms), so it doesn't bias the
# MAGIC on-title standalone estimate; it's only a (minor) caveat for the all-titles ITT temporal comparison.

# COMMAND ----------

from pyspark.sql import functions as F
import scipy.stats as st, math, json
import pandas as pd

ABF3 = 'ads_abf_3_v6'
PERIODS = {'P1_withV7': ('2026-05-29', '2026-06-02'),
           'P2_postV7': ('2026-06-03', '2026-06-10')}
PRE_START, PRE_END = '2026-05-07', '2026-05-20'
TITLES = 'core_dev.dsa.temp_bp_abf_v6_exp_titles'
ADV_EXCL = "1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452"
METRICS = ['tvt','rev']
Z = 1.959964

def welch(m1,v1,n1,m0,v0,n0):
    se=math.sqrt(v1/n1+v0/n0); diff=m1-m0
    dfree=(v1/n1+v0/n0)**2/((v1/n1)**2/(n1-1)+(v0/n0)**2/(n0-1))
    t=diff/se
    return dict(diff=diff, lift_pct=diff/m0*100,
                ci=[(diff-st.t.ppf(0.975,dfree)*se)/m0*100,(diff+st.t.ppf(0.975,dfree)*se)/m0*100],
                p=2*st.t.sf(abs(t),dfree), se=se, t=t, m1=m1, m0=m0, n1=n1, n0=n0)

# COMMAND ----------
# ## Builders parameterized by (period window, platform scope)

def build_period(tag, ps, pe, plat_vs, plat_im, on_title):
    """Create assign_/pre_/outc_/tot_ views for a (period, platform, scope) combo.
       on_title=True restricts outcomes+ToT to experiment titles (ToT/on-title); False = all-titles (for ITT)."""
    spark.sql(f"""
      CREATE OR REPLACE TEMP VIEW assign_{tag} AS
      SELECT device_id,
             MAX(CASE WHEN group_name='Test' THEN 1 ELSE 0 END) AS abf3,
             MIN(timestamp) AS first_exposure_ts
      FROM core_dev.statsig.exposures
      WHERE experiment_id='{ABF3}' AND CAST(timestamp AS DATE) BETWEEN '{ps}' AND '{pe}'
      GROUP BY device_id
    """)
    # CUPED covariate: clean pre window, platform-scoped to match
    spark.sql(f"""
      CREATE OR REPLACE TEMP VIEW pre_{tag} AS
      WITH vs AS (
        SELECT u.device_id, SUM(v.tvt_millisec/1000.0/60.0) AS x_tvt
        FROM assign_{tag} u JOIN core_prod.tubidw.video_session v ON u.device_id=v.device_id
        WHERE v.ds>='{PRE_START}' AND v.ds<='{PRE_END}' {plat_vs}
        GROUP BY u.device_id
      ),
      im AS (
        SELECT u.device_id,
          SUM(CASE WHEN ca.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                   AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS x_rev
        FROM assign_{tag} u JOIN core_prod.ads.impressions i ON u.device_id=i.device_id
        JOIN core_prod.mercurydb_cdc.campaigns ca ON i.campaign_id=ca.id
        WHERE i.date>='{PRE_START}' AND i.date<='{PRE_END}' AND i.unbillable='f' {plat_im}
        GROUP BY u.device_id
      )
      SELECT u.device_id, COALESCE(vs.x_tvt,0) x_tvt, COALESCE(im.x_rev,0) x_rev
      FROM assign_{tag} u LEFT JOIN vs ON u.device_id=vs.device_id LEFT JOIN im ON u.device_id=im.device_id
    """)
    title_vs = f"AND v.content_id IN (SELECT content_id FROM {TITLES})" if on_title else ""
    title_im = f"AND i.content_id IN (SELECT CAST(content_id AS STRING) FROM {TITLES})" if on_title else ""
    spark.sql(f"""
      CREATE OR REPLACE TEMP VIEW outc_{tag} AS
      WITH vs AS (
        SELECT u.device_id, SUM(v.tvt_millisec/1000.0/60.0) AS y_tvt
        FROM assign_{tag} u JOIN core_prod.tubidw.video_session v
          ON u.device_id=v.device_id AND v.start_ts>=u.first_exposure_ts AND v.ds>='{ps}' AND v.ds<='{pe}'
        WHERE 1=1 {plat_vs} {title_vs}
        GROUP BY u.device_id
      ),
      im AS (
        SELECT u.device_id,
          SUM(CASE WHEN ca.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                   AND i.advertiser_id NOT IN ({ADV_EXCL}) THEN i.cost ELSE 0 END) AS y_rev
        FROM assign_{tag} u JOIN core_prod.ads.impressions i
          ON u.device_id=i.device_id AND i.ts>=u.first_exposure_ts
        JOIN core_prod.mercurydb_cdc.campaigns ca ON i.campaign_id=ca.id
        WHERE i.date>='{ps}' AND i.date<='{pe}' AND i.unbillable='f' {plat_im} {title_im}
        GROUP BY u.device_id
      )
      SELECT u.device_id, COALESCE(vs.y_tvt,0) y_tvt, COALESCE(im.y_rev,0) y_rev
      FROM assign_{tag} u LEFT JOIN vs ON u.device_id=vs.device_id LEFT JOIN im ON u.device_id=im.device_id
    """)
    # ToT population: watched >=1 exp title in this period+platform (only meaningful when on_title)
    spark.sql(f"""
      CREATE OR REPLACE TEMP VIEW tot_{tag} AS
      SELECT DISTINCT u.device_id
      FROM assign_{tag} u JOIN core_prod.tubidw.video_session v
        ON u.device_id=v.device_id AND v.start_ts>=u.first_exposure_ts AND v.ds>='{ps}' AND v.ds<='{pe}'
      WHERE 1=1 {plat_vs} {title_vs}
    """)

def cuped_effect(tag, tot_filter):
    """Join assign+pre+outc (+tot if tot_filter), compute pooled-theta CUPED, return ABF3 Test-vs-Control welch per metric."""
    tot_join = f"JOIN tot_{tag} td ON td.device_id=o.device_id" if tot_filter else ""
    spark.sql(f"""
      CREATE OR REPLACE TEMP VIEW joined_{tag} AS
      SELECT a.abf3, o.y_tvt, o.y_rev, p.x_tvt, p.x_rev
      FROM outc_{tag} o JOIN pre_{tag} p ON o.device_id=p.device_id
      JOIN assign_{tag} a ON a.device_id=o.device_id {tot_join}
    """)
    cov = spark.sql(f"""
      SELECT covar_samp(y_tvt,x_tvt) c_tvt, var_samp(x_tvt) vx_tvt, avg(x_tvt) mx_tvt,
             covar_samp(y_rev,x_rev) c_rev, var_samp(x_rev) vx_rev, avg(x_rev) mx_rev
      FROM joined_{tag}""").collect()[0]
    theta={m:(float(cov['c_'+m])/float(cov['vx_'+m]) if float(cov['vx_'+m])>0 else 0.0) for m in METRICS}
    xbar={m:float(cov['mx_'+m]) for m in METRICS}
    agg=spark.sql(f"""
      SELECT abf3, COUNT(*) n,
        avg(y_tvt-{theta['tvt']}*(x_tvt-{xbar['tvt']})) ma_tvt, var_samp(y_tvt-{theta['tvt']}*(x_tvt-{xbar['tvt']})) va_tvt,
        avg(y_rev-{theta['rev']}*(x_rev-{xbar['rev']})) ma_rev, var_samp(y_rev-{theta['rev']}*(x_rev-{xbar['rev']})) va_rev
      FROM joined_{tag} GROUP BY abf3""").toPandas()
    agg['abf3']=agg['abf3'].astype(int)
    for c in agg.columns:
        if c!='abf3': agg[c]=pd.to_numeric(agg[c]).astype(float)
    ct=agg[agg.abf3==1].iloc[0]; cc=agg[agg.abf3==0].iloc[0]
    out={}
    for m in METRICS:
        out[m]=welch(float(ct['ma_'+m]),float(ct['va_'+m]),int(ct['n']),
                     float(cc['ma_'+m]),float(cc['va_'+m]),int(cc['n']))
    return out

# COMMAND ----------
# ## Run all (period × platform × scope) combos

PLATS = {
  'allOTT':  ('', ''),
  'nonRoku': ("AND v.platform<>'ROKU'", "AND lower(i.platform)<>'roku'"),
  'roku':    ("AND v.platform='ROKU'",  "AND lower(i.platform)='roku'"),
}

rows=[]
for pname,(ps,pe) in PERIODS.items():
    for plat,(pvs,pim) in PLATS.items():
        # on-title ToT (primary)
        tag=f"{pname}_{plat}_tot"
        build_period(tag, ps, pe, pvs, pim, on_title=True)
        eff=cuped_effect(tag, tot_filter=True)
        for m in METRICS:
            e=eff[m]; rows.append(dict(period=pname,plat=plat,scope='ToT_onTitle',metric=m,
                lift_pct=e['lift_pct'],ci_lo=e['ci'][0],ci_hi=e['ci'][1],p=e['p'],
                n_test=e['n1'],n_ctrl=e['n0'],se=e['se'],diff=e['diff'],m_ctrl=e['m0']))
        print(f"[{tag}] tvt {eff['tvt']['lift_pct']:.3f}% p={eff['tvt']['p']:.4f} | rev {eff['rev']['lift_pct']:.3f}% p={eff['rev']['p']:.4f} | n_t={eff['tvt']['n1']} n_c={eff['tvt']['n0']}", flush=True)
    # all-titles ITT, per platform (allOTT for power + nonRoku/roku for the platform falsification cut)
    for plat,(pvs,pim) in PLATS.items():
        tag=f"{pname}_{plat}_itt"
        build_period(tag, ps, pe, pvs, pim, on_title=False)
        eff=cuped_effect(tag, tot_filter=False)
        for m in METRICS:
            e=eff[m]; rows.append(dict(period=pname,plat=plat,scope='ITT_allTitles',metric=m,
                lift_pct=e['lift_pct'],ci_lo=e['ci'][0],ci_hi=e['ci'][1],p=e['p'],
                n_test=e['n1'],n_ctrl=e['n0'],se=e['se'],diff=e['diff'],m_ctrl=e['m0']))
        print(f"[{tag}] tvt {eff['tvt']['lift_pct']:.3f}% p={eff['tvt']['p']:.4f} | rev {eff['rev']['lift_pct']:.3f}% p={eff['rev']['p']:.4f} | n_t={eff['tvt']['n1']} n_c={eff['tvt']['n0']}", flush=True)

df=pd.DataFrame(rows)

# COMMAND ----------
# ## Temporal DiD: change in ABF3 effect P1->P2 (per platform×scope), with analytic SE (independent periods)

did=[]
for (plat,scope,metric),g in df.groupby(['plat','scope','metric']):
    g=g.set_index('period')
    if 'P1_withV7' not in g.index or 'P2_postV7' not in g.index: continue
    p1,p2=g.loc['P1_withV7'],g.loc['P2_postV7']
    # DiD in absolute (CUPED) units, normalized to P1 control mean for a % interpretation
    did_abs=p2['diff']-p1['diff']
    se=math.sqrt(p1['se']**2+p2['se']**2)
    base=p1['m_ctrl']
    z=did_abs/se if se>0 else float('nan')
    did.append(dict(plat=plat,scope=scope,metric=metric,
        eff_P1_pct=p1['lift_pct'],eff_P1_p=p1['p'],
        eff_P2_pct=p2['lift_pct'],eff_P2_p=p2['p'],
        did_pct=did_abs/base*100, did_ci_lo=(did_abs-Z*se)/base*100, did_ci_hi=(did_abs+Z*se)/base*100,
        did_z=z, did_p=2*st.norm.sf(abs(z))))
dfdid=pd.DataFrame(did)

# COMMAND ----------
# ## Summary

pd.set_option('display.width',260); pd.set_option('display.max_columns',60)
print("\n=== PER-PERIOD ABF3 EFFECT (CUPED) ===")
print(df[['period','plat','scope','metric','lift_pct','ci_lo','ci_hi','p','n_test','n_ctrl']].round(4).to_string(index=False))
print("\n=== TEMPORAL DiD (P2_postV7 − P1_withV7); did_pct<0 = effect dropped/more-negative post-V7 ===")
print("    nonRoku: expect TVT effect to RISE (less negative) post-V7 if V7 caused the hit.")
print("    roku (placebo): expect ~0 DiD (V7 never present); if it moves like nonRoku, it's time drift.\n")
print(dfdid[['plat','scope','metric','eff_P1_pct','eff_P1_p','eff_P2_pct','eff_P2_p','did_pct','did_ci_lo','did_ci_hi','did_p']].round(4).to_string(index=False))

dbutils.notebook.exit(json.dumps({'per_period':rows,'did':did}, default=str))
