-- Reconcile with Binoop's OTT report (2026-10-20). OTT only, ITT + ToT.
-- Binoop spec: window ds 2026-10-10..10-18 (from first exposure), pre-period 2026-09-17..09-30.
-- On-title computed two ways in one pass: a = our live ABF2-catalog CTE, t = ml_dev.tmp.abf3_v10_targeted_titles.
-- Output: one row per (pop, metric) as "arm:lift|lo|hi;..." (CUPED %, Welch 95%), plus n rows.
WITH exp AS (
  SELECT device_id, MAX(group_name) AS variant, MIN(timestamp) AS fe
  FROM core_dev.statsig.exposures
  WHERE experiment_id = 'ads_abf_3_v10_abf2_titles_only'
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
tgt AS (SELECT DISTINCT CAST(content_id AS STRING) AS content_id FROM ml_dev.tmp.abf3_v10_targeted_titles),
vs_post AS (
  SELECT e.device_id,
    SUM(v.tvt_millisec/60000.0) AS y_tvt,
    SUM(CASE WHEN a.content_id IS NOT NULL THEN v.tvt_millisec/60000.0 ELSE 0 END) AS ya_tvt,
    SUM(CASE WHEN t.content_id IS NOT NULL THEN v.tvt_millisec/60000.0 ELSE 0 END) AS yt_tvt,
    MAX(CASE WHEN a.content_id IS NOT NULL AND v.tvt_millisec >= 1000 THEN 1 ELSE 0 END) AS is_tot_a,
    MAX(CASE WHEN t.content_id IS NOT NULL AND v.tvt_millisec >= 1000 THEN 1 ELSE 0 END) AS is_tot_t
  FROM exp e JOIN core_prod.tubidw.video_session v
    ON e.device_id = v.device_id AND v.start_ts >= e.fe AND v.start_ts < '2026-10-19 00:00:00'
   AND v.ds >= '2026-10-10' AND v.ds <= '2026-10-18'
  LEFT JOIN abf2 a ON CAST(v.content_id AS STRING) = a.content_id
  LEFT JOIN tgt t ON CAST(v.content_id AS STRING) = t.content_id
  GROUP BY e.device_id
),
im_post AS (
  SELECT e.device_id,
    SUM(CAST(i.cost AS DOUBLE)) AS y_revt,
    SUM(CASE WHEN (c.budget IS NULL AND i.u0) THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS y_revu,
    SUM(CASE WHEN (c.budget IS NULL AND i.u0) AND a.content_id IS NOT NULL THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS ya_revu,
    SUM(CASE WHEN (c.budget IS NULL AND i.u0) AND t.content_id IS NOT NULL THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS yt_revu
  FROM exp e
  JOIN (SELECT *, (revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
                   AND advertiser_id NOT IN (1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452)) AS u0
        FROM core_prod.ads.impressions
        WHERE date >= '2026-10-10' AND date <= '2026-10-18' AND unbillable = 'f' AND ts < '2026-10-19 00:00:00') i
    ON e.device_id = i.device_id AND i.ts >= e.fe
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  LEFT JOIN abf2 a ON CAST(i.content_id AS STRING) = a.content_id
  LEFT JOIN tgt t ON CAST(i.content_id AS STRING) = t.content_id
  GROUP BY e.device_id
),
vs_pre AS (
  SELECT e.device_id, SUM(v.tvt_millisec/60000.0) AS x_tvt
  FROM exp e JOIN core_prod.tubidw.video_session v ON e.device_id = v.device_id
  WHERE v.ds >= '2026-09-17' AND v.ds <= '2026-09-30'
  GROUP BY e.device_id
),
im_pre AS (
  SELECT e.device_id,
    SUM(CAST(i.cost AS DOUBLE)) AS x_revt,
    SUM(CASE WHEN c.budget IS NULL AND i.revenue_stream IN ('PROGRAMMATIC_OPEN','PROGRAMMATIC_DIRECT')
             AND i.advertiser_id NOT IN (1,55025,55098,2,50237,56209,56360,56414,69,55013,56316,55010,13,56346,56359,56405,56411,56450,56452)
             THEN CAST(i.cost AS DOUBLE) ELSE 0 END) AS x_revu
  FROM exp e JOIN core_prod.ads.impressions i ON e.device_id = i.device_id
  JOIN core_prod.mercurydb_cdc.campaigns c ON i.campaign_id = c.id
  WHERE i.date >= '2026-09-17' AND i.date <= '2026-09-30' AND i.unbillable = 'f'
  GROUP BY e.device_id
),
dev AS (
  SELECT e.variant,
    COALESCE(vp.is_tot_a,0) AS is_tot_a, COALESCE(vp.is_tot_t,0) AS is_tot_t,
    COALESCE(vp.y_tvt,0) y_tvt, COALESCE(vp.ya_tvt,0) ya_tvt, COALESCE(vp.yt_tvt,0) yt_tvt,
    COALESCE(ip.y_revt,0) y_revt, COALESCE(ip.y_revu,0) y_revu, COALESCE(ip.ya_revu,0) ya_revu, COALESCE(ip.yt_revu,0) yt_revu,
    COALESCE(xv.x_tvt,0) x_tvt, COALESCE(xi.x_revt,0) x_revt, COALESCE(xi.x_revu,0) x_revu
  FROM exp e
  LEFT JOIN vs_post vp ON e.device_id = vp.device_id
  LEFT JOIN im_post ip ON e.device_id = ip.device_id
  LEFT JOIN vs_pre xv ON e.device_id = xv.device_id
  LEFT JOIN im_pre xi ON e.device_id = xi.device_id
),
agg AS (
  SELECT pop, variant, COUNT(*) n,
    SUM(x_tvt) sx_tvt, SUM(x_tvt*x_tvt) sxx_tvt,
    SUM(x_revt) sx_revt, SUM(x_revt*x_revt) sxx_revt,
    SUM(x_revu) sx_revu, SUM(x_revu*x_revu) sxx_revu,
    SUM(y_tvt) sy_tvt, SUM(y_tvt*y_tvt) syy_tvt, SUM(x_tvt*y_tvt) sxy_tvt,
    SUM(ya_tvt) sy_atvt, SUM(ya_tvt*ya_tvt) syy_atvt, SUM(x_tvt*ya_tvt) sxy_atvt,
    SUM(yt_tvt) sy_ttvt, SUM(yt_tvt*yt_tvt) syy_ttvt, SUM(x_tvt*yt_tvt) sxy_ttvt,
    SUM(y_revt) sy_revt, SUM(y_revt*y_revt) syy_revt, SUM(x_revt*y_revt) sxy_revt,
    SUM(y_revu) sy_revu, SUM(y_revu*y_revu) syy_revu, SUM(x_revu*y_revu) sxy_revu,
    SUM(ya_revu) sy_arevu, SUM(ya_revu*ya_revu) syy_arevu, SUM(x_revu*ya_revu) sxy_arevu,
    SUM(yt_revu) sy_trevu, SUM(yt_revu*yt_revu) syy_trevu, SUM(x_revu*yt_revu) sxy_trevu
  FROM dev
  LATERAL VIEW explode(array('ITT', IF(is_tot_a=1,'ToT_a',NULL), IF(is_tot_t=1,'ToT_t',NULL))) p AS pop
  WHERE pop IS NOT NULL
  GROUP BY pop, variant
),
u AS (
  SELECT pop, variant, CAST(n AS DOUBLE) AS n, stack(7,
    'tvt',   CAST(sx_tvt AS DOUBLE),  CAST(sxx_tvt AS DOUBLE),  CAST(sy_tvt AS DOUBLE),   CAST(syy_tvt AS DOUBLE),   CAST(sxy_tvt AS DOUBLE),
    'atvt',  CAST(sx_tvt AS DOUBLE),  CAST(sxx_tvt AS DOUBLE),  CAST(sy_atvt AS DOUBLE),  CAST(syy_atvt AS DOUBLE),  CAST(sxy_atvt AS DOUBLE),
    'ttvt',  CAST(sx_tvt AS DOUBLE),  CAST(sxx_tvt AS DOUBLE),  CAST(sy_ttvt AS DOUBLE),  CAST(syy_ttvt AS DOUBLE),  CAST(sxy_ttvt AS DOUBLE),
    'revt',  CAST(sx_revt AS DOUBLE), CAST(sxx_revt AS DOUBLE), CAST(sy_revt AS DOUBLE),  CAST(syy_revt AS DOUBLE),  CAST(sxy_revt AS DOUBLE),
    'revu',  CAST(sx_revu AS DOUBLE), CAST(sxx_revu AS DOUBLE), CAST(sy_revu AS DOUBLE),  CAST(syy_revu AS DOUBLE),  CAST(sxy_revu AS DOUBLE),
    'arevu', CAST(sx_revu AS DOUBLE), CAST(sxx_revu AS DOUBLE), CAST(sy_arevu AS DOUBLE), CAST(syy_arevu AS DOUBLE), CAST(sxy_arevu AS DOUBLE),
    'trevu', CAST(sx_revu AS DOUBLE), CAST(sxx_revu AS DOUBLE), CAST(sy_trevu AS DOUBLE), CAST(syy_trevu AS DOUBLE), CAST(sxy_trevu AS DOUBLE)
  ) AS (m, sx, sxx, sy, syy, sxy)
  FROM agg
),
th AS (
  SELECT pop, m, SUM(sx)/SUM(n) AS xbar,
    ((SUM(sxy) - SUM(sx)*SUM(sy)/SUM(n))/(SUM(n)-1)) / ((SUM(sxx) - SUM(sx)*SUM(sx)/SUM(n))/(SUM(n)-1)) AS theta
  FROM u GROUP BY pop, m
),
st AS (
  SELECT u.pop, u.variant, u.m, u.n,
    u.sy/u.n - th.theta*(u.sx/u.n - th.xbar) AS am,
    ((u.syy - u.n*pow(u.sy/u.n,2))/(u.n-1))
      - 2*th.theta*((u.sxy - u.n*(u.sx/u.n)*(u.sy/u.n))/(u.n-1))
      + pow(th.theta,2)*((u.sxx - u.n*pow(u.sx/u.n,2))/(u.n-1)) AS av
  FROM u JOIN th ON u.pop = th.pop AND u.m = th.m
),
fin AS (
  SELECT t.pop, t.m, t.variant,
    100*(t.am - c.am)/c.am AS l,
    100*((t.am - c.am) - 1.96*sqrt(t.av/t.n + c.av/c.n))/c.am AS lo,
    100*((t.am - c.am) + 1.96*sqrt(t.av/t.n + c.av/c.n))/c.am AS hi
  FROM st t JOIN st c ON t.pop = c.pop AND t.m = c.m AND c.variant = 'Control'
  WHERE t.variant <> 'Control'
)
SELECT pop, m, concat_ws(';', sort_array(collect_list(concat(variant, ':', round(l,3), '|', round(lo,3), '|', round(hi,3))))) AS s
FROM fin
WHERE (pop = 'ITT') OR (pop = 'ToT_a' AND m IN ('revu','tvt')) OR (pop = 'ToT_t' AND m IN ('revu','tvt'))
GROUP BY pop, m
UNION ALL
SELECT pop, 'n', concat_ws(';', sort_array(collect_list(concat(variant, ':', CAST(n AS BIGINT)))))
FROM agg GROUP BY pop
ORDER BY pop, m
