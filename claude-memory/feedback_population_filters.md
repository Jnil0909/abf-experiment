---
name: population-filters-post-randomization
description: "Experiment population filters: only condition on pre-treatment-safe events — 'watched ≥1 session SINCE FIRST EXPOSURE' is valid; window-scoped activity and 'had ≥1 ad break' are not"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9a58f1a4-e082-425f-ac74-37462bf2d489
  modified: 2026-08-20T06:43:14.415Z
---

When de-diluting an experiment population (v8 lesson: title-LOAD-triggered exposure → ~64% of exposed devices never watch), the filter must be treatment-independent **by construction**, not just empirically balanced:

- ✅ **"≥1 video session since first exposure"** — valid: a never-watcher never experienced treatment, so treatment cannot cause exclusion. (v8: balanced 35.6687% vs 35.6707%.)
- ❌ **"≥1 session within the analysis window"** (when exposure predates the window) — a device may have been churned BY treatment before the window; conditions on a post-treatment outcome. (v8 Window B: empirically balanced, z≈0.6, but unsafe by construction — use since-exposure as definition of record.)
- ❌ **"≥1 ad break fired"** — directly treatment-dependent (denser cue points → break more likely to fire). Measured pro-Test tilt +0.021pp, z≈2.2 in v8.

**Why:** post-randomization selection on treatment-affected events biases every downstream metric.

**How to apply:** in any windowed re-analysis (Window B-style), keep the Active filter anchored at first exposure, not the window start (`ACTIVE_FROM` widget in `ads_abf_3_v8__cuped_stat_sig`). Also remember: removing zero-outcome devices does NOT change relative (%) lifts — numerator and denominator scale identically; the filter buys interpretable per-device magnitudes and slightly tighter CIs, nothing else. Related: [[project-v8-experiment]].
