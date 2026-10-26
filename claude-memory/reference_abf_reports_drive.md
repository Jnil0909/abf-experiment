---
name: reference-abf-reports-drive
description: Google Drive IDs / links for ABF project reports (Google Docs)
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6a38b6e8-b694-4300-9419-9e3a9ffe953d
  modified: 2026-08-21T23:12:56.348Z
---

ABF project reports uploaded to Google Drive as native Google Docs (built via python-docx → upload_drive_file, per the cross-project [[feedback-google-docs-formatting]] convention).

All ABF report Docs live in Drive folder `0AE3wRIsB2WnhUk9PVA`.

| Report | Drive ID | Link |
|--------|----------|------|
| ABF3 Experiment v6 — Lift & Graduation Generalization Report (OTT; refreshed 2026-06-04) | `18e0CHXMsRIEZeoBKeeynEaVmf_07x9Yy` | https://docs.google.com/document/d/18e0CHXMsRIEZeoBKeeynEaVmf_07x9Yy/edit |
| ABF3 Experiment v6 — Mobile (2026-06-05) | `1uz-mn3gBME_O43-3Yy4AVw02XpVEvnhZ` | https://docs.google.com/document/d/1uz-mn3gBME_O43-3Yy4AVw02XpVEvnhZ/edit |
| ABF3 Experiment v6 — Web (2026-06-05) | `14FYkYXVVo_hwvhtzQiLW8wYtS7sTgVSE` | https://docs.google.com/document/d/14FYkYXVVo_hwvhtzQiLW8wYtS7sTgVSE/edit |
| ABF3 v6 (OTT) × V7 — TVT & Revenue Interaction Analysis (refreshed 2026-06-11; conclusion REVERSED → no interaction, see §6) | `1j_BAgDJPTwph44A9SpERrUIzq4jU8Tby4WFAYvl1kkc` | https://docs.google.com/document/d/1j_BAgDJPTwph44A9SpERrUIzq4jU8Tby4WFAYvl1kkc/edit |
| ABF3 Experiment v7 — Stronger Pruning: Results, Mechanism & Graduation Read (cross-platform; 2026-06-23; PAGELESS/wide) | `1gPBeoOh6PDBq8wMWIJdqA5Gc3tkIwHRrZCBfV5s445I` | https://docs.google.com/document/d/1gPBeoOh6PDBq8wMWIJdqA5Gc3tkIwHRrZCBfV5s445I/edit |
| ABF3 Experiment v7 — OTT — Lift & Graduation Report (2026-06-23; PAGELESS/wide) | `1Nwi5-Vrqd76DoEXHy7t3-LowYxxBuBKAQetRel6IMNE` | https://docs.google.com/document/d/1Nwi5-Vrqd76DoEXHy7t3-LowYxxBuBKAQetRel6IMNE/edit |
| ABF3 Experiment v7 — Mobile — Lift & Graduation Report (2026-06-23; PAGELESS/wide) | `1IrMG8eS-BMxI3FlRevcpGIX41lAUGw3N8pRkHtLVlFw` | https://docs.google.com/document/d/1IrMG8eS-BMxI3FlRevcpGIX41lAUGw3N8pRkHtLVlFw/edit |
| ABF3 Experiment v7 — Web — Lift & Graduation Report (2026-06-23; PAGELESS/wide) | `1taIUps7KU9pZwrLuUViJqliO93Uf1f8wKm62R4GiECw` | https://docs.google.com/document/d/1taIUps7KU9pZwrLuUViJqliO93Uf1f8wKm62R4GiECw/edit |
| ABF3 v8 — Full ABF1 Catalog Results (OTT) (2026-08-19, refreshed 2026-08-21 to 9-day Window B; Window B main / Window A appendix) | `1z70VEKZ0sfDJTuslRZ_wLacBaXaBFVcwLtzfR_M7E88` | https://docs.google.com/document/d/1z70VEKZ0sfDJTuslRZ_wLacBaXaBFVcwLtzfR_M7E88/edit |
| ABF3 v8 — Full ABF1 Catalog Results (Mobile) (2026-08-21; state `memory/abf_v8_mobile_report.docid`) | `1NSoVOcipzJ-yXRgqdzz60JV6Ippl_g_-oTUrerPdOe4` | https://docs.google.com/document/d/1NSoVOcipzJ-yXRgqdzz60JV6Ippl_g_-oTUrerPdOe4/edit |
| ABF3 v8 — Full ABF1 Catalog Results (Web) (2026-08-21; state `memory/abf_v8_web_report.docid`) | `1u5RN6dlFRf1UBr0JkyYIpB7njVs10bezViUP6yikSH0` | https://docs.google.com/document/d/1u5RN6dlFRf1UBr0JkyYIpB7njVs10bezViUP6yikSH0/edit |

Local markdown sources live in `/Users/bpulikkal/abf_experiment/` (`ABF3_experiment_v6_generalization_report.md`, `ABF3_experiment_v6_mobile_report.md`, `ABF3_experiment_v6_web_report.md`, `ABF3_v6_OTT_x_V7_interaction_report.md`). v7 report source: `/tmp/abf_v7_report.md` (state `memory/abf_v7_report.docid`).

**Pageless/wide Docs:** the publisher creates PAGES mode; to make pageless+wide, after publishing run a Docs-API `batchUpdate updateDocumentStyle` setting `documentStyle.documentFormat.documentMode='PAGELESS'` (fields `documentFormat.documentMode`) and reduce `marginLeft`/`marginRight` to ~18pt (the pageless content-width Narrow/Wide/Full toggle is UI-only — not in the API, so small margins approximate "wide"). The v7 report (`1gPBeoOh...445I`) was set this way.

**v8 report (2026-08-19) used the NEW path — `gdoc` CLI (gsuite MCP/publish_native_doc are dead post-Fox-migration):** source `ABF3_experiment_v8_report.md` (project root), state `memory/abf_v8_report.docid`. Republish in place: `python3 ~/.claude/plugins/cache/tubi-skills/gsuite/1.0.0/skills/gsuite-setup/scripts/gdoc.py update "$(cat memory/abf_v8_report.docid)" --from ABF3_experiment_v8_report.md`. gdoc converts markdown→native Doc directly (no docx step). Prefer this path for all future reports.

**LEGACY path (pre-2026-08) — to regenerate/republish a report Doc in place (STABLE link):** build the docx with the project converter `~/gsuite-mcp-server/.venv/bin/python /Users/bpulikkal/abf_experiment/md2docx.py <report.md> /tmp/out.docx` (parses headings/bold/bullets/pipe-tables/hr), then publish via the global stable-link publisher:
```
~/gsuite-mcp-server/.venv/bin/python ~/.claude/scripts/publish_native_doc.py \
  --docx /tmp/out.docx --name "<title>" --folder 0AE3wRIsB2WnhUk9PVA \
  --state memory/<report>.docid
```
The `--state` .docid file holds the stable Doc id → re-running overwrites content in place, id/link never change. V7 report state file = `memory/abf_v6_v7_interaction_report.docid`. Note: `--name` is honored only on FIRST creation (the V7 Doc's stored title shows "× Dynamic_ads_V7 —" from an earlier run; cosmetic, content/link fine — rename via Drive API if needed). Do NOT use MCP `update_drive_file` for Docs (string-only, breaks the link). See [[feedback-google-docs-formatting]].
