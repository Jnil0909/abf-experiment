-- v10 §2a/§2b/§2c: raw device-level sufficient stats on ABF2 titles by band, type, and arm-specific below-control tag.
WITH exp AS (
  SELECT device_id, MAX(group_name) AS variant, MIN(timestamp) AS fe
  FROM core_dev.statsig.exposures WHERE experiment_id = 'ads_mobile_abf_3_v10_abf2_titles_only'
  GROUP BY device_id HAVING COUNT(DISTINCT group_name) = 1
),
stream AS (
  SELECT movie_id AS content_id, 'Movie' AS tt, cue_points_abf AS cpa, cue_points_info AS cpi FROM core_prod.tubidw.content_movie_stream
  UNION ALL
  SELECT episode_id, 'Episode', cue_points_abf, cue_points_info FROM core_prod.tubidw.content_episode_stream
),
abf2 AS (
  SELECT content_id, MAX(tt) tt,
    size(filter(transform(split(regexp_replace(MAX(cpa),'[{}]',''),','), x -> try_cast(x AS DOUBLE)), x -> x IS NOT NULL AND x > 0)) AS n_ctl
  FROM stream
  WHERE cpa IS NOT NULL AND cpa NOT IN ('[]','{}','{0.0}','')
    AND COALESCE(cpi,'') <> 'abf3_pruned_v8'
    AND content_id NOT IN (SELECT content_id FROM core_dev.dsa.temp_bp_abf_v8_all_titles)
  GROUP BY content_id
),
meta AS (
  SELECT content_id, tt, n_ctl,
    CASE WHEN n_ctl <= 3 THEN '1-3' WHEN n_ctl <= 6 THEN '4-6' WHEN n_ctl <= 9 THEN '7-9'
         WHEN n_ctl <= 12 THEN '10-12' ELSE '13+' END AS band
  FROM abf2 WHERE n_ctl > 0
),
tags AS (
  SELECT s.content_id, s.slasher_version AS tag_arm, m.band,
         CASE WHEN size(s.slashed_cue_points_sec) < m.n_ctl THEN 'below' ELSE 'at/above' END AS below
  FROM ml_dev.tmp.abf3_new_pruner_cuepoints s JOIN meta m ON s.content_id = m.content_id
  WHERE m.band IN ('10-12','13+')
),
vs AS (
  SELECT e.device_id, e.variant, v.content_id, SUM(v.tvt_millisec/60000.0) AS tvt
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id = v.device_id AND v.start_ts >= e.fe AND v.start_ts < '2026-10-19 00:00:00'
   AND v.ds >= '2026-10-09' AND v.ds <= '2026-10-18'
  WHERE v.content_id IN (SELECT content_id FROM meta)
  GROUP BY e.device_id, e.variant, v.content_id
),
imp AS (
  SELECT i.device_id, CAST(i.content_id AS INT) AS content_id,
    SUM(CAST(i.cost AS DOUBLE)) AS rev, COUNT(*) AS imps
  FROM core_prod.ads.impressions i
  JOIN exp e ON i.device_id = e.device_id AND i.ts >= e.fe
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '2026-10-09' AND i.date <= '2026-10-18' AND i.ts < '2026-10-19 00:00:00' AND i.unbillable = 'f'
    AND c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
    AND i.advertiser_id NOT IN (1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452)
    AND i.content_id IN (SELECT CAST(content_id AS STRING) FROM meta)
  GROUP BY i.device_id, CAST(i.content_id AS INT)
),
dt AS (
  SELECT vs.device_id, vs.variant, vs.content_id, m.band, m.tt, vs.tvt,
         COALESCE(imp.rev,0) rev, COALESCE(imp.imps,0) imps
  FROM vs JOIN meta m ON vs.content_id = m.content_id
  LEFT JOIN imp ON vs.device_id = imp.device_id AND vs.content_id = imp.content_id
),
g AS (
  SELECT CONCAT('band|', band) grp, variant, device_id, SUM(rev) rev, SUM(tvt) tvt, SUM(imps) imps FROM dt GROUP BY 1,2,3
  UNION ALL
  SELECT CONCAT('type|', tt), variant, device_id, SUM(rev), SUM(tvt), SUM(imps) FROM dt GROUP BY 1,2,3
  UNION ALL
  SELECT CONCAT('below|', t.tag_arm, '|', t.band, '|', t.below), dt.variant, dt.device_id, SUM(rev), SUM(tvt), SUM(imps)
  FROM dt JOIN tags t ON dt.content_id = t.content_id
  WHERE dt.variant IN (t.tag_arm, 'Control')
  GROUP BY 1,2,3
)
SELECT grp, variant, COUNT(*) n,
  SUM(rev) s_rev, SUM(rev*rev) ss_rev, SUM(tvt) s_tvt, SUM(tvt*tvt) ss_tvt, SUM(imps) s_imps, SUM(CAST(imps AS DOUBLE)*imps) ss_imps
FROM g GROUP BY grp, variant ORDER BY grp, variant
