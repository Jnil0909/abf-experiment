CREATE OR REPLACE TABLE core_dev.dsa.temp_bp_v9_experiment_titles AS
WITH stream AS (
  SELECT movie_id AS cid, 'movie' AS src, cue_points_abf FROM core_prod.tubidw.content_movie_stream
  UNION ALL
  SELECT episode_id, 'episode', cue_points_abf FROM core_prod.tubidw.content_episode_stream
),
abf2 AS (
  -- titles serving ML cue points today (strict non-empty: catches '{}'/'{0.0}' variants)
  SELECT cid, MAX(src) AS src
  FROM stream
  WHERE cue_points_abf IS NOT NULL AND cue_points_abf NOT IN ('[]','{}','{0.0}','')
  GROUP BY cid
),
gemini AS (
  -- has a SERVABLE ABF3 set (non-empty v2 slash): dedupes PROCESSING only — these titles stay IN the experiment.
  -- v2 = the slasher version v9 serves (confirm w/ Aryan); processed-but-not-servable titles get re-slashed via the processing list.
  SELECT DISTINCT content_id AS cid
  FROM ml_prod.ads.abf3_slasher_cuepoints
  WHERE slasher_version = 'v2' AND slashed_cue_points_sec IS NOT NULL AND size(slashed_cue_points_sec) > 0
),
lic AS (
  -- current/future US licenses; captures off-rotation titles, drops expired
  SELECT CAST(video_id AS BIGINT) AS cid, MAX(end_ts) AS max_end_ts
  FROM core_prod.content.content_availability
  WHERE date = (SELECT MAX(date) FROM core_prod.content.content_availability)
    AND country = 'US' AND active = true
  GROUP BY 1
),
tvt AS (
  -- trailing TVT for PRIORITIZATION only, never selection
  SELECT content_id AS cid, SUM(tvt_min) AS tvt_min
  FROM core_prod.tubidw.content_daily_byepisodes_bycountry_byplatform
  WHERE ds >= DATE_SUB(CURRENT_DATE, 60) AND ds < CURRENT_DATE
  GROUP BY 1
)
SELECT a.cid AS content_id, a.src AS title_type,
       COALESCE(t.tvt_min, 0) AS tvt_min_60d,
       lic.max_end_ts,
       CASE WHEN g.cid IS NULL THEN 1 ELSE 0 END AS needs_processing
FROM abf2 a
JOIN lic ON a.cid = lic.cid AND lic.max_end_ts > CURRENT_DATE
LEFT JOIN core_dev.dsa.temp_bp_abf_v8_all_titles v8 ON a.cid = v8.content_id
LEFT JOIN gemini g ON a.cid = g.cid
LEFT JOIN tvt t ON a.cid = t.cid
WHERE v8.content_id IS NULL
