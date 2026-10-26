---
name: reference-abf-db-helper
description: abf_db.py Databricks helper script in the ABF project + serverless gotchas
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6a38b6e8-b694-4300-9419-9e3a9ffe953d
---

`/Users/bpulikkal/abf_experiment/abf_db.py` — Databricks helper that avoids the "cannot be statically analyzed" permission prompts (no heredocs/$()) by reading host+token from `~/.tubi-sql/config.yml` itself. Allowlisted in `~/.claude/settings.json` as `Bash(python3 abf_db.py:*)`.

Commands:
- `python3 abf_db.py sql "<inline sql>"` — run SQL via /api/2.0/sql/statements, prints JSON {columns, rows}
- `python3 abf_db.py sqlfile <path.sql>` — run SQL from a file (use for multi-line; avoids heredocs)
- `python3 abf_db.py upload <local.py> <ws_path>` — import notebook (SOURCE/PYTHON, overwrite)
- `python3 abf_db.py run <ws_path> <run_name> [params]` — submit serverless run, polls 60s, prints EXIT_RESULT (the dbutils.notebook.exit JSON) + ERROR. `params` (4th arg) sets notebook widget base_parameters; pass `@/path/to/params.json` (file of widget values) — NOT inline JSON, which triggers the "simple_expansion" prompt (see [[feedback-no-inline-json-args]]).
- `python3 abf_db.py export_run <run_id> <dst_ws>` — pull rendered HTML (code+outputs) of a completed run, import as HTML notebook (this is how to save run OUTPUTS to the workspace; plain copy/import only saves source, no outputs)
- `python3 abf_db.py copy <src_ws> <dst_ws>` — copy notebook SOURCE only (no outputs)
- `python3 abf_db.py mkdir <ws_path>` / `delete <ws_path>`

Serverless gotchas (all hit this session):
- NO `.cache()`/`.persist()` — "PERSIST TABLE not supported on serverless". Just re-query.
- Spark returns `Decimal` for revenue (decimal(11,7)) and duration (decimal(28,6)). numpy/Welch math throws `Decimal * float`. Cast in SQL (`CAST(x AS DOUBLE)`) or pandas (`pd.to_numeric(...).astype(float)`) before arithmetic.
- `print()` output is NOT captured by runs/get-output. Use `dbutils.notebook.exit(json.dumps(...))` to return results.
- Serverless run config: `environment_key:"serverless"` + `environments:[{environment_key:"serverless", spec:{client:"2"}}]`, no cluster spec.
- runs/export returns RAW html (not base64); must base64-encode before workspace/import.

ABF_3 workspace folder: `/Users/bpulikkal@tubi.tv/ABF_3` (id 3299235682911404). Naming: `ads_abf_3_v6__<desc>` for source, `__run_<date>_OUTPUT` for rendered-output HTML copies.

v6 suite is now **parameterized** (as of 2026-06-05): the 6 `ads_abf_3_v6__*` source notebooks read widgets `EXP`, `START_DS`, `END_DS`, baseline window (`TVT_START`/`TVT_END`/`PRE_START`/`PRE_END`/`WIN_START`/`WIN_END` per notebook), and `PLATFORM_TYPE` (ALL|MOBILE|WEB|OTT). Defaults = OTT values, so the OTT read reproduces unchanged. Pass mobile/web params via `@/tmp/params_<plat>.json`. Lift notebooks (metrics_stat_sig, lift_heterogeneity, title_generalization, cuped_stat_sig) need NO platform filter — they ride off `core_dev.statsig.exposures` filtered by `experiment_id`, and `device_id` is platform-specific. Only global_graduation_projection + the TVT-weight queries are platform-scoped (`platform_type` on video_session; lowercase `platform` name list on impressions — MOBILE={android,iphone,ipad,firetablet,android_samsung}, WEB={web}). Per-platform launch dates: mobile/web 2026-05-27, OTT 2026-05-29.
