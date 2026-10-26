---
name: ABF3 Experiment History and Active Experiment
description: History of ABF3 experiments and which one is currently active (v6 as of 2026-06-03)
type: project
originSessionId: 796e0244-4545-4f4f-8a1d-45356e427f60
---
Full detail lives in `ABF_BACKGROUND.md` (source of truth). Summary of the experiment series:

**ads_abf_3_v2:** Ran 2026-03-30 → 2026-04-17. 278 eligible titles. +5% revenue, -0.6% TVT. Stopped.

**ads_abf_3_v3:** Ran 2026-04-17 → 2026-04-21. ~1000 titles (~500 ABF1 + ~500 ABF2 control). ABF3 at native density (~3–4x more cue points). Quality+quantity confounded. +13% revenue, -2.41% TVT; 17–26% more breaks/hr. Stopped.

**ads_abf_3_v4:** Ran 2026-04-28 → 2026-05-06 (~8 days, ENDED). Two title sets: ~1000 non-WC titles (ABF3 pruned to ABF2 density → quality isolation) and 711 FIFA WC titles (native density). Day-7 final findings:
- ABF3 = ABF2 (definitively null after excluding ~75 over-pruned titles) — no quality advantage at equal density
- ABF3 > ABF1: +4.64% revenue, +5.13% imps, flat TVT
- TVT flat across all density-matched cuts — confirms v3's TVT drop was entirely quantity-driven
- WC (native density): +5.92% revenue BUT -3.66% TVT (both stat sig) — quantity tradeoff
- v4 over-pruning artifact: ad hoc pruning left ~75 titles with 1–2 cue points; ABF2-only users got fewer breaks than control

**ads_abf_3_v5:** ABANDONED due to bugs in experiment setup.

**ads_abf_3_v6 — ACTIVE:** Launched 2026-05-29, still running. Major change in v5/v6 = a NEW pruning algorithm to match ABF3 cue point density to ABF2 (replaces v4's ad hoc pruning that caused over-pruning). v6 is v5 relaunched after the setup bugs were fixed. SCOPE: ABF1 vs ABF3 ONLY — 1,084 titles that currently have ABF1 cue points; control = ABF1, treatment = ABF3 pruned to ABF2 density. No ABF2 arm, no WC set (v4 already showed ABF3 = ABF2, ABF3 > ABF1, so v6 targets the ABF1 upside). RUNS AS THREE PER-PLATFORM EXPERIMENTS: `ads_abf_3_v6` (OTT, launched 5/29), `ads_mobile_abf_3_v6` (mobile, launched 5/27), `ads_web_abf_3_v6` (web, launched 5/27). All three active.

**Analysis framework:** ITT + ToT (ToT primary). Graduation metric `me_score = 0.5*unbudgeted_revenue + 0.5*predicted_long_term_revenue` (uses `e_score`, both calculated offline — not yet computed). Primary metrics: `unbudgeted_revenue`, `TVT`, `QVD`.

**Open items:** me_score/e_score not yet computed (no graduation decision); stakeholder revenue-vs-TVT tradeoff threshold undefined; minimum cue point floor (≥3) recommended.

**v6 OTT analysis (refreshed 2026-06-04, window 05-29→06-03 complete days):** ABF3 vs ABF1, ToT/abf3-only revenue **+5.67%**, TVT −0.33%, +6.98% more breaks/hr. Stable vs day-5 read (+5.70%/−0.31%) — effect holding. Graduation generalization: title-clustered CI [+6.1%,+8.5%], poststratified projection +7.0% TVT-wtd / +6.0% rev-wtd on ABF1-title activity. **Global topline revenue lift +2.18%** (CI [+1.99,+2.37]), diluting by ABF1's **36.2% revenue share / 36.7% TVT — CONFIRMED official graduation denominator** (earlier ~45% retired). **Global TVT: −0.05% (on-title dilution, no spillover) to −0.40% (coverage-scaling, captures cross-title substitution)** — likely toward −0.4%; the all-titles TVT decline (ITT −0.16%/ToT −0.20% CUPED, both sig) exceeds on-title losses, evidence of real spillover. Graduation trade ≈ +2.2% global revenue for ~−0.4% global TVT. CUPED confirms all results (var reduction 45–57% all-titles). **Cross-validated against Statsig dashboard (CURE variance reduction, ITT all-titles, refreshed 2026-06-04): TVT point estimate identical (−0.16% both; CURE ±0.19 crosses zero/non-sig, our CUPED ±0.11 sig); revenue +0.84% CUPED vs +0.72% CURE — both sig, agree within ~0.12pp (gap = revenue-definition and/or Statsig including partial 06-04 day).** Report shows CUPED-only lifts (raw Welch no longer shown). Report: `ABF3_experiment_v6_generalization_report.md`.

**DEFERRED:** run the same suite on mobile (`ads_mobile_abf_3_v6`) and web (`ads_web_abf_3_v6`) — user said "later" on 2026-06-03.

**How to apply:** v6 OTT graduation case is well-supported (+7% on-title, +2.2% global, flat TVT). `me_score`/`e_score` (offline) remain the formal gate, not yet computed. Mobile/web still pending.
