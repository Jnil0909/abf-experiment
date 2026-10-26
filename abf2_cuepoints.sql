-- ABF2 cue points per title (live snapshot).
-- Saved 2026-10-19. Count comparison vs a Slasher version: abf_cuepoint_count_vs_abf2.sql
--
-- WHERE ABF2 CUE POINTS LIVE
--   There is no dedicated ABF2 cue-point table. ABF2 = `cue_points_abf` in
--   core_prod.tubidw.content_movie_stream (movie_id) / content_episode_stream (episode_id),
--   after removing titles that ABF3 v8 overwrote:
--     - cue_points_info = 'abf3_pruned_v8'   (all 187,646 such rows are in the v8 list)
--     - content_id IN core_dev.dsa.temp_bp_abf_v8_all_titles
--   Result (2026-10-19): ~300k titles, all parse to >=1 cue point.
--
-- CAVEATS
--   1. LIVE snapshot only. A title that served ABF2 earlier and was later overwritten by ABF3
--      no longer shows its old ABF2 cues. Future ABF3 rollouts must be added to the exclusions.
--   2. cue_points_info does NOT tag ABF2. Remaining titles: ~219k null, ~79.6k
--      "imported from partner's metadata", ~400 other notes. Partner-tagged rows look like ML output
--      (same {a,b,c} format, median first cue ~363s vs ~341s for null), so cue_points_info likely
--      describes the manual `cue_points` field. Stricter baseline: add AND cue_points_info IS NULL.
--   3. Format is brace-wrapped seconds: {657.89,1080.81,...}. Empty = '[]','{}','{0.0}',''.
--      Strip {} before splitting (see claude-memory/reference_cue_point_columns.md).
--   4. Movie and episode IDs never overlap, so the UNION is safe.
--
-- RELATED TABLES
--   core_dev.dsa.temp_bp_abf_v2_exp_titles  -- ABF2-vs-ABF1 title assignment for the Apr-2026 experiment
--                                              (content_id, cuepoint_type = ABF1/ABF2, excluded). Titles only, no cues.
--   ml_prod.ads.abf3_slasher_cuepoints      -- ABF3 slasher output by date; slasher_version raw / v1.1 / v2.
--                                              'v2' = ABF3 Slasher v2, NOT ABF2.
--   core_prod.tubidw.content_cue_points     -- submitted + raw ML-detected cue points; not the same as cue_points_abf.

WITH stream AS (
  SELECT movie_id AS content_id, 'movie' AS title_type, cue_points_abf, cue_points_info
  FROM core_prod.tubidw.content_movie_stream
  UNION ALL
  SELECT episode_id, 'episode', cue_points_abf, cue_points_info
  FROM core_prod.tubidw.content_episode_stream
)
SELECT content_id,
       title_type,
       cue_points_abf AS abf2_cue_points,
       size(filter(transform(split(regexp_replace(cue_points_abf,'[{}]',''),','), x -> try_cast(x AS DOUBLE)),
                   x -> x IS NOT NULL AND x > 0)) AS n_abf2
FROM stream
WHERE cue_points_abf IS NOT NULL
  AND cue_points_abf NOT IN ('[]','{}','{0.0}','')
  AND COALESCE(cue_points_info,'') <> 'abf3_pruned_v8'
  AND content_id NOT IN (SELECT content_id FROM core_dev.dsa.temp_bp_abf_v8_all_titles)
