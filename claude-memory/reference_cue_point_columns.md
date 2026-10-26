---
name: reference-cue-point-columns
description: Which stream-table column holds ABF1 baseline cue-point density vs ABF classification
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6a38b6e8-b694-4300-9419-9e3a9ffe953d
  modified: 2026-08-20T06:42:51.479Z
---

In `core_prod.tubidw.content_movie_stream` and `content_episode_stream`:

- **`cue_points`** = the actual served cue points (type: string). Format = **plain comma-separated floats**, e.g. `433.80,742.23,1021.98` (NO brackets/braces). For ABF1 titles these are the manual/pre-ABF ones. **Parse THIS column to count ABF1 baseline cue-point density per title.** Count via `size(split(cue_points, ','))`, but guard empties: `CASE WHEN cue_points IS NULL OR cue_points IN ('','[]') THEN 0 ELSE size(split(cue_points, ',')) END` (since `size(split('',','))` returns 1).
- **`cue_points_abf`** = the ABF (ML) cue points (ABF2/ABF3). NOT the density source for ABF1.

IMPORTANT (confirmed 2026-06-03): For the v6 experiment titles, `cue_points` STILL holds their original ABF1 baseline density even though `cue_points_abf` is also populated — `cue_points_abf` is populated because the treatment arm serves those ABF3 cue points. So `cue_points` is a reliable ABF1 baseline even for treated titles, and `has_abf = 1` does NOT mean a title isn't natively ABF1. Do not use `has_abf = 0` to define the ABF1 graduation universe — it wrongly excludes the experiment titles. Density comparisons must be TVT-weighted (the untreated ABF1 universe averages ~2.8 cue points with ~37% at zero — long tail of near-zero-TVT titles).

**⚠️ NO LONGER REPRODUCIBLE LIVE (discovered 2026-08-05):** `cue_points_abf` is a LIVE column — the v8 full-catalog launch (2026-07-23) populated it on ~152K formerly-ABF1 titles, so `has_abf=0` today returns ~364K not 492K. `core_dev.dsa.temp_bp_abf1_universe` is a point-in-time snapshot of 2026-06-03 (that's why it was persisted). For current ABF1 status use the snapshot + `core_dev.dsa.temp_bp_abf_v8_titles` (what v8 treated), never the live column. Note Aryan's variant of "pre-ABF" additionally checks `cue_points_abf IN ('{}','{0.0}')` (brace format) and excludes `cue_points_info = 'imported from partner''s metadata'` — near-identical result in practice.

ABF1 universe query (titles with no ABF cue points) — as of the 2026-06-03 snapshot:
```sql
WITH abf_status AS (
  SELECT movie_id AS content_id,
    MAX(CASE WHEN cue_points_abf IS NOT NULL AND cue_points_abf != '[]' THEN 1 ELSE 0 END) AS has_abf
  FROM core_prod.tubidw.content_movie_stream GROUP BY 1
  UNION ALL
  SELECT episode_id AS content_id,
    MAX(CASE WHEN cue_points_abf IS NOT NULL AND cue_points_abf != '[]' THEN 1 ELSE 0 END) AS has_abf
  FROM core_prod.tubidw.content_episode_stream GROUP BY 1
)
SELECT content_id FROM abf_status WHERE has_abf = 0 GROUP BY 1
```

**⚠️ FORMAT GOTCHA (burned once, 2026-08-19):** `cue_points` = plain comma-separated floats, but **`cue_points_abf` is BRACE-wrapped** (`{657.89,1080.81,...}`). Any parser must strip `{}[]` before splitting — `float('{657.89')` silently fails and reads the whole column as empty (this zeroed out an entire simulation run before being caught).

**ABF2 cue points (verified 2026-10-19):** there is no dedicated ABF2 table. ABF2 = live `cue_points_abf` minus the v8 overwrites (`cue_points_info = 'abf3_pruned_v8'` and `core_dev.dsa.temp_bp_abf_v8_all_titles`), about 300k titles. Canonical query: `abf2_cuepoints.sql`. Count-vs-slasher comparison: `abf_cuepoint_count_vs_abf2.sql`. Caveats: (a) live snapshot, so titles later overwritten by ABF3 lose their ABF2 cues; (b) `cue_points_info` doesn't tag ABF2 (~79.6k partner-tagged rows still look like ML output; use `cue_points_info IS NULL` for a strict baseline); (c) `slasher_version = 'v2'` in `abf3_slasher_cuepoints` is ABF3 Slasher v2, not ABF2. `core_dev.dsa.temp_bp_abf_v2_exp_titles` is only a title-assignment list (ABF1/ABF2) with no cues.

**Unpruned ABF3 candidates (with positions):** `core_prod.titancontrollerdb_cdc.product_ai_ad_breakfinder` — cols `asset_id` (video-asset UUID, NOT content_id — mapping needed), `ad_breaks` (JSON array w/ `timestamp` sec, `classifier_score`, `classifier_accept`, boundaries), `model` (e.g. gemini-3-flash-preview). This is the source for model-vs-pruner attribution of missing early cue points.

**Ad-config gates (per content TYPE, not duration; from `ad_config.json` OTT+US):** episodes base initial-ad-slot 420s / min-time-between-breaks 600s; movies 900s/720s; tolerant/low-fill segment deltas go lower. Realized breaks = greedy first-eligible over sorted cue points. Key resonance: kept-cue-point spacing just ABOVE the gate → every point fires; just BELOW → every other fires (~2× effective cadence). This is why type-blind ~9-min ABF3 spacing wins on movies (12-min gate) and loses on episodes (10-min gate) — see ABF_BACKGROUND §series-mechanism (2026-08-19).

Content metadata: `core_prod.tubidw.content_info` (content_type, duration, primary_genre, etc. — series title column is `program_name`, not `series_name`).
