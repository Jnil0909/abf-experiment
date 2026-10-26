-- v10 headline re-derivation: per-arm sufficient statistics for CUPED, by population.
-- Window: first exposure .. 2026-10-19 00:00 UTC (end of 10-18); pre-period 2026-09-25..2026-10-08 (all titles).
WITH exp AS (
  SELECT device_id, MAX(group_name) AS variant, MIN(timestamp) AS fe
  FROM core_dev.statsig.exposures WHERE experiment_id = 'ads_mobile_abf_3_v10_abf2_titles_only'
  GROUP BY device_id HAVING COUNT(DISTINCT group_name) = 1
),
stream AS (
  SELECT CAST(movie_id AS STRING) AS content_id, cue_points_abf AS cpa, cue_points_info AS cpi FROM core_prod.tubidw.content_movie_stream
  UNION ALL
  SELECT CAST(episode_id AS STRING), cue_points_abf, cue_points_info FROM core_prod.tubidw.content_episode_stream
),
abf2 AS (
  SELECT DISTINCT content_id FROM stream
  WHERE cpa IS NOT NULL AND cpa NOT IN ('[]','{}','{0.0}','')
    AND COALESCE(cpi,'') <> 'abf3_pruned_v8'
    AND content_id NOT IN (SELECT CAST(content_id AS STRING) FROM core_dev.dsa.temp_bp_abf_v8_all_titles)
),
vs_post AS (
  SELECT e.device_id,
    SUM(v.tvt_millisec/60000.0) AS y_tvt,
    SUM(CASE WHEN a.content_id IS NOT NULL THEN v.tvt_millisec/60000.0 ELSE 0 END) AS yo_tvt,
    MAX(CASE WHEN a.content_id IS NOT NULL AND v.tvt_millisec >= 1000 THEN 1 ELSE 0 END) AS is_tot
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id = v.device_id AND v.start_ts >= e.fe AND v.start_ts < '2026-10-19 00:00:00'
   AND v.ds >= '2026-10-09' AND v.ds <= '2026-10-18'
  LEFT JOIN abf2 a ON CAST(v.content_id AS STRING) = a.content_id
  GROUP BY e.device_id
),
im_post AS (
  SELECT e.device_id,
    SUM(CAST(i.cost AS DOUBLE)) AS y_revt,
    SUM(CASE WHEN c.budget IS NOT NULL THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS y_revb,
    COUNT(*) AS y_impt,
    SUM(CASE WHEN c.budget IS NOT NULL THEN 1 ELSE 0 END) AS y_impb,
    SUM(CASE WHEN (c.budget IS NULL AND i.u0) THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS y_revu,
    SUM(CASE WHEN (c.budget IS NULL AND i.u0) THEN 1 ELSE 0 END) AS y_impu,
    SUM(CASE WHEN (c.budget IS NULL AND i.u0) AND a.content_id IS NOT NULL THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS yo_revu,
    SUM(CASE WHEN (c.budget IS NULL AND i.u0) AND a.content_id IS NOT NULL THEN 1 ELSE 0 END) AS yo_impu
  FROM exp e
  JOIN (SELECT *, (revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                   AND advertiser_id NOT IN (1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452)) AS u0
        FROM core_prod.ads.impressions
        WHERE date >= '2026-10-09' AND date <= '2026-10-18' AND unbillable = 'f' AND ts < '2026-10-19 00:00:00') i
    ON e.device_id = i.device_id AND i.ts >= e.fe
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  LEFT JOIN abf2 a ON CAST(i.content_id AS STRING) = a.content_id
  GROUP BY e.device_id
),
vs_pre AS (
  SELECT e.device_id, SUM(v.tvt_millisec/60000.0) AS x_tvt
  FROM exp e JOIN core_prod.tubidw.video_session v ON e.device_id = v.device_id
  WHERE v.ds >= '2026-09-25' AND v.ds <= '2026-10-08'
  GROUP BY e.device_id
),
im_pre AS (
  SELECT e.device_id,
    SUM(CAST(i.cost AS DOUBLE)) AS x_revt,
    SUM(CASE WHEN c.budget IS NOT NULL THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS x_revb,
    COUNT(*) AS x_impt,
    SUM(CASE WHEN c.budget IS NOT NULL THEN 1 ELSE 0 END) AS x_impb,
    SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
             AND i.advertiser_id NOT IN (1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452)
             THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS x_revu,
    SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
             AND i.advertiser_id NOT IN (1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452)
             THEN 1 ELSE 0 END) AS x_impu
  FROM exp e JOIN core_prod.ads.impressions i ON e.device_id = i.device_id
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '2026-09-25' AND i.date <= '2026-10-08' AND i.unbillable = 'f'
  GROUP BY e.device_id
),
okr AS (
  SELECT e.device_id,
    MAX_BY(CASE WHEN o.visit_days_last28d_count >= 8
                 AND (o.tvt_sec_last28 + o.linear_tvt_sec_last28)/3600.0/NULLIF(o.visit_days_last28d_count,0) > 4
                THEN 1 ELSE 0 END, o.ds) AS pv
  FROM exp e JOIN core_prod.tubidw.device_okr_daily o
    ON e.device_id = o.device_id AND o.ds BETWEEN '2026-10-02' AND CAST(e.fe AS DATE)
  GROUP BY e.device_id
),
dev AS (
  SELECT e.variant,
    CASE WHEN vp.device_id IS NOT NULL THEN 1 ELSE 0 END AS is_active,
    COALESCE(vp.is_tot,0) AS is_tot, COALESCE(k.pv,0) AS pv,
    COALESCE(vp.y_tvt,0) y_tvt, COALESCE(vp.yo_tvt,0) yo_tvt,
    COALESCE(ip.y_revt,0) y_revt, COALESCE(ip.y_revb,0) y_revb, COALESCE(ip.y_impt,0) y_impt,
    COALESCE(ip.y_impb,0) y_impb, COALESCE(ip.y_revu,0) y_revu, COALESCE(ip.y_impu,0) y_impu,
    COALESCE(ip.yo_revu,0) yo_revu, COALESCE(ip.yo_impu,0) yo_impu,
    COALESCE(xv.x_tvt,0) x_tvt, COALESCE(xi.x_revt,0) x_revt, COALESCE(xi.x_revb,0) x_revb,
    COALESCE(xi.x_impt,0) x_impt, COALESCE(xi.x_impb,0) x_impb, COALESCE(xi.x_revu,0) x_revu, COALESCE(xi.x_impu,0) x_impu
  FROM exp e
  LEFT JOIN vs_post vp ON e.device_id = vp.device_id
  LEFT JOIN im_post ip ON e.device_id = ip.device_id
  LEFT JOIN vs_pre xv ON e.device_id = xv.device_id
  LEFT JOIN im_pre xi ON e.device_id = xi.device_id
  LEFT JOIN okr k ON e.device_id = k.device_id
)
SELECT pop, variant, COUNT(*) n,
  -- covariates
  SUM(x_tvt) sx_tvt, SUM(x_tvt*x_tvt) sxx_tvt,
  SUM(x_revt) sx_revt, SUM(x_revt*x_revt) sxx_revt,
  SUM(x_revb) sx_revb, SUM(x_revb*x_revb) sxx_revb,
  SUM(x_impt) sx_impt, SUM(x_impt*x_impt) sxx_impt,
  SUM(x_impb) sx_impb, SUM(x_impb*x_impb) sxx_impb,
  SUM(x_revu) sx_revu, SUM(x_revu*x_revu) sxx_revu,
  SUM(x_impu) sx_impu, SUM(x_impu*x_impu) sxx_impu,
  -- outcomes: y, y^2, x*y  (metric name : covariate)
  SUM(y_tvt) sy_tvt, SUM(y_tvt*y_tvt) syy_tvt, SUM(x_tvt*y_tvt) sxy_tvt,
  SUM(yo_tvt) sy_otvt, SUM(yo_tvt*yo_tvt) syy_otvt, SUM(x_tvt*yo_tvt) sxy_otvt,
  SUM(y_revt) sy_revt, SUM(y_revt*y_revt) syy_revt, SUM(x_revt*y_revt) sxy_revt,
  SUM(y_revb) sy_revb, SUM(y_revb*y_revb) syy_revb, SUM(x_revb*y_revb) sxy_revb,
  SUM(y_impt) sy_impt, SUM(y_impt*y_impt) syy_impt, SUM(x_impt*y_impt) sxy_impt,
  SUM(y_impb) sy_impb, SUM(y_impb*y_impb) syy_impb, SUM(x_impb*y_impb) sxy_impb,
  SUM(y_revu) sy_revu, SUM(y_revu*y_revu) syy_revu, SUM(x_revu*y_revu) sxy_revu,
  SUM(y_impu) sy_impu, SUM(y_impu*y_impu) syy_impu, SUM(x_impu*y_impu) sxy_impu,
  SUM(yo_revu) sy_orevu, SUM(yo_revu*yo_revu) syy_orevu, SUM(x_revu*yo_revu) sxy_orevu,
  SUM(yo_impu) sy_oimpu, SUM(yo_impu*yo_impu) syy_oimpu, SUM(x_impu*yo_impu) sxy_oimpu
FROM dev
LATERAL VIEW explode(array('ITT',
                           IF(is_active=1,'Active',NULL),
                           IF(is_tot=1,'ToT',NULL),
                           IF(pv=1,'PV','NPV'))) p AS pop
WHERE pop IS NOT NULL
GROUP BY pop, variant
ORDER BY pop, variant
