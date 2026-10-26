# ABF Experiment — Handover (from Binoop Pulikkal, 2026-10-02)

This repo is a full handover of the ABF3 experiment analysis project: working files
(code, SQL, reports) **plus the Claude Code memory** accumulated over ~6 months of
sessions, so your Claude picks up with all findings, data traps, and decisions intact.

## Project state at handover (TL;DR)

- **v8 (full ABF1 catalog): 🎓 GRADUATED, rolled out 2026-08-31.** All 3 platforms
  analyzed & reported — OTT +0.88% rev / −0.18% TVT (sig trade), Mobile +2.96%/flat,
  Web +3.21%/flat. Two systematic defects found (per-title floor, series/gate) — see
  `claude-memory/project_v8_experiment.md` for the full read and open follow-ups.
- **v9 (ABF2 catalog): ⚠️ ACTIVE — LAUNCH HELD as of 2026-09-15** pending a per-title
  pruner floor (slasher 2.0 puts 52–79% of mid/dense ABF2 titles below their own
  control). Title list (200,403) is built and audited. **Status is stale — check
  Slack / Statsig for where this stands now before acting.**
- Full history and conclusions: `ABF_BACKGROUND.md` (the living source of truth).

## Setup on your machine (one time)

```bash
# 1. Clone to your home dir (the path matters — Claude keys memory off the cwd path)
git clone git@github.com:adRise/abf-experiment.git ~/abf_experiment

# 2. Wire the Claude memory in (adjust if your home dir isn't /Users/<whoami>)
MEM=~/.claude/projects/-Users-$(whoami)-abf-experiment
mkdir -p "$MEM"
ln -sfn ~/abf_experiment/claude-memory "$MEM/memory"
```

Then open Claude Code in `~/abf_experiment`. Two context layers load:
1. `CLAUDE.md` tells Claude to read `ABF_BACKGROUND.md` at session start (project history).
2. The memory symlink gives it the distilled per-topic memory (`claude-memory/MEMORY.md`
   is the index — experiment conclusions, table references, analysis rules).

Memory worth skimming yourself: `project_v8_experiment.md`, `project_v9_experiment.md`,
`reference_content_availability.md` (data traps), `feedback_population_filters.md`
(estimand rules that bit us more than once).

## Environment mapping (things that were Binoop-specific)

| Thing | Where it is / what you need |
|---|---|
| Google Doc reports (11) | Shared with jvora@tubi.tv. IDs live in `memory/*.docid` + `claude-memory/reference_abf_reports_drive.md`. Updating a report in place keeps its link stable — reuse the IDs, don't create new Docs. |
| Databricks archived notebook runs | `/Users/bpulikkal@tubi.tv/ABF_3` (folder id 3299235682911404) — rendered `__run_<date>_OUTPUT` HTML copies of every analysis. Ask Binoop/workspace admin for access if you need the rendered outputs; the **source** `.py` for all key notebooks is in this repo's root. |
| Databricks auth | `abf_db.py` reads `~/.tubi-sql/config.yml` (host + token) — set up your own. Serverless-only gotchas are in `claude-memory/reference_abf_db_helper.md`. |
| Warehouse temp tables | `temp_bp_abf_v8_*`, `temp_bp_v8_topup_*` etc. referenced in memory were created ad hoc — they may have expired; recreation SQL is in the notebooks. |
| Report publishing | Binoop used a `gdoc` CLI (Drive API) to republish markdown → the same Doc id. Any flow works as long as you update the existing Docs in place. |

## Access checklist

- [x] This repo
- [x] 11 Google Doc reports (shared to jvora@tubi.tv)
- [ ] Databricks: `tubi-dev` workspace + DSA-Team: EDA warehouse (`34148fb208740945`)
- [ ] `/Users/bpulikkal@tubi.tv/ABF_3` notebook folder (if you want archived outputs)
- [ ] Slack / Statsig: wherever v9 launch coordination is happening (status was held 2026-09-15)
