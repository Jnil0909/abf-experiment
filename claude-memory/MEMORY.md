# Memory

- [ABF Background File](project_abf_background.md) — ABF_BACKGROUND.md is the living source of truth for the ABF project; read at session start, update on new developments
- [Update ABF_BACKGROUND.md on new developments](feedback_update_background.md) — Proactively update ABF_BACKGROUND.md when new facts or decisions arise
- [New ABF3 Experiment Design](project_new_experiment.md) — ~1000 title experiment launching ~2026-04-18, results ~2026-05-02; me_score/e_score calculated offline
- [Cue-point columns reference](reference_cue_point_columns.md) — cue_points = ABF1 baseline density source; cue_points_abf = ABF classification only (has_abf); ABF1 universe query
- [abf_db.py helper](reference_abf_db_helper.md) — Databricks helper script (no permission prompts) + serverless gotchas (no .cache, Decimal casts, notebook.exit, export_run for outputs)
- [ABF reports on Drive](reference_abf_reports_drive.md) — Google Doc IDs/links for ABF reports (v6 generalization report); how to regenerate docx
- [No inline JSON in Bash args](feedback_no_inline_json_args.md) — inline JSON braces trigger "simple_expansion" prompts; pass params via @file (abf_db.py run accepts @path.json)

_"Run code on Databricks, not locally" now lives in global ~/.claude/CLAUDE.md (former feedback_run_on_databricks merged there to avoid drift)._
- [v6 OTT × V7 interaction analysis](project_v6_v7_interaction.md) — CONCLUSION REVERSED 2026-06-11: NO V7 interaction (post-V7 clean window, ToT+ITT+Roku placebo all agree); ABF3 TVT cost is standalone & platform-driven; graduation doesn't depend on V7
- [v7 experiment (stronger pruning)](project_v7_experiment.md) — 2026-06-24: OTT v7 CONFIRMED revenue-for-TVT trade (global rev +1.36%, TVT ~flat vs v6 −0.4%; spillover diff p=0.033); mobile/web v6 dominates; on-title cost count-driven not placement; 4 reports published (me_score refs obsolete — dropped 2026-08-19)
- [v9 experiment (ABF2 catalog)](project_v9_experiment.md) — ⚠️ ACTIVE: title list built/audited (200,403; table + canonical SQL); LAUNCH HELD 2026-09-15 for per-title pruner floor (slasher 2.0 puts 52–79% of mid/dense ABF2 titles below own control; parity bar); status stale — check Slack/Statsig
- [v8 experiment (full ABF1 catalog)](project_v8_experiment.md) — 🎓 GRADUATED, rolled out 2026-08-31; 2026-08-21: ALL 3 platforms analyzed & reported (9-day Window B): OTT +0.88%/−0.16% sig trade; MOBILE +2.96%/flat (over-delivers projection); WEB +3.21%/flat (first-ever sig web topline); floor defect universal, series/gate defect OTT-only; ⚠️ me_score DROPPED — decision on rev/TVT lifts; next: model-vs-pruner split, OTT series sizing, stakeholder threshold, Window C after pruner fix
- [Content availability table](reference_content_availability.md) — active-now = core_prod.dsa.dsac (NEVER core_dev — dead copy); future expiration = content.content_availability.end_ts (MUST filter country+active); rotating-window titles: off today ≠ expired — use end_ts for batch selection, dsac for exposure analysis
- [v8 report framing](feedback_v8_report_framing.md) — Window B (full catalog) = main view in v8 reports; Window A + comparisons = appendix
- [Population filters & post-randomization safety](feedback_population_filters.md) — Active = "≥1 session SINCE FIRST EXPOSURE" only; never window-scoped activity or "≥1 break fired"; zero-outcome devices don't change % lifts
