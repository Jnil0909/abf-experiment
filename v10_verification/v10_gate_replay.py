# Databricks notebook source
# MAGIC %md
# MAGIC # v10 — Gate replay: fireable breaks, ABF2 control vs each pruner arm (served lists)
# MAGIC Control positions = live `cue_points_abf` on the ABF2 catalog; arm positions = `ml_dev.tmp.abf3_new_pruner_cuepoints`
# MAGIC (T1 = v4, T2 = v6, T3 = v5b). Greedy first-eligible gate, episodes 420s/600s, movies 900s/720s.
# MAGIC TVT weight = in-window TVT per title. Same gate both arms -> delta is pure count + position.

# COMMAND ----------

import pandas as pd, numpy as np, json

dbutils.widgets.text('W_START', '2026-10-09')
dbutils.widgets.text('W_END', '2026-10-15')
dbutils.widgets.text('PLATFORM', '')   # '' = all platforms; e.g. OTT
dbutils.widgets.text('GATES', '420,600,900,720')   # episode initial, episode spacing, movie initial, movie spacing
W_START = dbutils.widgets.get('W_START'); W_END = dbutils.widgets.get('W_END')
PLATFORM = dbutils.widgets.get('PLATFORM').strip()
plat = f"AND platform_type = '{PLATFORM}'" if PLATFORM else ""

df = spark.sql(f"""
WITH stream AS (
  SELECT movie_id AS content_id, 'Movie' AS tt, cue_points_abf AS cpa, cue_points_info AS cpi FROM core_prod.tubidw.content_movie_stream
  UNION ALL
  SELECT episode_id, 'Episode', cue_points_abf, cue_points_info FROM core_prod.tubidw.content_episode_stream
),
abf2 AS (
  SELECT content_id, MAX(tt) tt, MAX(cpa) cpa FROM stream
  WHERE cpa IS NOT NULL AND cpa NOT IN ('[]','{{}}','{{0.0}}','')
    AND COALESCE(cpi,'') <> 'abf3_pruned_v8'
    AND content_id NOT IN (SELECT content_id FROM core_dev.dsa.temp_bp_abf_v8_all_titles)
  GROUP BY content_id
),
tvt AS (
  SELECT content_id, SUM(tvt_millisec)/3600000.0 AS tvt_hr
  FROM core_prod.tubidw.video_session
  WHERE ds >= '{W_START}' AND ds <= '{W_END}' {plat}
  GROUP BY content_id
)
SELECT a.content_id, a.tt, a.cpa, s.slasher_version AS arm, s.duration_sec,
       CAST(s.slashed_cue_points_sec AS ARRAY<DOUBLE>) AS srv, COALESCE(t.tvt_hr, 0) AS tvt_hr
FROM abf2 a
JOIN ml_dev.tmp.abf3_new_pruner_cuepoints s ON a.content_id = s.content_id
LEFT JOIN tvt t ON a.content_id = t.content_id
WHERE s.duration_sec > 300
""").toPandas()
df['duration_sec'] = df['duration_sec'].astype(float); df['tvt_hr'] = pd.to_numeric(df['tvt_hr']).astype(float)

def parse(s):
    out = []
    for x in str(s).strip().strip('{}[]').split(','):
        x = x.strip().strip('{}[]')
        if x:
            try:
                v = float(x)
                if v > 0: out.append(v)
            except ValueError:
                pass
    return sorted(out)

df['cp_ctl'] = df['cpa'].map(parse)
df['cp_srv'] = df['srv'].map(lambda a: sorted(float(x) for x in a) if a is not None else [])
df['n_ctl'] = df.cp_ctl.map(len); df['n_srv'] = df.cp_srv.map(len)
df = df[df.n_ctl > 0].copy()
mx = df.apply(lambda r: max(r.cp_ctl + r.cp_srv + [0]), axis=1)
bad = mx > df.duration_sec * 1.2
n_bad = int(bad.sum()); df = df[~bad].copy()
df['band'] = pd.cut(df.n_ctl, [0, 3, 6, 9, 12, 10**6], labels=['1-3', '4-6', '7-9', '10-12', '13+']).astype(str)

_g = [float(x) for x in dbutils.widgets.get('GATES').split(',')]
GATE = {'Episode': (_g[0], _g[1]), 'Movie': (_g[2], _g[3])}
def fired(cps, dur, ini, spc):
    out = []; last = None
    for cp in cps:
        if cp < ini or cp > dur: continue
        if last is None or cp - last >= spc:
            out.append(cp); last = cp
    return out

def sim(row, col):
    ini, spc = GATE[row.tt]
    return fired(row[col], row.duration_sec, ini, spc)
df['f_ctl'] = df.apply(lambda r: sim(r, 'cp_ctl'), axis=1)
df['f_srv'] = df.apply(lambda r: sim(r, 'cp_srv'), axis=1)
df['nf_ctl'] = df.f_ctl.map(len).astype(float); df['nf_srv'] = df.f_srv.map(len).astype(float)
df['first_ctl'] = df.f_ctl.map(lambda l: l[0] if l else np.nan); df['first_srv'] = df.f_srv.map(lambda l: l[0] if l else np.nan)

def wdelta(g):
    w = g.tvt_hr; d = (g.nf_ctl * w).sum()
    return float(((g.nf_srv * w).sum() - d) / d * 100) if d > 0 else None

def wmean(x, w):
    m = ~np.isnan(x) & (w > 0)
    return float((x[m] * w[m]).sum() / w[m].sum()) if m.any() else None

cells = []
for (tt, band, arm), g in df.groupby(['tt', 'band', 'arm']):
    cells.append(dict(tt=tt, band=band, arm=arm, n=int(len(g)), sim_delta=round(wdelta(g), 2) if wdelta(g) is not None else None))
band_pooled = []
for (band, arm), g in df.groupby(['band', 'arm']):
    band_pooled.append(dict(band=band, arm=arm, sim_delta=round(wdelta(g), 2)))
first = []
for (tt, arm), g in df.groupby(['tt', 'arm']):
    both = g[g.first_ctl.notna() & g.first_srv.notna()]
    first.append(dict(tt=tt, arm=arm, first_ctl=round(wmean(g.first_ctl.values, g.tvt_hr.values), 0),
                      first_srv=round(wmean(g.first_srv.values, g.tvt_hr.values), 0),
                      both_ctl=round(wmean(both.first_ctl.values, both.tvt_hr.values), 0),
                      both_srv=round(wmean(both.first_srv.values, both.tvt_hr.values), 0),
                      raw_first_srv=round(wmean(g.cp_srv.map(lambda l: l[0] if l else np.nan).values.astype(float), g.tvt_hr.values), 0),
                      raw_first_ctl=round(wmean(g.cp_ctl.map(lambda l: l[0] if l else np.nan).values.astype(float), g.tvt_hr.values), 0),
                      unw_first_srv=round(float(np.nanmean(g.first_srv.values)), 0),
                      unw_first_ctl=round(float(np.nanmean(g.first_ctl.values)), 0)))
decomp = []
for arm, g in df[df.tt == 'Episode'].groupby('arm'):
    w = g.tvt_hr; den = (g.nf_ctl * w).sum(); dd = (g.nf_srv - g.nf_ctl) * w
    fewer = g.n_srv < g.n_ctl
    pos = (~fewer) & (g.nf_srv < g.nf_ctl)
    gains = (~fewer) & (g.nf_srv >= g.nf_ctl)
    decomp.append(dict(arm=arm, total=round(float(dd.sum() / den * 100), 2),
                       from_fewer=round(float(dd[fewer].sum() / den * 100), 2),
                       from_placement=round(float(dd[pos].sum() / den * 100), 2),
                       from_gains=round(float(dd[gains].sum() / den * 100), 2)))

dbutils.notebook.exit(json.dumps(dict(platform=PLATFORM or 'ALL', gates=GATE, n_rows=int(len(df)), n_bad=n_bad,
    cells=cells, band_pooled=band_pooled, first=first, episode_decomp=decomp), default=str))
