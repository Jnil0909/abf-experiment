-- v10 served-cue checks: arm mapping, cue points/hour vs ABF2, first cue, below/equal/more by band.
WITH stream AS (
  SELECT movie_id AS content_id, 'Movie' AS tt, cue_points_abf AS cpa, cue_points_info AS cpi FROM core_prod.tubidw.content_movie_stream
  UNION ALL
  SELECT episode_id, 'Episode', cue_points_abf, cue_points_info FROM core_prod.tubidw.content_episode_stream
),
abf2 AS (
  SELECT content_id, MAX(tt) tt, MAX(cpa) cpa FROM stream
  WHERE cpa IS NOT NULL AND cpa NOT IN ('[]','{}','{0.0}','')
    AND COALESCE(cpi,'') <> 'abf3_pruned_v8'
    AND content_id NOT IN (SELECT content_id FROM core_dev.dsa.temp_bp_abf_v8_all_titles)
  GROUP BY content_id
),
abf2_n AS (
  SELECT content_id, tt,
    filter(transform(split(regexp_replace(cpa,'[{}]',''),','), x -> try_cast(x AS DOUBLE)), x -> x IS NOT NULL AND x > 0) AS pts
  FROM abf2
),
srv AS (
  SELECT content_id, slasher_version AS arm, pruner_arm, duration_sec,
         size(slashed_cue_points_sec) AS n_srv,
         array_min(slashed_cue_points_sec) AS first_srv
  FROM ml_dev.tmp.abf3_new_pruner_cuepoints
),
j AS (
  SELECT s.*, a.tt, size(a.pts) AS n_ctl, array_min(a.pts) AS first_ctl,
    CASE WHEN size(a.pts) <= 3 THEN '1-3' WHEN size(a.pts) <= 6 THEN '4-6' WHEN size(a.pts) <= 9 THEN '7-9'
         WHEN size(a.pts) <= 12 THEN '10-12' ELSE '13+' END AS band
  FROM srv s JOIN abf2_n a ON s.content_id = a.content_id
  WHERE size(a.pts) > 0 AND s.duration_sec > 0
)
SELECT 'cphr' AS k, tt, arm, pruner_arm, NULL AS band, COUNT(*) n,
  ROUND(AVG(n_ctl/(duration_sec/3600.0)),2) ctl_cphr, ROUND(AVG(n_srv/(duration_sec/3600.0)),2) srv_cphr,
  ROUND(AVG(first_ctl),0) ctl_first, ROUND(AVG(first_srv),0) srv_first,
  NULL pct_below, NULL pct_equal, NULL pct_more
FROM j GROUP BY tt, arm, pruner_arm
UNION ALL
SELECT 'band', tt, arm, pruner_arm, band, COUNT(*),
  NULL, NULL, NULL, NULL,
  ROUND(100*AVG(CASE WHEN n_srv < n_ctl THEN 1.0 ELSE 0 END),1),
  ROUND(100*AVG(CASE WHEN n_srv = n_ctl THEN 1.0 ELSE 0 END),1),
  ROUND(100*AVG(CASE WHEN n_srv > n_ctl THEN 1.0 ELSE 0 END),1)
FROM j GROUP BY tt, arm, pruner_arm, band
ORDER BY 1, 2, 5, 3
