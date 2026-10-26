-- Which Active/ToT definition reproduces the doc's Control counts (Active 4,057,913; ToT 3,252,581)?
WITH exp AS (
  SELECT device_id, MIN(timestamp) fe FROM core_dev.statsig.exposures
  WHERE experiment_id = 'ads_abf_3_v10_abf2_titles_only' AND group_name = 'Control' GROUP BY device_id
),
stream AS (
  SELECT CAST(movie_id AS STRING) content_id, cue_points_abf cpa, cue_points_info cpi FROM core_prod.tubidw.content_movie_stream
  UNION ALL SELECT CAST(episode_id AS STRING), cue_points_abf, cue_points_info FROM core_prod.tubidw.content_episode_stream
),
abf2 AS (
  SELECT DISTINCT content_id FROM stream
  WHERE cpa IS NOT NULL AND cpa NOT IN ('[]','{}','{0.0}','') AND COALESCE(cpi,'') <> 'abf3_pruned_v8'
    AND content_id NOT IN (SELECT CAST(content_id AS STRING) FROM core_dev.dsa.temp_bp_abf_v8_all_titles)
),
s AS (
  SELECT e.device_id, v.start_ts, v.ds, v.tvt_millisec, CAST(v.content_id AS STRING) cid,
         a.content_id IS NOT NULL AS on_title
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id = v.device_id AND v.start_ts >= e.fe AND v.ds >= '2026-10-09' AND v.ds <= '2026-10-15'
  LEFT JOIN abf2 a ON CAST(v.content_id AS STRING) = a.content_id
),
d AS (
  SELECT device_id,
    MAX(CASE WHEN start_ts < '2026-10-15 14:00:00' THEN 1 ELSE 0 END) act_cap14,
    MAX(CASE WHEN start_ts < '2026-10-15 14:00:00' AND tvt_millisec > 0 THEN 1 ELSE 0 END) act_cap14_tvt,
    MAX(CASE WHEN ds <= '2026-10-14' THEN 1 ELSE 0 END) act_ds14,
    MAX(CASE WHEN start_ts < '2026-10-15 10:00:00' THEN 1 ELSE 0 END) act_cap10,
    MAX(CASE WHEN start_ts < '2026-10-15 14:00:00' AND on_title AND tvt_millisec >= 1000 THEN 1 ELSE 0 END) tot_sess1s,
    SUM(CASE WHEN start_ts < '2026-10-15 14:00:00' AND on_title THEN tvt_millisec ELSE 0 END) tot_ms_cap14,
    SUM(CASE WHEN ds <= '2026-10-14' AND on_title THEN tvt_millisec ELSE 0 END) tot_ms_ds14,
    SUM(CASE WHEN start_ts < '2026-10-15 10:00:00' AND on_title THEN tvt_millisec ELSE 0 END) tot_ms_cap10
  FROM s GROUP BY device_id
)
SELECT SUM(act_cap14) act_cap14, SUM(act_cap14_tvt) act_cap14_tvt, SUM(act_ds14) act_ds14, SUM(act_cap10) act_cap10,
  SUM(tot_sess1s) tot_sess1s,
  SUM(CASE WHEN tot_ms_cap14 >= 1000 THEN 1 ELSE 0 END) tot_sum1s_cap14,
  SUM(CASE WHEN tot_ms_cap14 > 0 THEN 1 ELSE 0 END) tot_pos_cap14,
  SUM(CASE WHEN tot_ms_ds14 >= 1000 THEN 1 ELSE 0 END) tot_sum1s_ds14,
  SUM(CASE WHEN tot_ms_cap10 >= 1000 THEN 1 ELSE 0 END) tot_sum1s_cap10
FROM d
