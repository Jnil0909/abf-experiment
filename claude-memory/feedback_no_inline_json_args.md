---
name: feedback_no_inline_json_args
description: "Avoid inline JSON (braces/quotes) in Bash commands — triggers \"simple_expansion\" permission prompts; pass via file instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9b4d39d7-89e1-456f-9e21-b30b7d6fecb4
---

User does not want to be repeatedly asked the "Contains simple_expansion / Do you want to proceed?" permission prompt. This fires when a Bash command contains inline JSON or shell-expansion characters (`{}`, `""`) even when `Bash(python3 *)` is allowlisted.

**Why:** The harness shell-safety check flags `{...}` and quoting as expansion regardless of the permission allowlist, so each such call prompts.

**How to apply:** Never pass inline JSON on the command line. Write the JSON to a file with the Write tool, then pass the file path. For `abf_db.py run`, the 4th arg accepts `@/path/to/params.json` (a file of notebook base_parameters) precisely so widget params avoid inline braces. See [[reference_abf_db_helper]].
