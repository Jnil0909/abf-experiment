---
name: project-v7-experiment
description: "ABF3 v7 (stronger pruning) — results, mechanism, graduation read, and reports as of 2026-06-24"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7f40cec8-739f-48e9-81f2-129caea0888c
---

ABF3 **v7** = stronger-pruner successor to v6. Experiments `ads_abf_3_v7` (OTT), `ads_mobile_abf_3_v7`, `ads_web_abf_3_v7`; launched 2026-06-16, same 1,084 ABF1 content_ids as v6. Goal: eliminate v6's TVT cost by pruning ABF3 cue points harder, while keeping a meaningful revenue lift. Analyzed at 6-day read (window 06-17→06-22) on 2026-06-23/24. Full detail in ABF_BACKGROUND.md (the source of truth) — this is just the pickup pointer.

**Headline verdict (per platform):**
- **OTT — v7 WORKED (confirmed):** global rev +1.36% vs v6 +2.2%; global TVT ~flat vs v6 −0.4%. The TVT improvement is **statistically significant** and lives in the *spillover* (cross-title total-watch-time) channel, NOT the on-title channel (on-title TVT = −0.33% in BOTH versions). CUPED-vs-CUPED ITT all-titles TVT: v6 −0.173% (sig p=0.005) → v7 +0.016% (ns); v6→v7 diff +0.19pp, **p=0.033 significant**. So v7 is a confirmed revenue-for-engagement trade on OTT.
- **Mobile — v6 dominates:** v6 spillover never significant (−0.137% p=0.33; v6→v7 diff p=0.91); mobile's real cost is on-title −0.85% (sig), which v7 didn't fix. v7 just loses revenue (+2.46% vs v6 +3.19%).
- **Web — v6 dominates:** noisy both versions; v7 loses most revenue (+1.86% vs +4.68%).

**Mechanism (why on-title TVT didn't move):** ABF3's on-title TVT cost is concentrated in MOVIES, tiny, and driven by break COUNT not placement (no break mispositioned; flat dose-response; the "+4.8pp early-break" effect was a sub-360s replay/seek ARTIFACT — retracted). So pruning the count trades on-title revenue ~linearly without moving the on-title cost. Don't pursue a harder-pruned v8. Final v6-vs-v7 call = me_score/e_score gate (offline, not computed).

**Key gotchas / lessons (don't repeat):**
- CUPED pre-window for v7 = **2026-05-07→05-20** (clean; v6 default 05-15→05-28 is contaminated by v5+v6 on these titles). Notebook widget DEFAULTS still show old window — runs override via base_parameters; verify via jobs API, not the notebook source.
- Always compare **CUPED-vs-CUPED** (not raw-vs-CUPED) — comparing raw v7 to CUPED v6 wrongly showed "no difference."
- Two different revenue CIs: (1) topline global rev +1.36% [+1.13,+1.59] DEVICE-level (the reported number, significant); (2) title-clustered generalization CI (title as unit, projects to full ABF1 catalog). **The original title-clustered [−0.03,+3.97] "touches zero" flag was a BROKEN-ESTIMATOR ARTIFACT — RETRACTED 2026-06-24.** It bootstrapped noisy small-sample per-title %lifts (rev-weighted variant corrupted by pre-launch-weighted/in-experiment-empty −100% junk titles). FIX = bootstrap the actual topline estimator (device-pooled decile lifts → universe-revenue poststrat); near-empty titles auto-get ~0 weight. **Coherent CIs CLEAR ZERO on all platforms: OTT [+2.91,+4.79], Mobile [+5.46,+7.87], Web [+2.83,+5.95].** Fix applied to v6 leaves it unchanged ([+5.28,+6.87]) → principled. Generator notebook `abf_v7_coherent_titleci` (param'd by PLATFORM_TYPE). Both topline AND generalization are comfortably positive — OTT generalization is NOT at risk.
- Densest-decile over-prune: v7's stronger pruner serves the densest ABF1 titles (decile 8 / control ≥13 cue pts) BELOW their control (13.6 vs 16.6 cue pts; 54.5% below; 9.8% of all 1084 titles below control, concentrated in top-2 deciles) → that decile's rev lift flips +2.17% (v6) to −3.58% (v7), dragging the v7 global down ~0.3pp. Fixable via a per-title FLOOR ("serve ≥ control"), distinct from "prune harder" (ruled out); unvalidated → would need a v8 arm. Notebooks `abf_v7_decile_concentration`, `abf_v7_estimator_gap`.
- Web has ~11% cross-platform leakage (FireTablet/Samsung = MOBILE platform_type sessions in the web experiment); lift notebooks don't platform-filter. Platform-restricted web on-title TVT = +1.6% (vs +0.8% unfiltered).
- `now_pos` = content playhead seconds; 360s = initial-ad-slot floor (holds both arms); sub-360 records are replays/seeks. Unit for session analysis = `video_session_id`; map impressions→session by `parent_ts BETWEEN start_ts AND end_ts`.

**Reports (Google Docs, pageless/wide, folder 0AE3wRIsB2WnhUk9PVA):** cross-platform `1gPBeoOh6PDBq8wMWIJdqA5Gc3tkIwHRrZCBfV5s445I`; OTT `1Nwi5-Vrqd76DoEXHy7t3-LowYxxBuBKAQetRel6IMNE`; Mobile `1IrMG8eS-BMxI3FlRevcpGIX41lAUGw3N8pRkHtLVlFw`; Web `1taIUps7KU9pZwrLuUViJqliO93Uf1f8wKm62R4GiECw`. See [[reference-abf-reports-drive]].

**Mechanism notebooks (OTT+US):** `abf_v7_placement`, `abf_v7_early_breaks`, `abf_v7_hazard_survival` in `/Users/bpulikkal@tubi.tv/ABF_3/`. Suite + headline notebooks: `ads_abf_3_v7__*` (+ mobile/web variants). Distinct from the unrelated "V7" ad-load experiment in [[project-v6-v7-interaction]].

**Open / next (priority):** (1) **me_score/e_score gate — still NOT computed; THE formal graduation decision for v6-vs-v7.** (2) Web platform-filter suite re-run (data-quality TODO; OTT/mobile clean). (3) More v7 runtime — all reads 6-day, v6 moderated over time; confirm at 10–14d. (4) Optional v8 with floored pruner if dense-decile upside matters; else floor-to-control is the safe conservative ship. Reports refreshed/republished 2026-06-24 with coherent CIs + dual-basis topline row (device vs title-clustered-diluted) in each §2b — stable links unchanged.
