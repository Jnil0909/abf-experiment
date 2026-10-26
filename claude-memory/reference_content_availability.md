---
name: reference-content-availability
description: How to filter titles by active/expired status — core_prod.dsa.dsac_content_availability (daily licensing-window snapshot)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 363de33d-83d1-42c0-ada5-cb663946c934
  modified: 2026-08-07T02:01:32.553Z
---

**Title expiration/active status lives in `core_prod.dsa.dsac_content_availability`** — neither `content_info` nor the stream tables have an expiration date (`content_info.active` exists but no window dates).

**⚠️ Use `core_prod`, NEVER `core_dev`:** `core_dev.dsa.dsac_content_availability` is a STALE dead copy (no rows past ~2024-05; zero US titles with 2026 data as of 2026-08-06). Same table name, silently wrong answers — e.g. title 522076 shows "expired 2024-05-31" in core_dev but is live under a renewed revshare deal in core_prod (25–30K TVT hrs/day). Also: `window_end` rolls forward with the daily snapshot (often ≈ ds+1) — it is NOT a long-horizon contractual expiration date; only use it for point-in-time active checks. Do NOT derive expiration from `avail_movies/avail_episodes.policy` text either — renewed titles keep stale policy dates (this bug excluded the top ABF1 titles from the v8 batch).

- Grain: one row per title × country × licensing window, snapshotted daily. Columns: `content_id (INT), program_id, content_type, season, duration_sec, ds (DATE), country, day_live, deal_type, window, window_start (DATE), window_end (DATE), window_day_live, updated_at`.
- Fresh: `max(ds)` = today (verified 2026-08-05, ~12.7M rows/day).
- "Active as of date D" filter:
```sql
SELECT DISTINCT content_id
FROM core_prod.dsa.dsac_content_availability
WHERE ds = 'D' AND country = 'US'
  AND window_start <= 'D' AND window_end >= 'D'
```
- For "active during an experiment window" use `window_start <= exp_end AND window_end >= exp_start` instead.
- Sibling tables: `dsac_program_availability` (program grain), `dsac_content_metadata` (also has window_start/end).

**For FUTURE expiration dates use `core_prod.content.content_availability`** (video_id, series_id, country, platform, active, start_ts, end_ts, date=YYYYMMDD daily partition): `end_ts` IS a real forward-looking contractual window end (e.g. 522076: 2026-09-01; catalog-wide most are months-to-years out; note ~25% of active titles show end_ts ≤2d out — short/rolling windows, treat "active now + short end_ts" carefully, don't equate to dead). Grain is per-platform — dedupe with `MAX(end_ts)` per video_id/country. **BOTH `country='US' AND active=true` filters are mandatory** — without them MAX(end_ts) picks up foreign/inactive rows and resurrects dead titles (6,633 such in the v8 top-up reconciliation). Validated 2026-08-06: all 27,539 gap-list titles are active with future end_ts here (two independent sources agree).

**Rotating-window gotcha (which check for which question):** big-studio titles rotate on monthly licensing windows — off-catalog *today* but licensed for years (Furious 7, Norbit, Madea Goes to Jail: dsac window closed ~2026-08-01, ca end_ts→2027, back on next rotation; 2,871 such titles carried 41.2M hrs/14d). So: **point-in-time dsac check** = "serving traffic on date D" (analysis exposure questions); **ca `end_ts > cutoff` with country+active** = "part of the ongoing catalog" (batch/processing selection — cue points don't expire, so rotating titles belong in processing batches even when off today).

Gotcha this solved: the June-2026 ABF1 universe snapshot (492K titles) is two-thirds expired by Aug 2026 — only 160K still active in US. Any title-list comparison spanning months MUST be availability-filtered or expired titles dominate the diff. See [[project-v8-experiment]].
