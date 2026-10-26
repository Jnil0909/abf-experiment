---
name: project-v9-experiment
description: "ABF3 v9 — ABF2 catalog experiment (planning): title list built & audited, launch held for per-title pruner floor (prevalence check 2026-09-15)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9a58f1a4-e082-425f-ac74-37462bf2d489
  modified: 2026-10-02T18:45:31.889Z
---

ABF3 **v9** = the ABF2-catalog experiment (ABF3/slasher-2.0 vs ABF2 control), following v8's graduation. **Success bar = PARITY with ABF2** (v4 proved ABF3 ≈ ABF2 at matched density); the business value is retiring the human-review pipeline, not revenue lift.

- **Title list (built & verified 2026-09-01):** `core_dev.dsa.temp_bp_v9_experiment_titles` — 200,403 titles = **1,429 Gemini-ready ADD-ONLY (servable v2) + 198,974 to process**. Canonical SQL `abf_v9_experiment_titles_selection.sql` (project root), verified to regenerate the table exactly; snapshot-dependent → re-run at launch. Audit vs Aryan's pull: his dropped 1,497 processed titles (13.9% of ABF2-catalogue TVT / 8.3% of ALL platform TVT) via the gemini WHERE-filter (the 888-lesson again), included 18,127 expired titles, missed 7,570 off-rotation licensed ones; `'[]'` never occurs in `cue_points_abf` (real empties: `'{}'` 6,033 + `'{0.0}'` 9,664 rows). Audit table `temp_bp_v9_audit_universe`.
- **Slasher architecture (Aryan, confirmed 2026-09-15):** ABF1 slasher = same pruner + EXTRA 20% slash (explains v8's ~6.5 vs 8.2 cp/hr); ABF2 titles get slasher 2.0 (no extra 20%); table `ml_prod.ads.abf3_slasher_cuepoints`, versions raw/v1.1/v2 — **v2 = servable** (189,692 titles have non-empty v2 of 195,452 processed).
- **LAUNCH HELD — wait-for-floor recommendation (2026-09-15):** pre-launch prevalence check (v2 slash vs live ABF2 control per title): below-control = 21.6% of titles (band 1–3), 52.0% (4–6), **79.1% (7–9)**, 53.0% (10–12), **79.5% (13+)** — 14–73% of band TVT. On ABF2 the target ≈ control average → half the catalog below its own control BY CONSTRUCTION (v8's "not as extensive" intuition inverts). v8 proved below-control = −4 to −8% revenue, no TVT give-back ⇒ YOLO ⇒ likely negative read vs a parity bar ⇒ relaunch. **Recommendation: wait ~2 wks for per-title floor (slash ≥ title's ABF2 count), then launch the graduating config (Window C rule).** Pre-flight when floored output lands: (1) count check slashed ≥ control for every title (~1 hr); (2) optional gate simulation (predicted v8 realized breaks at r=0.962) for a revenue-direction forecast before traffic.
- **⚠️ Status as of 2026-09-15 (STALE by October — check Slack/Statsig next session):** wait-for-floor + follow-up replies DRAFTED, send status unconfirmed; floor fix was "~2 weeks" out → may be done; launch may have happened.
- Launch playbook ready = v8's: windows w/ clean pre-period, populations ITT/Active(since-exposure)/ToT, metrics rev/imps/TVT/NPV_TVT with p-values, bands × below-control × type cuts, CUPED notebooks parameterized (`ads_abf_3_v8__cuped_stat_sig` takes EXP/TITLES widgets).

Predecessor: [[project-v8-experiment]] (GRADUATED, rolled out 2026-08-31). Full detail in ABF_BACKGROUND.md.
