-- v10 gate replay in pure SQL (port of v10_gate_replay.py), refresh 2026-10-20.
-- Control positions = live cue_points_abf on the ABF2 catalog; arm positions = ml_dev.tmp.abf3_new_pruner_cuepoints
-- (slasher_version: T1 = v4, T2 = v6, T3 = v5b). Greedy first-eligible gate; TVT weights = in-window TVT per title
-- (ds 2026-10-09..2026-10-19). Gate profiles: A = OTT base (episodes 420/600, movies 900/720); B = tolerant (360/360, 540/420).
-- Weight sets: ALL platforms (OTT doc), MOBILE, WEB. Combos returned: (A,ALL) (A,MOBILE) (B,MOBILE) (A,WEB) (B,WEB).
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
    AND content_id IN (SELECT content_id FROM ml_dev.tmp.abf3_v10_targeted_titles)
  GROUP BY content_id
),
tvt AS (
  SELECT content_id, SUM(tvt_millisec)/3600000.0 AS w_all,
    SUM(CASE WHEN platform_type = 'MOBILE' THEN tvt_millisec ELSE 0 END)/3600000.0 AS w_mobile,
    SUM(CASE WHEN platform_type = 'WEB' THEN tvt_millisec ELSE 0 END)/3600000.0 AS w_web
  FROM core_prod.tubidw.video_session
  WHERE ds >= '2026-10-09' AND ds <= '2026-10-19'
  GROUP BY content_id
),
b0 AS (
  SELECT a.content_id, a.tt, s.slasher_version AS arm, CAST(s.duration_sec AS DOUBLE) AS dur,
    array_sort(filter(transform(split(regexp_replace(a.cpa,'[{}]',''),','), x -> try_cast(trim(x) AS DOUBLE)), x -> x IS NOT NULL AND x > 0)) AS ctl,
    array_sort(COALESCE(CAST(s.slashed_cue_points_sec AS ARRAY<DOUBLE>), array())) AS srv,
    COALESCE(t.w_all,0) w_all, COALESCE(t.w_mobile,0) w_mobile, COALESCE(t.w_web,0) w_web
  FROM abf2 a JOIN ml_dev.tmp.abf3_new_pruner_cuepoints s ON a.content_id = s.content_id
  LEFT JOIN tvt t ON a.content_id = t.content_id
  WHERE s.duration_sec > 300 AND s.slasher_version IN ('v4','v5b','v6')   -- table now also holds non-v10 arms (v4e300, v4e360, v6m, r2me)
),
b1 AS (
  SELECT *, size(ctl) AS n_ctl, size(srv) AS n_srv FROM b0
  WHERE size(ctl) > 0 AND array_max(concat(ctl, srv, array(CAST(0 AS DOUBLE)))) <= dur * 1.2
),
g AS (
  SELECT b1.*, p.prof,
    CASE WHEN tt = 'Episode' THEN p.e_ini ELSE p.m_ini END AS ini,
    CASE WHEN tt = 'Episode' THEN p.e_spc ELSE p.m_spc END AS spc
  FROM b1 CROSS JOIN (SELECT * FROM VALUES ('A',420.0,600.0,900.0,720.0),('B',360.0,360.0,540.0,420.0) AS p(prof,e_ini,e_spc,m_ini,m_spc)) p
),
f AS (
  SELECT content_id, tt, arm, prof, n_ctl, n_srv, w_all, w_mobile, w_web,
    CASE WHEN n_ctl <= 3 THEN '1-3' WHEN n_ctl <= 6 THEN '4-6' WHEN n_ctl <= 9 THEN '7-9'
         WHEN n_ctl <= 12 THEN '10-12' ELSE '13+' END AS band,
    aggregate(ctl, named_struct('last', CAST(NULL AS DOUBLE), 'n', 0, 'first', CAST(NULL AS DOUBLE)),
      (acc, x) -> CASE WHEN x >= ini AND x <= dur AND (acc.last IS NULL OR x - acc.last >= spc)
                       THEN named_struct('last', x, 'n', acc.n + 1, 'first', COALESCE(acc.first, x)) ELSE acc END) AS fc,
    aggregate(srv, named_struct('last', CAST(NULL AS DOUBLE), 'n', 0, 'first', CAST(NULL AS DOUBLE)),
      (acc, x) -> CASE WHEN x >= ini AND x <= dur AND (acc.last IS NULL OR x - acc.last >= spc)
                       THEN named_struct('last', x, 'n', acc.n + 1, 'first', COALESCE(acc.first, x)) ELSE acc END) AS fs
  FROM g
),
w AS (
  SELECT f.content_id, f.tt, f.arm, f.prof, f.n_ctl, f.n_srv, f.band, f.fc, f.fs, ws.wset, ws.wt
  FROM f LATERAL VIEW stack(3, 'ALL', w_all, 'MOBILE', w_mobile, 'WEB', w_web) ws AS wset, wt
  WHERE (f.prof = 'A') OR (f.prof = 'B' AND ws.wset IN ('MOBILE','WEB'))
),
cells AS (
  SELECT 'cell' AS k, prof, wset, tt, band,
    concat_ws(';', sort_array(collect_list(concat(arm, ':', round(d, 2))))) AS s
  FROM (SELECT prof, wset, tt, band, arm,
          100.0 * (SUM(fs.n * wt) - SUM(fc.n * wt)) / NULLIF(SUM(fc.n * wt), 0) AS d
        FROM w GROUP BY prof, wset, tt, band, arm) x
  GROUP BY prof, wset, tt, band
),
pooled AS (
  SELECT 'pooled' AS k, prof, wset, 'ALL' AS tt, band,
    concat_ws(';', sort_array(collect_list(concat(arm, ':', round(d, 2))))) AS s
  FROM (SELECT prof, wset, band, arm,
          100.0 * (SUM(fs.n * wt) - SUM(fc.n * wt)) / NULLIF(SUM(fc.n * wt), 0) AS d
        FROM w GROUP BY prof, wset, band, arm) x
  GROUP BY prof, wset, band
),
decomp AS (
  SELECT 'decomp' AS k, prof, wset, 'Episode' AS tt, 'ALL' AS band,
    concat_ws(';', sort_array(collect_list(concat(arm, ':', round(tot, 2), '|', round(fewer, 2), '|', round(pos, 2), '|', round(gains, 2))))) AS s
  FROM (SELECT prof, wset, arm,
          100.0 * SUM((fs.n - fc.n) * wt) / SUM(fc.n * wt) AS tot,
          100.0 * SUM(CASE WHEN n_srv < n_ctl THEN (fs.n - fc.n) * wt ELSE 0 END) / SUM(fc.n * wt) AS fewer,
          100.0 * SUM(CASE WHEN n_srv >= n_ctl AND fs.n < fc.n THEN (fs.n - fc.n) * wt ELSE 0 END) / SUM(fc.n * wt) AS pos,
          100.0 * SUM(CASE WHEN n_srv >= n_ctl AND fs.n >= fc.n THEN (fs.n - fc.n) * wt ELSE 0 END) / SUM(fc.n * wt) AS gains
        FROM w WHERE tt = 'Episode' GROUP BY prof, wset, arm) x
  GROUP BY prof, wset
),
firsts AS (
  SELECT 'first' AS k, prof, wset, tt, 'ALL' AS band,
    concat_ws(';', sort_array(collect_list(concat(arm, ':', round(a, 0), '|', round(b, 0), '|', round(e, 0), '|', round(f, 0))))) AS s   -- first_ctl|first_srv (TVT-weighted) | unweighted ctl|srv
  FROM (SELECT prof, wset, tt, arm,
          SUM(CASE WHEN fc.first IS NOT NULL AND wt > 0 THEN fc.first * wt END) / SUM(CASE WHEN fc.first IS NOT NULL AND wt > 0 THEN wt END) AS a,
          SUM(CASE WHEN fs.first IS NOT NULL AND wt > 0 THEN fs.first * wt END) / SUM(CASE WHEN fs.first IS NOT NULL AND wt > 0 THEN wt END) AS b,
          AVG(fc.first) AS e, AVG(fs.first) AS f
        FROM w GROUP BY prof, wset, tt, arm) x
  GROUP BY prof, wset, tt
),
meta AS (
  SELECT 'meta' AS k, prof, wset, 'ALL' AS tt, 'ALL' AS band,
    concat('titles_arm:', COUNT(*), ';excluded_note:see b0/b1 counts') AS s
  FROM w GROUP BY prof, wset
)
SELECT * FROM cells UNION ALL SELECT * FROM pooled UNION ALL SELECT * FROM decomp UNION ALL SELECT * FROM firsts UNION ALL SELECT * FROM meta
ORDER BY k, prof, wset, tt, band
