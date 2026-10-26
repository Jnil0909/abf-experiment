-- Titles missing from the v8 experiment, under ARYAN'S OWN pre-ABF definition
-- (his screenshot logic), restricted to titles active in the US today.
WITH pre_abf AS (
  -- Aryan's pre-ABF condition on the stream tables
  SELECT CAST(movie_id AS STRING) content_id
  FROM core_prod.tubidw.content_movie_stream
  WHERE (cue_points_abf IS NULL OR cue_points_abf IN ('{}','{0.0}'))
    AND (cue_points_info IS NULL OR cue_points_info <> "imported from partner's metadata")
  UNION
  SELECT CAST(episode_id AS STRING)
  FROM core_prod.tubidw.content_episode_stream
  WHERE (cue_points_abf IS NULL OR cue_points_abf IN ('{}','{0.0}'))
    AND (cue_points_info IS NULL OR cue_points_info <> "imported from partner's metadata")
),
avail_now AS (
  -- Active in the US as of today (licensing window covers 2026-08-05)
  SELECT DISTINCT CAST(content_id AS STRING) content_id
  FROM core_prod.dsa.dsac_content_availability
  WHERE ds = '2026-08-05' AND country = 'US'
    AND window_start <= '2026-08-05' AND window_end >= '2026-08-05'
),
vs AS (
  -- 14d pre-launch TVT (2026-07-09..07-22) for sizing
  SELECT content_id, sum(tvt_millisec)/3600000.0 tvt_hr
  FROM core_prod.tubidw.video_session
  WHERE ds BETWEEN '2026-07-09' AND '2026-07-22' GROUP BY 1
),
abf1_cp AS (
  -- ABF1 (manual) cue point count from the cue_points column
  SELECT CAST(movie_id AS STRING) content_id,
    MAX(CASE WHEN cue_points IS NOT NULL AND cue_points NOT IN ('','[]') THEN size(split(cue_points,',')) ELSE 0 END) n_cp
  FROM core_prod.tubidw.content_movie_stream GROUP BY 1
  UNION ALL
  SELECT CAST(episode_id AS STRING),
    MAX(CASE WHEN cue_points IS NOT NULL AND cue_points NOT IN ('','[]') THEN size(split(cue_points,',')) ELSE 0 END)
  FROM core_prod.tubidw.content_episode_stream GROUP BY 1
),
abf1_cp_d AS (SELECT content_id, MAX(n_cp) abf1_cue_points FROM abf1_cp GROUP BY 1),
gap AS (
  SELECT p.content_id
  FROM pre_abf p
  JOIN avail_now a USING(content_id)
  LEFT ANTI JOIN (SELECT CAST(content_id AS STRING) content_id FROM core_dev.dsa.temp_bp_abf_v8_titles) v USING(content_id)
)
SELECT g.content_id,
       ci.content_name,
       ci.content_type,
       ci.primary_genre,
       CAST(ci.duration AS DOUBLE) AS duration_sec,
       coalesce(c.abf1_cue_points,0) AS abf1_cue_points,
       CASE WHEN u.content_id IS NOT NULL THEN u.in_experiment ELSE 0 END AS was_v67_exp_title,
       CASE WHEN u.content_id IS NOT NULL THEN 1 ELSE 0 END AS in_june_universe,
       round(coalesce(vs.tvt_hr,0),1) AS tvt_hr_14d
FROM gap g
LEFT JOIN abf1_cp_d c USING(content_id)
LEFT JOIN core_dev.dsa.temp_bp_abf1_universe u ON g.content_id = CAST(u.content_id AS STRING)
LEFT JOIN vs ON vs.content_id = g.content_id
LEFT JOIN core_prod.tubidw.content_info ci ON g.content_id = CAST(ci.content_id AS STRING)
ORDER BY coalesce(vs.tvt_hr,0) DESC
