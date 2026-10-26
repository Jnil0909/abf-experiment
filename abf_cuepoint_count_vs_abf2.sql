-- ABF2 live cue-point count vs a Slasher version.
-- Saved 2026-10-13 from the v10 pre-restart check (that run used slasher_version = 'v2').
-- Reuse for later ABF3 experiments: change the version filter in `v2`.
--
-- What it answers: on titles still serving ABF2 (not the graduated v8 ABF1 set),
-- does this Slasher version keep fewer, the same, or more cue points than ABF2?
--
-- Snapshot result shared 2026-10-13 (stopped v10, Slasher v2):
--   episode  191,035 titles  avg ABF2 4.86  avg v2 4.36  v2 vs ABF2 -10.14%
--            fewer 47.8%  equal 36.4%  more 15.8%
--   movie     33,704 titles  avg ABF2 12.48 avg v2 11.77 v2 vs ABF2 -5.69%
--            fewer 57.5%  equal 16.1%  more 26.5%
--
-- Notes (verified 2026-10-19; full context in abf2_cuepoints.sql):
--   - `v2` = ABF3 Slasher v2 (ml_prod.ads.abf3_slasher_cuepoints), NOT ABF2.
--   - Inner join: only ABF2 titles that have a slasher row count (~224k of ~300k).
--   - n_abf2 drops cues <= 0; n_v2 counts every element. Use the same filter on both if slasher arrays can hold 0.
--   - ABF2 side is a live snapshot; titles overwritten by later ABF3 rollouts must be added to the exclusions.

WITH stream AS (
  SELECT movie_id AS content_id, 'movie' AS title_type, cue_points_abf AS cpa, cue_points_info AS cpi
  FROM core_prod.tubidw.content_movie_stream
  UNION ALL
  SELECT episode_id, 'episode', cue_points_abf, cue_points_info
  FROM core_prod.tubidw.content_episode_stream
),
abf2 AS (
  SELECT content_id, MAX(title_type) title_type, MAX(cpa) cpa, MAX(cpi) cpi
  FROM stream
  WHERE cpa IS NOT NULL AND cpa NOT IN ('[]','{}','{0.0}','')
    AND COALESCE(cpi,'') <> 'abf3_pruned_v8'
    AND content_id NOT IN (SELECT content_id FROM core_dev.dsa.temp_bp_abf_v8_all_titles)
  GROUP BY content_id
),
abf2_n AS (
  SELECT content_id, title_type,
         size(filter(transform(split(regexp_replace(cpa,'[{}]',''),','), x -> try_cast(x AS DOUBLE)),
                     x -> x IS NOT NULL AND x > 0)) AS n_abf2
  FROM abf2
),
v2 AS (
  SELECT content_id, size(slashed_cue_points_sec) AS n_v2
  FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY content_id ORDER BY date DESC) rn
        FROM ml_prod.ads.abf3_slasher_cuepoints WHERE slasher_version = 'v2')
  WHERE rn = 1
)
SELECT a.title_type, COUNT(*) titles,
       ROUND(AVG(a.n_abf2),2) avg_abf2, ROUND(AVG(v.n_v2),2) avg_v2,
       ROUND(100*(AVG(v.n_v2)/AVG(a.n_abf2)-1),2) v2_vs_abf2,
       100*ROUND(AVG(CASE WHEN v.n_v2 < a.n_abf2 THEN 1.0 ELSE 0 END),3) share_v2_fewer,
       100*ROUND(AVG(CASE WHEN v.n_v2 = a.n_abf2 THEN 1.0 ELSE 0 END),3) share_equal,
       100*ROUND(AVG(CASE WHEN v.n_v2 > a.n_abf2 THEN 1.0 ELSE 0 END),3) share_v2_more
FROM abf2_n a JOIN v2 v ON a.content_id = v.content_id
GROUP BY a.title_type
