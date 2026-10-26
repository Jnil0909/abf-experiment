-- v10 headline, all three platforms in ONE query, CUPED lifts computed in SQL (refresh 2026-10-20).
-- Window: first exposure .. 2026-10-20 00:00 UTC (end of 2026-10-19); pre-period 2026-09-25..2026-10-08 (all titles).
-- On-title / ToT use the 224,739 targeted titles (ml_dev.tmp.abf3_v10_targeted_titles), NOT the 299k live ABF2 catalog.
-- Same definitions as headline.sql (+ _mobile/_web). Output: one text row per (plat, pop, metric):
--   "arm:lift|lo|hi;..." (percent, CUPED, Welch 95%), plus 'n' rows (devices per arm) and 'cm' rows (ITT Control per-device means).
-- Note: raw-stat versions (headline*.sql) feed build_values.py; this one skips the raw sums to keep the output small.
WITH exp AS (
  SELECT device_id,
    CASE experiment_id WHEN 'ads_abf_3_v10_abf2_titles_only' THEN 'OTT'
                       WHEN 'ads_mobile_abf_3_v10_abf2_titles_only' THEN 'MOBILE' ELSE 'WEB' END AS plat,
    MAX(group_name) AS variant, MIN(timestamp) AS fe
  FROM core_dev.statsig.exposures
  WHERE experiment_id IN ('ads_abf_3_v10_abf2_titles_only','ads_mobile_abf_3_v10_abf2_titles_only','ads_web_abf_3_v10_abf2_titles_only')
  GROUP BY device_id, experiment_id HAVING COUNT(DISTINCT group_name) = 1
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
    AND content_id IN (SELECT CAST(content_id AS STRING) FROM ml_dev.tmp.abf3_v10_targeted_titles)
),
vs_post AS (
  SELECT e.device_id,
    SUM(v.tvt_millisec/60000.0) AS y_tvt,
    SUM(CASE WHEN a.content_id IS NOT NULL THEN v.tvt_millisec/60000.0 ELSE 0 END) AS yo_tvt,
    MAX(CASE WHEN a.content_id IS NOT NULL AND v.tvt_millisec >= 1000 THEN 1 ELSE 0 END) AS is_tot
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id = v.device_id AND v.start_ts >= e.fe AND v.start_ts < '2026-10-20 00:00:00'
   AND v.ds >= '2026-10-09' AND v.ds <= '2026-10-19'
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
        WHERE date >= '2026-10-09' AND date <= '2026-10-19' AND unbillable = 'f' AND ts < '2026-10-20 00:00:00') i
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
  SELECT e.plat, e.variant,
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
),
agg AS (
  SELECT plat, pop, variant, COUNT(*) n,
    SUM(x_tvt) sx_tvt, SUM(x_tvt*x_tvt) sxx_tvt,
    SUM(x_revt) sx_revt, SUM(x_revt*x_revt) sxx_revt,
    SUM(x_revb) sx_revb, SUM(x_revb*x_revb) sxx_revb,
    SUM(x_impt) sx_impt, SUM(CAST(x_impt AS DOUBLE)*x_impt) sxx_impt,
    SUM(x_impb) sx_impb, SUM(CAST(x_impb AS DOUBLE)*x_impb) sxx_impb,
    SUM(x_revu) sx_revu, SUM(x_revu*x_revu) sxx_revu,
    SUM(x_impu) sx_impu, SUM(CAST(x_impu AS DOUBLE)*x_impu) sxx_impu,
    SUM(y_tvt) sy_tvt, SUM(y_tvt*y_tvt) syy_tvt, SUM(x_tvt*y_tvt) sxy_tvt,
    SUM(yo_tvt) sy_otvt, SUM(yo_tvt*yo_tvt) syy_otvt, SUM(x_tvt*yo_tvt) sxy_otvt,
    SUM(y_revt) sy_revt, SUM(y_revt*y_revt) syy_revt, SUM(x_revt*y_revt) sxy_revt,
    SUM(y_revb) sy_revb, SUM(y_revb*y_revb) syy_revb, SUM(x_revb*y_revb) sxy_revb,
    SUM(y_impt) sy_impt, SUM(CAST(y_impt AS DOUBLE)*y_impt) syy_impt, SUM(CAST(x_impt AS DOUBLE)*y_impt) sxy_impt,
    SUM(y_impb) sy_impb, SUM(CAST(y_impb AS DOUBLE)*y_impb) syy_impb, SUM(CAST(x_impb AS DOUBLE)*y_impb) sxy_impb,
    SUM(y_revu) sy_revu, SUM(y_revu*y_revu) syy_revu, SUM(x_revu*y_revu) sxy_revu,
    SUM(y_impu) sy_impu, SUM(CAST(y_impu AS DOUBLE)*y_impu) syy_impu, SUM(CAST(x_impu AS DOUBLE)*y_impu) sxy_impu,
    SUM(yo_revu) sy_orevu, SUM(yo_revu*yo_revu) syy_orevu, SUM(x_revu*yo_revu) sxy_orevu,
    SUM(yo_impu) sy_oimpu, SUM(CAST(yo_impu AS DOUBLE)*yo_impu) syy_oimpu, SUM(CAST(x_impu AS DOUBLE)*yo_impu) sxy_oimpu
  FROM dev
  LATERAL VIEW explode(array('ITT', IF(is_active=1,'Active',NULL), IF(is_tot=1,'ToT',NULL), IF(pv=1,'PV','NPV'))) p AS pop
  WHERE pop IS NOT NULL
  GROUP BY plat, pop, variant
),
u AS (
  SELECT plat, pop, variant, CAST(n AS DOUBLE) AS n, stack(10,
    'tvt',   CAST(sx_tvt AS DOUBLE),  CAST(sxx_tvt AS DOUBLE),  CAST(sy_tvt AS DOUBLE),   CAST(syy_tvt AS DOUBLE),   CAST(sxy_tvt AS DOUBLE),
    'otvt',  CAST(sx_tvt AS DOUBLE),  CAST(sxx_tvt AS DOUBLE),  CAST(sy_otvt AS DOUBLE),  CAST(syy_otvt AS DOUBLE),  CAST(sxy_otvt AS DOUBLE),
    'revt',  CAST(sx_revt AS DOUBLE), CAST(sxx_revt AS DOUBLE), CAST(sy_revt AS DOUBLE),  CAST(syy_revt AS DOUBLE),  CAST(sxy_revt AS DOUBLE),
    'revb',  CAST(sx_revb AS DOUBLE), CAST(sxx_revb AS DOUBLE), CAST(sy_revb AS DOUBLE),  CAST(syy_revb AS DOUBLE),  CAST(sxy_revb AS DOUBLE),
    'impt',  CAST(sx_impt AS DOUBLE), CAST(sxx_impt AS DOUBLE), CAST(sy_impt AS DOUBLE),  CAST(syy_impt AS DOUBLE),  CAST(sxy_impt AS DOUBLE),
    'impb',  CAST(sx_impb AS DOUBLE), CAST(sxx_impb AS DOUBLE), CAST(sy_impb AS DOUBLE),  CAST(syy_impb AS DOUBLE),  CAST(sxy_impb AS DOUBLE),
    'revu',  CAST(sx_revu AS DOUBLE), CAST(sxx_revu AS DOUBLE), CAST(sy_revu AS DOUBLE),  CAST(syy_revu AS DOUBLE),  CAST(sxy_revu AS DOUBLE),
    'impu',  CAST(sx_impu AS DOUBLE), CAST(sxx_impu AS DOUBLE), CAST(sy_impu AS DOUBLE),  CAST(syy_impu AS DOUBLE),  CAST(sxy_impu AS DOUBLE),
    'orevu', CAST(sx_revu AS DOUBLE), CAST(sxx_revu AS DOUBLE), CAST(sy_orevu AS DOUBLE), CAST(syy_orevu AS DOUBLE), CAST(sxy_orevu AS DOUBLE),
    'oimpu', CAST(sx_impu AS DOUBLE), CAST(sxx_impu AS DOUBLE), CAST(sy_oimpu AS DOUBLE), CAST(syy_oimpu AS DOUBLE), CAST(sxy_oimpu AS DOUBLE)
  ) AS (m, sx, sxx, sy, syy, sxy)
  FROM agg
),
th AS (
  SELECT plat, pop, m, SUM(sx)/SUM(n) AS xbar,
    ((SUM(sxy) - SUM(sx)*SUM(sy)/SUM(n))/(SUM(n)-1)) / ((SUM(sxx) - SUM(sx)*SUM(sx)/SUM(n))/(SUM(n)-1)) AS theta
  FROM u GROUP BY plat, pop, m
),
st AS (
  SELECT u.plat, u.pop, u.variant, u.m, u.n,
    u.sy/u.n - th.theta*(u.sx/u.n - th.xbar) AS am,
    ((u.syy - u.n*pow(u.sy/u.n,2))/(u.n-1))
      - 2*th.theta*((u.sxy - u.n*(u.sx/u.n)*(u.sy/u.n))/(u.n-1))
      + pow(th.theta,2)*((u.sxx - u.n*pow(u.sx/u.n,2))/(u.n-1)) AS av
  FROM u JOIN th ON u.plat = th.plat AND u.pop = th.pop AND u.m = th.m
),
fin AS (
  SELECT t.plat, t.pop, t.m, t.variant,
    100*(t.am - c.am)/c.am AS l,
    100*((t.am - c.am) - 1.96*sqrt(t.av/t.n + c.av/c.n))/c.am AS lo,
    100*((t.am - c.am) + 1.96*sqrt(t.av/t.n + c.av/c.n))/c.am AS hi
  FROM st t JOIN st c ON t.plat = c.plat AND t.pop = c.pop AND t.m = c.m AND c.variant = 'Control'
  WHERE t.variant <> 'Control'
)
SELECT plat, pop, m, concat_ws(';', sort_array(collect_list(concat(variant, ':', round(l,4), '|', round(lo,4), '|', round(hi,4))))) AS s
FROM fin
WHERE pop = 'ITT'
   OR (pop IN ('Active','ToT') AND m IN ('revt','revu','impu','orevu','oimpu','tvt','otvt'))
   OR (pop IN ('NPV','PV') AND m = 'tvt')
GROUP BY plat, pop, m
UNION ALL
SELECT plat, pop, 'n', concat_ws(';', sort_array(collect_list(concat(variant, ':', CAST(n AS BIGINT)))))
FROM agg GROUP BY plat, pop
UNION ALL
SELECT plat, 'ITT', 'cm', concat('revt:', round(sy_revt/n,5), ';revb:', round(sy_revb/n,5), ';impt:', round(sy_impt/n,3), ';tvt:', round(sy_tvt/n,3))
FROM agg WHERE pop = 'ITT' AND variant = 'Control'
ORDER BY plat, pop, m
