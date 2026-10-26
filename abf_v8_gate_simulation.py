# Databricks notebook source
# MAGIC %md
# MAGIC # v8 — Deterministic ad-gate simulation: do ABF3's series positions fire fewer breaks?
# MAGIC PROVE/REFUTE: "series lose realized breaks due to cue-point POSITIONS (vs ad-config gates), not count."
# MAGIC For every treated title we have both arms' actual cue point positions:
# MAGIC `cue_points` (ABF1 control) vs `cue_points_abf` (served pruned ABF3).
# MAGIC Simulate the pod-placement gate (initial-ad-slot + min-time-between-breaks, greedy first-eligible)
# MAGIC over each list → max fireable breaks per title per arm. Same gate both arms → the Δ is pure position/count.
# MAGIC Validation: TVT-weighted simulated Δ per band×type is compared against the OBSERVED realized-break Δ
# MAGIC (Window A impressions measurement). Gate profiles swept (baseline + tolerant) for robustness.

# COMMAND ----------

from pyspark.sql import functions as F
import pandas as pd, numpy as np, json

dbutils.widgets.text('TITLES_TABLE', 'core_dev.dsa.temp_bp_abf_v8_all_titles')
dbutils.widgets.text('TVT_START', '2026-07-09')
dbutils.widgets.text('TVT_END', '2026-07-22')
TT = dbutils.widgets.get('TITLES_TABLE')
TVT_START = dbutils.widgets.get('TVT_START'); TVT_END = dbutils.widgets.get('TVT_END')
UNIVERSE = 'core_dev.dsa.temp_bp_abf1_universe'

# COMMAND ----------

# per-title: band, type, duration, both cue point strings, baseline TVT weight
df = spark.sql(f"""
WITH stream AS (
  SELECT movie_id AS content_id, cue_points, cue_points_abf, duration FROM core_prod.tubidw.content_movie_stream
  UNION ALL
  SELECT episode_id, cue_points, cue_points_abf, duration FROM core_prod.tubidw.content_episode_stream
),
s AS (
  SELECT content_id,
    MAX(CASE WHEN cue_points IS NOT NULL AND cue_points NOT IN ('','[]') THEN cue_points END) AS cps_ctrl,
    MAX(CASE WHEN cue_points_abf IS NOT NULL AND cue_points_abf NOT IN ('[]','{{}}','{{0.0}}','') THEN cue_points_abf END) AS cps_test,
    MAX(duration) AS duration_sec
  FROM stream GROUP BY 1
),
tvt AS (
  SELECT content_id, SUM(tvt_millisec)/1000.0/3600.0 AS tvt_hr
  FROM core_prod.tubidw.video_session
  WHERE ds >= '{TVT_START}' AND ds <= '{TVT_END}'
  GROUP BY 1
)
SELECT u.content_id, COALESCE(u.content_type,'UNKNOWN') AS content_type,
  CASE WHEN u.abf1_cue_points <= 0 THEN '0'
       WHEN u.abf1_cue_points <= 3 THEN '1-3'
       WHEN u.abf1_cue_points <= 6 THEN '4-6'
       WHEN u.abf1_cue_points <= 9 THEN '7-9'
       WHEN u.abf1_cue_points <= 12 THEN '10-12'
       ELSE '13+' END AS band,
  s.cps_ctrl, s.cps_test, s.duration_sec, COALESCE(t.tvt_hr, 0) AS tvt_hr
FROM {UNIVERSE} u
JOIN {TT} v ON u.content_id = v.content_id
JOIN s ON u.content_id = s.content_id
LEFT JOIN tvt t ON u.content_id = t.content_id
WHERE s.cps_ctrl IS NOT NULL AND s.cps_test IS NOT NULL AND s.duration_sec > 300
""").toPandas()
df['duration_sec'] = pd.to_numeric(df['duration_sec']).astype(float)
df['tvt_hr'] = pd.to_numeric(df['tvt_hr']).astype(float)
print(len(df), 'titles with both arms cue points')
print(df.groupby(['content_type','band']).size())

# COMMAND ----------

def parse(s):
    out = []
    for x in str(s).strip().strip('{}[]').split(','):
        x = x.strip().strip('{}[]')
        if not x:
            continue
        try:
            out.append(float(x))
        except ValueError:
            pass
    return sorted(out)

df['cp_ctrl'] = df['cps_ctrl'].map(parse)
df['cp_test'] = df['cps_test'].map(parse)
df['n_ctrl'] = df['cp_ctrl'].map(len)
df['n_test'] = df['cp_test'].map(len)
# sanity: cue point units are content-seconds; drop titles whose max cp exceeds duration by >20% (bad metadata)
mx_c = df['cp_ctrl'].map(lambda l: max(l) if l else 0); mx_t = df['cp_test'].map(lambda l: max(l) if l else 0)
bad = (mx_c > df.duration_sec*1.2) | (mx_t > df.duration_sec*1.2)
print('dropped bad-metadata titles:', int(bad.sum()))
df = df[~bad].copy()

def fired(cps, dur, initial, spacing):
    """greedy first-eligible: list of fired positions"""
    out = []; last = None
    for cp in cps:
        if cp < initial or cp > dur:
            continue
        if last is None or cp - last >= spacing:
            out.append(cp); last = cp
    return out

# gate profiles per content type: (name, initial, spacing) — baseline + tolerant/low-fill ladder
PROFILES = {
    'SERIES': [('base_420_600', 420, 600), ('mid_390_510', 390, 510), ('tolerant_360_360', 360, 360)],
    'MOVIE':  [('base_900_720', 900, 720), ('mid_780_630', 780, 630), ('tolerant_540_420', 540, 420)],
}

rows = []
pertitle = {}
for ct, profs in PROFILES.items():
    sub = df[df.content_type == ct]
    for pname, ini, spc in profs:
        fc = sub.apply(lambda r: fired(r.cp_ctrl, r.duration_sec, ini, spc), axis=1)
        ft = sub.apply(lambda r: fired(r.cp_test, r.duration_sec, ini, spc), axis=1)
        nfc = fc.map(len).astype(float); nft = ft.map(len).astype(float)
        first_c = fc.map(lambda l: l[0] if l else np.nan); first_t = ft.map(lambda l: l[0] if l else np.nan)
        tail_c = sub.duration_sec - fc.map(lambda l: l[-1] if l else np.nan)
        tail_t = sub.duration_sec - ft.map(lambda l: l[-1] if l else np.nan)
        w = sub.tvt_hr.values
        for band in ['0','1-3','4-6','7-9','10-12','13+']:
            m = (sub.band == band).values
            if m.sum() == 0: continue
            wm = w[m]; wsum = wm.sum()
            if wsum <= 0: continue
            simc = float((nfc.values[m]*wm).sum()/wsum); simt = float((nft.values[m]*wm).sum()/wsum)
            rows.append(dict(content_type=ct, profile=pname, band=band, n_titles=int(m.sum()),
                mean_cp_ctrl=float(sub.n_ctrl.values[m].mean()), mean_cp_test=float(sub.n_test.values[m].mean()),
                sim_fired_ctrl=round(simc,3), sim_fired_test=round(simt,3),
                sim_delta_pct=round((simt-simc)/simc*100,2) if simc>0 else None,
                pct_titles_fewer=round(float((nft.values[m] < nfc.values[m]).mean())*100,1),
                pct_titles_more=round(float((nft.values[m] > nfc.values[m]).mean())*100,1),
                first_fire_ctrl=round(float(np.nanmean(first_c.values[m])),0),
                first_fire_test=round(float(np.nanmean(first_t.values[m])),0),
                tail_ctrl=round(float(np.nanmean(tail_c.values[m])),0),
                tail_test=round(float(np.nanmean(tail_t.values[m])),0)))
        if pname.startswith('base'):
            pertitle[ct] = pd.DataFrame(dict(content_id=sub.content_id.values, band=sub.band.values,
                n_ctrl=sub.n_ctrl.values, n_test=sub.n_test.values, nfc=nfc.values, nft=nft.values,
                tvt=w, dur=sub.duration_sec.values))

res = pd.DataFrame(rows)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(res.to_string(index=False))

# COMMAND ----------

# OBSERVED realized-break delta (Window A impressions measurement) for side-by-side validation
OBS = {('MOVIE','1-3'): 6.1, ('MOVIE','4-6'): 13.9, ('MOVIE','7-9'): 8.0, ('MOVIE','10-12'): 2.0, ('MOVIE','13+'): -5.1,
       ('SERIES','1-3'): -0.7, ('SERIES','4-6'): -0.6, ('SERIES','7-9'): -6.9, ('SERIES','10-12'): -3.5, ('SERIES','13+'): -12.7}
base = res[res.profile.str.startswith('base')].copy()
base['observed_delta_pct'] = base.apply(lambda r: OBS.get((r.content_type, r.band)), axis=1)
print(base[['content_type','band','n_titles','mean_cp_ctrl','mean_cp_test','sim_fired_ctrl','sim_fired_test','sim_delta_pct','observed_delta_pct','pct_titles_fewer','pct_titles_more','first_fire_ctrl','first_fire_test','tail_ctrl','tail_test']].to_string(index=False))
v = base.dropna(subset=['observed_delta_pct','sim_delta_pct'])
if len(v) > 2:
    corr = np.corrcoef(v.sim_delta_pct, v.observed_delta_pct)[0,1]
    print(f"\nsim-vs-observed correlation across band×type cells: r = {corr:.3f} (n={len(v)})")

# COMMAND ----------

# THE SMOKING-GUN SUBSET: series titles with MORE test cue points but FEWER simulated fired breaks (baseline gate)
sg = pertitle['SERIES']
sg_sub = sg[(sg.n_test > sg.n_ctrl) & (sg.nft < sg.nfc)]
sg_share = sg_sub.tvt.sum()/sg.tvt.sum()*100
print(f"SERIES titles w/ MORE cue points but FEWER simulated breaks: {len(sg_sub)}/{len(sg)} titles, {sg_share:.1f}% of series TVT")
print(sg_sub.nlargest(10, 'tvt')[['content_id','band','n_ctrl','n_test','nfc','nft','dur','tvt']].to_string(index=False))
# and decompose the series deficit: count-driven (n_test<n_ctrl) vs position-driven (n_test>=n_ctrl but fewer fired)
for band in ['4-6','7-9','10-12','13+']:
    b = sg[sg.band == band]
    if not len(b): continue
    w = b.tvt.sum()
    dcount = b[(b.n_test < b.n_ctrl)]; dpos = b[(b.n_test >= b.n_ctrl) & (b.nft < b.nfc)]
    tot_delta = ((b.nft*b.tvt).sum() - (b.nfc*b.tvt).sum())/(b.nfc*b.tvt).sum()*100
    d_from_count = ((dcount.nft - dcount.nfc)*dcount.tvt).sum()/(b.nfc*b.tvt).sum()*100
    d_from_pos = ((dpos.nft - dpos.nfc)*dpos.tvt).sum()/(b.nfc*b.tvt).sum()*100
    print(f"SERIES band {band}: total simΔ {tot_delta:+.2f}% = count-driven {d_from_count:+.2f}% + position-driven {d_from_pos:+.2f}% + gains")

# COMMAND ----------

decomp = []
for band in ['1-3','4-6','7-9','10-12','13+']:
    b = sg[sg.band == band]
    if not len(b): continue
    dcount = b[(b.n_test < b.n_ctrl)]; dpos = b[(b.n_test >= b.n_ctrl) & (b.nft < b.nfc)]
    denom = (b.nfc*b.tvt).sum()
    decomp.append(dict(band=band,
        total_sim_delta_pct=round(float(((b.nft*b.tvt).sum()-denom)/denom*100),2),
        count_driven_pct=round(float(((dcount.nft-dcount.nfc)*dcount.tvt).sum()/denom*100),2),
        position_driven_pct=round(float(((dpos.nft-dpos.nfc)*dpos.tvt).sum()/denom*100),2)))

prevalence = []
for ct in ['SERIES','MOVIE']:
    p = pertitle[ct]
    for scope, q in [('ALL', p)] + [(b, p[p.band==b]) for b in ['1-3','4-6','7-9','10-12','13+']]:
        if not len(q): continue
        tv = q.tvt.sum()
        fewer = q[q.nft < q.nfc]; equal = q[q.nft == q.nfc]; more = q[q.nft > q.nfc]
        prevalence.append(dict(content_type=ct, band=scope, n_titles=int(len(q)),
            pct_titles_fewer=round(len(fewer)/len(q)*100,1),
            pct_titles_equal=round(len(equal)/len(q)*100,1),
            pct_titles_more=round(len(more)/len(q)*100,1),
            pct_tvt_fewer=round(float(fewer.tvt.sum()/tv*100),1) if tv>0 else None,
            pct_tvt_equal=round(float(equal.tvt.sum()/tv*100),1) if tv>0 else None,
            pct_tvt_more=round(float(more.tvt.sum()/tv*100),1) if tv>0 else None,
            mean_breaks_lost_when_fewer=round(float((fewer.nfc-fewer.nft).mean()),2) if len(fewer) else None))

dbutils.notebook.exit(json.dumps({
  'prevalence_baseline_gate': prevalence,
  'baseline_vs_observed': base[['content_type','band','sim_delta_pct','observed_delta_pct','pct_titles_fewer','pct_titles_more','first_fire_ctrl','first_fire_test','tail_ctrl','tail_test']].to_dict('records'),
  'sim_obs_correlation': round(float(corr),3) if len(v) > 2 else None,
  'series_smoking_gun': dict(n_titles=int(len(sg_sub)), n_series=int(len(sg)), tvt_share_pct=round(float(sg_share),2)),
  'series_decomp_baseline_gate': decomp,
}, default=str))
