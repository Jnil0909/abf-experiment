-- How deep do viewers get into an ABF2 episode/movie per platform? Share of device x title views (Control arms of the three
-- v10 experiments, in-window) whose total watch time reaches ABF2's average first cue (~6.3 min) vs v4/v6's (~9.7 min).
WITH exp AS (
  SELECT device_id, MIN(timestamp) fe,
    CASE experiment_id WHEN 'ads_abf_3_v10_abf2_titles_only' THEN 'OTT'
                       WHEN 'ads_mobile_abf_3_v10_abf2_titles_only' THEN 'MOBILE' ELSE 'WEB' END AS plat
  FROM core_dev.statsig.exposures
  WHERE experiment_id IN ('ads_abf_3_v10_abf2_titles_only','ads_mobile_abf_3_v10_abf2_titles_only','ads_web_abf_3_v10_abf2_titles_only')
    AND group_name = 'Control'
  GROUP BY device_id, experiment_id
),
stream AS (
  SELECT movie_id AS content_id, 'Movie' AS tt, cue_points_abf cpa, cue_points_info cpi FROM core_prod.tubidw.content_movie_stream
  UNION ALL SELECT episode_id, 'Episode', cue_points_abf, cue_points_info FROM core_prod.tubidw.content_episode_stream
),
abf2 AS (
  SELECT content_id, MAX(tt) tt FROM stream
  WHERE cpa IS NOT NULL AND cpa NOT IN ('[]','{}','{0.0}','') AND COALESCE(cpi,'') <> 'abf3_pruned_v8'
    AND content_id NOT IN (SELECT content_id FROM core_dev.dsa.temp_bp_abf_v8_all_titles)
    AND content_id IN (SELECT content_id FROM ml_dev.tmp.abf3_v10_targeted_titles)
  GROUP BY content_id
),
views AS (
  SELECT e.plat, a.tt, e.device_id, v.content_id, SUM(v.tvt_millisec)/60000.0 AS mins
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id = v.device_id AND v.start_ts >= e.fe AND v.ds >= '2026-10-09' AND v.ds <= '2026-10-19'
   AND v.start_ts < '2026-10-20 00:00:00'
  JOIN abf2 a ON v.content_id = a.content_id
  GROUP BY 1, 2, 3, 4
)
SELECT plat, tt, COUNT(*) views,
  ROUND(percentile_approx(mins, 0.5), 1) median_min,
  ROUND(100*AVG(CASE WHEN mins >= 6.3 THEN 1.0 ELSE 0 END), 1) pct_reach_6_3,
  ROUND(100*AVG(CASE WHEN mins >= 9.7 THEN 1.0 ELSE 0 END), 1) pct_reach_9_7
FROM views GROUP BY plat, tt ORDER BY tt, plat
