-- Infer pod-placement gates (initial-ad-slot, min-time-between-breaks) per platform group x content type
-- from observed midroll positions (now_pos, content seconds). Sample: 1/10 of devices, 2026-10-12..13.
WITH pods AS (
  SELECT CASE WHEN platform IN ('android','iphone','ipad','firetablet','android_samsung') THEN 'MOBILE'
              WHEN platform = 'web' THEN 'WEB'
              WHEN platform IN ('roku','amazon','samsung','vizio','lgtv','tvos','androidtv','ps4','ps5','xboxone','chromecast','comcast','sony','hisense','tivo') THEN 'OTT'
         END AS pg,
         content_type, device_id, content_id, ROUND(CAST(now_pos AS DOUBLE), 0) AS pos
  FROM core_prod.ads.impressions
  WHERE date IN ('2026-10-12','2026-10-13') AND CAST(now_pos AS DOUBLE) > 30
    AND abs(hash(device_id)) % 10 = 0
  GROUP BY 1, 2, 3, 4, 5
),
seq AS (
  SELECT pg, content_type, device_id, content_id, pos,
         pos - LAG(pos) OVER (PARTITION BY pg, device_id, content_id ORDER BY pos) AS gap,
         ROW_NUMBER() OVER (PARTITION BY pg, device_id, content_id ORDER BY pos) AS rk
  FROM pods WHERE pg IS NOT NULL
)
SELECT pg, content_type,
  COUNT(CASE WHEN rk = 1 THEN 1 END) n_first,
  percentile_approx(CASE WHEN rk = 1 THEN pos END, array(0.01, 0.05, 0.10, 0.25, 0.5)) first_pos_pcts,
  COUNT(gap) n_gap,
  percentile_approx(CASE WHEN gap > 60 THEN gap END, array(0.01, 0.05, 0.10, 0.25, 0.5)) gap_pcts
FROM seq GROUP BY pg, content_type ORDER BY pg, content_type
