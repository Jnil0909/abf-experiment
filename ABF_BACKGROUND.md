# Ad Break Finder (ABF) — Project Background

## Overview

In Tubi, ABF is an acronym for ad break finder. 
We have 3 versions of it ABF1.0, ABF2.0, ABF3.0. 
ABF1.0 can also be called pre-ABF, as this was before the idea of ABF. 
ABF2.0 was luanched around mid-2023. 
Ad break finder is an ML algorithm to detect cue points for ad breaks in the video. 
Prior to ABF2.0, this was done manually by a team in Philippines. They watch each title and identify cue points.

ABF2.0 introduced an ML / computer vision based model to do this. Then these cue points go through manual review process
Human reviewers can reject cue points and/or insert additional cue points (~80% of cue points are human modified/inserted).
Half the cue points aren’t even human reviewed because it’s quicker/easier to insert a cue point than it is to review and then modify it.
Reviewers have been binning cue points that are too close to each other thinking that cue points being too close to each other will cause a bad viewing experience and not realizing that the ad load is controlled by the ad config. We ran an experiment to measure the impact of ABF2.0 over pre-ABF , the impact was 3% unbudgeted revenue lift. 

Now we wanto to introduce ABF3.0 . This is a new ML model, which will produce cue points & they go through manual review process. However, human reviewers can only accept or reject (no insertions). This is expected to significantly reduce time taken to process titles, as it reduces human review time. ABF3.0 model produces significantly more cue points per content title. These cue points are also expected to have better quality (better positioning within video)

Now we want to run an experiment designed to measure the impact of ABF3.0 (new ML model) compared to ABF2.0. The core challenge is that the new model produces **more** cue points per title than the existing model while claiming **better quality** (superior positioning within video). Simply deploying the new model would conflate two separate effects:

- **Quality effect** — better-positioned ad breaks improving user experience
- **Quantity effect** — more frequent ad breaks harming user engagement

The experiment is designed to isolate these two effects from each other.

---

## Experiment Updates

### What Actually Happened

Despite the three-arm RCT being the recommended design, the experiment was run differently. ABF3.0 cue points were **not downsampled or subset to match ABF2.0 cue point density**. The experiment was run as a simpler two-arm A/B test — ABF2.0 (control) vs ABF3.0 (treatment) — with ABF3.0 exposed at its native, higher cue point density.

As a result, quality and quantity effects are **not isolated** — any observed difference between arms reflects the combined impact of both better cue point positioning and more frequent ad breaks.

### New Experiment: ABF3 vs Existing (ABF1/ABF2)

### Previous Experiment (Stopped)

**Timeline:** Started **2026-03-30**, stopped **2026-04-17** (~18 days runtime).

This was the first attempt — ~414 ABF3 titles, 136 contaminated (excluded), leaving 278 eligible titles. See findings above (early signal: +5% revenue, -0.6% TVT).

---

### Experiment: ABF3 vs ABF1/ABF2 — Quantity Confounded (Stopped)

**Experiment name:** `ads_abf_3_v3`

**Timeline:** Launched **2026-04-17**, stopped **2026-04-21** (~4 days runtime).

**Allocation ramp:**
- Day 1: 1%
- Weekend (04/19–04/20): 10%
- Monday 04/21: 100% ✓ (reached)

**Structure:**
- **~1000 titles** total
- ~500 titles with ABF1 cue points (control)
- ~500 titles with ABF2 cue points (control)
- Treatment arm: ABF3.0 cue points for all ~1000 titles
- Control arm: existing cue points (ABF1 or ABF2, per title)

**Exposure definition:** A user is considered exposed if their device **loads any of the ~1000 titles** — they do not need to actually watch it.

**Secondary comparisons (subgroup analyses):**
- ABF3 vs ABF2 — subset of titles where control = ABF2 (~500 titles)
- ABF3 vs ABF1 — subset of titles where control = ABF1 (~500 titles)

The control baseline (ABF1 vs ABF2) is known per title. The split is roughly equal, so both subgroup comparisons are reasonably powered.

**Known limitation:** Quality and quantity effects are **not isolated**. ABF3.0 runs at its native, higher cue point density with no min-spacing control to equalize ad break frequency. Any observed difference reflects the **combined effect of better cue point positioning AND more frequent ad breaks**. This is an accepted trade-off in this design — the goal is measuring net impact, not decomposing it.

**Randomization:** User-level. Users are assigned to treatment or control — a user cannot be in both arms. If a treatment user loads one of the ~1000 titles, they receive ABF3.0 cue points. Control users loading the same title receive the existing (ABF1 or ABF2) cue points.

**Dilution and analysis approach:**

The ~1000 ABF3 titles are a small fraction of the full catalog. Treatment users who never watch any of these titles receive no different experience — they are assigned to treatment but unexposed. This dilutes the measured effect.

Two analysis approaches are required:

| Analysis | Population | Purpose |
|---|---|---|
| **Intent-to-Treat (ITT)** | All users assigned to treatment vs control | Conservative estimate; reflects real-world impact at current title coverage |
| **Treatment on the Treated (ToT)** | Only users who watched ≥1 of the ~1000 ABF3 titles | True effect of ABF3 exposure among affected users |

ToT is the primary lens for understanding ABF3's actual impact. ITT tells you what to expect if ABF3 were shipped at current coverage levels.

**TVT coverage of experiment titles:**

| Title Group | % of Total TVT |
|---|---|
| ABF2 titles (~500) | 15.0% |
| ABF1 titles (~500) | 13.3% |
| ABF1 + ABF2 combined | **28.2%** |

This is far greater coverage than the prior experiment (0.7% of TVT), giving meaningful signal.

**ABF3 cue point density vs existing models (from `abf_3_cue_point_ratio.csv`):**

| Comparison | n titles | Median ratio | Mean ratio |
|---|---|---|---|
| ABF3 vs ABF1 | 510 | 3.88x | 3.82x |
| ABF3 vs ABF2 | 489 | 2.75x | 2.97x |

ABF3 produces ~4x more cue points than ABF1 and ~3x more than ABF2. This higher density is the likely primary driver of both the revenue uplift and the TVT cost in the results below.

**Success Metrics and Criteria:**

Primary metrics: `unbudgeted_revenue`, `TVT`, `QVD`

| Outcome | Criteria |
|---|---|
| All three neutral or better | Clear success — ship ABF3 |
| Revenue up, TVT/QVD down | Acceptable if tradeoff is favorable (thresholds TBD) |
| Revenue neutral/down, TVT/QVD down | Failure — do not ship |

A pre-agreed tradeoff threshold (e.g. "X% revenue lift acceptable for up to Y% TVT drop") should be defined before analysis to avoid post-hoc rationalization. **Thresholds to be confirmed with stakeholders.**

**Graduation Decision Metric: `me_score` (Monetization Efficiency Score)**

A single composite metric that encodes the revenue vs engagement tradeoff. The graduation decision is: is `me_score` statistically significantly positive?

- **Status:** Not yet implemented in the experiment pipeline — will be **calculated offline** post-experiment
- **Formula:** `me_score = w1 * short_term_revenue + w2 * predicted_long_term_revenue`
  - `short_term_revenue` = `unbudgeted_revenue` measured during the experiment
  - `predicted_long_term_revenue` = predicted using `e_score` (engagement score — see below)
- **Graduation threshold:** `me_score` must be **statistically significantly positive**
- **Weights:** `w1 = w2 = 0.5` (equal weighting of short-term and predicted long-term revenue)

**`e_score` (Engagement Score)**

- Used to predict long-term revenue as an input to `me_score`
- **Status:** Not yet implemented in the experiment pipeline — currently calculated offline
- **Based on:** user content completion and retention behavior

### Early Results — 2026-04-20 (3 days post-launch, ramping to 100%)

All results are **statistically significant** (95% CI does not cross zero). Full analysis in `ABF3_experiment_v2_early_results.ipynb` and `ABF3_experiment_v2_early_results_report.md`.

Two scopes reported: **ABF3 titles only** (direct treatment effect) and **All titles** (diluted by non-experiment titles).

**ABF3 vs ABF1+ABF2 combined — users who watched either ABF1 or ABF2 titles:**

| Metric | ABF3 Titles Only | All Titles |
|---|---|---|
| TVT | -2.41% | -1.64% |
| Unbudgeted Revenue | +13.00% | +6.28% |
| Unbudgeted Impressions | +15.04% | +7.20% |

**ABF3 vs ABF2 only — users who watched ABF2 titles (not ABF1):**

| Metric | ABF3 Titles Only | All Titles |
|---|---|---|
| TVT | -1.95% | -1.33% |
| Unbudgeted Revenue | +9.93% | +3.99% |
| Unbudgeted Impressions | +11.42% | +4.56% |

**ABF3 vs ABF1 only — users who watched ABF1 titles (not ABF2):**

| Metric | ABF3 Titles Only | All Titles |
|---|---|---|
| TVT | -1.63% | -1.24% |
| Unbudgeted Revenue | +18.37% | +7.86% |
| Unbudgeted Impressions | +21.32% | +8.95% |

**Interpretation:**
- Consistent pattern across all cuts: significant revenue/impression uplift, small but significant TVT decline
- ABF3 vs ABF1 shows nearly 2x the revenue lift vs ABF3 vs ABF2 — expected, since ABF1 had no ML-based placement
- Both effects are likely driven primarily by ABF3's higher cue point density (quantity), not quality — still confounded
- `me_score` not yet calculated; no graduation decision can be made yet
- Tradeoff threshold (revenue lift vs TVT drop) not yet confirmed with stakeholders

**Ad break intensity diagnostic (non-empty ad breaks per TVT hour, ABF3 titles only):**

ABF3 treatment users experience **17–26% more ad breaks per hour** than control across all subgroups. This directly quantifies the quantity effect and is the primary explanation for both the revenue uplift and TVT decline.

| User Subgroup | Control | Treatment | % Increase |
|---|---|---|---|
| Either ABF1 or ABF2 users | 12.99 | 15.80 | +21.6% |
| ABF1-only users | 13.86 | 17.49 | +26.2% |
| ABF2-only users | 12.90 | 15.11 | +17.1% |
| Both ABF1 and ABF2 users | 12.71 | 15.49 | +21.9% |

ABF1-only subgroup sees the largest increase, consistent with ABF1 titles having the fewest baseline cue points. Source: `ABF3_experiment_v2_early_results.ipynb` cells 9–12.

---

### Experiment: ABF3 Quality Isolation — Density-Matched (Ended)

**Experiment name:** `ads_abf_3_v4`

**Timeline:** Ran **2026-04-28 10:30 AM PST → 2026-05-06** (~8 days). Now ended. Final results in `ABF3_experiment_v4_early_results_report.md` and `ABF3_experiment_v4_early_results_excluded_content_report.md`.

**Purpose:** Two simultaneous sub-experiments within a single A/B test, analyzed separately by title set.

**Structure:**

| Title Set | n Titles | Control | Treatment | What It Measures |
|---|---|---|---|---|
| Original titles (from v3) | ~1000 | ABF1 or ABF2 (per title) | ABF3 pruned to match ABF2 density | Quality effect only |
| FIFA World Cup titles | 711 | ABF1 or ABF2 (per title, no distinction) | ABF3 at native density | Combined quality + quantity |

- Same user-level randomization across both title sets — a user is in one arm only
- The two title sets will be **analyzed as separate subgroups**
- For WC titles, the ABF1 vs ABF2 control distinction is not a focus — treated as a single control baseline
- Pruning method for original titles: TBD (not yet available)

**Key difference from v3:** Original titles now have density equalized to isolate quality. WC titles are intentionally unpruned — the goal there is measuring net revenue and TVT impact on a new, high-value content category.

---

### Results — 2026-05-05 (Day 7)

Source: `ABF3_experiment_v4_early_results.ipynb` (non-WC), `ABF3_experiment_v4_early_results_wc.ipynb` (WC), `ABF3_experiment_v4_early_results_excluded_content.ipynb` (excluded analysis).

#### Non-WC Titles (density-matched — quality isolation)

**Title coverage:** ABF2 titles = 10.54% of TVT, ABF1 titles = 8.88%, combined = **19.30%** of total TVT.

**Ad break density (ABF3 titles only):**

| User Subgroup | Control | Treatment | Δ |
|---|---|---|---|
| ABF1 or ABF2 combined | 12.85 | 12.96 | +0.9% |
| ABF1-only users | 13.18 | 13.92 | +5.6% |
| ABF2-only users | 13.39 | 13.04 | **-2.6%** (over-pruned) |
| Both ABF1 and ABF2 users | 12.63 | 12.76 | +1.0% |

ABF2-only users are over-pruned (treatment has fewer breaks than control) — suppresses treatment revenue mechanically.

**Metric lifts — full analysis (ABF3 titles only):**

| Comparison | TVT | Revenue | Impressions | Stat Sig? |
|---|---|---|---|---|
| ABF3 vs ABF1+ABF2 (both) | +0.23% | **+1.04%** | **+1.16%** | TVT: yes (marginal, z=1.98); Rev/Imps: yes |
| ABF3 vs ABF2 only | +0.07% | **-1.55%** | **-1.76%** | Rev/Imps: yes (artifact); TVT: no |
| ABF3 vs ABF1 only | +0.02% | **+4.58%** | **+5.07%** | Rev/Imps: yes; TVT: no |
| ABF3 vs ABF1+ABF2 (either) | +0.10% | **+0.93%** | **+1.00%** | Rev/Imps: yes; TVT: no |

**Metric lifts — excluded analysis** (~75 over-pruned titles removed, ABF3 titles only):

| Comparison | TVT | Revenue | Impressions | Stat Sig? |
|---|---|---|---|---|
| ABF3 vs ABF1+ABF2 (both) | +0.19% | **+2.49%** | **+2.74%** | Rev/Imps: yes; TVT: no |
| ABF3 vs ABF2 only | -0.03% | **-0.06%** | **-0.17%** | **All null — definitive parity** |
| ABF3 vs ABF1 only | -0.004% | **+4.64%** | **+5.13%** | Rev/Imps: yes; TVT: no |
| ABF3 vs ABF1+ABF2 (either) | +0.04% | **+2.24%** | **+2.44%** | Rev/Imps: yes; TVT: no |

**Conclusions:**
- **ABF3 quality = ABF2 quality**: After removing over-pruned titles, ABF3 vs ABF2 is fully null across all metrics. ABF3 offers no positioning advantage over ABF2.
- **ABF3 quality > ABF1**: +4.64% revenue, +5.13% impressions, flat TVT. Robust and highly significant.
- **TVT flat across all cuts**: The -2.4% TVT drop in v3 was entirely quantity-driven, confirmed by v4 with density equalized.
- **Revenue lifts have moderated from day 3 to day 7**: +1.83% → +0.93% for ABF3 vs either group (full analysis). More stable estimates at day 7.

#### FIFA World Cup Titles (native density — quality + quantity)

**Title coverage: 0.0213% of total TVT**

**Ad break density:** Control = 13.02 breaks/hr → Treatment = 14.61 breaks/hr → **+12.2%**

**Metric lifts (WC titles only):**

| Metric | Lift | Stat Sig? | 95% CI |
|---|---|---|---|
| TVT | **-3.66%** | **yes** | -6.73% to -0.59% |
| Revenue | **+5.92%** | **yes** | +1.41% to +10.43% |
| Impressions | **+8.45%** | **yes** | +3.97% to +12.92% |

WC results are now statistically significant. ABF3 at native density on WC titles delivers +5.92% revenue but at a confirmed -3.66% TVT cost. Stakeholder tradeoff threshold needed before any WC rollout decision.

**Open question:** Whether to ship ABF3 at native density on WC titles requires a pre-agreed threshold (e.g. "X% revenue lift per Y% TVT drop"). This has not been defined.

---

### Experiment: ABF3 with New Pruning Algorithm — v5 (Abandoned) and v6 (Active)

**Major change (v5 and v6):** A **new pruning algorithm** to match ABF3 cue point density to ABF2 density. This replaces the v4 pruning approach (whose ad hoc method produced the over-pruning artifact — ~75 titles left with only 1–2 cue points and ABF2-only users receiving *fewer* breaks than control).

**`ads_abf_3_v5` (Abandoned):** Launched but abandoned due to bugs in the experiment setup.

**`ads_abf_3_v6` (Active):** Launched **2026-05-29**, still running. Same new pruning algorithm as v5, launched after the v5 setup bugs were fixed.

**v6 scope — ABF1 vs ABF3 only:** Unlike v4 (which had two title sets — ~1000 non-WC + 711 FIFA WC), v6 tests **only ABF1 vs ABF3**: the impact of ABF3 cue points on titles that currently have ABF1 cue points. No ABF2 control arm and no WC title set.
- **1,084 titles** total
- Control: existing ABF1 cue points
- Treatment: ABF3 cue points, pruned via the new pruning algorithm to match ABF2 density
- Rationale: v4 already established ABF3 = ABF2 at equal density (no quality advantage), while ABF3 > ABF1 (+4.64% revenue). v6 focuses on the ABF1 comparison, where the real upside is.

**v6 platform variants (all active):** The v6 ABF1-vs-ABF3 test runs as three separate per-platform experiments:

| Experiment | Platform | Launched |
|---|---|---|
| `ads_abf_3_v6` | OTT | 2026-05-29 |
| `ads_mobile_abf_3_v6` | Mobile | 2026-05-27 |
| `ads_web_abf_3_v6` | Web | 2026-05-27 |

Mobile and web launched two days before OTT. All three still running.

#### v6 Results — refreshed 2026-06-04 (OTT, window 05-29→06-03, complete days)

**Refresh note (2026-06-04):** Re-ran all 6 notebooks with one more complete day (window capped at 06-03; 06-04 was a partial day, excluded). Numbers stable vs the day-5 read — effect holding, not moderating. Added a **global TVT** estimate. Headline lifts now: ToT abf3-only revenue **+5.67%**, TVT **−0.33%**; global revenue **+2.18%** (CI [+1.99,+2.37]). **Global TVT: −0.05% (on-title dilution) to −0.40% (coverage-scaling w/ spillover)** — likely toward −0.4% given measured cross-title substitution (all-titles TVT decline exceeds on-title losses). Graduation trade ≈ **+2.2% global revenue for ~−0.4% global TVT**. Run outputs: `ads_abf_3_v6__*__run_2026-06-04_OUTPUT`. (Figures below are the original day-5 read, kept for history.)

#### v6 Results — 2026-06-03 (OTT, ~6 days post-launch)

Full report: `ABF3_experiment_v6_generalization_report.md`. Notebooks: `/Users/bpulikkal@tubi.tv/ABF_3/ads_abf_3_v6__*` (dated archive copies `__run_2026-06-03`). Analysis run via Databricks serverless; helper `abf_db.py` in project root.

**Supporting tables (Databricks):**
- `core_dev.dsa.temp_bp_abf_v6_exp_titles` — 1,084 experiment title content_ids
- `core_dev.dsa.temp_bp_abf1_universe` — 492,024 titles = {no ABF cue points} ∪ {1,084 exp titles}; cols: abf1_cue_points (from `cue_points`), content_type, duration, primary_genre, in_experiment

**Headline lift (device-level, ToT, Welch t-test):**

| Metric | ABF3 titles only | All titles |
|---|---|---|
| Unbudgeted Revenue | **+5.70%** ([+5.45,+5.94]) | +1.33% ([+1.12,+1.53]) |
| Unbudgeted Impressions | **+6.37%** ([+6.12,+6.63]) | +1.42% ([+1.21,+1.64]) |
| TVT | **−0.31%** ([−0.54,−0.08]) | −0.11% (ns) |

n_control 3,174,716 / n_test 3,173,859 devices. Coverage = 13.10% of exposed-device TVT. Ad-break density Control 13.58 → Test 14.53/hr (+6.98%) — ABF3 pruned to ABF2 density runs hotter than sparse ABF1 baseline, so lift carries a residual quantity component.

**Graduation generalization (can the lift hold on ALL ABF1 titles ≈ 45% of TVT?):** YES.
- Sample (1,084) was random; carries 41.4% of ABF1 TVT (large titles). Raw per-title traits skew hugely (density 7.44 vs 2.80, std diff 1.19) but TVT-weighted they're close (density 8.95 vs 7.43) — raw skew is the zero-TVT long tail.
- Revenue lift is heterogeneous across ABF1-density deciles (+1.2% to +12.3%, peak at mid-density 7–9 cue points); MOVIE +8.14% vs SERIES +1.95%. TVT flat in every cut.
- **Poststratified projection onto full ABF1 universe = +7.0% revenue**; **title-clustered 95% CI [+6.1%, +8.5%]** (2,000-iter title bootstrap, much wider than device CI but comfortably positive). Flat TVT.
- Conclusion: graduating ABF3 on all ABF1 titles via random sample is well-supported at ~+7% revenue, flat TVT. `me_score`/`e_score` (offline) remain the formal gate, not yet computed.

**Global (topline) lift if graduated (notebook `ads_abf_3_v6__global_graduation_projection`):**
- ABF1 universe = **36.2% of total unbudgeted revenue / 36.7% of TVT** (14d pre-launch window, universe = {has_abf=0} ∪ 1,084 exp titles). **CONFIRMED as the official graduation denominator (2026-06-03)** — SUPERSEDES the earlier "~45% of TVT" planning figure, which could not be reproduced under any definition tested (strict untreated-ABF1 = 21.5% TVT @14d, 29.4% @90d).
- 70.1% of devices (39.4M/56.3M) watch ≥1 ABF1 title in 14d.
- Diluting the ~+6% ABF1-wide lift by the 36.2% revenue share → **GLOBAL unbudgeted revenue lift ~+2.2%** (poststratified point +2.19%, CI [+1.99%, +2.38%]), **GLOBAL TVT −0.05%** (negligible).
- **Cross-check (two independent methods bracket +1.9–2.2%):** The 1,084 exp titles' revenue share was measured directly at **15.75%** of total (14d window). Scaling the ITT all-titles lift (+0.83%) by coverage ratio 36.2/15.75 ≈ 2.30× → **+1.9%**, vs bottom-up poststratification +2.2%. The ~0.3pp gap: ITT identity implies exp-title on-title lift ~5.3% vs measured 5.80% / projected 6.04% — the random draw landed on titles slightly below the full-universe lift (dense/long skew over-indexes non-top-lift deciles). Defensible launch range **+1.9% to +2.5%**, point **~+2.2%**.

**CUPED variance-reduced significance (notebook `ads_abf_3_v6__cuped_stat_sig`):** Covariate = pre-period (05-15..05-28) same-metric per device, pooled θ. Matrix {ITT,ToT}×{all-titles,abf3-only}.
- Confirms all headline results; lifts essentially unchanged (e.g. ToT/abf3 revenue +5.73%→+5.69% CUPED).
- Variance reduction large for all-titles cuts (45–57%), modest for abf3-only (8–17%).
- CUPED flips two small all-titles TVT results to significant: ITT/all −0.165%, ToT/all −0.201% — tiny but real engagement dip worth monitoring.
- First time CUPED has been applied to v6 experiment data (prior stat-sig was raw Welch only).

**Run outputs:** All 6 notebook runs saved as rendered HTML (with outputs) in `/Users/bpulikkal@tubi.tv/ABF_3/ads_abf_3_v6__*__run_2026-06-03_OUTPUT`. Source notebooks (no outputs) are the un-suffixed names. Helper `abf_db.py` (project root) runs SQL/notebooks/exports via Databricks REST without permission prompts.

**Report (Google Doc, refreshed 2026-06-04):** [ABF3 Experiment v6 — Lift & Graduation Generalization Report](https://docs.google.com/document/d/18e0CHXMsRIEZeoBKeeynEaVmf_07x9Yy/edit) — Drive ID `18e0CHXMsRIEZeoBKeeynEaVmf_07x9Yy`. Local markdown source: `ABF3_experiment_v6_generalization_report.md`. Reports CUPED-only lifts; cross-validated against Statsig CURE dashboard (ITT all-titles: TVT −0.16% both, revenue +0.84% CUPED vs +0.72% CURE).

**Deferred follow-up — COMPLETED 2026-06-05:** The full v6 analysis suite (metrics/stat-sig, representativeness, heterogeneity, title-generalization, global projection, CUPED) was run on the **mobile** (`ads_mobile_abf_3_v6`) and **web** (`ads_web_abf_3_v6`) variants. See the per-platform results section below.

#### v6 Results — Mobile & Web — 2026-06-05

**Method:** The 6 OTT notebooks were parameterized (widgets `EXP`, `START_DS`, `END_DS`, baseline window, and `PLATFORM_TYPE`) with OTT values as defaults, so the OTT notebooks still reproduce as-is. Mobile/web ran the same notebooks with per-platform params. Lift notebooks need no platform filter (they ride off the `core_dev.statsig.exposures` table, which is already scoped per `experiment_id`, and `device_id` is platform-specific). Only the **global-projection denominators** (ABF1 share of total revenue/TVT, device-exposure rate) and the **TVT-weight queries** are platform-scoped — to `platform_type='MOBILE'`/`'WEB'` on `video_session`, and to the matching lowercase `platform` name list on `impressions` (MOBILE = android/iphone/ipad/firetablet/android_samsung; WEB = web). So mobile/web "global lift" is each platform's lift diluted by **that platform's** topline (self-consistent per-platform graduation number).

- **Window:** experiment **2026-05-27 → 2026-06-04** (complete days; mobile/web launched 05-27, two days before OTT). Baseline/pre-period shifted to **2026-05-13 → 2026-05-26** (clean pre-launch for the 05-27 launch — the OTT 05-15→05-28 window would leak 2 post-launch days into the CUPED covariate and baseline shares).
- **Run outputs:** rendered HTML in `/Users/bpulikkal@tubi.tv/ABF_3/ads_{mobile,web}_abf_3_v6__*__run_2026-06-05_OUTPUT` (12 notebooks).

**Headline (device-level ToT, ABF3 titles only, CUPED) — three-platform comparison:**

| Platform | Unbudgeted Revenue | Impressions | TVT | Global rev (platform-scoped) | Global TVT |
|---|---|---|---|---|---|
| OTT (`ads_abf_3_v6`) | +5.67% | +6.35% | **−0.33%** (sig) | ~+2.2% (CI [+1.99,+2.37]) | −0.05% to −0.40% |
| **Mobile** (`ads_mobile_abf_3_v6`) | **+6.89%** | +7.88% | **−0.90%** (sig) | **+3.19%** (CI [+2.45,+3.94]) | **−0.34% to −0.70%** |
| **Web** (`ads_web_abf_3_v6`) | **+8.95%** | +9.65% | **−0.17%** (flat, ns) | **+4.68%** (CI [+2.73,+6.63]) | **+0.27% to +1.47%** (flat/positive) |

**Key takeaways:**
- **Web is the cleanest, strongest case:** highest revenue lift (+8.95% on-title, ~+4.68% global), **no measurable TVT cost** (flat-to-positive). Smallest device base (ToT ≈261K/arm) so widest CIs. ABF1 = 41.1% of web revenue.
- **Mobile has the largest engagement cost:** significant **−0.90%** on-title TVT (vs OTT −0.33%, web flat) and a global mobile TVT estimate of **−0.34% to −0.70%** (spillover end more realistic — all-titles TVT decline exceeds on-title losses). Revenue still strong (+6.89% on-title, +3.19% global). ABF1 = 39.0% of mobile revenue.
- **Generalization holds on all platforms:** revenue lift monotone-decreasing in ABF1 density (sparsest titles gain most, +20–30% in decile 1), positive in nearly every decile; title-clustered CIs comfortably positive (mobile [+5.22,+8.49], web [+6.96,+10.53]). SERIES > MOVIE revenue lift on both.
- **Graduation trade by platform:** OTT ~+2.2% rev / ~−0.4% TVT; mobile ~+3.2% rev / −0.4% to −0.7% TVT; **web ~+4.7% rev / ~flat TVT (most favorable)**. `me_score`/`e_score` (offline) remain the formal gate for all platforms; not computed.

**Reports (Google Docs, folder `0AE3wRIsB2WnhUk9PVA`):**
- Mobile: [ABF3 Experiment v6 — Mobile](https://docs.google.com/document/d/1uz-mn3gBME_O43-3Yy4AVw02XpVEvnhZ/edit) — Drive ID `1uz-mn3gBME_O43-3Yy4AVw02XpVEvnhZ`. Local source: `ABF3_experiment_v6_mobile_report.md`.
- Web: [ABF3 Experiment v6 — Web](https://docs.google.com/document/d/14FYkYXVVo_hwvhtzQiLW8wYtS7sTgVSE/edit) — Drive ID `14FYkYXVVo_hwvhtzQiLW8wYtS7sTgVSE`. Local source: `ABF3_experiment_v6_web_report.md`.

#### v6 OTT × V7 concurrent-experiment interaction — 2026-06-10

**Question:** ABF3 v6 OTT ran concurrently with a second ad-load experiment, `dynamic_ads_tolerance_mtml_device_xgboost_session` ("V7", Bing Wang, ran 2026-05-21→06-02). V7 reduces ad-break spacing (→ more ads) for tolerant/stable devices via ML targeting; 1 control + 10 treatment arms (~1.5M devices/arm); all OTT platforms **except Roku** (+ Web/Amazon). Many devices were co-exposed. Did the interaction better/worsen ABF3's TVT (and revenue) effect, or is there no interaction?

**Design:** 2×2 factorial (ABF3 Control/Test × V7 Control/any-treatment) on **2.62M co-exposed devices**, overlap window **2026-05-29→06-02** (only period both live), ABF3-titles-only ToT, CUPED (clean joint pre-period 05-07→05-20, before both launches). Randomizations independent (no cross-exp SRM: 90.01% vs 89.98% V7-treated across ABF3 arms). **Roku natural control** (Part B): V7 never served Roku and device_id is platform-specific → 0 Roku devices in V7 → ABF3 effect on Roku (1.56M devices/arm) = pure ABF3 at zero V7. Notebook `/Users/bpulikkal@tubi.tv/ABF_3/abf_v6_v7_interaction`.

**⚠️ CONCLUSION REVERSED 2026-06-11 by a clean post-V7 follow-up (see next subsection). The co-exposure analysis below (its "likely-real interaction" lean) is SUPERSEDED — there is NO V7 interaction. ABF3's TVT cost is standalone and platform-driven. Kept for history.**

**Result (ORIGINAL 2026-06-10, now superseded) — a TVT interaction is LIKELY REAL but underpowered to prove (not a clean null).** The interaction misses 95% (ITT TVT p=0.092, ToT p=0.17), but this is a power failure — V7 starved its control arm 10-to-1 — not evidence of no effect; the CI permits a meaningful negative interaction. Evidence leans toward V7 deepening ABF3's TVT cost. The v6 OTT −0.33% TVT headline is therefore likely NOT *entirely* intrinsic to ABF3 — part is attributable to V7 co-exposure (so ABF3's standalone cost is probably <−0.33%). Do not read "not significant" as "no interaction."
- Interaction (identical under both framings — algebraically symmetric): **TVT −1.60% [−3.87,+0.67], p=0.17**; **revenue −1.16% [−3.23,+0.91], p=0.27**. Both CIs straddle zero.
- ABF3-side: ABF3 TVT effect = +1.02% in V7-control vs −0.58% in V7-treated; revenue +6.32% vs +5.13%. V7-side: V7 TVT effect = +0.37% (ns) in ABF3-control vs −1.22% (ns) in ABF3-test.
- **All-titles ITT cut (higher power, ~3× V7-control cell: 131k/arm):** interaction tightens but still misses 95% — **TVT −1.32% [−2.85,+0.21], p=0.092 (marginal)**; rev p=0.123. Decisive new result: **ABF3's TVT effect among V7-treated devices is significantly negative, −0.70% [−1.18,−0.22], p=0.0045**, vs +0.61% (ns) among V7-control.
- **Confident simple effect + likely-real interaction (keep separate):** the −0.70% on V7-treated devices is a significant effect *within that cell*; whether it's *larger than* ABF3's cost off V7 (= the interaction) is likely real but not yet proven at 95%. Coherent dose gradient — **zero V7 (Roku, 1.56M/arm): +0.01% [−0.31,+0.33] p=0.95 (precise flat)** → V7-control (ITT): +0.61% (ns) → **V7-treated (ITT): −0.70% (sig)** — with the off-V7 end *precisely* measured flat on Roku (not just noisily flat) and a clear mechanism (both add ad load → compounding). Difference-of-differences misses 95% (p=0.092) only because the V7-control arm is starved 10-to-1. Compounding is the most likely reading; confirm with more data, don't rule out.
- **Revenue rises strongly everywhere — never a drop**: ABF3 rev lift +5.13% (V7-treated) / +6.32% (V7-ctrl) ToT. The "more ads → more money" effect is real and lives in *revenue per watch-hour*, which is unchanged by V7 (≈+5.3% V7-ctrl vs +5.7% V7-treated; implied per-hour interaction ≈0). Total rev% ≈ rev/hour% + TVT%, so the slightly smaller *total* lift on V7-treated devices is just the same per-hour rate × fewer hours (the TVT cost), NOT a monetization penalty. Higher ad load *simultaneously* lifts per-hour revenue and trims hours — no contradiction; the larger TVT cost despite identical per-hour revenue reflects a convex annoyance curve (extra breaks hurt more when baseline ad load is already high). Revenue follows TVT; not independent evidence.
- **Caveats:** binding constraint is power — even ITT's V7-control cell (~131k) is the noisy arm (V7 ran 10 treatment vs 1 control), so full interaction misses 95%. Roku is corroborating not confirmatory (confounded with platform). V7 "treatment" pools all 10 arms incl. the opposite-direction `DGSpacingIncrease20Pct`. Single 5-day overlap window.
- **Bottom line:** a TVT interaction is likely real but not provable at 95% — underpowered, NOT a clean null. Confident finding: on V7-treated devices ABF3 costs −0.70% TVT (p=0.0045) — a *simple effect* within one cell. Likely real but unproven: that this is *worse than* ABF3's cost off V7 (the interaction); difference-of-differences stays ns (p=0.092 ITT, p=0.17 ToT) only because V7 starved its control arm 10-to-1. The case is strong — coherent dose gradient + precisely-measured flat off-V7 effect on Roku + clear mechanism — so ABF3's standalone TVT cost is *likely* smaller than the v6 OTT on-title ToT −0.33% headline, with part attributable to V7 (the all-OTT/global TVT figure is separately −0.05% to −0.40%; −0.33% is the on-title ToT number). Revenue is a follower of TVT (per-hour monetization unchanged), not independent evidence. Confirm with more data; do not rule out.

#### v6 OTT — post-V7 clean-window follow-up — 2026-06-11 (REFUTES the interaction)

**Setup:** V7 ended 2026-06-02 (confirmed: zero exposures after 06-02 in `core_dev.statsig.exposures`); ABF3 v6 OTT still running → clean V7-free window **06-03→06-10**. Re-measured ABF3's effect with V7 present (P1=05-29→06-02) vs absent (P2=06-03→06-10), on-title ToT, CUPED (same 05-07→05-20 pre). **Platform falsification cut** (device_id platform-specific → Roku/non-Roku disjoint): non-Roku = where V7 operated (expect TVT cost to shrink if V7 caused it); Roku = placebo (V7 never present either period). Periods defined independently (no first-exposure cohorting). Notebook `/Users/bpulikkal@tubi.tv/ABF_3/abf_v6_prepost_v7` (run 2026-06-11, output `__run_2026-06-11_OUTPUT`).

**Per-period ABF3 TVT effect (on-title ToT, CUPED):**

| Platform | P1 V7-on | P2 V7-off | DiD (P2−P1), p | Revenue P1→P2 |
|---|---|---|---|---|
| all-OTT | −0.32% (p=.005) | −0.53% (p=.004) | +0.01%, p=.60 | +5.75%→+5.40% |
| **non-Roku** (V7 lived) | −0.60% | −0.76% | **−0.01%, p=.97** | +4.75%→+5.03% |
| **Roku** (placebo) | +0.01% | −0.19% | −0.15%, p=.58 | +6.96%→+5.98% |

n/arm well-powered (all-OTT 3.34M/1.68M; non-Roku 1.78M/0.97M; Roku 1.56M/0.71M). P1 all-OTT −0.32% reproduces the v6 headline −0.33% (pipeline ties out).

**ITT robustness (all-titles, same platform split, randomization-preserving — ToT conditions on a post-randomization watch outcome; ITT doesn't):** identical verdict. non-Roku TVT −0.32%→−0.36%, **DiD +0.05% p=0.75**; Roku +0.01%→−0.05%, DiD p=0.78; all-OTT DiD +0.01% p=0.94. Refutation holds under BOTH estimands. ITT also confirms the revenue softening is general drift not V7: revenue DiD significantly negative on *all three* platforms incl. Roku (non-Roku −0.44% p=.003, Roku −0.55% p=7e-5) — V7 never touched Roku, so this can't be V7.

**Result — NO V7 interaction; ABF3's TVT cost is standalone & platform-driven:**
1. Removing V7 from the platforms where it operated (non-Roku) left ABF3's TVT cost **unchanged** (−0.60%→−0.76%, DiD p=0.97). CI [−0.50%,+0.48%] **rules out** the originally-hypothesized −1.3% to −1.6% interaction. The interaction prediction was tested directly at power and failed.
2. The original "dose gradient" was **platform heterogeneity**, not a V7 dose: Roku stays flat / non-Roku stays negative *with V7 entirely gone* — matching the known platform split (web −0.17%, OTT −0.33%, mobile −0.90%). The 2026-06-10 analysis anchored on Roku as "zero V7" and mistook a platform contrast for a V7 contrast (the confound its own caveats flagged).
3. ABF3 **does** carry a genuine standalone TVT cost (−0.53% all-OTT, −0.76% non-Roku, flat Roku) — the −0.33% headline is real, not inflated by V7.
4. Mild P1→P2 softening (both metrics, *all* platforms incl. Roku) = runtime/seasonality drift, not V7.

**Bottom line:** no detectable ABF3×V7 interaction. ABF3's small TVT cost is intrinsic & platform-varying, unchanged by V7. The graduation trade (≈+2.2% global rev for small TVT cost) **does not depend on V7's status** (stays valid whether V7 is retired or re-run). Density pruning remains a *possible* lever to reduce TVT cost on high-cost platforms (mobile/non-Roku), not a requirement to neutralize an interaction (there is none).

**Report:** [ABF3 v6 (OTT) × V7 — TVT & Revenue Interaction Analysis](https://docs.google.com/document/d/1j_BAgDJPTwph44A9SpERrUIzq4jU8Tby4WFAYvl1kkc/edit) — Drive ID `1j_BAgDJPTwph44A9SpERrUIzq4jU8Tby4WFAYvl1kkc`. Local source: `ABF3_v6_OTT_x_V7_interaction_report.md` (Key Takeaways reflect the 06-11 reversal; §1–§5 historical; §6 = post-V7 follow-up).

---

### Experiment: ABF3 v7 — Stronger Pruning to Eliminate TVT Cost (Active)

**Reports (Google Docs, pageless/wide, folder `0AE3wRIsB2WnhUk9PVA`):**
- Cross-platform (mechanism + all-platform topline): [v7 — Results, Mechanism & Graduation Read](https://docs.google.com/document/d/1gPBeoOh6PDBq8wMWIJdqA5Gc3tkIwHRrZCBfV5s445I/edit) — `1gPBeoOh6PDBq8wMWIJdqA5Gc3tkIwHRrZCBfV5s445I`. Source `/tmp/abf_v7_report.md`, state `memory/abf_v7_report.docid`.
- Per-platform (v6-style, generated by `/tmp/abf_v7_{ott,mobile,web}_report.md`): **OTT** `1Nwi5-Vrqd76DoEXHy7t3-LowYxxBuBKAQetRel6IMNE` · **Mobile** `1IrMG8eS-BMxI3FlRevcpGIX41lAUGw3N8pRkHtLVlFw` · **Web** `1taIUps7KU9pZwrLuUViJqliO93Uf1f8wKm62R4GiECw`. State files `memory/abf_v7_{ott,mobile,web}_report.docid`.

> ⚠️ **Naming note — two different "V7"s.** Elsewhere in this file "V7" refers to the *concurrent ad-load experiment* `dynamic_ads_tolerance_mtml_device_xgboost_session` (Bing Wang) that overlapped v6 OTT — see the §"v6 OTT × V7 interaction" section. That experiment is **unrelated** to the ABF3 **v7** described here. "ABF3 v7" / `ads_*_abf_3_v7` = the next version of *our* ABF3 experiment (the successor to v6). Keep them distinct.

**Timeline:** v6 experiments (all platforms) **ended 2026-06-15**. ABF3 **v7 launched 2026-06-16** (all three platforms same day) as the successor, on the **same set of content_ids** as v6 (the 1,084 ABF1 titles). All three **still running** as of 2026-06-23.

**Experiment names:** `ads_abf_3_v7` (OTT), `ads_web_abf_3_v7` (Web), `ads_mobile_abf_3_v7` (Mobile).

**Only change from v6:** an **even stronger pruner**. v6 pruned ABF3 cue points down to ABF2 density; v7 prunes ABF3 cue points **further** (fewer cue points than v6) specifically to **remove the small TVT hit** observed in v6.

**Motivation:** v6's TVT cost was small but real and platform-varying (OTT −0.33%, mobile −0.90%, web flat). The 06-11 follow-up confirmed this cost is **standalone and intrinsic to ABF3's higher ad-break density** (not a V7-interaction artifact), so reducing density via stronger pruning is the natural lever to neutralize it.

**Goal / success criterion:** **neutral TVT** while **retaining a meaningful revenue lift**. The bet is that ABF3's revenue advantage over ABF1 survives the extra pruning even as ad-break density drops closer to (or below) ABF2 — i.e. capture most of the revenue upside at zero engagement cost.

**Open / to confirm:**
- The new pruner's target density (how much lower than v6 / vs ABF1 baseline) — not documented; inferred from realized density below.

#### v7 Early Results — 2026-06-23 (6 days, window 06-17→06-22, all complete days)

Run via the v6 notebooks copied to `ads_abf_3_v7__*` (parameterized — same `core_dev.dsa.temp_bp_abf_v6_exp_titles` 1,084-title set, unchanged for v7). **CUPED pre-window = `2026-05-07 → 2026-05-20`** — deliberately moved back from the v6 default (05-15→05-28) because that window is contaminated by v5 (05-22→05-25) and v6 (05-27→06-14). 05-07→05-20 is verified **completely free of all ABF exposures** (after v4 ended 05-06, before v5 launched 05-22) — same clean window the v6×V7 interaction notebooks used. v7 exposure ranges (from `core_dev.statsig.exposures`): all three platforms 06-17→06-22.

**Headline (device-level, ToT, ABF3-titles-only, CUPED) — v7 vs v6:**

| Platform | v7 Revenue | v7 TVT | v7 density Δ | v6 Revenue | v6 TVT | v6 density Δ |
|---|---|---|---|---|---|---|
| OTT (`ads_abf_3_v7`) | **+3.53%** [3.26,3.80] sig | **−0.33%** [−0.59,−0.07] **sig** | +4.3% (15.32→15.97/hr) | +5.67% | −0.33% sig | +6.98% |
| Mobile (`ads_mobile_abf_3_v7`) | **+6.04%** [5.12,6.95] sig | **−0.85%** [−1.57,−0.14] **sig** | +9.4% (6.86→7.50/hr) | +6.89% | −0.90% sig | n/a |
| Web (`ads_web_abf_3_v7`) | **+4.96%** [2.71,7.21] sig | **+0.79%** [−0.99,2.56] ns | +3.2% (7.77→8.02/hr) | +8.95% | −0.17% ns | n/a |

(Raw Welch and CUPED agree closely, as in v6. ITT all-titles cuts: OTT rev +0.35% / TVT +0.02% ns; mobile rev +0.39% / TVT −0.11% ns; web rev −0.42% ns / TVT −0.66% ns.)

**Result — the v7 premise is NOT supported by the early read:** the stronger pruner lowered the excess ad-break density (OTT +4.3% vs v6 +6.98%) and, as a mechanical side effect, **shrank the revenue lift** (OTT +5.67%→+3.53%, web +8.95%→+4.96%) — but the **TVT cost did not improve**: OTT unchanged at −0.33% (still sig), mobile −0.85% (still sig, ≈ v6's −0.90%), web flat (as in v6). On the platforms that had a TVT cost, v7 **gave up revenue without buying back engagement**.
- This challenges the v6-era assumption that the TVT cost is purely a quantity/ad-load effect. If it were, lower density should have reduced it. Either the cost has a non-density component, or the residual density excess (still +3–9% hotter than ABF1 control — the pruner reduced but didn't eliminate it; mobile still +9.4% and kept the biggest TVT cost) is enough to sustain it.
- Caveats: only 6 days (matched to the v6 reads compared against, so fair, but early — v6 lifts moderated over runtime); density still runs hotter than control on every platform; full graduation suite (representativeness/heterogeneity/title-generalization/global-projection) NOT yet run for v7.
- **Tentative takeaway:** stronger pruning looks like a net-negative trade so far (less revenue, same TVT cost), not the hoped-for "neutral TVT, meaningful revenue." Confirm with more runtime + full suite before concluding.

#### v7 Full Graduation Suite — 2026-06-23 (v6-parity, same window 06-17→06-22, clean pre/baseline 05-07→05-20)

Ran the full v6 suite for all three platforms: `representativeness`, `lift_heterogeneity`, `title_generalization`, `global_graduation_projection` (notebooks copied to `ads_abf_3_v7__*`, parameterized identically to v6; platform scoping OTT→`PLATFORM_TYPE=ALL` (matches v6), mobile→`MOBILE`, web→`WEB`). Baseline/share/weight windows all set to the clean **05-07→05-20** (v6 default 05-15→05-28 is contaminated by v5+v6 on these exact titles, which would bias the topline shares and per-title TVT weights).

**Global graduation projection (the headline graduation number) — v7 vs v6:**

| Platform | ABF1 rev share | ABF1-wide rev lift | **Global rev lift** | Global TVT (dilution → spillover) | v6 global rev |
|---|---|---|---|---|---|
| OTT (ALL) | 37.03% | +3.68% | **+1.36%** | −0.09% → +0.04% (≈flat) | ~+2.2% |
| Mobile | 40.06% | +6.15% | **+2.46%** | −0.43% → −0.61% | +3.19% |
| Web | 41.67% | +4.45% | **+1.86%** | +0.13% → −3.14% | +4.68% |

**Title generalization (revenue, title-clustered bootstrap CI):**

| Platform | TVT-weighted lift | Projected (full ABF1) | Title-clustered 95% CI | v6 CI |
|---|---|---|---|---|
| OTT | +2.08% | +2.29% | **[−0.03%, +3.97%]** (touches 0) | [+6.1, +8.5] |
| Mobile | +5.78% | +7.10% | [+4.51%, +7.11%] | [+5.22, +8.49] |
| Web | +3.92% | +5.32% | [+1.87%, +5.97%] | [+6.96, +10.53] |

**Representativeness:** unchanged from v6 (same 1,084 titles). Experiment titles carry ~40% of platform ABF1 TVT; raw per-title density skews high (mean 7.44 vs universe 2.80) but TVT-weighted is close (≈9.9 vs 7.5) — same "zero-TVT long tail" story as v6. Sample remains a valid random draw for generalization.

**Heterogeneity:** revenue lift still positive across most ABF1-density deciles and both content types, but **uniformly lower than v6** at every cut (consistent with the smaller overall lift). TVT flat-to-negative across cuts as before.

**Suite conclusion — v7 generalizes, but to a smaller prize and without fixing TVT:**
- Graduation trade by platform is now: **OTT ~+1.4% global rev / ≈flat TVT; mobile ~+2.5% global rev / −0.4 to −0.6% TVT; web ~+1.9% global rev / flat-to-negative TVT.** Every revenue number is below its v6 counterpart (OTT 2.2→1.4, mobile 3.2→2.5, web 4.7→1.9).
- **⚠️ OTT title-clustered CI "touches zero" — SUPERSEDED/RESOLVED later on 2026-06-24 (see the §"COHERENT TITLE-CLUSTERED CI" subsection below): it was a BROKEN-ESTIMATOR ARTIFACT, not real generalization risk. The corrected coherent CI is [+2.91%, +4.79%], comfortably clears zero. The text in this bullet + the next is kept for history but is NO LONGER the conclusion.** (Original now-wrong reasoning: "touches zero [−0.03,+3.97], method validated on v6, REAL not a bug, driven by smaller lift + wider per-title SD." The flaw: the original `title_generalization` bootstrap resampled NOISY small-sample per-title %lifts; pooling within decile before each title votes halves the SD and lifts the band off zero. The v6 re-validation reproduced v6's *original* CI but didn't catch that the original METHOD itself over-disperses — v6 stayed positive regardless, so it masked the bug.)
- **IMPORTANT — two different CIs, don't conflate (clarified 2026-06-24):** (1) **Topline global revenue lift = +1.36% [+1.13%, +1.59%]** is DEVICE-level CI from `global_graduation_projection` — **comfortably significant**, THE reported topline. (2) The **title-clustered CI** is a SEPARATE *generalization* measure (title as unit). **Its CORRECT value is the coherent [+2.91%, +4.79%] (clears zero), NOT the original [−0.03,+3.97].** The on-title device-level lift (+3.53%, p≈1e-133) is unambiguously significant. **Bottom line after this session: BOTH the topline AND the generalization are comfortably positive on OTT — the earlier "OTT generalization at risk / touches zero" flag is RETRACTED.**
- **ABF1-wide rev lift (+3.68% OTT) derivation (traced 2026-06-24):** = Σ_decile(decile_rev_lift × decile_revenue_share_in_full_ABF1_universe) / Σ weights — revenue-weighted avg of per-decile experiment lifts. Then global = +3.68% × ABF1 rev share 37.03% = **+1.36%** (arithmetic verified). NOTE: global-projection notebook uses 0-indexed deciles with different cut points than the heterogeneity notebook's 1–10 — decile numbers don't line up 1:1 between notebooks, but aggregate is robust. Revenue-weighted (+3.68%) > TVT-weighted (+2.08%) because high-lift mid-density deciles carry more revenue than TVT weight.
- **Net (CORRECTED 2026-06-24 with significance test — supersedes both "strictly worse" AND "suggestive not established" wording):** On-title revenue fell on every platform; on-title ToT TVT did NOT improve where it existed (OTT −0.33% both). BUT the **global topline TVT improvement on OTT is REAL and statistically significant** — it lives in the *spillover* (cross-title, total-watch-time) channel, not the on-title channel. CUPED-vs-CUPED ITT all-titles TVT: **OTT v6 −0.173% (sig, p=0.005) → v7 +0.016% (ns); v6→v7 difference +0.19pp, SIGNIFICANT p=0.033.** So v6's −0.4% global TVT (spillover-driven) is genuinely brought to ~flat by v7's lighter ad load. **Per-platform verdict:** OTT — v7 is a *confirmed* revenue-for-TVT trade (+1.4% rev / ~flat global TVT vs v6 +2.2% / −0.4%). MOBILE — v6 spillover was never significant (−0.137%, p=0.33; v6→v7 diff p=0.91 ns), real cost is on-title −0.85% which v7 didn't fix → **v6 dominates**. WEB — noisy both versions (v6 −0.185% ns, v7 −0.662% ns, diff p=0.41) → **v6 dominates**.
  - **Method note (important):** earlier I wrongly called the OTT spillover difference "within noise" by comparing RAW v7 vs CUPED v6 (apples-to-oranges). The correct CUPED-vs-CUPED test is significant (p=0.033). CUPED is the right tool for BOTH (legitimate variance reduction, doesn't change point estimate). v6 mobile/web global-TVT figures in the v6 reports (−0.34→−0.70% mobile) used the global-projection notebook's raw ITT (−0.27%); the CUPED ITT for v6 mobile is −0.137% (ns) — the mobile spillover was never robust.

**Run outputs (archived HTML, 2026-06-23):** all 18 v7 runs (6 headline + 12 suite) saved as `…__run_2026-06-23_OUTPUT` in `/Users/bpulikkal@tubi.tv/ABF_3/`. Headline notebooks `ads_abf_3_v7__{metrics_stat_sig,cuped_stat_sig}` (single param'd notebook run per platform, archived with `__OTT`/`mobile`/`web` prefixes). Density via ad-hoc SQL (non-empty ad breaks per TVT hr, ToT, ABF3 titles only). **Reports:** 4 Google Docs published (cross-platform + OTT/mobile/web), links in the §"Reports" block above. **Validation reruns (2026-06-24):** v6 OTT/mobile/web `cuped_stat_sig` re-run for clean CUPED ITT all-titles TVT (v6 OTT −0.173% p=0.005; mobile −0.137% p=0.33; web −0.185% p=0.61); v6 OTT `title_generalization` re-run reproduced published CI [+6.07,+8.46] (method validated). Local helper SQL: `/tmp/itt_all_tvt.sql` (param'd v6/v7 ITT all-titles TVT). Per-platform v7 report sources: `/tmp/abf_v7_{ott,mobile,web}_report.md` (generated programmatically from suite JSON — see generator logic if regenerating).

#### THE THREE "PROJECT-TO-ALL-ABF1" NUMBERS — reconciliation (pinned 2026-06-24)

There are **three** distinct "lift on ABF1 titles" numbers, from **two notebooks** with **two different decile weightings**, and they get confused constantly. This is the canonical reconciliation (figures = v7 OTT).

**The revenue funnel (three stages — the headline path):**

| Stage | Number (v7 OTT) | Weighting | What it means |
|---|---|---|---|
| 1. On-title (MEASURED) | **+3.53%** | device-pooled | Lift on the 1,084 experiment titles, ToT, ABF3-titles-only. Not a projection. |
| 2. ABF1-wide | **+3.68%** | **REVENUE** | Per-decile lifts reweighted to the full ABF1 universe's **revenue** mix. "If each density decile's measured rev lift applied to all ABF1 titles in that decile, weighted by revenue dollars at stake → +3.68%." |
| 3. Global (topline) | **+1.36%** [+1.13,+1.59] | × 37.03% | Stage 2 diluted by ABF1's share of TOTAL business revenue. **THE reported topline.** Device-level CI. |

So **+3.68% = the revenue-weighted ABF1-wide lift**, the middle stage feeding the +1.36% topline. Source: `global_graduation_projection` notebook, block (D). global = 3.68% × 37.03% = +1.36% (verified).

**The fourth-ish number — +2.29% — is the SAME stage 2, but TVT-weighted, from a DIFFERENT notebook:**

| | `global_graduation_projection` | `title_generalization` |
|---|---|---|
| ABF1-wide projected lift | **+3.68%** | **+2.29%** (and raw sample +2.08%) |
| Decile weighting | **revenue** share in universe | **TVT** share in universe |
| CI | device-level, on the *global* [+1.13,+1.59] | title-bootstrap [−0.03,+3.97] |

**Why 3.68% (rev-wtd) > 2.29% (TVT-wtd) — the weighting divergence:** v7's lift concentrates in **mid-density deciles (2–5) that carry more REVENUE weight than TVT weight**, while the **densest decile 8 is TVT-heavy but revenue-NEGATIVE (−3.58%)** (the over-prune, see next section). Revenue-weighting leans on the strong mid deciles → higher (3.68%); TVT-weighting gives decile 8 more pull → lower (2.29%). In v6 these two nearly coincided (broad uniform lift, ~+7.0% both) — the divergence is NEW in v7 and is a symptom of the dense-decile sign flip.

**Which is "the" ABF1-wide lift?** For a **revenue** projection, **+3.68% (revenue-weighted) is methodologically correct** — you weight a revenue projection by revenue — and it's what feeds the +1.36% topline. **+2.29% (TVT-weighted) is the conservative GENERALIZATION-ROBUSTNESS lens**, lower precisely because it over-weights the dense titles where v7 is worst; it's the basis for the title-clustered CI that touches zero.

**Two known method caveats in `title_generalization` (flagged 2026-06-24):**
1. The reported "+2.29%, CI [−0.03,+3.97]" **staples a CI built around the +2.08% raw-sample estimate onto the +2.29% poststratified point** — the bootstrap does NOT re-poststratify inside each iteration, so strictly the CI belongs to +2.08%, not +2.29% (they're ~0.2pp apart so roughly compatible, but not a proper interval for the projection). A coherent fix = poststratify inside each bootstrap iteration.
2. The title-bootstrap resamples ONLY the 1,084 exp titles as exchangeable draws from an assumed population — it's blind to (a) systematic differences in the ~492K unmeasured titles and (b) the fact that exp titles already cover 50–59% of dense-decile universe revenue. (b) means it likely **OVERSTATES** ordinary sampling risk (no finite-population correction); (a) could understate it. The CI's validity rests entirely on the "1,084 are a representative random draw" assumption (which the `representativeness` notebook supports, modulo the known density skew).

**Generalization framing (corrected — NOT "worst-case draw"):** at full rollout there is no random draw — the catalog is fixed and all ABF1 titles serve all users. The true full-catalog lift is a **fixed unknown number**; we estimate it from the 1,084-title sample. The title-clustered CI is the **epistemic imprecision of that estimate** (how far our sample-based projection could be from the true population value), NOT the chance of a bad random outcome. "Touches zero" = our estimate is imprecise enough that the true OTT value *could* be near flat — driven by dispersion in the over-pruned dense titles. Within-decile coverage (≥20%, dense ~50–59%) suggests the bootstrap is on the conservative side.

#### Revenue-weighted title-clustered CI (consistency fix) — 2026-06-24

> **⚠️ THIS SUBSECTION IS AN INTERMEDIATE STEP — its conclusion ("touches-zero is ROBUST / flag stands") is SUPERSEDED by the next subsection ("COHERENT TITLE-CLUSTERED CI"). The revenue-weighted bootstrap here was itself partly broken (corrupted by pre-launch-weighted/in-experiment-empty −100% junk titles). Final answer: the touches-zero was an ESTIMATOR ARTIFACT; coherent CI = [+2.91,+4.79], clears zero. Read this subsection only for the diagnostic trail.**

**Motivation:** `title_generalization` computes the title-clustered CI **TVT-weighted**, but the topline revenue projection is **revenue-weighted** — inconsistent currency for the same revenue estimand (harmless in v6 where the two weightings agreed; surfaced in v7 via the dense-decile sign flip). Re-ran the title bootstrap with **weight = pre-launch per-title revenue** (and a poststratify-inside-bootstrap variant that reweights per-decile to the universe revenue mix on every resample, so the CI properly belongs to the projected point). Notebook `/Users/bpulikkal@tubi.tv/ABF_3/abf_v7_revwt_titleboot` (local `abf_v7_revwt_titleboot.py`), run for v7 + v6 OTT, 2000 iters, seed 12345.

| | v7 OTT | v6 OTT |
|---|---|---|
| TVT-weighted (original) | +2.08%, CI [−0.03, +3.97] | +7.27%, CI [+6.07, +8.46] |
| **Revenue-weighted** | **+1.165%, CI [−1.12, +3.22]** | +6.74%, CI [+5.42, +8.04] |
| Poststratify-inside (rev) | +1.178%, CI [−0.91, +3.03] | +6.45%, CI [+5.42, +7.49] |

**Result — the touches-zero generalization flag is ROBUST, and revenue-weighting makes it WORSE not better (my prior prediction that it would clear zero was WRONG):** under the consistent revenue currency, v7 OTT's lower bound drops from −0.03% → **−1.12%** (poststratified −0.91%). So OTT generalization risk is real under both weightings; the TVT-weighted version was if anything *understating* it. **v6 stays comfortably positive under every weighting** — the v6≫v7 generalization contrast is rock-solid.

**PUZZLE — two "revenue-weighted ABF1-wide" numbers disagreed by 2.5pp — RESOLVED 2026-06-24: the title-level +1.165% is a BUGGY estimator; the topline +3.68% is sound. My earlier "headline might be flattered" worry is RETRACTED.** Diagnosis (notebook `abf_v7_estimator_gap`):
- The title-level revenue-weighted estimator weights each title by its **pre-launch** revenue but takes the lift from the **in-experiment** sample. These decouple: 380/1021 titles have negative per-title lift holding 47.9% of pre-launch rev-weight, and the top rev-weight titles are dominated by **exactly −100% lifts** — e.g. content 712894 (decile 7, **$133K pre-launch rev**, the single largest weight) but in-experiment has ~13 devices/arm, **0 watch-min, ~$0.00–0.03 rev in BOTH arms** → mean_rev_Test=0, mean_rev_Control=a few cents → lift −100%, carrying the full $133K weight on pure noise. Same for 589292/695535/550826/625256. So huge pre-launch weight × near-empty in-experiment signal = garbage −100% contributions. Per-decile proof: decile 7 device-pooled −3.64% vs title-rev-wtd −8.70%; decile 5 pooled +4.68% vs title-rev-wtd −3.07% — the gaps are entirely these junk titles.
- **The global notebook (+3.68%) does NOT have this bug:** it weights by **device-pooled sums within the experiment window**, so a near-empty title contributes ~zero weight — weight and signal come from the same data. SOUND estimator. The +1.165% is NOT a valid "more conservative" read; it's mis-weighted (pre-launch weight × in-experiment noise). The decile-smoothed topline is correct, not optimistic.
- **Consequence for the CIs:** the **revenue-weighted** title CI [−1.12,+3.22] is partly junk-inflated (those −100% titles resampled with huge weight depress the lower bound) → DISCOUNT it. The **TVT-weighted** CI [−0.03,+3.97] does NOT have this problem (a near-zero-watch title has ~0 TVT weight → junk titles get ~0 weight), so it remains the **cleaner generalization read** — and its touching-zero is driven by the GENUINE −3.58% dense decile, not attribution artifacts. **Net: generalization-risk flag on OTT stands (real dense-decile dispersion), but the revenue-weighted CI overstated the downside.**
- **Latent bug to fix in `title_generalization`/`revwt_titleboot`:** title weights should come from the SAME window/data as the lift (or drop titles with ~0 in-experiment exposure), else pre-launch-heavy/in-experiment-empty titles inject −100% noise. TVT-weighted version is largely immune. (Global notebook already correct.)

Run outputs not archived (cheap to re-run; `abf_v7_estimator_gap.py` + results in run JSON / this note).

**COHERENT TITLE-CLUSTERED CI — FIX + RESULT (2026-06-24): v7 OTT generalization CLEARS ZERO; the "touches zero" was a broken-estimator artifact.** The original `title_generalization` bootstrap resamples **per-title %lifts** (each from a possibly-tiny device sample) weighted by TVT → high-variance/near-empty titles inject noise → bootstrap SD ~1.0 → band touched zero. FIX (notebook `abf_v7_coherent_titleci`): bootstrap the **actual topline estimator** — on each resample recompute **device-POOLED** decile lifts, then re-aggregate with fixed **universe-revenue** decile weights. Device-pooling means weight = in-experiment device count, so near-empty titles auto-contribute ~0 (no filter hack) and the junk −100% titles can't distort it.

| | v7 OTT | v6 OTT |
|---|---|---|
| Coherent ABF1-wide point | **+3.86%** (ties out w/ global notebook +3.68%) | +6.09% (cf +6.02%) |
| **Coherent title-clustered CI** | **[+2.91%, +4.79%]** (CLEARS 0) | [+5.28%, +6.87%] |
| bootstrap SD | 0.49 (vs original ~1.0) | 0.41 |
| Robustness: ≥100 dev/arm, window-matched control-rev wt | +2.99%, [+1.67, +4.31] | +5.84%, [+4.91, +6.83] |

**Verdict (supersedes the "OTT generalization touches zero / at risk" flag from earlier 2026-06-24 entries):** bootstrap SD halves (1.0→0.49) once per-title noise is pooled within decile before the title votes. v7 OTT ABF1-wide rev generalization CI = **[+2.91%, +4.79%]** (robustness [+1.67,+4.31]) — **comfortably positive, clears zero under both the coherent and the explicit-min-exposure methods.** The −3.58% dense decile is REAL but a modest, well-measured drag that universe-revenue weighting correctly down-weights; it does NOT threaten the ABF1-wide lift. **Three worries from this session collapse as estimator artifacts: (1) title-CI touches zero, (2) "headline +1.36% might be flattered", (3) revenue-weighted CI downside [−1.12,+3.22]. All were artifacts of resampling noisy per-title lifts / mismatched pre-launch-vs-in-experiment weights. The +1.36% global OTT topline is SOUND and GENERALIZES.** v6 > v7 on magnitude (+6.09 vs +3.86 ABF1-wide) as expected, both now clean positive CIs.

**`title_generalization` notebook should be updated** to use the coherent (device-pooled-decile, poststratified) bootstrap as its CI of record — the published TVT-weighted per-title bootstrap CI ([−0.03,+3.97] v7, [+6.07,+8.46] v6) overstates dispersion (v6 stayed positive so it didn't matter there; v7 it spuriously touched zero). Notebook `abf_v7_coherent_titleci.py`.

**Coherent CI — all three platforms (2026-06-24):** ran `abf_v7_coherent_titleci` for mobile (`PLATFORM_TYPE=MOBILE`) and web (`WEB`) too (universe-rev weights platform-scoped like the global notebook; in-experiment lift rides off per-exp exposures so needs no platform filter). Coherent title-clustered CIs, all clear zero:

| Platform | Coherent ABF1-wide pt (≈global) | Coherent title CI | Robustness (≥100 dev/arm) | Superseded per-title CI |
|---|---|---|---|---|
| OTT | +3.86% (≈+3.68) | **[+2.91, +4.79]** | +2.99% [+1.67,+4.31] | [−0.03,+3.97] |
| Mobile | +6.64% (≈+6.15) | **[+5.46, +7.87]** | +4.55% [+3.16,+5.94] | [+4.51,+7.11] |
| Web | +4.35% (≈+4.45) | **[+2.83, +5.95]** | +0.95% [−0.84,+2.92] | [+1.87,+5.97] |

(Web's stricter ≥100-dev robustness cut straddles zero — small device base drops many titles under a hard filter; the coherent CI down-weights rather than drops, and is the better read.)

**REPORTS UPDATED & REPUBLISHED 2026-06-24** with the coherent CIs (stable links unchanged — `publish_native_doc.py` updated-in-place via the `memory/abf_v7_*.docid` state files): cross-platform `1gPBeoOh6PDBq8wMWIJdqA5Gc3tkIwHRrZCBfV5s445I` (§2a + Appendix B), OTT `1Nwi5-Vrqd76DoEXHy7t3-LowYxxBuBKAQetRel6IMNE` (TL;DR + §2b), mobile `1IrMG8eS-BMxI3FlRevcpGIX41lAUGw3N8pRkHtLVlFw`, web `1taIUps7KU9pZwrLuUViJqliO93Uf1f8wKm62R4GiECw`. Source md in `/tmp/abf_v7_{report,ott_report,mobile_report,web_report}.md`. Earlier per-title figures retained in each report as explicitly-labeled "superseded".

**Dual-basis topline (added to each per-platform §2b, 2026-06-24):** the generalization (ABF1-wide) coherent CI diluted by ABF1 rev share gives a topline CI on the **title-clustered** basis, directly comparable to the official **device-level** topline in §2c. Two decompositions of uncertainty on the same ~point (NOT to be combined): device-level holds titles fixed/varies device noise; title-clustered varies the title draw then dilutes.

| Platform | Topline device-level (§2c, official) | Topline title-clustered basis (§2b, = ABF1-wide × share) |
|---|---|---|
| OTT | +1.36% [+1.13, +1.59] | +1.43% [+1.08, +1.77] |
| Mobile | +2.46% [+1.47, +3.46] | +2.66% [+2.19, +3.15] |
| Web | +1.86% **[−0.50, +4.22]** (crosses 0) | +1.81% **[+1.18, +2.48]** (positive) |

OTT/mobile agree closely across both lenses. **Web's device-level topline crosses zero only because its device base is small (noisy dilution) — NOT a generalization problem; on the title-clustered (catalog) basis web is clearly positive.**

#### v7 OTT — per-decile concentration of the global lift + densest-decile sign flip — 2026-06-24

**Why run it:** worry that the +1.36% global lift might be (a) fragile — riding on 1–2 lucky deciles — or (b) structurally concentrated away from TVT-heavy titles. Decomposed the global lift into per-decile contributions `lift_d × abf1_universe_rev_d` and added a within-decile coverage check (# exp titles + exp share of that decile's universe revenue). Notebook `/Users/bpulikkal@tubi.tv/ABF_3/abf_v7_decile_concentration` (local `abf_v7_decile_concentration.py`), run for both v7 (default widgets) and v6 (params via `/tmp/v6params.json`). `qcut` collapses to **9 deciles** (0–8) on tied density values.

**Method correction (important):** the global-projection notebook builds the global CI as a **LINEAR sum of per-decile bounds** (`Σ rev_lo_d × rev_d / total_rev`), NOT a quadrature sum of variances — i.e. it treats deciles as perfectly correlated (conservative/wider). Reproduced the published +1.36% [+1.13,+1.59] exactly from the per-decile table.

**Fragility worry — RESOLVED (lift is broad, not concentrated):** 8/9 deciles positive, every CI excludes 0. Positive lift spread across four mid-density deciles (2–5), each highly significant; no single decile is >26% of the lift numerator (top = decile 2 at 25.7%). Drop the single best decile → global still ~+1.01%; drop top 3 → still ~+0.40% positive. **Within-decile coverage is strong everywhere** (≥20% of each decile's universe revenue; dense deciles ~50–59%), so the wide title-clustered CI is genuine cross-decile *dispersion*, NOT thin sampling.

**Structural worry — CONFIRMED + MECHANISM FOUND: v7 over-prunes the densest decile BELOW control.** The densest ABF1 decile (decile 8, 14.7% of ABF1 revenue — the single largest weight) is significantly **NEGATIVE in v7: −3.58% [−4.19,−2.98]**, dragging global by −0.19pp. **It was POSITIVE in v6: +2.17% [+1.73,+2.61], +0.11pp.** Same titles, same baseline window — the only change is the stronger pruner. This single decile's sign flip ≈ −0.30pp of the v6→v7 global gap (2.18%→1.36%).

| Decile 8 (densest) | v6 | v7 |
|---|---|---|
| Rev lift | +2.17% (sig +) | **−3.58% (sig −)** |
| ABF1 rev weight | 14.4% | 14.7% |
| Contribution to global | +0.11pp | **−0.19pp** |

**Direct cause verified (raw served cue-point counts — `size(split(cue_points_abf))` v7 vs `size(split(cue_points))` ABF1 control, exp titles; NOTE this is RAW cue-point candidates, not realized ad breaks). Deciles are cut on CONTROL (ABF1) density.** Across all 1,084 titles, **106 (9.8%)** have v7-served ABF3 RAW cue points BELOW their ABF1 control (movies 12.8% / series 6.0%; overall mean still above, 8.32 vs 7.44). **The below-control titles concentrate in the top TWO control-density deciles** (verified cross-tab, `/tmp/below_by_decile.sql`):

| Decile | Control range (cue pts) | n titles | n below ctrl | % of decile below | % of all 106 |
|---|---|---|---|---|---|
| 0–6 | 1–9 | 660 | 17 | ≤8% (noise) | 16% |
| **7** | **10–12** | 256 | **41** | **16.0%** | 38.7% |
| **8** | **13–36** | 88 | **48** | **54.5%** | 45.3% |

So over-pruning below control is a **dense-control phenomenon, threshold ≈ control ≥10 cue pts (top two deciles 7+8 = 89/106 = 84%)** — NOT solely the single densest decile (earlier "localized to decile 8" was an overstatement). On decile 8 specifically, v7 prunes to ~13.6 cue pts vs control ~16.6. The gradient matches revenue exactly: decile 8 (54.5% below) → rev **−3.58%**; decile 7 (16% below) → **+2.55%** (weakest positive); deciles 2–6 (≤6% below) → **+4.7–7.7%** (strong). This is the **v4 over-pruning artifact re-emerging on dense-control titles**; v6's lighter (ABF2-density, ~9.9 mean) prune stayed at/above control even on dense titles → decile 8 **+2.17%**. (v6 raw served counts NOT recoverable — overwritten at v7 launch, past 7-day time-travel horizon; inference rests on the positive v6 revenue sign + lighter mean.)

**Constructive implication + VALIDITY GAP (clarified 2026-06-24):** v7's OTT weakness (title-CI touching zero, lower global lift) is NOT intrinsic to ABF3 — it's an **avoidable over-prune** on dense-control titles. A pruner with a per-title floor (`served cue points ≥ ABF1 control`, never prune below baseline) is the candidate fix (distinct from "prune harder", which the flat dose-response ruled out — this is "prune *with a floor*"). BUT the fix splits into a SAFE part and an UNVALIDATED part, and the experiment as run does NOT measure the shipped configuration:
- **Floor to EXACTLY control (clamp the 106 below-control titles up to = control):** those titles then serve identical cue points to control → **~0% lift and ~0 TVT effect by construction** (no contrast). Removes the −0.19pp decile-8 drag → OTT global **+1.36% → ~+1.55%**. This part generalizes safely (it's a no-op on those titles, no extrapolation).
- **Serve ABOVE control to recover v6's dense-decile upside (decile 8 +2.17%):** v7 NEVER measured this — v7's only dense-decile data point is the *below-control* (−3.58%) one. Recovering the positive lift relies on v6 extrapolation (different runtime window; v6 served set now unrecoverable). This is the **generalization risk**: the measured +1.36% is partly an artifact of over-pruning we'd remove, so projecting a *floored* pruner onto all ABF1 titles (decile 8 = 14.7% of ABF1 revenue) is a MODEL, not a measurement. Also the flat global TVT is partly propped by decile 8's +0.46% TVT bonus (an under-serving artifact) — flooring removes it; v6 says TVT stays ~neutral (+0.06%) at control density but that too is v6, not measured here.
- **Resolution:** don't graduate a revenue number from a configuration you intend to change. If the dense-title upside matters (it does at 14.7% of ABF1 rev), warrants a short **v8 arm that actually serves the floored pruner** and re-measures deciles 7–8 directly. Safe fallback = floor-to-control (~+1.55%, low risk).

Local SQL `/tmp/decile_density.sql`, `/tmp/below_control.sql`, `/tmp/below_by_decile.sql`; concentration outputs in the v7/v6 run JSON.

#### v7 — Raw Cue-Point Density (v6 vs v7) — 2026-06-23

Direct measure of what the pruner did (the per-hour break number is gated by ad config; raw cue-point count is not). Source: `cue_points` (ABF1 baseline, control) vs `cue_points_abf` (pruned ABF3, treatment) in `content_movie_stream`/`content_episode_stream`, over the 1,084 exp titles.

| Version | Raw pruned ABF3 (mean cue pts/title) | vs ABF1 baseline (7.44) |
|---|---|---|
| v6 | **~9.9** (inferred) | ~+33% |
| v7 | **8.32** (confirmed, stable 06-18→06-23) | **+11.7%** |

- v7 confirmed via Delta time-travel (stable 8.315 across 06-18..06-23). ABF1 baseline = 7.44 (matches durable `temp_bp_abf1_universe`).
- **v6 NOT directly recoverable:** the pruned set lives only in the live `cue_points_abf` snapshot; v7 overwrote it on launch (06-16), and Delta `deletedFileRetentionDuration` is **168h (7 days)** — all of v6's window (05-27→06-14) is past the horizon. The ~9.9 is **inferred** from a transitional time-travel snapshot (06-17 00:00 read 9.89 mid-rollout, settled to 8.32 by 06-18) — treat as approximate.
- **Durable-record gap to fix going forward:** no table snapshots per-experiment pruned cue-point counts at launch. Future versions should write the served pruned set to a durable table so v-over-v raw density is recoverable.

#### v7 — Correctness Verification & Counterintuitive-Result Diagnosis — 2026-06-23

**Context / the puzzle:** v7 has *less* ad load than v6 (realized break excess OTT +6.98%→+4.27%, mobile +12.16%→+9.40%, web +10.91%→+3.16%) and *less* revenue/impressions — yet TVT did **not** improve vs v6 (OTT −0.33% both; mobile −0.90%→−0.85%). Expectation was: less ad load → TVT recovery. Did not happen.

**Correctness checks — all PASS (analysis is sound):**
- **ITT SRM:** test share OTT 0.4997 (chi2 p=.012, fine at scale), mobile 0.5001, web 0.5002. Clean.
- **ToT set balance (the main worry):** qualification rate (watched ≥1 ABF3 title) near-identical across arms — OTT 26.52% vs 26.53%, mobile 22.48% vs 22.52%, web 11.39% vs 11.32%. No post-randomization selection bias.
- **v6→v7 carryover:** v7 re-randomized independent of v6 (arm crosstab ~even, ~3.90M/cell). v7 on-title TVT cost is identical across v6-history strata: v6=Control −0.36%, v6=Test −0.43%, **v6=never-exposed −0.54%**. TVT cost is intrinsic, not carryover.
- **Cross-experiment device overlap:** the 3 experiments are mutually exclusive at device level (web×mobile 84, web×OTT 7, mobile×OTT 106 — negligible).

**⚠️ ONE DATA-QUALITY ISSUE FOUND — web cross-platform leakage (OTT & mobile are clean):**
- The lift notebooks count ALL watching by exposed devices (no platform filter — relied on "device_id is platform-specific"). True for OTT (574 stray) and mobile (190 stray), but **NOT web**: ~82K web-experiment devices watch mostly on **FIRETABLET (69K) / ANDROID_SAMSUNG (13K)** = `platform_type=MOBILE`. ~11% of web on-title TVT (34.3K of 310.7K hrs) is non-web surface.
- **Corrected web headline (restrict to `platform_type='WEB'` / `platform='web'`):** TVT **+0.80%→+1.57%**, revenue +4.60%→+4.77% (ToT, on-title, raw). Removing the mobile-surface sessions makes web TVT *more* positive — strengthens web as the most favorable platform; does not change overall v7-vs-v6 story.
- **TODO (not yet done):** re-run the **full web suite** (metrics/CUPED/global/title-gen/heterogeneity/representativeness) with the platform filter to lock in corrected web numbers of record. OTT & mobile need no change.

**Mechanism diagnosis (per-watch-hour decomposition, v7 OTT, ToT, on-title):**
- `total rev +3.49% = rev/hour +3.94% × TVT −0.43%`; `rev/hour +3.94% ≈ ad-load (imps/hr) +4.27% × CPM −0.31%`. Identity ties out (imps/hr% + TVT% ≈ total imps%).
- **Revenue lift is still ~entirely ad-load-driven (CPM flat).** v7 still runs hotter than ABF1 control (+4.27% breaks/hr), just less than v6. So: revenue scales ~linearly with ad load (cutting load cut revenue, as expected), but **TVT cost did NOT scale down with ad load** — the engagement hit is not a simple per-hour dose response in this range. Likely a **placement/timing** or **presence-vs-frequency** effect that stronger pruning of *count* doesn't fix.

**TVT DOSE-RESPONSE — COMPLETED 2026-06-23 (decisive: pruning is NOT the TVT lever):**
Within-platform (v6→v7, only pruning level changed), matched 6-day ToT on-title; density = Test-vs-Control breaks/hr excess, web TVT platform-corrected:

| Platform | Density excess v6→v7 | TVT cost v6→v7 | Slope (ΔTVT/ΔDensity) |
|---|---|---|---|
| OTT | +7.0%→+4.3% (−2.7pp) | −0.33%→−0.40% | **+0.03 (~zero)** |
| Mobile | +12.2%→+9.4% (−2.8pp) | −1.08%→−0.99% | **−0.03 (~zero)** |
| Web | +10.9%→+3.2% (−7.7pp) | +0.57%→+1.57% | −0.13 |

- **Verdict: flat dose-response.** Cutting density ~23–40% of excess on the two TVT-cost platforms moved TVT by ~nothing (within noise). If the cost were ad-quantity-driven, slopes would be strongly positive. They aren't.
- **Implications:** (1) "prune harder" (a v8) will NOT neutralize TVT — strictly dominated by v6 (less revenue, no TVT gain). (2) TVT cost tracks **platform** (mobile −1.0% / OTT −0.3% / web positive), not ad load — same platform heterogeneity the 06-11 V7-interaction analysis found, now robust to a large density change. (3) **The lever is placement/timing, not count.** Stop tuning density; next experiment should target break *positioning* (ABF3's original claimed advantage).

**REALIZED-BREAK PLACEMENT + TITLE-LEVEL TVT — COMPLETED 2026-06-23 (answers "why lower load didn't help TVT"):**
Notebook `/Users/bpulikkal@tubi.tv/ABF_3/abf_v7_placement` (run `v7_placement`, 2026-06-23). Scope **OTT + US** (`ads_abf_3_v7`, 06-17→06-22). Unit = `video_session_id` (NOT device×content — separates viewings across days). Breaks = realized *filled* ad pods from `impressions` (empty breaks invisible by construction — fine, fill balanced across arms), mapped to sessions by `parent_ts BETWEEN start_ts AND end_ts` (90.6% map 1:1). Pre-rolls (`now_pos<5`) excluded; placement metrics on **seek-free sessions only** (`seek_total_count=0`; seek corrupts now_pos — verified 22× more non-monotonic gaps). `now_pos` = realized break position in content-seconds. Pre-checks clean: seek rate balanced (C 9.57% / T 9.55% — ABF3 doesn't induce seeking), pre-roll share & pod fill balanced.

**Analysis A — extra ABF3 load hits MIDDLE/LATE breaks, NOT early ones:**
- By break ordinal (Test−Control): 1st +0.5%, 2nd −1.6% (early breaks ≈IDENTICAL) → surplus appears at **5th +19%, 6th +26%** and beyond (deep in session).
- By content fraction: first decile (0–10%) Test −52% (FEWER early breaks); Test surplus in **40–60% mid-session** (+11–16%).
- First mid-roll position ≈ identical (SERIES 726 vs 725s; MOVIE 1054 vs 981s) — the ad-config `initial-ad-slot` gate (900s movie / ~420s series) binds the first break identically in both arms, so **ABF3 cannot front-load the damaging first break**. Its denser candidates only fill *more late slots* that sparse ABF1 leaves empty → extra ads land on already-committed deep viewers (low marginal TVT damage).

**Analysis B — TVT hit is BROADLY SPREAD (movies), not a fixable subset:**
- Per-title agg lift −0.10%; **518/987 titles (52%) negative** carrying 58% of control TVT. Worst-100 titles = −0.26pp but total only −0.10pp (other ~887 net +0.16pp offset) — diffuse, not a defective cluster.
- **Entire hit is MOVIES (−0.24%); SERIES flat-positive (+0.02%).** Sparsest-ABF1 tercile positive (+0.07%); mid/high negative (−0.22%/−0.18%). Consistent with A: movies have the long mid/late section where ABF3 packs late breaks; series too short for late surplus.

**ANSWER to "why lower load didn't improve TVT": v7 cut the WRONG load.** The abandonment-driving *early* breaks are ad-config-gated → identical in both arms, untouchable by pruning. ABF3's surplus (and everything pruning removed) lives in *late mid-session breaks on long movies*, where marginal TVT cost is low. So pruning trimmed cheap late ads (lost revenue) without touching the gated early breaks (the real engagement lever) → exactly the flat dose-response. Residual cost is diffuse across movies, not a removable subset.
**Implication: neither pruning nor title-exclusion fixes TVT. The lever is the early-break experience on MOVIES — which is config-gated → an AD-CONFIG question (initial-ad-slot / early-session pod policy), not a cue-point question.**

Note: `ad_config.json` (project root) refreshed 2026-06-23 — OTT+US, base `initial-ad-slot=900s`, `min-time-between-breaks=720s` (movies); episodes ~420s/600s; floors 360s. Config is OTT+US only → placement analysis scoped to OTT+US.

**CORRECTED EARLY-BREAK + CADENCE ANALYSIS — 2026-06-23 (fixes ordinal survivorship bias):**
The earlier "by break ordinal" cut had survivorship bias (only long sessions have a 6th break). Redone as **non-empty breaks within first X content-minutes** (fixed position windows) + **realized inter-break gaps**. Notebook `/Users/bpulikkal@tubi.tv/ABF_3/abf_v7_early_breaks` (run `v7_early_breaks`, OTT+US, seek-free sessions, `now_pos`). Thresholds MOVIE 8/15/25/30/45/60min, SERIES 5/10/15/25/35/45min.

**Breaks within first X min (Test−Control, conditional on reaching X):**
- MOVIE: first **8 min IDENTICAL** (0.62 vs 0.62 — the 900s/15min `initial-ad-slot` gate binds both arms equally), then ABF3 **+10–15% more breaks at every horizon ≥15min** (60min: 4.22 vs 3.83).
- SERIES: ABF3 first break slightly earlier (+11% by 5min) but **converges/crosses** — −2.3% by 45min. Net ~neutral.

**Realized inter-break gap (median) — THE mechanism:**
- **MOVIE: ABF1 907s (~15.1min) vs ABF3 809s (~13.5min)** — ABF3 fires ~100s sooner between *every* break, steady across all break-pairs (1→2 through 5→6: ABF3 ~810s flat vs ABF1 ~915–928s).
- SERIES: realized breaks ~equal/slightly fewer for ABF3 (0.0615 vs 0.0627 brk/min; 2.14 vs 2.19 breaks/session) despite ABF3 having MORE raw candidates (4.55 vs 4.15 cp/title). NOT ABF3 spacing series out on purpose — episodes are too short (~40min) for cadence to differ: both arms realize ~2 breaks gated by config (~600s min-spacing, ~420s initial), and realized count then turns on placement-vs-gate alignment (small-numbers/gating noise), so series TVT is flat. The earlier "ABF3 looser on series" wording was misleading — it's a gating artifact in short content, not a real spacing-out.
- First mid-roll ≈ equal (MOVIE 1054 vs 981s, SERIES 726 vs 725s) — confirms NO front-loading.
- Raw candidates (both denser for ABF3): MOVIE 11.35 vs 10.1 cp; SERIES 4.55 vs 4.15 cp. Movies' long runtime is what lets ABF3's extra candidates become a sustained tighter realized cadence; series have no room for it.

**Refined mechanism (supersedes the earlier "late-break" framing):** The differentiator is **NOT the first break** (config-gated identical) but a **sustained tighter, more regular cadence on MOVIES** — ABF3 runs ~13.5min spacing vs ABF1's ~15.1min through the whole body of long movies (~10% more breaks). Series get *looser*, not tighter. This maps exactly onto the title-level TVT split (hit entirely MOVIES −0.24%, series flat-positive +0.02%). v7's pruning cut break *count* but left ABF3's movie cadence ~100s tighter than ABF1 — a structural rhythm difference (ABF3 density × ad-config `min-time-between-breaks` floor, in long-form) that pruning at this level didn't neutralize. **Lever = movie inter-break spacing policy (raise effective min-time-between-breaks for ABF3 on movies), an ad-config interaction — not cue-point count.**

**HAZARD + SURVIVAL + POST-BREAK DROP-OFF — 2026-06-23 (connects packing→TVT, pinpoints mechanism):**
Notebook `/Users/bpulikkal@tubi.tv/ABF_3/abf_v7_hazard_survival` (run 412540094068291, OTT+US). Scope: seek-free **fresh-start** sessions (have a pre-roll, now_pos<5 → now_pos = content-min-from-start = same axis as TVT, which is content-only). Fresh-start share balanced for MOVIE (54.2% C / 54.5% T); SERIES 36.8/40.8 (4pp gap, minor). Hazard(m)=breaks in content-min m / sessions at-risk at m; Survival(m)=frac still watching at m (TVT=area under).

**MOVIES — survival gap is real & accumulates (the −0.24% TVT hit visualized):** Test survival runs below Control from ~min 15, widening monotonically: −0.17pp@15min → −0.30pp@30 → −0.33pp@60 → −0.35pp@75. First break identical (min 1–15 ≈ equal hazard); Test hazard excess in the body (min 25/40/60).
**SERIES — survival BETTER for Test** (+0.1 to +0.4pp through min 40) — corroborates flat-positive series TVT; no extra ad burden (config-gated ~2 breaks).

**POST-BREAK DROP-OFF — ⚠️ INITIAL FINDING RETRACTED (was an artifact), corrected below.**
- FIRST (WRONG) read: "MOVIE 0–10min break Test 26.3% vs Control 21.5% quit (+4.77pp); ABF3 fires first break at 196s vs 358s." **This was an artifact.** The `now_pos BETWEEN 5 AND 600` slice was polluted by sub-360s records that are NOT real early mid-rolls — they're replays/seek-backs (same device, same content, low playhead, breaks 12–23min apart in wall-clock). The 360s `initial-ad-slot` floor DOES hold for both arms (now_pos histogram: near-empty 1–359s ~90k pods, mid-rolls bulk at 360s+). Stakeholder (correctly) flagged: initial-ad-slot is identical across arms and forbids breaks <360s — so "3.3min" was impossible.
- **CORRECTED (mid-rolls ≥360s only, fresh-start seek-free MOVIE):**
  - First mid-roll: Control median 1018s (~17.0min) vs Test 952s (~15.9min) — ABF3 ~1min earlier (real but small; both respect 360s floor, zero violations).
  - Post-break drop-off (P quit within 120s): **Test ≤ Control at EVERY position** — 6–15m −0.88pp, 15–25m +0.15pp, 25–35m −0.15pp, 35–50m −0.11pp, 50m+ −0.57pp. **No position where ABF3 breaks are more abandonment-triggering.**

**CORRECTED FINAL MECHANISM:** The movie TVT hit is NOT from worse-placed or earlier-triggering breaks — no single ABF3 break is more abandonment-triggering than ABF1 (drop-off ≤ control everywhere). It's from **cumulative break COUNT**: among movie viewers reaching the same depth, ABF3 serves more breaks, each ~equally tolerable, but more of them → steady survival bleed (−0.17pp@15min → −0.35pp@75min). Series: ABF3 not denser (config-gated ~2 breaks), survival ≥ control → no hit.

**TENSION RESOLVED 2026-06-23 — cumulative movie break count v6 vs v7 (conditional on reaching depth, ≥360s, fresh-start seek-free OTT+US MOVIE):**

| | 30min: Ctrl(ABF1) | Test(ABF3) | excess | 60min: Ctrl | Test | excess |
|---|---|---|---|---|---|---|
| v6 (6d matched) | 1.318 | 1.622 | **+23.1%** | 3.342 | 3.858 | **+15.5%** |
| v7 | 1.300 | 1.536 | **+18.1%** | 3.331 | 3.754 | **+12.7%** |

Pruning DID lower v7's movie break count (excess +23%→+18% @30min, +15.5%→+12.7% @60min) — yet OTT TVT stayed −0.33%→−0.33%. **Conclusion: per-break movie TVT cost is genuinely tiny; −0.24% movie hit is near the noise floor.** Cutting ~5pp of movie-break excess recovered NO measurable TVT. → reconciliation #2 confirmed (not "pruning didn't go far enough").

**PROGRAM CONCLUSION (mechanism hunt converged):** (1) ABF3's movie TVT cost is real but tiny & count-driven — each extra break nearly free in TVT. (2) **Pruning is a poor lever** — cuts revenue ~linearly (each removed break = lost impression) but recovers ~nothing in TVT (confirmed at movie level, not just aggregate). (3) **No "bad placement" to fix** — the +4.8pp early-break effect was an artifact; no worse-per-break abandonment anywhere; so no ad-config repositioning recovers TVT while keeping revenue. A break either exists (earns revenue, costs a sliver of TVT) or not (neither). **The revenue/TVT trade is a genuine frontier — can't engineer "revenue lift at zero TVT cost." Graduation = a me_score weighting choice of WHERE on the frontier (v6 level vs v7 level), not a mechanism to engineer away.** v6 and v7 are two frontier points: v6 = more revenue + small TVT cost; v7 = less revenue + smaller/flat TVT cost (on OTT topline). On **mobile/web v6 dominates** (v7 loses revenue for no significant TVT gain); on **OTT** v7 is a **CONFIRMED** revenue-for-engagement trade — the global-TVT improvement is statistically significant (CUPED-vs-CUPED v6→v7 spillover diff p=0.033; see the 2026-06-24 CORRECTED net above, which supersedes any earlier "unconfirmed/noisy" wording). A harder-pruned v8 is NOT worth pursuing (flat dose-response → more revenue lost for negligible TVT). Final v6-vs-v7 call = the me_score/e_score gate (not yet computed). v7 = 6-day read; confirm with more runtime.

**QUEUED FOLLOW-UP ANALYSES:**
2. **(SUPERSEDED — done above) Break-position diagnostic:** time-to-first-break, inter-break gaps, early clustering — v7 Test vs Control. Served positions recoverable now from live `cue_points_abf`. Tests "placement not count."
3. **Drop-off/retention around breaks:** abandonment at first break; survival by % content elapsed.
4. **Segment cuts:** new vs returning, light vs heavy (v6=none devices showed largest cost −0.54%).
5. **Completion-rate vs raw TVT:** distinguishes abandonment from shorter sessions.
- Optional/known-TODO: web platform-filter suite re-run (above).

#### SESSION-END STATUS — 2026-06-24 (resume here)

**What this session did (generalization-CI deep dive + report refresh):**
1. Decomposed the +1.36% OTT global lift per density-decile → broad/robust (8/9 deciles +, no decile >26%), BUT the **densest decile (decile 8 / control ≥13 cue pts) is sig NEGATIVE −3.58%** in v7 (was +2.17% in v6). Cause VERIFIED: v7's stronger pruner serves the densest titles BELOW their ABF1 control (decile 8: 13.6 vs 16.6 cue pts; 54.5% of titles below control; 106/1084 = 9.8% below control overall, concentrated in top-2 control deciles 7+8). v6's lighter prune stayed at/above control → positive. Fix candidate = "prune WITH a per-title floor (serve ≥ control)" — distinct from "prune harder" (ruled out). NOTE the floor fix is UNVALIDATED (v7 never served it) → would need a v8 arm; safe fallback = floor-to-control ≈ no-op on those titles → OTT global +1.36%→~+1.55%.
2. **BIG RESULT: the "OTT title-clustered CI touches zero" flag was a BROKEN-ESTIMATOR ARTIFACT — RETRACTED.** Original `title_generalization` bootstrapped noisy small-sample per-title %lifts (and a revenue-weighted variant was corrupted by pre-launch-weighted/in-experiment-empty −100% junk titles, e.g. content 712894 $133K pre-launch rev but ~0 in-experiment). FIX = bootstrap the actual topline estimator (device-pooled decile lifts → universe-revenue poststratification); near-empty titles auto-get ~0 weight. Coherent CIs all CLEAR ZERO: **OTT [+2.91,+4.79], Mobile [+5.46,+7.87], Web [+2.83,+5.95]**. Applying the fix to v6 leaves v6 unchanged ([+5.28,+6.87]) → principled, not result-shopping.
3. Reports REFRESHED & republished in place (stable links) with coherent CIs + a dual-basis topline row (device-level vs title-clustered-diluted) in each per-platform §2b.

**CURRENT HEADLINE NUMBERS (v7, 6-day read 06-17→06-22):** ⚠️ Web/Mobile SUPERSEDED by the 8-day refresh (06-17→06-24) in the §"v7 Web + Mobile — 8-day refresh" section below — web topline confirmed NOT significant at 8 days. OTT unchanged (not re-run). Table kept for history.
| Platform | Topline global rev (device CI) | Generalization ABF1-wide (coherent title CI) | Global TVT |
|---|---|---|---|
| OTT | +1.36% [+1.13,+1.59] | +3.86% [+2.91,+4.79] | ~flat (sig improvement vs v6 −0.4%) |
| Mobile | +2.46% [+1.47,+3.46] | +6.64% [+5.46,+7.87] | −0.4 to −0.6% (v6 dominates) |
| Web | +1.86% [−0.50,+4.22]* | +4.35% [+2.83,+5.95] | flat/noisy (v6 dominates) |

*Web topline device CI crosses zero only due to small device base; on title-clustered basis it's +1.81% [+1.18,+2.48], clearly positive.

**OPEN / NEXT (priority order):**
1. **`me_score`/`e_score` (offline) — THE formal graduation gate, still NOT computed.** This is the decision metric for the v6-vs-v7 frontier call. Highest-priority open item across all versions.
2. **Web platform-filter suite re-run** (known data-quality TODO — ~11% of web on-title TVT is mobile-surface FIRETABLET/ANDROID_SAMSUNG; corrected raw web TVT +0.80%→+1.57%). OTT/mobile clean.
3. **More v7 runtime** — all reads are 6-day; v6 lifts moderated over time. Confirm v7 holds at 10–14 days.
4. **(Optional) v8 with a floored pruner** — only if the dense-decile upside (decile 8) matters enough to measure; otherwise floor-to-control is the safe conservative ship.
5. Queued mechanism follow-ups #3–5 above (drop-off/retention, segment cuts, completion-rate vs TVT) — lower priority, mechanism already converged.

**Decision frame (unchanged):** v6 vs v7 = a me_score weighting choice of WHERE on the revenue/TVT frontier. v6 = more rev + small TVT cost; v7 = less rev + smaller/flat TVT (OTT). On mobile/web v6 dominates; on OTT v7 is a confirmed revenue-for-TVT trade. Pruning is a poor lever (flat dose-response); the real TVT lever is movie early-break/cadence ad-config, not cue-point count.

**Notebooks added this session (in `/Users/bpulikkal@tubi.tv/ABF_3/`, local .py in project root):** `abf_v7_decile_concentration`, `abf_v7_estimator_gap`, `abf_v7_coherent_titleci` (the CI-of-record generator — param'd by PLATFORM_TYPE; run for v6+v7 OTT/mobile/web). Local SQL: `/tmp/decile_density.sql`, `/tmp/below_control.sql`, `/tmp/below_by_decile.sql`, `/tmp/check_neg.sql`.

#### v7 Web + Mobile — 8-day refresh (06-17→06-24) — 2026-06-25

**Why:** review comments (Dylan, on Aryan's "ABF 3.0 v7 — Decision Brief") flagged that the **web global revenue was being stated as "+1.9% trade" despite a device-level CI that crosses zero**. Re-ran web + mobile `global_graduation_projection` and `cuped_stat_sig` with 2 extra complete days (06-23, 06-24 — v7 launched 06-16; 06-24 confirmed complete: video_session/impressions have 06-25 partial) to see if the larger sample makes web statsig. Clean pre-window unchanged (05-07→05-20). OTT not re-run this pass (already significant at 6 days).

**Verdict: the extra 2 days did NOT rescue web — web topline revenue still crosses zero, point estimate drifted DOWN. Mobile stays clean & significant. The "+1.9% global web revenue" framing was overstated and is corrected below.**

**Full 8-day matrix (CUPED, ToT & ITT, on-title [ABF3-only] & all-titles, + device-level global topline):**

| Cut | Web Revenue | Web TVT | Mobile Revenue | Mobile TVT |
|---|---|---|---|---|
| On-title ToT | **+3.46%** [+1.42,+5.50] p=9e-4 ✅ | +0.08% [−1.57,+1.72] p=.93 flat | **+6.04%** [+5.21,+6.88] p≈1e-45 ✅ | **−0.70%** [−1.37,−0.03] p=.042 ✅sig− |
| On-title ITT | +3.72% [+1.65,+5.79] p=4e-4 ✅ | −0.08% [−1.86,+1.71] p=.93 flat | +6.21% [+5.33,+7.09] p≈2e-43 ✅ | −0.51% [−1.23,+0.22] p=.17 ns |
| All-titles ToT | −0.12% [−1.52,+1.28] p=.87 | −1.23% [−2.39,−0.07] p=.038 ⚠️noisy ToT | +0.58% [+0.06,+1.10] p=.029 ✅ | −0.30% [−0.74,+0.14] p=.18 ns |
| All-titles ITT (spillover input) | −0.36% [−1.27,+0.55] p=.44 | −0.65% [−1.50,+0.20] p=.13 ns | +0.30% [−0.07,+0.67] p=.11 | −0.14% [−0.46,+0.18] p=.40 ns |
| **Global (topline, device-level)** | **+1.38% [−0.74,+3.51]** ❌ crosses 0 | m1 +0.01% / m2 −2.98% (noisy) | **+2.42% [+1.53,+3.31]** ✅ | m1 −0.39% / m2 −0.63% |

n (8-day): web ToT 187K/arm, ITT 1.64M/arm; mobile ToT 912K/arm, ITT 3.82M/arm.

**Key reads:**
- **WEB topline revenue 6d→8d: +1.86% [−0.50,+4.22] → +1.38% [−0.74,+3.51] — STILL not significant**, and the point moved *down* not up. Web's device base is fundamentally too small to resolve the diluted topline at this allocation; more runtime won't fix a per-day noise problem. On-title web revenue IS solidly significant (+3.46%, p=9e-4) — it's only the *diluted topline* that's underpowered. Web all-titles ITT TVT still ns (−0.65%, p=0.13). (The all-titles ToT TVT −1.23% p=0.038 is a noisy ToT cut — conditions on a post-randomization watch outcome, opposite sign to the cleaner ITT — treat as noise, not a real cost.)
- **MOBILE stays clean & significant:** global rev +2.42% [+1.53,+3.31] (≈ unchanged from 6d +2.46%), on-title rev +6.04%, and a **real on-title TVT cost −0.70% (p=0.042)**. Confirms "mobile = revenue-for-engagement, v6 dominates."
- **Correction to the web report wording:** the TL;DR/§2d trade line stated "+1.9% global web revenue for a TVT effect too noisy to call" — asymmetric: on the device-level (official) topline lens, the **revenue is ALSO not significant**. Web is underpowered on BOTH metrics at the topline. The decision conclusion (v6 > v7 on web, on point estimates) is unchanged; only the significance framing of web revenue is corrected.

**Generalization (coherent title-clustered CI) + heterogeneity, also refreshed to 8 days:**

| | Web 8d | Mobile 8d |
|---|---|---|
| Coherent ABF1-wide rev lift | +3.51% [+2.09,+4.98] | +6.45% [+5.33,+7.53] |
| Topline on title-clustered basis (× ABF1 rev share) | +1.46% [+0.87,+2.07] (positive) | +2.58% [+2.14,+3.02] |
| Robustness (≥100 dev/arm) | +0.42% [−1.24,+2.10] (straddles 0, small base) | +4.57% [+3.38,+5.92] |
| Decile-10 (densest) rev lift | −3.90% [−8.43,+0.63] ns | −3.90% [−5.68,−2.11] sig (over-prune) |
| Content type (rev) | MOVIE +1.20% ns / SERIES +6.37% sig | MOVIE +5.75% sig / SERIES +6.28% sig |

Web coherent CI still clears zero (generalization fine); it's only the **device-level topline** that's underpowered. Mobile clean and positive on every lens. (Coherent CIs ran via `abf_v7_coherent_titleci`, heterogeneity via `ads_abf_3_v7__lift_heterogeneity`, both 8-day.)

**Run outputs:** not archived (cheap to re-run; numbers in this note). Param files `/tmp/web_8d.json`, `/tmp/mobile_8d.json` (END_DS=2026-06-24). Notebooks unchanged (`ads_abf_3_v7__{global_graduation_projection,cuped_stat_sig,lift_heterogeneity}`, `abf_v7_coherent_titleci`, param'd by platform).

**Reports FULLY REWRITTEN to 8-day & republished in place (stable links, 2026-06-25):** Web `1taIUps7KU9pZwrLuUViJqliO93Uf1f8wKm62R4GiECw` and Mobile `1IrMG8eS-BMxI3FlRevcpGIX41lAUGw3N8pRkHtLVlFw` — all sections (headline matrix, heterogeneity, generalization, global projection, conclusion, caveats) now on the 06-17→06-24 window. Sources `/tmp/abf_v7_{web,mobile}_report.md`. Web report states the device-level topline is NOT significant; mobile states it is. Recreated missing docid state files `memory/abf_v7_{web,mobile,report}.docid`. Cross-platform report (`1gPBeoOh...`) web trade-lines also corrected (8-day confirmation noted). **Mobile/web 6-day report figures fully superseded.** OTT report not changed (OTT not re-run this pass).

**CURRENT HEADLINE NUMBERS (UPDATED — OTT 6-day 06-17→06-22; Web/Mobile 8-day 06-17→06-24):**
| Platform | Topline global rev (device CI) | On-title rev (ToT) | Global TVT | Topline rev statsig? |
|---|---|---|---|---|
| OTT | +1.36% [+1.13,+1.59] | +3.53% | ~flat (sig improvement vs v6 −0.4%) | ✅ yes |
| Mobile | +2.42% [+1.53,+3.31] | +6.04% | −0.4 to −0.6% (v6 dominates) | ✅ yes |
| Web | +1.38% [−0.74,+3.51] | +3.46% | flat/noisy (underpowered) | ❌ **no — crosses zero** |

---

### Experiment: ABF3 v8 — Full ABF1 Catalog Rollout Test (Active)

**The scale jump:** unlike v6/v7 (1,084-title random sample), v8 applies ABF3 cue points to the **entire processed ABF1 catalog** — **154,348 titles** (40,434 movies / 113,914 series). This directly tests the graduation projection instead of extrapolating from a sample.

**Experiment names (Statsig, all `device_id`-randomized, 50/50 Control/Test, 100% allocation, planned duration 14 days):**

| Experiment | Platform | Layer | Launched |
|---|---|---|---|
| `ads_abf_3_v8` | OTT (all OTT apps incl. Roku) | `ads_abf3` | 2026-07-23 |
| `ads_mobile_abf_3_v8` | Mobile (iOS, Android) | `ads_abf3_mobile` | 2026-07-23 |
| `ads_web_abf_3_v8` | Web | `ads_abf3_web` | 2026-07-23 |

All three launched 2026-07-23 ~20:00 UTC, all still active as of 2026-08-05 (~13 days in — planned 14-day duration nearly complete).

**Hypothesis (from Statsig):** ABF3 cue points **pruned to match ABF2.0 density** on ABF1 titles → at-par-or-better engagement and revenue. Primary metrics: `revenue_unbudgeted`, `tvt_capped_daily`, `qualified_view_days`.

**Pruning level:** ABF2-density matching = the **v6-level pruner**, NOT v7's stronger pruner — consistent with the v7 finding that stronger pruning is a poor trade (loses revenue, flat TVT dose-response) and that v6 dominates on mobile/web.

**Title/cue-point file:** `abf_batch_20260709_pruned_cuepoints_v1_1.csv` (project root) — all 154,348 processed titles with their pruned ABF3 cue points. Columns: `content_id, content_name, content_type, duration_sec, n_candidates, n_cue_points, cue_points`. **Terminology: `cue_points` = the pruned candidate cue points made ELIGIBLE for the treatment arm** (e.g. The Waterboy 639561: 33 candidates → 11 pruned) — NOT realized ad breaks. Whether a cue point actually fires an ad break depends on ad-config gating (initial-ad-slot, min-time-between-breaks) and pod fill at watch time. Realized break density must be measured from `impressions` as in v6/v7. This snapshot also closes the v6-era durable-record gap (v6's raw pruned set was unrecoverable).

**Pruning distribution (from the CSV, analyzed 2026-08-05):**

| | Overall (154,348) | MOVIE (40,434) | SERIES (113,914) |
|---|---|---|---|
| Mean duration (min) | 44.9 | 82.8 | 31.4 |
| Candidates: mean / median | 16.05 / 13 | 29.90 / 31 | 11.13 / 9 |
| Kept: mean / median | 4.94 / 4 | 9.22 / 10 | 3.42 / 3 |
| Keep ratio (pooled) | 0.308 | 0.308 | 0.307 |
| Kept cue points per hour (mean) | 6.36 | 6.67 | 6.25 |

Keep ratio is remarkably uniform (~31%) across content types and per-title deciles (80% of titles between 0.25–0.38); 4,818 titles keep 0 cue points. Pruned density ≈6.4 cp/hr on both movies and series.

**⚠️ CSV vs the v6/v7 ABF1 universe (`core_dev.dsa.temp_bp_abf1_universe`, 492,024 titles) — NOT the same set (measured 2026-08-05, TVT = 14d pre-launch window 07-09→07-22, total 549M hrs):**

| Set | n titles | % of total TVT |
|---|---|---|
| v8 CSV (treated) | 154,348 | **16.27%** |
| Old ABF1 universe | 492,024 | 35.59% |
| Overlap (in both) | 141,032 | 15.16% |
| **Universe titles NOT in v8** | **350,992** | **20.43%** |
| v8-only (not in universe) | 13,316 | 1.11% |

- **v8 treats less than half of the ABF1 opportunity by TVT** (16.3% of total TVT vs the universe's 35.6%). The 350,992 missing universe titles are NOT just the zero-TVT long tail: 169,663 of them have ABF1 cue points and carry **19.89% of total TVT**, including the highest-TVT ABF1 movies (top misses: 589281, 559066, 694398 — ~2.3–2.6M hrs each, 8–11 ABF1 cue points, no live ABF3). Missing titles skew toward DENSE ABF1 (7–12 cp bands: 12.1% of total TVT missing vs 8.2% included). Confirmed genuinely untreated: only 2,924 of the 350,992 have live `cue_points_abf`.
- **The 13,316 v8-only titles:** 9,634 are older content with ABF1 cue points that the universe table's `has_abf=0` filter excluded (they had ABF2 cue points populated), 3,639 zero-cue-point old titles, 43 new content since June. So v8 slightly extends beyond "pure ABF1" into some previously-ABF2 titles.
- **Only 395 of the 1,084 v6/v7 experiment titles are in the v8 CSV** — 689 of the old experiment titles are untreated in v8.
- Consequence for analysis: v8's ITT is the real global effect *of this batch*, but the batch ≈ 45% of ABF1-universe TVT — the remaining ~20% of total TVT is still-unprocessed upside. Dilution-scaling comparisons vs the v6/v7 projections must use the 16.3% treated-TVT share, not the 36% universe share.

**Dense-title over-prune persists in v8 (NO per-title floor — the v7 open question is answered):** comparing CSV kept cue points vs ABF1 control per title (TVT-weighted ratio v8/control):

| ABF1 band | n titles | mean ABF1 → v8 cp | % titles below control | TVT-wtd density ratio |
|---|---|---|---|---|
| 1–3 | 68,179 | 2.1 → 2.57 | 6.1% | 1.254 |
| 4–6 | 39,717 | 4.75 → 5.49 | 8.4% | 1.212 |
| 7–9 | 20,067 | 8.03 → 9.54 | 6.8% | 1.235 |
| 10–12 | 8,958 | 10.62 → 11.07 | **24.7%** | 1.059 |
| 13+ | 1,430 | 14.55 → 13.96 | **45.9%** | **0.756** |

Sparse/mid bands run ~1.2× control (v6-like, revenue-positive territory); the densest bands are pruned at/below control — same pattern that flipped v7's decile 8 to −3.58% revenue. Mitigating factor: the 13+ band is only ~1.1% of total TVT in v8 (many dense high-TVT titles are in the *missing* set), so the drag is bounded; expect weak/negative lift on 10+ cp titles.

**Supporting table:** `core_dev.dsa.temp_bp_abf_v8_titles` (Databricks) — the 154,348 CSV titles with content_type, duration_sec, n_candidates, n_cue_points.

**Active-catalog view (2026-08-05, via `core_prod.dsa.dsac_content_availability` — daily snapshot of licensing windows per title × country; filter = `ds='2026-08-05' AND country='US' AND window_start<=today AND window_end>=today`):** only 160,498 of the 492,024 June universe titles (33%) are still active in the US — two-thirds churned off catalog. This reframes the "350,992 untreated titles" more favorably: most are expired. The universe × active × treated split (TVT = 14d pre-launch):

| Segment | n titles | % of total TVT |
|---|---|---|
| Active + treated in v8 | 129,253 | 13.61% |
| **Active + untreated (actionable gap)** | **31,245** | **13.13%** |
| Expired + treated in v8 | 11,779 | 1.54% |
| Expired + untreated | 319,747 | 7.30% |

The actionable untreated set is only 31,245 titles but carries nearly as much TVT as everything v8 treated; it skews dense/heavy (10+ cue-pt band: 2,698 titles / 3.44% of TVT; 7–9: 3.0%). Several of the June top-miss movies (589281, 559066, 694398) have since expired. 920 of the 1,084 v6/v7 exp titles remain active.

**CSV of the actionable gap:** `abf1_active_untreated_by_v8_20260805.csv` (project root) — the 31,245 active-untreated titles with `content_id, content_name, content_type, primary_genre, duration_sec, abf1_cue_points, was_v67_exp_title, tvt_hr_14d`, sorted by TVT desc (total 72.1M hrs / 14d). Generator SQL: `/tmp/untreated_active.sql`.

**Slack thread on the coverage gap (2026-08-05, #[C0BBU1T4QM6], `p1785953115919659`):** Raised the gap with Aryan Gupta (who built the v8 title list) and Christian Green. Aryan confirmed ~155K titles processed (~4,800 of them got no cue points — too short for a midroll, hence 4,818 zero-cue-point rows in the CSV). His selection logic (screenshot in thread): **pre-ABF = `cue_points_abf IS NULL OR IN ('{}','{0.0}')` AND `cue_points_info <> 'imported from partner''s metadata'`** on the stream tables, ∪ the v6/v7 experiment ids, with content expiration date > 07/06/26. Christian confirmed 589281 looks ABF1. The 31K active-untreated list was shared in-thread (Google Sheet `1-m2KEVZ2aDpY0OF9ZP9zaZiou4Lek_ed18mkz3Q-vns`).

**Definition reconciliation (2026-08-05):** Aryan's pre-ABF definition differs from the June universe's (`cue_points_abf != '[]'` vs his `('{}','{0.0}')` + his extra partner-metadata exclusion). BUT the gap is NOT a definitional artifact: re-running **Aryan's own filter** on today's data (active US titles, not in v8) still yields **27,540 untreated titles** (25,709 in the June universe; 516 former v6/v7 exp titles; 5,904 movies / 21,636 series; **66.95M hrs 14d TVT = 12.19% of total**). None of the 31,245 are partner-metadata titles (all `partner_meta=0`), so his exclusion doesn't explain it either; 29,166 of the 31,245 have `cue_points_abf` NULL even today (clearly never processed). Why his July run missed them is unresolved — open question with Aryan.
- **Deliverables (project root):** `abf1_missing_from_v8_aryan_def.sql` (the reproducible query — Aryan's pre-ABF condition ∩ active-US-today ∖ v8 titles, with metadata joins) and `abf1_missing_from_v8_aryan_def_20260805.csv` (the 27,540 titles, sorted by 14d TVT desc; cols: content_id, content_name, content_type, primary_genre, duration_sec, abf1_cue_points, was_v67_exp_title, in_june_universe, tvt_hr_14d).

**ROOT CAUSE FOUND (2026-08-06) — stale expiration dates in the `avail_*` policy parse.** Aryan posted a revised selection query ("ABF 3.0 - V8 Cue points", Databricks query `a9607b7f-d7f2-4358-acad-4991e8e42a31`, editor id 2960397307470799) asking us to verify before processing a top-up batch. Verified — **the query is NOT correct**; materialized it to `core_dev.dsa.temp_bp_aryan_v8_rerun` (37,135 rows; 31,820 net-new after removing already-treated) and diagnosed:
- **His expiration filter:** `avail_movies`/`avail_episodes` → regex `date <= MM/dd/yyyy` out of the `policy` text → `MAX(end date) > 07/06/26`. **These parsed dates are stale**: e.g. Here Comes the Boom (522076, 710K hrs/14d) has policy max_end 2020-05-31, Walking Tall 2018-10-31, Joe 2019-12-31 — all dropped as "expired" while being among the most-watched titles on the service. Titles renewed under new deals keep old policy text; `dsac_content_availability` (licensing windows, daily snapshot) is the correct source.
- **Impact on my 27,540 real-gap list:** 25,901 titles (66.5M hrs/14d TVT) are dropped by the stale-expiration filter; 369 more drop via the `tvt_6mo` INNER JOIN (no row in `content_daily_byepisodes_bycountry_byplatform` window); only 1,269 pass.
- **His 31,820 net-new are ~95% dead titles:** only 1,606 are active today per dsac (270K hrs); 30,214 are NOT active (2.7K hrs ≈ zero). Processing his list would add ~30K expired titles and still miss the real 66M-hr gap.
- **This also explains the ORIGINAL July gap — VERIFIED by fingerprint (not just inference):** the screenshot of his July query was only a fragment (no expiration clause visible), but the treated set proves the logic: **all 154,348 treated titles pass the `avail_max` filter with ZERO violations** (131,368 pass via `max_end IS NULL` — no policy dates parse at all; 22,980 via genuine future dates; 0 fail). A clean 0-violation partition across 154K titles is the fingerprint of that exact filter incl. its NULL-passes behavior and the same 07/06 cutoff literal. So July used the same stale-policy logic; renewed long-running high-TVT titles were deterministically excluded, while the long tail (no parseable policy dates → NULL → passes) got in — an inversion where dead metadata gated the best content out.
- **Fix — use `core_prod.content.content_availability.end_ts` for future expiration (bpulikkal's pointer, verified):** `end_ts` IS a real forward-looking contractual window end (522076: active window 2026-07-01→2026-09-01, renewed revshare deal; catalog-wide most end_ts are months-to-years out). Filter: `date='<YYYYMMDD>' AND country='US' AND active=true AND end_ts > '<cutoff>'`, dedupe `MAX(end_ts)` per video_id (grain is per-platform). This preserves Aryan's "expiration > cutoff" semantics with correct data. Alternative: dsac active-window check (what the 27,540 CSV used). **Cross-validation: all 27,539/27,540 gap titles are active with future end_ts in content_availability — two independent sources agree.**
- **⚠️ Two decoy sources found (do NOT use):** (1) `core_dev.dsa.dsac_content_availability` is a DEAD copy frozen ~2024-05 (bpulikkal's spot-check of 522076 there showed "expired 2024-05-31" while the title does 25–30K TVT hrs/DAY — always use `core_prod`); (2) `core_prod.dsa.dsac_content_availability.window_end` rolls forward daily (100% of 361,797 active titles have window_end ≤2d from snapshot) — good for point-in-time active checks only, NEVER a future expiration date. A genuine forward-expiration also exists via Rightsline (`content_info.rightsline_deal_id`) if ever needed.
- Side notes on his query: hardcoded experiment ids = 2,827 raw / 1,407 unique (contains all 1,084 true exp titles + 323 extras); pre-ABF partner-metadata exclusion is commented out in this version (union with exp ids makes it moot for those).

**Current 154,348 treated titles — VALIDITY AUDIT (2026-08-06): all valid, fix is purely additive (nothing to remove/reprocess):**
- The 13,316 v8-only titles (not in June universe): genuinely pre-ABF — `adfinder_status` ~all `completed` (same profile as the 141K overlap); June exclusion was the `'{}'`-vs-`'[]'` format difference in the has_abf check. Only 1.11% of TVT anyway.
- The 4,818 zero-cue-point titles: 4,356 have zero ABF1 control cps too (mean 3.5 min — too short for a midroll; no contrast, harmless). Only 462 titles serve strictly below control (~81K hrs = 0.015% of TVT) — microscopic, ignore.
- 12,548 treated titles expired since launch: valid at selection, earned 4.5M hrs during the exp window (~4.6% of treated TVT) before churning — normal licensing churn, not an error.
- Note for top-up: the 27,540 includes 516 former v6/v7 exp titles that already have ABF3 candidates from earlier runs — fine, but the model needn't re-run on those.

**Continue-vs-restart decision (2026-08-06, recommendation: CONTINUE the same experiment, per Aryan's plan, with guardrails):**
- Restart costs: resets treatment continuity for the 154K (devices reshuffle arms → destroys the cumulative exposure history e_score/me_score needs), and a new XP's CUPED pre-window would sit inside v8 period 1 (contaminated). Restart buys only dashboard legibility + uniform durations.
- Continuing is sound: device randomization is title-independent (unchanged by the add); control devices never saw ABF3 on the 27.5K → clean on-title contrast from add date; carryover measured ≈nil in the v6→v7 transition (effect identical across v6-history strata).
- Guardrails: (1) record exact add timestamp + snapshot the 27.5K served cue points to a durable table; (2) analysis in windows — A = 07-23→add (154K read), B = add+14d (full-set + fresh-cohort reads), same clean pre-window 07-09→07-22 for both; (3) never quote Statsig dashboard across the add boundary (blends configs) — graduation numbers from windowed offline analysis; (4) re-verify carryover as a fresh-vs-long-exposed cut on the 27.5K read.
- **Why Window A (current 14d data) still matters even if Window B is the decision window:** (1) the ONLY at-scale test of the v6/v7 decile-projection machinery (154K measured vs projected — validates every projection-based number incl. future remainder projections); (2) answers the dense-band question NOW (no pruner floor → v7 decile-8 −3.58% pattern should recur) in time to fix the pruner BEFORE the 27.5K top-up ships, so Window B measures a debugged config; (3) baseline that makes B interpretable (spillover from the add, time-stability/moderation for me_score, novelty-effect control); (4) still contributes to the graduation estimate — cleanest read = 154K-cohort pooled A+B + 27.5K-cohort from B, TVT-weighted (B-only is simpler presentation, not better estimate); (5) e_score needs cumulative exposure duration — A is where 84% of treated TVT accrues history; (6) free SRM/density/platform sanity checks before committing 3 more weeks.
- Restart trigger (would flip the call): stakeholders demand dashboard-readable graduation numbers, or the top-up slips by weeks.

**Thread update (2026-08-06 afternoon):** Root-cause + `content.content_availability.end_ts` fix + "add the 27K, continue same XP" posted to the thread (bpulikkal). Christian offered to backfill; **Aryan will run ABF on the top-up titles over the weekend, delivering Mon/Tue (Aug 10–11)**. Aryan then posted a THIRD query (Databricks `15c0ed73-a32e-4b4f-ad3a-ddd246a99bed`, "New Query 2026-08-06 14:05:51") — now using `content.content_availability` correctly + a NEW Gemini-processed exclusion (`bpm_processes` AbfMediavisionPipeline COMPLETED × `product_ai_ad_breakfinder.ad_breaks` non-empty = his dedup vs already-processed) — and gets **39,644**, asking why still higher than our 27,540.

**RECONCILIATION of 39,644 vs 27,540 (2026-08-06, materialized his query to `core_dev.dsa.temp_bp_aryan_v8_rerun2`):** overlap = 26,279; every diff title classified (TVT = 14d 07-09→07-22):

| Bucket | n | 14d TVT | Verdict |
|---|---|---|---|
| ARYAN-ONLY: rotating-window titles — ca-US-active (end_ts→2027) but dsac window closed ~08-01 | 2,871 | **41.2M hrs** | **INCLUDE — my miss.** The original top-misses live here (Furious 7 3.2M, Madea Goes to Jail, Norbit, Central Intelligence, Dumb and Dumber…). Big-studio titles on monthly rotating windows; off TODAY (589281: TVT 50K hrs 08-01 → 2.6K 08-04 as window closed) but licensed to 2027 and will rotate back on. My point-in-time (active-on-08-05) check wrongly drops them; cue points don't expire — process them. |
| ARYAN-ONLY: partner-metadata pre-ABF titles (dsac-US-active) | 3,726 | 2.8M hrs | Judgment call — his new query COMMENTS OUT the partner-meta exclusion (July's had it active). These have curated partner-imported cue points, no ML. Flag to Aryan: intentional? |
| ARYAN-ONLY: dead/foreign (no US-active row anywhere; 5,684 no ca row at all, 949 foreign-only) | 6,633 | 0.34M hrs | **EXCLUDE — his remaining bug:** his `avail_max` has NO `country='US' AND active=true` filter (just `MAX(end_ts)` per video across all countries/rows). Fix: add both predicates. |
| MINE-ONLY: excluded by his Gemini filter but NOT in the v8 experiment | 888 | **21.6M hrs** | **CRITICAL — must not be dropped.** Already Gemini-processed (ad_breaks ready) but never added to the XP (not in the v8 CSV/table). Correct handling: skip PROCESSING, but ADD to the experiment. His query conflates "needs processing" with "needs adding" — as written these 21.6M hrs silently fall through. |
| MINE-ONLY: dropped by his `tvt_6mo` INNER JOIN | 369 | 0.16M hrs | Minor: active titles with no TVT in his 6-mo window; should still process (LEFT JOIN or drop the join). |

- **Net correct top-up ≈** 26,279 (agreed) + 2,871 (rotating) + 888 (gemini-ready, add-only) [+ 3,726 partner-meta if intended] ≈ **30.0–33.8K titles**; the two "lists" to keep distinct: PROCESSING list (excludes the 888) vs EXPERIMENT-ADD list (includes them).
- **Row-level deliverable:** `abf1_v8_topup_reconciliation_20260806.csv` (project root) — all 40,766 titles in (mine ∪ his net-new), one row each with `bucket` label (`AGREED_both_lists` / `ARYAN_ONLY_rotating_window_INCLUDE` / `MINE_ONLY_gemini_ready_ADD_NO_PROCESS` / `ARYAN_ONLY_partner_metadata_DECIDE` / `ARYAN_ONLY_dead_or_foreign_EXCLUDE` / `MINE_ONLY_dropped_by_tvt_join_INCLUDE`) + flags (gemini_processed, partner_metadata_cps, us_license_end_dt, active_on_20260805, tvt_hr_14d), sorted by TVT desc. Generator: `/tmp/buckets_csv.sql`. Bucket totals tie out exactly to the reconciliation table above.
- **Lesson on availability filters:** point-in-time dsac check (mine) misses rotating-window titles that are off *today*; end_ts check (his) includes dead/foreign without `country+active`. Right recipe for the top-up: `content.content_availability` with `country='US' AND active=true AND end_ts > cutoff` (captures rotating titles) — NOT active-today.

**⚠️ v8 PRUNER DENSITY vs ABF2 — RUNS ~20% BELOW TARGET (2026-08-07, recovered from unwrapped session):** The Statsig hypothesis says v8 cue points are "pruned to match ABF 2.0 density," but a direct benchmark says otherwise. ABF2 benchmark set = 265,004 titles with live ML cue points, not v8-treated, not in the June universe; both sides restricted to >5 min duration, same normalization:

| | ABF2 (265,004) | v8 pruned (151,463) | delta |
|---|---|---|---|
| Mean cp/hr | 8.20 | 6.48 | **−21%** |
| Median cp/hr | 8.24 | 6.66 | −19% |
| TVT-weighted cp/hr | 8.02 | 6.68 | **−17%** |
| MOVIE mean | 8.52 | 6.67 | −22% |
| EPISODE mean | 8.14 | 6.42 | −21% |

**Conclusion: v8's pruning is more aggressive than v6 — closer to (possibly beyond) v7-level, NOT the claimed ABF2 match.** Implications: (a) expect v8's revenue lift nearer v7's +1.36% global than v6's +2.2%; (b) explains the dense-band over-pruning severity (13+ band TVT-wtd ratio 0.756); (c) **the ask to Aryan becomes TWO pruning-parameter fixes for the top-up batch — add the per-title floor (serve ≥ ABF1 control) AND raise the density target to actual ABF2 level (~8 cp/hr)** — parameter changes only, no model re-run needed. Also confirm with Aryan what the pruner's *configured* target is vs this realized output. (Band context: 13+ band = 1,430 titles ≈ 1.14% of platform TVT; 10+ = 10,388 titles ≈ 4.2%; the top-up set is denser — its 10+ band alone = 3.44% of platform TVT.)

**TOP-UP SHIPPED (update 2026-08-19):** The reconciliation reply to Aryan WAS sent, and **Aryan added the missing titles into the (continuing) v8 experiment on Tuesday 2026-08-11**. This fixes the analysis windows:
- **Window A = 2026-07-23 → 2026-08-11** (original 154,348-title config; ~19 days, COMPLETE — ready to analyze).
- **Window B = 2026-08-11 → ~2026-08-25** (full set incl. top-up; 14-day read, in flight).
- Same clean pre-window 07-09→07-22 for both; never quote Statsig across the 08-11 boundary.
- **Pruner: CONFIRMED UNCHANGED (2026-08-19, per bpulikkal):** the top-up was processed with the SAME pruner that's been running since XP launch — floorless and ~20% under the stated ABF2 density target (the two proposed fixes did NOT ship). Consequences: Window B measures the same config at larger coverage (clean to pool with Window A), but the dense-band over-prune (13+ TVT-wtd ratio 0.756) applies to the top-up too — and the top-up skews DENSE (its 10+ cp band alone = 3.44% of platform TVT), so expect the v7-decile-8-style negative-revenue pattern to be *larger* in the top-up cohort. The dense-band Window A read is the direct forecast of that drag.
- **TOP-UP VERIFIED (2026-08-19, via live `cue_points_abf` × reconciliation buckets):** **38,116 of the 40,766 reconciliation-CSV titles now have live ABF3 cue points** (~111.0M of 111.3M candidate hrs). Bucket-by-bucket: AGREED 25,222/26,279; rotating-window 2,855/2,871; **Gemini-ready 873/888 — the 21.6M-hr bucket DID get added (did not fall through)**; tvt-join 326/369; **partner-meta 3,627/3,726 → the DECIDE bucket was INCLUDED**; dead/foreign EXCLUDE 5,213/6,633 also processed (wasted compute, ~zero TVT, harmless). Bucket table: `core_dev.dsa.temp_bp_v8_topup_buckets` (loaded from `abf1_v8_topup_reconciliation_20260806.csv`).
- **Durable snapshot guardrail DONE (2026-08-19):** `core_dev.dsa.temp_bp_abf_v8_topup_cuepoints` — all 40,766 candidate titles with bucket, live `cue_points_abf` (= as-added, since pruner unchanged since launch), control `cue_points`, per-title counts, snapshot_ds.
- **Activation date VERIFIED empirically (impressions test/control ratio on top-up titles, v8 OTT arms):** flat ≈1.000 through 08-10, **jumps +2.9% on 08-11** (partial add day), settles ~**+3.1%** steady-state 08-12→08-18. → **Window A = 07-24 → 08-10 complete days; Window B first full day = 08-12.** Early directional read: ~+3.1% on-title impression lift on the top-up cohort ≈ v7-level, consistent with the v7-aggressive pruner. v8 OTT exposures: 63.3M devices/arm cumulative through 08-18, still running.

**Population-definition finding (2026-08-19, prompted by bpulikkal):** v8's exposure trigger is title-LOAD, not watch → **~64% of exposed devices never watch anything post-exposure** (Window A, exposed by 08-11: 52.0M/arm; watched ≥1 session = 35.806% C / 35.810% T). Decisions:
- **"Watched ≥1 session post-exposure" (Active) is a VALID population filter** — treatment-independent by construction (a never-watcher never experienced cue points, so treatment can't cause exclusion) and empirically balanced (0.004pp gap, ns). Adds an `Active` population lens to v8 analyses alongside ITT/ToT to de-dilute the ~64% drive-by devices.
- **"≥1 ad break fired" is NOT a valid filter** — break firing is downstream of treatment (denser ABF3 cue points → break more likely to fire); measured: pct-with-impressions 35.224% C vs 35.245% T (+0.021pp, z≈2.2, p≈0.03) — a real pro-Test selection. Never gate the population on it.
- SRM clean at the exposed level (51,995,231 vs 52,002,549).

#### v8 Window A — per-ABF1-band on-title lifts + dense-band over-prune read — 2026-08-19

Notebook `abf_v8_winA_bands` (run 890141839328500, archived `abf_v8_winA_bands__run_2026-08-19_OUTPUT`). Scope: OTT (`ads_abf_3_v8`), Window A = 07-23→08-10, baseline weights 07-09→07-22. Titles = v8-treated ∩ June universe (141,032), banded on ABF1 control cue points; device-level ToT-per-band Welch lifts (same estimator as `abf_v7_decile_concentration`).

| Band | Rev lift [95% CI] | TVT lift | n/arm (devices) |
|---|---|---|---|
| 0 | **+163.9%** [+156.5,+171.3] | **−14.9%** [−18.4,−11.4] | 74K |
| 1–3 | −0.33% [−0.82,+0.15] **ns** | +0.69% (sig +) | 2.67M |
| 4–6 | +0.97% [+0.51,+1.42] sig | −0.75% (sig −) | 3.22M |
| 7–9 | **+5.62%** [+5.42,+5.82] sig | −0.27% (sig −) | 6.72M |
| 10–12 | +0.95% [+0.73,+1.17] sig | −0.14% ns | 5.15M |
| 13+ | **−6.50%** [−6.91,−6.10] sig | +0.38% (p=.089) | 1.91M |

**Dense bands split by below-control (v8 kept cps < ABF1 control) — the over-prune isolation:**

| Cut | Rev lift | TVT | n/arm |
|---|---|---|---|
| 10–12 at/above control | **+2.40%** sig | −0.13% ns | 4.39M |
| 10–12 below control | **−4.21%** sig | −0.04% ns | 2.10M |
| 13+ at/above control | +0.28% ns | +0.20% ns | 0.59M |
| 13+ below control | **−8.19%** sig | +0.44% (p=.066) | 1.49M |

**Key findings:**
1. **Over-prune recurrence CONFIRMED at scale and cleanly isolated:** dense titles pruned below control lose revenue (13+ below: −8.19%; 10–12 below: −4.21%) while at/above-control dense titles are fine (+2.40% / +0.28% ns). Direct at-scale validation of the per-title-floor fix — the damage is entirely in the below-control subset. (13+ below-control also shows the familiar under-serving TVT bonus, +0.44% p=.066.)
2. **Sparse-band NULL — a real projection failure:** band 1–3 revenue is flat (−0.33% ns) where the v6/v7 sample heterogeneity predicted the *largest* gains (+20–30% in the sparsest decile). Likely composition: the full-catalog sparse band is dominated by short series episodes where ad-config gating (~2 breaks) prevents extra candidates from realizing (the v7 placement mechanism), whereas the 1,084-sample's sparse titles were long movies. MOVIE/SERIES split needed to confirm. Band 1–3 TVT is *positive* +0.69%.
3. **Mid-dense is the engine:** band 7–9 = +5.62% rev at −0.27% TVT; 4–6 = +0.97% at −0.75% TVT.
4. **Band 0 (titles with NO ABF1 cue points):** +163.9% revenue (ads where none existed) at **−14.9% TVT** — the worst engagement hit anywhere, but tiny reach (74K devices/arm). Note its baseline-rev weight is ~$0 by construction (no ads pre-launch), so revenue-weighted aggregates mechanically under-count it.
5. **Aggregate: treated-wide (banded) rev-weighted lift = +1.73%**, banded rev share = 14.29% of total → global contribution ≈ **+0.25pp** from the banded set. The at-scale composition (sparse null + dense negative) lands the treated-wide lift at roughly HALF the v7-style ABF1-wide projection (+3.68%); official global read comes from the CUPED all-titles ITT (pending).

#### v8 Window A — HEADLINE (CUPED, OTT) — 2026-08-19

Notebook `ads_abf_3_v8__cuped_stat_sig` (run 727863492710270, archived `…__winA_OTT__run_2026-08-19_OUTPUT`). Window 07-23→08-10, CUPED pre 07-09→07-22. n: ITT 63.28M/63.27M devices, ToT 10.70M/arm (ToT = watched ≥1 v8 title in-window; ≈20.6% of window-exposed). CUPED variance reduction 55–62% (all-titles) / 24–28% (on-title). All figures CUPED:

| Cut | Unbudgeted Revenue | Impressions | TVT |
|---|---|---|---|
| **ITT all-titles (GLOBAL topline — MEASURED, not projected)** | **+0.365%** [+0.279,+0.452] p≈1e-16 ✅ | +0.431% [+0.343,+0.519] ✅ | **−0.041%** [−0.130,+0.049] **ns — FLAT** |
| ITT on-title (v8 titles) | +2.222% [+2.051,+2.392] ✅ | +2.557% ✅ | −0.036% ns |
| ToT all-titles | +0.464% [+0.372,+0.557] ✅ | +0.541% ✅ | −0.045% ns |
| ToT on-title | **+2.146%** [+1.984,+2.308] ✅ | +2.486% ✅ | −0.073% [−0.242,+0.095] ns |

**Reads:**
1. **Global TVT is precisely FLAT at enormous power** — CI [−0.13%,+0.05%] even *rules out* v6's global spillover cost (−0.17% ITT-all CUPED). At v7-aggressive pruning on the full catalog, OTT engagement cost ≈ zero. The revenue-for-TVT frontier at this operating point is: +0.37% global revenue for ~nothing.
2. **Measured global revenue +0.365% vs projection:** v7's machinery projected +1.36% at the FULL ABF1 universe (37% rev share); v8 Window A treats only ~14.3% banded rev share (~16% incl. non-banded) → scale-adjusted projection ≈ +0.55–0.59%. Measured +0.365% ≈ **62–66% of the scaled projection** — the shortfall matches the band decomposition (sparse-band null + dense-band over-prune negative).
3. **On-title ToT +2.15%** vs v7 sample's +3.53% / v6's +5.67% (composition differs: full catalog vs 1,084 large titles).
4. **Floor-fix upside (rough, from band weights):** below-control drag ≈ −0.09pp (13+) + −0.03pp (10–12 below) ≈ **+0.12pp recoverable** by a per-title floor → same-set global ≈ +0.48%; the 08-11 top-up roughly doubles treated coverage on top of that.
5. Method note: the exp view doesn't cap exposures at window end, so ITT includes ~11M devices/arm first exposed after 08-10 with structurally-zero outcomes — relative lifts are unaffected (numerator and denominator scale identically); power slightly conservative.

#### v8 Window A — band × content-type split: MOVIES WIN, SERIES LOSE — 2026-08-19

Run 449507107363092 (archived `abf_v8_winA_bands__bytype__run_2026-08-19_OUTPUT`). Same estimator, band × content_type:

| Band | MOVIE rev lift | SERIES rev lift | MOVIE n/arm | SERIES n/arm |
|---|---|---|---|---|
| 0 | +413.1% (TVT −18.6%) | +55.3% (TVT −8.3%) | 29K | 47K |
| 1–3 | **+4.61%** [+3.13,+6.08] ✅ | −0.39% ns | 234K | 2.54M |
| 4–6 | **+11.19%** [+10.80,+11.57] ✅ | **−1.81%** [−2.35,−1.26] ❌ | 2.16M | 1.47M |
| 7–9 | **+6.42%** [+6.21,+6.62] ✅ | **−5.87%** [−6.61,−5.13] ❌ | 6.49M | 552K |
| 10–12 | +1.15% [+0.94,+1.37] ✅ | **−3.46%** [−5.31,−1.61] ❌ | 5.00M | 253K |
| 13+ | **−4.84%** [−5.16,−4.52] ❌ | **−9.75%** [−10.65,−8.85] ❌ | 1.63M | 391K |

**MOVIES: positive in every band except 13+** — and the 13+ negative IS the count-driven over-prune (47.2% of 13+ movies served below control). The earlier aggregate "sparse-band null" was a composition artifact: sparse-band MOVIES are +4.61%; the band is 98% series by device count.

**SERIES: revenue-negative in every band ≥4 cp — and it is NOT a cue-point-count problem.** Structural check (universe × v8 titles): series serve ABOVE control on average in the losing bands (4–6: 5.19 v8 vs 4.63 ctrl, only 9.5% below; 7–9: 8.16 vs 7.56, 27.7% below) yet lose 2–6% revenue. Working hypothesis: **realized-break deficit from placement × ad-config gating** — short episodes realize ~2 config-gated breaks, and ABF3's candidate positions align worse with the gates than ABF1's human-placed cue points (v7 placement analysis measured series realized breaks 2.14 vs 2.19, −2.3%, on the sample; at catalog scale, and on shorter episodes than the sample's top series, the deficit plausibly grows with control density). NEEDS CONFIRMATION via a realized-breaks-per-session cut by type × band (v7-placement-style, `now_pos` / pod mapping).
- Band 0 (never had cue points): MOVIE +413% rev at −18.6% TVT; SERIES +55% at −8.3% — ads-from-nothing monetize hugely but hurt engagement badly; tiny reach.
- Reconciliation with the sample: v6 OTT already showed MOVIE ≫ SERIES (+8.14% vs +1.95%); the catalog just pushes series from "weakly positive" (big/long sample series) to negative (short-episode long tail).
- **Implication for the pruner/config ask:** the per-title floor fixes the MOVIE 13+ band; it does NOT fix series (they're already above control). The series fix is a different lever — either exclude/hold-back series bands 4+ from ABF3 (serve control), or fix candidate placement relative to the episode ad-config gates. At minimum, Window B/top-up interpretation must split by content type.

#### v8 Window A — Active-population CUPED + realized-break-density mechanism CONFIRMED — 2026-08-19

**Active population (≥1 post-exposure session; run 867434767174221, archived `…winA_OTT_Active__run_2026-08-19_OUTPUT`; n=18.62M/arm):** all-titles rev **+0.351%** [+0.268,+0.434], TVT −0.059% ns; on-title rev +2.189%, TVT −0.054% ns. **Relative lifts ≈ identical to ITT (+0.365%) — as they must be:** zero-outcome devices scale numerator and denominator identically, so removing them doesn't change % lifts (an earlier "expect ~1.7× larger" expectation was wrong reasoning, corrected). Value of the Active lens = interpretable per-active-device magnitudes + slightly tighter CIs; keep reporting it, but it doesn't change conclusions.

**Realized break density (non-empty pods per TVT-hr, Window A, by band × type × arm) — the series mechanism is CONFIRMED as a realized-break deficit, and revenue tracks realized ad load ~1:1 everywhere:**

| Band | MOVIE ctrl→test (Δ) | MOVIE rev | SERIES ctrl→test (Δ) | SERIES rev |
|---|---|---|---|---|
| 0 | 0.52→3.65 (+599%) | +413% | 2.09→3.74 (+79%) | +55% |
| 1–3 | 2.97→3.15 (**+6.1%**) | +4.61% | 3.49→3.47 (**−0.7%**) | −0.39% |
| 4–6 | 3.40→3.87 (**+13.9%**) | +11.19% | 4.27→4.25 (**−0.6%**) | −1.81% |
| 7–9 | 3.60→3.89 (**+8.0%**) | +6.42% | 4.43→4.12 (**−6.9%**) | −5.87% |
| 10–12 | 3.78→3.86 (+2.0%) | +1.15% | 1.84→1.78 (−3.5%) | −3.46% |
| 13+ | 4.46→4.23 (**−5.1%**) | −4.84% | 4.46→3.89 (**−12.7%**) | −9.75% |

- **Revenue ≈ realized break density in every cell** (CPM flat, consistent with all v6/v7 mechanism work). No cell needs a quality/CPM story.
- **SERIES: ABF3 realizes FEWER breaks than ABF1 in every band ≥1 cp — despite serving MORE raw candidates** (e.g. 4–6 band: 5.19 candidates vs 4.63 control, yet realized 4.25 vs 4.27/hr; 7–9: −6.9% realized; 13+: −12.7%). On short config-gated episodes, ABF1's human-placed cue points align better with the gates (initial-ad-slot ~420s, min-spacing ~600s) than ABF3's ML positions → breaks fail to fire. This is the v7 placement finding (−2.3% series realized) writ large at catalog scale and growing with control density.
- **MOVIE: ABF3 realizes more breaks in bands 0–12 (+2 to +14%) → positive revenue; 13+ realizes −5.1% (the count over-prune) → −4.84%.**
- **Fix map (two separate defects):** (1) MOVIE 13+ → per-title floor (count fix). (2) SERIES ≥4 cp → placement-vs-gate alignment on short content (NOT count; floor won't help). Options: hold series bands 4+ on control cue points, or re-position/snap ABF3 candidates to gate-compatible positions on episodes. Series bands 4–6+7–9 carry meaningful weight (1.47M+552K devices/arm).

#### v8 WINDOW B (post-top-up) — first read, 7 days 08-12→08-18 — 2026-08-19

Population = all devices exposed since launch (07-23); outcomes windowed to 08-12→08-18 (post-add config). Titles = full treated set `core_dev.dsa.temp_bp_abf_v8_all_titles` (192,464 = 154,348 original + 38,116 top-up; zero overlap). Same clean pre 07-09→07-22 (CUPED θ≈0.36–0.39, var-reduction 35–42% — weaker than Window A's 55–62% since the pre-period is further away). Runs archived: `…winB_OTT__`, `…winB_Active_windowscoped__`, `abf_v8_winA_bands__winB_{alltreated,topup}__run_2026-08-19_OUTPUT`.

**Headline (CUPED, run 366064367526370):**

| Cut | Revenue | Impressions | TVT |
|---|---|---|---|
| **ITT all-titles (GLOBAL)** | **+0.879%** [+0.767,+0.992] ✅ | +1.091% ✅ | **−0.179%** [−0.296,−0.061] **SIG −** |
| ITT on-title (192K) | +2.376% [+2.229,+2.524] ✅ | +2.916% ✅ | −0.305% [−0.460,−0.150] sig − |
| ToT all-titles (n 9.65M/arm) | +0.973% ✅ | +1.220% ✅ | −0.210% sig − |
| ToT on-title | +2.308% [+2.175,+2.441] ✅ | +2.850% ✅ | −0.322% [−0.461,−0.183] sig − |

**Window A → Window B: global rev +0.365%→+0.879% (2.4×, the top-up is paying); global TVT flat(−0.04% ns)→−0.179% SIG.** The free lunch is over — post-add the trade is **~+0.88% global revenue for ~−0.18% global TVT** (a classic me_score question). Whether the TVT cost is CAUSED by the top-up (long dense rotating-window movies = the cadence-cost titles) or is temporal drift is being decomposed via a Window B run on the ORIGINAL 154K set only (if its on-title TVT also went negative → temporal; if still flat → top-up-driven). Window-scoped-Active sensitivity run agrees (+0.833% rev / −0.216% TVT).

**Band structure (all-treated, Window B):** banded rev share of total now **34.98%** (vs 14.29% pre-add) → banded global contribution **+0.82pp**. Engine 7–9 band +7.08% (movies +7.67%); 13+ −3.75% (below-control −7.34% vs at/above +1.37% ✅); movies positive in bands 0–12; **series negative in every band, worst 13+ −9.66%**; 13+ series TVT +1.41% sig (under-serving bonus). Same structure as Window A — the two defects are systematic, not sample artifacts.

**Top-up cohort alone (38,116 titles, run 1099942884555490):** treated-wide **+2.64%** rev-weighted; banded rev share 20.7% → **+0.55pp global contribution from the top-up alone**. 7–9 band +8.12% (movies +8.64%, 4.4M devices/arm). Over-prune recurs on fresh titles: 13+ below-control −6.78% vs at/above **+1.79% ✅ sig** (the floor works when respected); series negative again (13+ −14.1%). Real TVT cost on its big bands (7–9 −0.54%, 10–12 −0.42%, both sig) — consistent with long-movie cadence cost on the rotating-window blockbusters.

**Population-definition fix (2026-08-19, bpulikkal's catch):** Active for Window B must be defined **since first exposure** (not within-window) to stay treatment-independent by construction — a July-exposed device could be churned BY treatment before Window B, so window-scoped Active conditions on a post-treatment outcome. Empirically both definitions are balanced (window-scoped 20.8282% C vs 20.8239% T, z≈0.6; since-exposure 35.6687% vs 35.6707%, z≈0.3) so the sensitivity run isn't materially biased, but since-exposure is the definition of record. Notebook widget `ACTIVE_FROM` added (`ads_abf_3_v8__cuped_stat_sig`).

**Window B follow-up runs (2026-08-19, all archived `…__run_2026-08-19_OUTPUT`):**
- **Active on the since-exposure basis (definition of record, 22.57M/arm):** global rev **+0.846%** [+0.735,+0.957], global TVT **−0.195%** [−0.311,−0.080] sig; on-title +2.321% / −0.321% sig. All three population lenses agree (ITT +0.879/−0.179; window-scoped Active +0.833/−0.216) — Window B conclusion robust to population definition.
- **Fresh-cohort carryover check (first exposure ≥08-12, zero prior ABF3 history; 8.86M/arm ITT):** top-up on-title ToT rev **+4.47%** [+4.12,+4.82], TVT −0.35% p=.09; ITT on-title −0.54% sig TVT; all-titles −0.47% sig TVT. **TVT cost present for fresh devices → NOT cumulative-exposure carryover.** (Fresh cohort = light/new users — CUPED var-reduction only 2–6%; like-for-like veteran comparison = the all-device top-up run.)
- **DECOMPOSITION ANSWERED — the Window B TVT cost is TOP-UP-DRIVEN, not temporal drift (run 694406961910467):** original 154K set during the SAME Window B period: on-title TVT **−0.039% [−0.265,+0.186] ns — still flat**, reproducing Window A's −0.036% ns; on-title rev +2.035% (vs +2.222% winA, mild moderation). Meanwhile combined on-title TVT is −0.31% sig and fresh-device top-up on-title −0.54% sig. → The −0.18% global TVT cost entered exactly when/where the top-up's long dense rotating-window movies did — the v6/v7 movie-cadence cost carried by the new cohort, matching its band TVT (7–9 −0.54%, 10–12 −0.42%, both sig). Original set remains a TVT-free +2% on-title lift.

- **All-device top-up CUPED (run 1083000873353827, archived) — carryover comparison complete:** top-up on-title ITT rev **+2.585%** [+2.409,+2.761], TVT **−0.490%** [−0.679,−0.302] sig; ToT (7.21M/arm) +2.535% / −0.471% sig. Vs fresh-cohort +4.58% / −0.54%: **fresh devices show ~1.8× the revenue lift of the (veteran-dominated) all-device read, but the SAME TVT cost (−0.49 vs −0.54).** Interpretation: not evidence of contamination — the gap is novelty/early-exposure moderation (fresh read = days 0–7 of exposure; veterans = steady state) plus device-mix composition (fresh = new/light users, CUPED nearly inert for them), the same moderation-over-runtime pattern v6/v7 showed. The TVT cost being identical across exposure history is further confirmation it's config-intrinsic, not fatigue. **Steady-state (all-device) numbers are the graduation-relevant ones.** ToT-per-title top-up read: +2.5% rev / −0.47% TVT.

**REPORT PUBLISHED (2026-08-19):** [ABF3 v8 — Full ABF1 Catalog Results (OTT)](https://docs.google.com/document/d/1z70VEKZ0sfDJTuslRZ_wLacBaXaBFVcwLtzfR_M7E88/edit) — Doc id `1z70VEKZ0sfDJTuslRZ_wLacBaXaBFVcwLtzfR_M7E88`, folder `0AE3wRIsB2WnhUk9PVA`, stable-link state `memory/abf_v8_report.docid`. Source: `ABF3_experiment_v8_report.md` (project root); published via the `gdoc` CLI (`gdoc update "$(cat memory/abf_v8_report.docid)" --from ABF3_experiment_v8_report.md` to refresh in place). **Framing per bpulikkal (2026-08-19): Window B (full catalog) = MAIN view; Window A + A/B comparisons = appendix.**

**⚠️ DECISION-METRIC CHANGE (2026-08-19, bpulikkal): me_score/e_score is DROPPED as the graduation gate for this project.** The graduation decision will be made on the **measured revenue and TVT lifts directly** (the v8 Window B global ITT numbers). All earlier references throughout this file to "me_score/e_score = the formal graduation gate, not yet computed" (v3 design onward) are SUPERSEDED — the composite metric will not be computed for this decision. The open question that replaces it: the acceptable revenue-per-TVT exchange rate for the top-up cohort's trade (~+0.5pp rev / −0.18pp TVT) — a stakeholder threshold call. The v8 report intentionally does not mention me_score/e_score, and leads with measured-vs-projected (v8 +0.879% measured ≈ 65% of v7's +1.36% projection at comparable coverage).

#### v8 — SERIES MECHANISM PROVEN by deterministic gate simulation — 2026-08-19

Challenged by bpulikkal ("serious claim — prove it with real data"). Notebook `abf_v8_gate_simulation` (run 346515401805909, archived `__run_2026-08-19_OUTPUT`): replayed the pod-placement gate (greedy first-eligible; episodes 420s initial/600s spacing baseline, movies 900/720, + tighter tolerant profiles) over BOTH arms' actual served cue point positions (`cue_points` vs `cue_points_abf` — note ABF column is BRACE-wrapped `{...}`, parser must strip) for ~193K treated∩universe titles, TVT-weighted.

**Verdict: mechanism CONFIRMED — simulated Test−Control fireable-break deltas reproduce the observed realized pattern across all 10 band×type cells, r = 0.962.**
- **Failure mode = NO EARLY CUE POINTS on dense series.** First fireable break, ABF1→ABF3: series 7–9 599→806s (+3.5 min), 10–12 591→936s (+5.8 min), 13+ 585→997s (+6.9 min); unused tail also grows (e.g. 13+ 811→1126s). Break train compressed from both ends → fewer spacing slots fit. Sparse series (1–3/4–6): lag only ~+40s. Movies: no lag (first fire ~equal) → extra candidates fill the grid → +7 to +26% simulated fireable.
- **Smoking gun:** 4,268 series titles fire FEWER simulated breaks despite MORE cue points (3.66% of series TVT).
- **Band split of the series deficit (baseline gate):** 13+ = mostly COUNT (below-control prune: −7.2pp of −8.2pp total) → floor helps; 7–9/10–12 = mostly POSITION (−3.2/−2.0pp position vs −1.7/−0.7 count) → floor does NOT help.
- **Static-sim vs observed offsets explained:** sim assumes full watch-through — real partial sessions penalize late placement further (observed < sim everywhere, exactly ABF3's late-shift signature); tighter tolerant-segment gates deepen series sim deficits to −5 to −15%, matching observed (−0.6 to −12.7%).
- 13+ MOVIES show the same late-shift signature (tail 920→1182s) + 47% below-control count — consistent with observed −5.1% realized despite base-gate sim +7.4%.
- **Fix map (updated):** per-title floor (13+ count) + pruner constraint "always keep the earliest gate-eligible candidate" (dense-series position) — OR hold series 4+ on control. **Model-vs-pruner split still open:** unpruned candidates with positions exist in `core_prod.titancontrollerdb_cdc.product_ai_ad_breakfinder` (cols: asset_id UUID, ad_breaks JSON w/ timestamp+classifier_score, model='gemini-3-flash-preview') — needs asset_id↔content_id mapping; if early candidates exist unpruned → pruner's fault; else model placement.
- **Follow-up validations (2026-08-19, same notebook, run 1001443593965209):**
  - **Prevalence (falsification test #2 — issue IS series-concentrated):** share of TVT where ABF3 fires FEWER simulated breaks: SERIES 10.6% vs MOVIE 5.2% overall; dense bands 5–10× (series 7–9: 23.8% vs movies 2.5%; 13+: 54.6% vs 11.1%). Mirror image on gains: movies fire MORE on 51.5% of TVT vs series 19.4% (series mostly "equal" 70% — gate-pinned). Severity ~1.0 lost break both types, but that's −33% of an episode's ad load vs −17% of a movie's.
  - **"Series" = LONG-FORM series content.** Top-TVT typical episodes (Shooter, 42 min, 3–4 cps) are FLAT-TO-POSITIVE (ABF3 fires ≥ control — extra candidates fill ABF1's gaps); the losers are movie-length series titles (The Temptations 87 min 24→10 cps 6→5 fired; Doc West 106 min; Columbo 98 min 9→10 cps but 6→5 fired; Jesus of Nazareth 187 min). Don't frame as "sitcoms broken".
  - **Gate-resonance explanation of the movie/series asymmetry (same policy, opposite alignment):** gates are per content TYPE not duration (movies 900/720s, episodes 420/600s). ABF1 humans tuned placement per type (episode points from ~7–9 min, spread 10–12 min = just ABOVE the episode gate → all fire; movie points ~11.6-min spread = just UNDER the 12-min movie gate → overshoot to ~23-min cadence). ABF3's type-blind policy (late start, ~9-min spread) lands just ABOVE-grid on movies (better tracking, +16–26% fireable) and just UNDER-gate on episodes (every other point skipped, ~18-min cadence, first slot lost). Spacing just above gate = all fire; just below = half fire.
  - **Fix (refined): gate-aware pruning per content type** — keep earliest gate-eligible candidate (~7–10 min episodes) + target kept spacing at gate+margin (~11 min episodes / ~12.5 min movies) instead of flat per-hour density; + per-title floor. Selection-time only, no model re-run. Fallback: hold series 4+ on control.
- Report §2c updated with the proof, worked examples (Columbo/Shooter/Temptations), gate-resonance explanation, and prevalence table; republished (same link).

**Claim-scrutiny pass (2026-08-20, bpulikkal challenged the decision-frame wording — report corrected & republished):**
- "Genuine trade" is supported by 4 legs: significance/robustness (63M/arm, all population lenses), localization (original set flat, top-up carries all the cost), fresh-device presence (not carryover), mechanistic coupling (both effects = more realized breaks on long movies; v6/v7 flat dose-response = can't prune the cost away without losing the revenue ~1:1). Caveats: 7-day, OTT-only, no within-v8 dose-response on the top-up.
- **"Fix at no engagement price" was OVERSTATED — corrected:** floor-to-CONTROL is TVT-neutral BY CONSTRUCTION (identical serving → no contrast; gives back only ~+0.005pp under-serving bonus). But serving dense titles ABOVE control, or fixing series under-firing, raises load above today's treatment → expect the usual small TVT price (precedent: series 4–6, where ABF3 already fires more, TVT −0.95% sig). The at/above-control subset's +1.4–2.4%/flat-TVT is contemporaneous but NOT config-randomized (title-selection differs). **Standing guardrail: re-measure any changed pruner config (Window C) before using its numbers for graduation** — same lesson as the v7 floor validity-gap note.

#### v8 — MOBILE & WEB full analyses + OTT 9-day refresh — 2026-08-21

Full v8 suite (Window A + B CUPED w/ 3 populations, bands winA/winB-all/winB-topup, original-set decomposition) replicated for `ads_mobile_abf_3_v8` and `ads_web_abf_3_v8`; OTT refreshed to Window B = **08-12→08-20 (9 complete days)**. All runs archived `…__run_2026-08-21_OUTPUT`; result JSONs in project `.v8_refresh_results/`. Platform scoping: bands (B) denominator platform-filtered (new `IMP_PLAT_FILTER` widget); ZeroDivision guard added to `abf_v8_winA_bands` (thin $0-control cells on mobile/web).

**CROSS-PLATFORM WINDOW B HEADLINE (global ITT, CUPED, 08-12→08-20):**

| Platform | Revenue | TVT | vs v7 projection |
|---|---|---|---|
| OTT (65.5M/arm) | **+0.877%** [+0.768,+0.986] | **−0.161%** [−0.275,−0.047] sig | 65% of +1.36% |
| **Mobile** (15.9M/arm) | **+2.957%** [+2.597,+3.316] | −0.168% [−0.492,+0.156] **ns flat** | **122% of +2.42%** |
| **Web** (35.8M/arm) | **+3.205%** [+2.231,+4.179] | +0.319% ns flat/positive | **232% of +1.38% (which was ns)** |

- **Mobile = strongest platform:** over-delivers projection; the v6/v7 mobile TVT fear (−0.90% on-title sig) did NOT materialize — TVT flat on every lens/band/cohort (global CI can't yet exclude −0.4%). On-title +8.13%. WinA +1.16% global; top-up adds +1.78pp (additivity ties out). Series POSITIVE on mobile (1–3 +11.8%, 4–6 +5.2%, 7–12 flat, only 13+ −9.7%).
- **Web topline significant for the FIRST TIME in the program** (sample era never cleared zero): +3.21% global at flat/positive TVT; even Window A alone was sig (+1.35%, p=9e-4). On-title +6.06%. Series intermediate: positive ≤7–9, dense negative (13+ series −20%, mostly count/below-control; thin cells). Caveats: noisiest platform, cookie device churn (35.8M "devices"), ~11% cross-surface leakage (uncorrected, consistent w/ v6/v7).
- **OTT refresh: rock stable** — global +0.877/−0.161 (vs 7d +0.879/−0.179; TVT slightly softer), on-title +2.376/−0.295, origset on-title TVT still flat (−0.035 ns) → decomposition holds; bands nearly identical (7–9 +7.06, 13+ −3.71, below-control splits unchanged); topup treated-wide +2.66, contribution +0.55pp.
- **Defect universality:** below-control dense over-prune replicates on ALL THREE platforms (below vs at/above: OTT −7.3/+1.4; mobile −6.3/+1.6; web −9.7/+1.5 at 13+) → per-title floor is platform-universal. **Series/gate-alignment defect is OTT-SPECIFIC** (mobile/web series positive in sparse/mid bands — their ad-config gates differ; OTT episode gates are what expose ABF3's placement). 13+ series negative everywhere = the count defect, floor's territory.
- **Reports published:** [Mobile `1NSoVOcipzJ-yXRgqdzz60JV6Ippl_g_-oTUrerPdOe4`](https://docs.google.com/document/d/1NSoVOcipzJ-yXRgqdzz60JV6Ippl_g_-oTUrerPdOe4/edit) (state `memory/abf_v8_mobile_report.docid`), [Web `1u5RN6dlFRf1UBr0JkyYIpB7njVs10bezViUP6yikSH0`](https://docs.google.com/document/d/1u5RN6dlFRf1UBr0JkyYIpB7njVs10bezViUP6yikSH0/edit) (state `memory/abf_v8_web_report.docid`); sources `ABF3_experiment_v8_{mobile,web}_report.md` (project root). OTT report refreshed in place to 9-day numbers.

**OTT overall series TVT/revenue (pooled across bands, device-level on-title; 2026-08-25, ad-hoc SQL `/tmp/so_win{A,B}.sql`):** SERIES Window B rev **−1.31%** [−1.63,−0.99] sig / TVT **+0.20% [−0.12,+0.53] ns** (Window A: −1.63% / +0.14% ns; n≈3.3–3.9M devices/arm). MOVIE contrast: winB +3.66% / −0.48% sig. **The series ad-load discount buys NO measurable engagement** — matches the v7 flat dose-response; the scattered per-band TVT significances (7–9 −1.06 sig, 13+ +1.29 sig in winB) cancel in the pooled cut → multiplicity noise around flat, not per-break placement harm. **Series-fix sizing conclusion: restoring series load recovers ~1.3% of series revenue at a giveback bounded by a ns +0.2% series TVT — essentially free.**

#### v8 — NPV_TVT (non-power-viewer TVT, Statsig metric) + p-values added to all reports — 2026-08-27

New Statsig-faithful metric implemented in notebook `abf_v8_npv_tvt` (project root; widgets EXP/RUN_START/windows). Power viewer = ≥8 visit-days last-28d AND >4 watch-hrs/visit-day, from the latest `core_prod.tubidw.device_okr_daily` snapshot in [run_start−7, first_exposure_ds] via MAX_BY (absent → non-power); TVT source = `statsig_video_session_metrics_daily.tvt`; pre-exposure classification → valid population cut (balance verified all platforms). Raw+CUPED Welch; PV complement computed as contrast. 6 runs archived `abf_v8_npv_tvt__{ott,mobile,web}_{winA,winB}__run_2026-08-27_OUTPUT`; JSONs in `.v8_refresh_results/npv_*.json`. **Reported Window B only (per bpulikkal).**

| Platform (winB) | NPV_TVT (CUPED) | Power viewers (contrast) | PV share/arm balance |
|---|---|---|---|
| **OTT** | **−0.272%** [−0.411,−0.133] **p=1.3e-4** | +0.010% p=0.92 | 2.549/2.546% ✓ |
| Mobile | −0.237% [−0.585,+0.111] p=0.18 ns | +0.109% p=0.78 | 0.678/0.678% ✓ |
| Web | +0.188% [−0.599,+0.974] p=0.64 ns | +0.762% p=0.39 | 0.081/0.081% ✓ |

**KEY FINDING: the OTT TVT cost is carried ENTIRELY by non-power (casual) viewers** — NPV −0.27% (deeper than the all-device −0.16%) while power viewers are precisely flat; the all-device number is the TVT-weighted blend. Sharpens the engagement concern toward the retention-sensitive casual audience. Mobile/web NPV flat (matching their overall TVT); on web PV is nearly nonexistent (cookie churn → no 28-day history) so NPV ≈ all-device. WinA (reference only, not reported): OTT NPV −0.103% p=.058; mobile +0.06 ns; web +0.15 ns.

**All three reports updated & republished (same links):** §1 headline tables now carry explicit p-values in every cell (revenue/impressions/TVT × populations, global + on-title) + an NPV_TVT block; OTT TL;DR gained the NPV concentration bullet.

#### 🎓 v8 GRADUATED — rolled out 2026-08-31 (recorded 2026-09-01)

**The v8 experiment graduated: ABF3 cue points (v8 config) rolled out to the full treated ABF1 catalog on 2026-08-31.** Decision made on the measured revenue/TVT lifts (OTT +0.88%/−0.16%; mobile +2.96%/flat; web +3.21%/flat). Consequences for data hygiene:
- `cue_points_abf` is now the PRODUCTION serving column for the ~192K former-ABF1 titles on all traffic (no more Control arm serving ABF1 on those titles). Any experiment-era on-title analysis must use the archived windows; post-08-31 the contrast is gone.
- The pruner defect fixes (per-title floor, OTT gate-aware series placement) are now POST-graduation optimization items rather than graduation blockers.

---

### Experiment: ABF3 v9 — ABF2 Catalog (Planning, 2026-09-01)

**Goal:** repeat the v8 playbook on the **ABF2 catalog** (titles currently serving ABF2 ML cue points) — ABF3 vs ABF2 at catalog scale. Reference prior: v4's density-matched read found ABF3 ≈ ABF2 at equal density (excluded-analysis parity), so the upside driver is ABF3's higher (pruned) density on sparse-ABF2 titles + the fixed pruner if it ships.

**Title-selection audit — COMPLETE (2026-09-01).** Aryan's pull materialized (`core_dev.dsa.temp_bp_aryan_v9_pull`: **209,618 titles / 72.58B TVT-min per 60d**); per-title audit universe `temp_bp_v9_audit_universe` (flags: aryan/strict has_abf, in_v8, in_gemini via `ml_prod.ads.abf3_slasher_cuepoints` [195,434 processed titles], 60d TVT, US `content_availability` max end_ts, in_pull). Findings:

| Check | n | 60d TVT (M min) | Verdict |
|---|---|---|---|
| B. v8 titles leaking in | 54 | 0.24 | Negligible — Gemini exclusion catches v8; still add the durable `temp_bp_abf_v8_all_titles` guard |
| C. `'{}'`/`'{0.0}'` format artifacts | 119 | 12 | Fix filter → `NOT IN ('[]','{}','{0.0}','')` |
| D. Licensed (future end_ts) but zero 60d TVT — off-rotation | **7,570** | 0 | ADD to processing (rotating-window lesson) |
| **E. Gemini-ready TRUE-ABF2, excluded by `gm IS NULL`** | **1,497** | **11,775 (=16.2% of pull TVT)** | **CRITICAL — must be IN the experiment, no re-processing** (888-lesson ×13 TVT; only 10 are v6/v7 residue) |
| F. No future US license (dead going forward) | **18,127** | 4,101 | EXCLUDE/deprioritize |
| G. True ABF2 universe (strict, ¬v8) | 275,720 | 84,485 | reference |

**Corrected lists (durable): `core_dev.dsa.temp_bp_v9_experiment_titles`** = strict-ABF2 ∧ ¬v8 ∧ US end_ts > today, w/ `needs_processing` flag: **200,403 titles / 80.24B TVT-min (+10.5% TVT vs his pull despite −9K titles)** = 198,952 to process + **1,451 Gemini-ready ADD-ONLY**. Two-list rule again: EXPERIMENT list = all 200,403; PROCESSING list = the 198,952. Reconciliation vs his pull: in-both 191,382; his-only dropped 18,236 (expired/artifacts/leaks); mine-only +7,570 rotating +1,451 gemini-ready. Missing-TVT framings: 8.3% of ALL platform TVT / 13.9% of ABF2-catalogue TVT / 16.2% of his pull. Expiry breakdown of the 18,127: 13,338 no-US-row (delisted), 4,789 end_ts-passed (bulk expired 8–30d ago — trailing-TVT artifact). **Canonical selection SQL: `abf_v9_experiment_titles_selection.sql` (project root) — self-contained, verified to reproduce the table exactly (200,403/200,403, 0 mismatches); snapshot-dependent (licenses/gemini/live column move daily) → re-run at launch.** Reply to Aryan drafted 2026-09-01 (3 fixes + two-list split); NOT yet sent.

**Second-reviewer query audited (2026-09-01):** a teammate's revision of Aryan's query = brace-format fix + gemini presence-only. Verified: (1) **`'[]'` occurs ZERO times in `cue_points_abf`** — Aryan's original empty-filter was a literal no-op; the real empties are `'{}'` (6,033 rows, their fix catches) and **`'{0.0}'` (9,664 rows — the BIGGER leak, still passing their `<> '{}'`)** → strict filter `NOT IN ('{}','{0.0}')` required (ours has it). (2) Gemini presence-only vs size>0 = 18-title delta (their "near no-op" comment correct); their v2 nugget was the useful part — **servable-v2 sets exist for 189,692 of 195,452 processed titles**; of our 1,451 add-only titles, 1,429 (99.999% of the TVT) have servable v2, the other 22 (0.11M min) were FLIPPED to needs_processing (re-slash) → table now = **1,429 add-only + 198,974 to process**. **Canonical SQL updated to the servable-v2 gemini definition and RE-VERIFIED to regenerate the table exactly (200,403 rows, 0 mismatches incl. flags)** — table and SQL are in sync. (3) Their query still carries all three substantive gaps (single-list, TVT-based selection, no explicit v8 guard). Open q for Aryan: confirm v9 serves the v2 slasher output (defines "servable").

**v9 LAUNCH DECISION — pre-launch audit says WAIT FOR THE PRUNER FLOOR (2026-09-15):** Aryan asked "YOLO with slasher 2.0 now vs wait ~2 wks for pruner improvements" (ABF2 titles now processed; static pruner unfixed but 2.0 drops the extra ~20% density reduction). Pre-launch below-control prevalence check (servable v2 slash count vs live ABF2 control per title; SQL `/tmp/v9audit/13_prevalence.sql` pattern, runnable anytime):

| ABF2 band | n | ctrl→v9 mean cp | % titles below | % TVT below |
|---|---|---|---|---|
| 1–3 | 67,418 | 2.70→2.66 | 21.6 | 14.1 |
| 4–6 | 66,610 | 4.88→4.52 | 52.0 | 40.7 |
| 7–9 | 35,557 | 7.68→6.58 | **79.1** | **62.9** |
| 10–12 | 13,024 | 10.90→10.35 | 53.0 | 20.7 |
| 13+ | 16,132 | 15.56→13.58 | **79.5** | **73.2** |

**"Not as extensively" is INVERTED on ABF2:** v8's control was sparse ABF1 (pruner mostly above control; below-control 6–25% + tiny 13+); v9's control IS the density the slasher targets → ~half the catalog below its own control by construction. v8 proved (all 3 platforms) below-control = −4 to −8% revenue, no TVT give-back. With 40–73% of big-band TVT below control and a PARITY success bar (v4: ABF3≈ABF2 at matched density; v9's value = killing human review), YOLO ⇒ likely negative measured revenue ⇒ failed read + burned pre-period + relaunch. **Recommendation: wait ~2 wks for the per-title floor (serve ≥ ABF2 control) — it eliminates the below-control mass by construction — then launch the config that will graduate (Window C rule).** Optional pre-launch extra: run the gate simulation on both arms' cue points (all in tables now) to forecast realized-break deltas before spending traffic.

**Slasher architecture CONFIRMED by Aryan (2026-09-15):** "Slasher for ABF1 titles uses the same pruner but slashes an additional 20% cue points on top of it"; ABF2 titles get slasher 2.0 (no extra 20%). This retroactively CONFIRMS the v8 density mechanism we inferred on 2026-08-07 (v8 realized ~6.5 cp/hr vs ABF2-actual ~8.2 = the extra 20% layer) — now fact, not inference. Our prevalence check already used the v2 (slasher 2.0) output, so the wait-for-floor numbers reflect exactly the config he proposed to launch; aggregate reduction −7 to −14% per band confirms the extra-20% layer is absent in v2. Follow-up reply drafted making the point that the issue is the missing per-title floor, not the 20%: a target at the ABF2 *average* necessarily puts every denser-than-average title below its own control.

**Open / next (priority):**
- Send Aryan the wait-for-floor recommendation + prevalence table (drafted 2026-09-15).
- Pre-launch gate simulation on the v9 sets (optional, ~1 day) once the floored pruner output lands — verify floor works BEFORE launch (count check: slashed ≥ control per title).
- v9 launch playbook ready: same windows/populations/metrics as v8 (incl. NPV_TVT, p-values); two-list split maintained (`temp_bp_v9_experiment_titles`).
- Carry-over post-graduation items: model-vs-pruner split for OTT series placement; business-wide rollup if wanted.
- Snapshot the top-up's served cue points to a durable table (verify against live `cue_points_abf`) + capture the added-title list and add timestamp; verify pruner config of the top-up batch.
- Window B read after ~08-25 (add+14d): full-set + fresh-cohort (27.5K) reads, carryover re-check fresh-vs-exposed.
- me_score/e_score gate — still uncomputed; v8 is the dataset it will run on.

---

### Experiment: ABF3 v10 — ABF2 Titles Only (Active, recorded 2026-10-15)

**Experiment:** `ads_abf_3_v10_abf2_titles_only` (OTT, Statsig owner Aniruddha Basak, layer `ads_ml_abf3`). Restarted **2026-10-09 23:30 UTC**, 4 arms × 25%: Control = ABF2 cue points; **v4** = T1 equal-load pruner; **v6** = T2 equal load + ~7% on 60–120 min movies; **v5b** = T3 ABF2-like counts, gate-aware placement. Served lists: `ml_dev.tmp.abf3_new_pruner_cuepoints` (snapshot 10-08). Report: "ABF3 v10 — ABF2 Titles Results (OTT)" (docx; scripts in `v10_verification/`).

**Early read (10-09→10-15 10:00 EDT, global ITT CUPED, nominal 95%):** total revenue v4 −0.10% ns / v6 +0.35% sig / **v5b +0.85% sig** (budgeted +2.39%); TVT v4 +0.20% sig / v6 +0.02% ns / v5b −0.19% sig. Movies gain, episodes lose on every arm (dense episodes pruned below ABF2 on ~75% of titles; v4/v6 first episode cue ~3.5 min late) → per-title floor + earlier episode cue is the fix.

**PM question (2026-10-15): "Statsig doesn't show stat-sig negative TVT but the report does — is that because the report is ABF2-titles-only?" Answer: NO.** The report's sig −0.187% (v5b) is the **global, all-titles** number; on ABF2 titles only v5b TVT is −0.18% **ns**. Point estimates match Statsig (−0.17%). The gap is interval width: report = fixed-horizon nominal 95% CUPED Welch (±~0.17pp); the Statsig scorecard has **sequential testing ON + Benjamini-Hochberg for 3 variants**, widening every interval ~1.8× (TVT ±0.30, unbudgeted rev ±0.33 vs report ±0.17–0.18). Under Statsig's adjustments TVT is ns on all arms → read TVT as flat. Report should label its sig calls as nominal/unadjusted.

#### v10 docs refreshed on the extended window — 2026-10-19

The three docs in `ABF Files/` (`ABF3 v10 — ABF2 Titles Results (OTT|Mobile|Web).docx`) were regenerated by re-running every query. **Window: 2026-10-09 → end of 2026-10-18** (outcomes capped 2026-10-19 00:00 UTC, the latest day in `core_dev.statsig.exposures`; was 10-15 14:00 UTC). Pre-period (09-25→10-08), definitions and populations unchanged. ITT devices/arm: OTT 5.96M→9.74M, mobile 2.01M→3.07M, web 3.42M→6.28M. Previous docs backed up in `v10_verification/prev_20261015/`.

**Global ITT CUPED lifts (v4 / v5b / v6; "sig" = nominal 95%):**

| Platform | Total revenue | TVT |
|---|---|---|
| OTT | +0.015% ns / **+1.068% sig** / **+0.484% sig** | +0.131% ns / **−0.166% sig** / −0.051% ns |
| Mobile | **−1.642%** / **+0.710%** / **−1.264%** (all sig) | +0.029% ns / **−0.397% sig** / −0.219% ns |
| Web | **−1.529% sig** / **+1.921% sig** / −0.280% ns | −0.071% / +0.179% / +0.012% (all ns) |

- **Same story as 10-15:** v5b is the only arm that wins on every platform (total revenue), v6 is a smaller positive on OTT but loses on mobile and is flat on web, v4 is parity on OTT and loses on mobile/web. Episodes leak, movies gain; below-control titles lose and at/above-control titles gain on every platform (per-title floor case holds).
- **What changed:** (1) mobile v5b TVT dip is now nominally significant (−0.397%, was −0.359% ns) in ITT/Active/ToT; (2) OTT v4's small significant TVT gain (+0.20%) is gone (ns); (3) OTT v5b and v6 global unbudgeted revenue now significant (+0.280%, +0.321%); on-title v5b/v6 grew from ~+0.4% to +0.685%/+0.615%; (4) OTT v6 13+ band now significantly positive (+0.62%), OTT v5b episodes −0.33% ns (impressions −0.45% sig); (5) OTT power-viewer share fell 12.6%→8.8% because the ~3.8M devices added are only ~2.7% power viewers; v5b power-viewer TVT −0.231% sig is the only NPV/PV significance.
- **Sig calls are nominal.** Statsig widened intervals ~1.8× on the 10-15 OTT read (sequential testing + BH); applying that, v5b's OTT and mobile TVT dips would not be significant (approximation; no scorecard pull for this window — docs say so).
- **Method notes:** CUPED/Welch now computed in SQL (`v10_verification/headline_all_lifts.sql`, `bands_all_lifts.sql`; checked vs the Python estimator on OTT ITT revenue sums, match to 0.001pp); gate replay ported from the notebook to SQL (`gate_replay_all.sql`, validated against the 10-15 run: OTT cells, first-break timings, episode decomposition reproduced to rounding). All three platforms run as single combined queries. Outputs in `v10_verification/results_20261019/` (TSV/JSON), parsed by `load_results.py`; docs built by `make_narr_r2.py` + `build_report.py` (mobile/web) and `edit_ott_r2.py` (OTT, edits the existing doc in place).
- **Data traps found:** `ml_dev.tmp.abf3_new_pruner_cuepoints` now also holds non-v10 arms (`v4e300`, `v4e360`, `v6m`, `r2me`) — filter `slasher_version IN ('v4','v5b','v6')`; the v4/v5b/v6 rows and ABF2 control counts reproduced unchanged vs the 10-08 snapshot. The exposures table lags a day, so cap outcomes at the last loaded day.
- **Not refreshed:** OTT §B.5 pacing / pre-roll analysis (budget-capped line items, shift-share, rollout range) — no scripts in the repo, working tables `ml_dev.tmp.jv_abf10_bp2_*`; left as the 10-15 analysis with a visible note in the doc (only its CUPED impression-pool table was refreshed). Gate-inference sample (`gates_infer.sql`, 10-12/13) also not re-run.

#### Reconciliation with Binoop's OTT v10 report — 2026-10-20

Binoop's report ("ABF3 v10 — ABF2 Catalog, Three Pruner Arms (OTT)", Databricks notebooks in `/Users/bpulikkal@tubi.tv/ABF_3/`) was compared with ours. Its headline revenue is **unbudgeted only**; ours leads with total revenue. Re-ran our estimator on Binoop's spec (`v10_verification/binoop_reconcile_ott.sql`: outcomes ds 10-10→10-18 from first exposure, pre-period 09-17→09-30, OTT; on-title computed against both the live ABF2-catalog CTE and `ml_dev.tmp.abf3_v10_targeted_titles`):

| Global ITT (unbudgeted rev / TVT) | v4 | v5b | v6 |
|---|---|---|---|
| Binoop | −0.05 / +0.13 | +0.27 / −0.20 | +0.30 / −0.05 |
| Ours on Binoop's spec | −0.062 / +0.121 | +0.270 / −0.195 | +0.311 / −0.038 |
| Ours as published (10-09→10-18, pre 09-25→10-08) | −0.052 / +0.131 | +0.280 / −0.166 | +0.321 / −0.051 |

- **Global numbers reconcile.** Remaining gaps (e.g. v5b TVT −0.166 vs −0.20) come from the window and CUPED pre-period, not from definitions. Total revenue on Binoop's spec: v4 +0.024, v5b +1.057, v6 +0.492 (same as our published, so the "v5b is the money arm on total revenue" conclusion is not an artifact of the window).
- **On-title set was the main difference, and our docs used the wrong set.** On-title ITT unbudgeted revenue against the targeted table: v4 −0.354, v5b +0.902, v6 +0.849 (TVT +0.155 / −0.236 / +0.003); this matches Binoop (−0.34 / +0.90 / +0.84). Against our live ABF2-catalog CTE (299,272 titles): −0.272 / +0.674 / +0.605. **Our published "on-title (ABF2 catalog only)" tables use the 299k catalog, which includes ~74.5k titles not served any v10 cue points (identical cues in every arm), diluting the on-title lift by roughly a quarter.** The correct treated set is the 224,739 targeted titles. Band, movie/episode and below-control tables in our docs also key on the ABF2 catalog (`bands_all_lifts.sql` builds bands from the same CTE); not re-run, likely diluted too, although the below-control (served-list-based) cuts matched Binoop's closely.
- **n note:** the exposures table now includes 10-19 exposures, so ITT n/arm is now 10.48M (was 9.74M). These devices have no outcomes before the cap, so relative lifts barely move. ToT (live-catalog definition) 5.04M/arm matches Binoop's 5.02M; ToT against the targeted table is 4.74M.
- **Resolved the same day:** all three docs were re-run with the targeted-title set (see the next section).

#### v10 docs re-run on window 10-09 → 10-19 with targeted-title on-title set — 2026-10-20

The three docs in `ABF Files/` were rebuilt. **Window: 2026-10-09 → end of 2026-10-19** (outcomes capped 2026-10-20 00:00 UTC). The user asked for "10/9–10/20", but exposures are loaded only through the end of 10-19 (10-20 is a partial day), so 10-20 is excluded; ITT devices/arm now OTT 10.48M, mobile 3.31M, web 6.99M. Pre-period (09-25→10-08) unchanged. **On-title, ToT, band, type and below-control now use the 224,739 titles in `ml_dev.tmp.abf3_v10_targeted_titles`** (queries add `content_id IN (targeted)` to the `abf2` CTE in `headline_all_lifts.sql`, `bands_all_lifts.sql`, `gate_replay_all.sql`, `watch_depth.sql`). Previous docs backed up in `v10_verification/prev_20261019/` (`docs/`, `sql/`, `results/`); new outputs in `results_20261020/`. Built by `edit_ott_r3.py` (OTT, from the original 10-15 doc as template) and `make_narr_r3.py` + `build_report.py` (mobile/web).

Global ITT CUPED (total revenue / TVT; v4 | v5b | v6):

| Platform | Total revenue | TVT |
|---|---|---|
| OTT | +0.025% ns \| +1.113% sig \| +0.529% sig | +0.113% ns \| −0.162% sig \| −0.025% ns |
| Mobile | −1.660% \| +0.676% \| −1.277% (all sig) | +0.058% ns \| −0.422% sig \| −0.197% ns |
| Web | −1.635% sig \| +1.853% sig \| −0.329% ns | −0.143% \| +0.248% \| +0.049% (all ns) |

- **On-title ITT unbudgeted revenue (targeted set):** OTT −0.319% / +0.993% / +0.920% (all sig); mobile −3.006% / +2.431% / −1.569% (all sig); web −2.012% sig / +4.123% sig / +0.601% ns. These are larger in magnitude than the earlier catalog-based tables.
- **Conclusions unchanged in direction:** v5b wins on total revenue on every platform (mobile with a significant TVT dip −0.42%); v6 is a safe positive on OTT, loses on mobile, flat on web; v4 is parity on OTT and loses on mobile/web.
- **Narrative changes from the re-run:** mobile v5b power-viewer TVT is now significant (−0.741%); OTT band-level TVT: only v5b 1–3 (−0.53%) is significant (v6 4–6 −0.42% is ns now); web v4 episode loss (−4.00%) and v5b movie gain (+2.40%) are now significant; web v4 on-title unbudgeted is significantly negative (−2.01%) even though global unbudgeted is ns; web v5b 10–12 at/above and 13+ below are significant in the below-control table.
- **Gate replay and viewing depth** barely moved (the replay already ran on served titles only).
- **Not refreshed:** OTT §B.5 pacing / pre-roll analysis (10-15 window, flagged in the doc); no Statsig re-reconciliation; the pre-period still differs from the independent OTT analysis's (09-17→09-30), which explains the small global differences with it (e.g. v5b TVT −0.162% vs −0.20%).
- **"Global numbers" section added to the OTT doc (2026-10-20, last section after Appendix C):** two Binoop-style combined cross-platform tables (ITT, unbudgeted revenue and TVT, no impressions): all titles and the 224,739 targeted titles. Combined lift = 0.85×OTT + 0.10×mobile + 0.05×web (shares supplied by the business per the independent OTT report's Appendix C), CI treats platforms as independent, n = summed ITT devices per arm. All titles: revenue v4 −0.233% sig / v5b +0.422% sig / v6 +0.223% sig; TVT +0.095% ns / −0.167% sig / −0.039% ns. On-title: revenue −0.673% / +1.294% / +0.655% (all sig); TVT +0.097% ns / −0.237% sig / −0.020% ns. The on-title weighting is an approximation (company-level shares applied to on-title lifts); the exact version would weight by each platform's targeted-title share of baseline revenue/TVT (not queried). Script: `v10_verification/add_global_section.py`; pre-edit copy in `prev_20261020_pre_global/`. Combined total/budgeted revenue and impressions (not in the doc): total revenue v4 −0.23% / v5b +1.11% / v6 +0.31% (all sig).
- **Housekeeping:** `results_20261020/gate.tilde` is an empty leftover temp file (sandbox could not delete it); safe to remove.

#### ABF3 pruning algorithms repo — T1/T2/T3 pruners behind v10 (recorded 2026-10-20)

**Repo:** `github.com/adRise/abf3_pruning_algos` (private). Local clone: `~/Documents/GitHub/abf3_pruning_algos` (single commit `b805cca`, "Add ABF3 treatment-arm pruners (T1/T2/T3) and docs"). Contents: three standalone pruner scripts (plain Python 3, no dependencies), `docs/` (one md per pruner plus the combined `ABF3_pruners_report.html`), `SHA256SUMS.txt`, README. Docs dated 2026-10-07, validation updates 2026-10-08; status "offline-projected, OTT only".

**Mapping to v10 arms** (all use only raw ABF3 candidates plus classifier scores; no ABF2 or human input; same interface as `pruning_v2.py`: `prune_cuepoints(candidates, duration, content_type)`, `prune_times(...)`, JSONL CLI):

| v10 arm | `slasher_version` | File | Idea |
|---|---|---|---|
| Control | n/a | none | ABF2 human-curated cue points |
| T1 | `v4` | `abf3_pruner_t1_equal_load_v4.py` | Equal ad load to ABF2 per segment. Replaces humans at no load change; the "pure replacement" baseline. |
| T2 | `v6` | `abf3_pruner_t2_targeted_load_v6.py` | T1 plus about +7% filled breaks and impressions in movies 60–120 min only (calibrated +6.7% on the unseen day; κ hit its floor of −2). |
| T3 | `v5b` | `abf3_pruner_t3_abf2_density_v5b.py` | ABF2's cue count per type and duration bucket, placed where ad config accepts requests. Higher load; the surplus cue is parked early (before the initial slot) where config rejects it. |

**T1/T2 rules:** six groups (series <30, 30–60, 60+ min; movies <60, 60–120, 120+ min). Candidates only at or after 360s; utility = classifier score + 2 × value(t), value = (E[revenue] − κ × RPI × E[impressions]) / MED_R from lookup tables; keep candidates with u ≥ τ greedily, never closer than 210s to a kept cue; fallback keeps the best candidate, so every title with candidates keeps at least one cue. τ is solved so filled breaks match ABF2 and κ so impressions per filled break match ABF2. κ stops post-17:00 pods (longer) from inflating ad time. T2 differs from T1 only in the parameters (movie 60–120m: τ 1.702→4.866, κ 0.52→−1.99; other groups recalibrated slightly).

**T3 rules:** target n = max(1, round(rate[type, duration bin] × hours)) with 11 duration bins per type (rates about 8.0–8.8 cues/hour); an exact dynamic programme over sorted candidates picks n cues at least 240s apart that maximize expected accepted requests (plus 0.02 × score tie-break), using acceptance curves from logs (first-cue and after-served-break gap curves, Early/Late branch).

**Ad-config findings the pruners rely on (from `ABF3_slasher_v4.md`):** configs branch at content position 17:00 (Early/Late; Late has longer pods: episodes 3.2–3.6 ads vs 2.2–2.4); episode initial slot 6–7 min and sharp; movie first midroll effectively blocked until about 15 min; spacing fuzzy and counted from the last *filled* break; also a wall-clock gap since the last midroll across titles. Rules are fit to configs as of early October 2026 (identical Oct 5 and Oct 7). If configs change, refit.

**Offline projections vs ABF2, topline = all OTT viewing, central (pessimistic):**

| Arm | Revenue | Impressions | TVT from load |
|---|---|---|---|
| T1 / v4 | −0.01% (−0.17%) | 0.00% (−0.19%) | about 0% |
| T2 / v6 | +0.43% (+0.27%) | +0.56% (+0.37%) | −0.04% (−0.02%) |
| T3 / v5b | +1.31% | +1.73% | −0.11% |

Each also carries a possible 0 to −0.1% TVT from placement quality (v9 showed an unexplained −0.10%). The T2−T1 and T3−T1 contrasts measure the engagement cost of extra load with ABF3 placements (about +0.6% and +1.7% total impressions). Universe→topline conversion uses v9's ratios (impressions ×0.27, revenue ×0.21). Chance of a statsig TVT drop from load: T1 about 2.5%, T2 about 4–39% (central 7–10%), T3 about 30–70%.

**Observed vs projected, for context:** v10 live results (10-09→10-18, global ITT CUPED) came out above the offline projections on OTT: v5b revenue +1.07% sig, v6 +0.48% sig, v4 +0.015% ns. Topline TVT: v5b −0.17% sig (nominal), v6 −0.05% ns, v4 +0.13% ns. The directions and ordering (v5b > v6 > v4 on revenue) match the projections.

**Simulator caveats (from the 10-08 validation updates):**
- The environment model (HistGradientBoosting acceptance with AUC about 0.98 and fill models, session replay of 1.02M Oct 6 views) was validated against v9 (ABF3 v2 vs ABF2). The v9 treatment arm switched back to ABF2 at about 17:56 UTC on Oct 6; clean evidence is Oct 4, 5 and Oct 6 before 17:00 UTC.
- On clean windows it under-predicts how much v2 loses to ABF2 by 0.7–0.9pt, concentrated in movies 60–120m, movies 120m+ and series 30–60m. Cause not found: per-view history closes about 20% of the gap; user carry-over, title mix, config routing and time features were ruled out. The earlier "within 0.3pt" claim is withdrawn. This is why the pessimistic ranges exist. v5b's biggest contribution (short series, +20% impressions) is where the simulator is accurate.
- T3's load increase is concentrated in short series (+20.4% impressions) and barely touches movies (first midroll floor about 15 min).
- Not modeled: placement-quality effects on engagement, retention, binge spillover, tier feedback loops. v3 (`prune_abf3_v3.py`) is superseded and must not be used (matched breaks but moved them past 17:00, +5.4% impressions).

**Data sources named in the docs:** `core_dev.statsig.first_exposures_ads_abf_3_v9_abf2_titles_only`, `core_prod.ads.server_impressions` / `impressions`, `core_prod.session.video_session`, `core_prod.adconfigdb_cdc.ad_configuration_v2` (62,833 configs), `ml_prod.ads.abf3_slasher_cuepoints` (raw candidates, about 15.5 per title), `core_prod.tubidw.experiment_summary` (286 ad-load arms; TVT −0.065%, capped TVT −0.035%, revenue +0.83% per +1% impressions). Segment load sensitivity from `ads_ott_dynamic_ad_load_v1_2`, `ads_ott_dynamic_spacing_v4`, `ads_ott_auto_rebalance_midroll_v2` (movies 60–120m elasticity −0.090 ± 0.012; best revenue per unit TVT, which is why T2 targets it).

**Where the research code is:** not in this repo. It lives in the original working folder `Ads/abf_sim/` (`t11_*` environment model and simulator, `t12_*` T1/T2 learning, `t13_*` T3, `t14_*` T2 segment sensitivity and build). The repo pruners are copies of `prune_abf3_v4.py`, `prune_abf3_v6.py` and `prune_abf3_v5b.py`, with identical output on 3,000 sampled titles each. They slash the 224,739 experiment titles in about 18s (T1/T2) and 52s (T3). Paths inside `docs/` refer to the original folder.

**Same title set:** the 224,739 titles the pruners were built and projected on are the ABF2 ∩ served set, which equals `ml_dev.tmp.abf3_v10_targeted_titles` (see the on-title section below).

#### Where ABF2 cue points live — reference (recorded 2026-10-19)

There is **no dedicated ABF2 cue-point table**. ABF2 = live `cue_points_abf` in `core_prod.tubidw.content_movie_stream` / `content_episode_stream`, **excluding** `cue_points_info = 'abf3_pruned_v8'` and `core_dev.dsa.temp_bp_abf_v8_all_titles`, which leaves about 300k titles. Query: `abf2_cuepoints.sql`. Count comparison vs a slasher version: `abf_cuepoint_count_vs_abf2.sql`. Caveats:
- Live snapshot only. Titles later overwritten by ABF3 lose their ABF2 cues, so add each new rollout to the exclusions.
- `cue_points_info` is not an ABF2 tag: ~219k null, ~79.6k "imported from partner's metadata" (these still look like ML output), ~400 other notes.
- `slasher_version = 'v2'` in `ml_prod.ads.abf3_slasher_cuepoints` is ABF3 Slasher v2, **not** ABF2.
- `core_dev.dsa.temp_bp_abf_v2_exp_titles` is the Apr-2026 ABF1/ABF2 title-assignment list and has no cue points.

#### ABF2 catalog size and on-title set — verified 2026-10-20

- **ABF2 catalog (definition above, non-empty `cue_points_abf` excluding `'[]'`, `'{}'`, `'{0.0}'`, `''`) = 299,272 titles** (253,352 episodes + 45,920 movies); 219,246 have `cue_points_info` null.
- **"On-title" set = 224,739 titles** = ABF2 catalog ∩ titles served in `ml_dev.tmp.abf3_new_pruner_cuepoints`. The other 74,533 ABF2 titles have no served v10 cue points.
- **Identical to `ml_dev.tmp.abf3_v10_targeted_titles`** (columns `content_id`, `content_id_type`, `title_type`; 224,739 rows, all distinct). Set differences in both directions = 0, and every targeted title is in the ABF2 list. That table is a fixed list, so it can replace the live stream-table rebuild as the on-title source (queries not switched yet; docs unchanged).
- **Served table composition** (`abf3_new_pruner_cuepoints`, all arms): 418,671 distinct titles = 224,739 ABF2-class + 187,656 Pre-ABF + 6,276 Other. Seen in the user's screenshot, which also shows `ml_dev.tmp.abf3_oracle_cuepoints` = 224,736 titles (all ABF2-class) and production `ml_prod.ads.abf3_slasher_cuepoints` (latest date) = 418,668 (224,739 ABF2-class, 187,655 Pre-ABF, 6,274 Other). The screenshot's "ABF2-class" definition is not visible; counts agree with our filter. The oracle table is not used in v10.

---

### Aniruddha Basak's Per-Tolerance-Spacing Proposal — 2026-07-06

**Context:** Aniruddha Basak (Staff ML, abasak@tubi.tv) is analyzing ABF3 alongside the ad-config/spacing experiments and shared a first-draft analysis + XP proposal doc: **"Ad-Break Optimization: Analysis & Experiment Proposal"** — [Google Doc `1RsSXIIfFK6Z-EMjxRKalRTyacXNvKlrVTuN2oEaNat0`](https://docs.google.com/document/d/1RsSXIIfFK6Z-EMjxRKalRTyacXNvKlrVTuN2oEaNat0/edit). Public link-viewable; read via plain-text export URL (`.../export?format=txt`) since the gsuite OAuth token is currently revoked. Posted 2026-07-02 in #ml-video-understanding tagging bpulikkal, agupta, Aidean, dmackinnon; he'll block time next week to review. (He also DM'd two questions 07-02: the v7 title list — `core_dev.dsa.temp_bp_abf_v6_exp_titles`, 1,084 titles — and the raw cuepoint ratio pre-ABF vs ABF3+slasher, which we re-validated live 07-02: **7.44 → 8.32 mean, ratio ≈1.12×**, matching his doc's 8.23/1.11×–1.25×.)

The doc has **two tabs**: Tab 1 is an earlier draft (single arm, used "The Equalizer" as example, and classifier-accepted-39 as "slashed"); **Tab 2 is the current/corrected version** (two-arm design, correct DP-pruned `cue_points_abf` data, Mad Money / Jeepers Creepers 2 examples). Read Tab 2.

**Core thesis:** ABF3 and spacing (MTML) are two orthogonal ad-load levers. ABF3 supplies denser *candidate* cuepoints, but at current V6 spacing most extras are blocked by the timing filter — so monetize ABF3 density without TVT harm via **per-tolerance spacing**: lower spacing only for *tolerant* devices (high_lvl_1+2, ~30%) to unlock ABF3 positions, keep mid/sensitive unchanged.

**Design (Tab 2, two arms, same control, top-1,000-TVT titles, 10% each):**

| | Control | Arm B (conservative) | Arm A (aggressive) |
|---|---|---|---|
| Tolerant cuepoints | pre-ABF | ABF3 slashed | ABF3 slashed |
| Tolerant spacing | 576s | 576s | **480s (−33% preQVD)** |
| Sensitive/mid | pre-ABF, 720s | unchanged | unchanged |

Key design move: **sensitive devices keep their current pre-ABF cuepoints** → zero impression change for them → TVT structurally protected. Start with B (within proven evidence), escalate to A only if TVT holds 7 days; 3-day tripwire (raise 480s→576s if tolerant TVT < −0.5%).

**Estimated impact (his):** Arm B +1.5% on-title / +0.4% global OTT, flat TVT; Arm A +3.8% on-title / +1.1% global, flat TVT (monitor).

**Evidence base he cites:** (1) MTML −17% spacing XP → +0.60% rev, −0.30% TVT (ns), fill rate per break unchanged (3.10→3.11); (2) v3 tolerance-stratified TVT — only high_lvl_1+2 absorb extra breaks at ~flat TVT (−0.12%), while mid (heaviest viewers, 18.9 hrs/device) and low show real harm (−1.11% / −0.85%); (3) v4 pure-quality effect small (+0.29% rev at matched density); (4) his cuepoint-ratio distribution (movies 1.11×, episodes 1.25×) matches ours.

#### Our feedback / commentary on the proposal (bpulikkal, 2026-07-06)

**Where it aligns with our v6/v7 findings:**
- His cuepoint-ratio numbers match ours (8.23 vs our 8.32; ~1.11–1.25×).
- Revenue = ad-load-driven at constant fill is consistent with our per-watch-hour decomposition (CPM flat, revenue scales with impressions/hr).
- Strategic direction is exactly where our v7 mechanism hunt converged: **the real lever is an ad-config/spacing lever, not cuepoint count** (our "stop tuning density; target placement/timing").

**Tensions / pushback to raise:**
1. **"At current V6 spacing ABF3 serves the same positions as pre-ABF" is overstated and internally inconsistent.** Our v7 measured **+3.53% on-title rev / +3.86% impressions at unchanged v6 spacing** — impossible if positions were identical. His own Tab 2 §3.4 says ABF3-slashed serves MORE breaks than pre-ABF at *every* spacing level (DP pruner covers full duration; pre-ABF stops early / has wide gaps). The exec-summary "blocked" claim contradicts his own body + our data. The truth is in between: ABF3 adds breaks now mainly on *sparse* pre-ABF titles (gap-filling), which is precisely our v6/v7 heterogeneity result (sparsest-density deciles gain most).
2. **The flat-TVT-for-tolerant bet contradicts our strongest v7 mechanism finding.** We found the movie TVT cost comes from a **sustained tighter cadence** (~13.5 vs ~15.1 min through long movies) with a **flat dose-response** — cutting density 23–40% recovered ~zero TVT (v6→v7 slope ≈0). Arm A *lowers spacing further* for tolerant devices → tightens cadence exactly where we localized the damage. The proposal's whole safety case rests on tolerance-tier heterogeneity being real AND stable at +17–50% break volumes, but the v3 evidence only covers ~+5%; he flags this extrapolation as "risk" himself (Arm A effective +4.8% dilution-adjusted, right at the +5% edge).
3. **The revenue multiplier leans on a metric the doc itself calls inflated.** His "2.6× / 0.62% ABF3 quality multiplier" derives from v3's +21% breaks → +13% rev — but his §3.5/§3.6 say that +21% breaks/hr was inflated by TVT-denominator shrinkage (72% of titles had FLAT break count). So the headline +5–6% is built partly on a chain he disowns two sections later. Rebuild the estimate off the impression-simulation (his Tab 2 §6.1) rather than the inflated ratio.
4. **Minor:** title count flips between **1,084** (correct — our `temp_bp_abf_v6_exp_titles`) and **1,158** (his simulation set) — reconcile. Also his framing "sensitive would gain +10.9% breaks if given ABF3" (why sensitive keeps pre-ABF) is sound and matches our below/above-control per-title analysis.

**Net assessment:** The per-tolerance-spacing framing is a genuinely good idea and complements our conclusion (lever = ad-config, not cue-point count). But **"flat TVT" is the crux and it directly bets against our count-driven / flat-dose-response / movie-cadence finding.** Arm B is defensible (within v3 evidence); Arm A needs the 3-day TVT tripwire and its revenue estimate rebuilt without the inflated multiplier. Also note: this is orthogonal to — but does not replace — the still-uncomputed **`me_score`/`e_score` graduation gate**, which remains the formal decision metric for where to sit on the revenue/TVT frontier.

**Status:** Draft DM reply to his two questions prepared (title list + 1.12× ratio); not yet sent. Feedback above not yet sent to him. Review meeting to be scheduled next week.

---

### ABF3.0 Title Coverage

ABF3.0 was only run on a **subset of titles** (414 titles) due to the time it takes to run the model on the full catalog — the team wanted to launch the experiment quickly rather than wait for full coverage.

Key implications for analysis:
- **414 titles** have ABF3.0 cue points; all other titles use ABF2.0
- These 414 titles represent only **~0.7% of total watch time** since the experiment started
- Roughly **6% of users** watched at least one of these titles during the experiment
- Analysis must be **restricted to these 414 titles** — users watching other titles see no treatment difference between arms, so including them would dilute the signal significantly

### Contaminated Titles (Must Exclude)

Of the 414 ABF3.0 titles, **136 had missing ABF2.0 cue points**. This means these titles were serving ABF3.0 cue points to **all users regardless of experiment arm** — both control and treatment. There is no valid comparison for these titles.

These 136 titles must be **excluded from analysis**, leaving **278 titles** eligible for the experiment results.

### Broader Discovery: ~50% of Titles Have No ABF2.0 Cue Points

Investigating the 136 contaminated titles revealed a much larger issue: roughly **50% of titles that had any TVT in the past two weeks have never had ABF2.0 cue points processed**. These titles also represent approximately **50% of total TVT** over that period. Despite the 3% revenue lift ABF2.0 demonstrated, it was never applied to the full catalog.

This represents a significant untapped revenue opportunity.

#### ABF2.0 vs ABF3.0 for Uncovered Titles

The question is whether to backfill these titles with ABF2.0 or go directly to ABF3.0. Early experiment results on the 278 eligible titles show:
- **+5% unbudgeted revenue lift** for ABF3.0 over ABF2.0
- **-0.6% TVT drop** for ABF3.0 vs ABF2.0 — ABF3.0 appears to hurt engagement

This trade-off (more revenue, less watch time) is likely a consequence of the higher cue point density in ABF3.0 not being controlled for in the experiment.

**Updated decision: Process uncovered titles with ABF2.0 first, then experiment with ABF3.0.**

Rationale:
- The uncovered titles represent ~50% of TVT. A -0.6% TVT drop observed on 278 small titles could be much larger at this scale, and the impact would be hard to reverse quickly.
- If we skip ABF2.0 entirely, we permanently lose the ability to measure ABF3.0 vs ABF2.0 on these titles — no counterfactual exists.
- ABF2.0's +3% revenue lift is proven with no known TVT cost — it's a safe, measurable gain.
- The current ABF3.0 experiment signal is too noisy to act on at scale: only 278 eligible titles, 0.7% TVT, and quality/quantity effects are confounded.
- Processing with ABF2.0 first establishes a clean baseline, enabling a proper ABF3.0 experiment on these titles later.

---

## The Problem

| | Old Model | New Model |
|---|---|---|
| Cue points per title | Fewer | More |
| Positioning quality | Baseline | Claimed better |
| Min spacing policy | 4 min | TBD (calibrated) |

A naive A/B test (old vs new model) would mix quality and quantity signals, making it impossible to attribute any engagement change to positioning quality alone.

---

## Experimental Design

A **three-arm randomized controlled trial (RCT)** is used to disentangle the two effects.

### Arms

| Arm | Model | Min Spacing | Traffic |
|---|---|---|---|
| A — Control | Old | 4 min | 40% |
| B — New + Wide | New | ~7 min (calibrated) | 30% |
| C — Old + Wide | Old | ~7 min (calibrated) | 30% |

The wider spacing in Arms B and C is calibrated so that the **average number of realized ad breaks per session is approximately equal** across all three arms. This is the key design choice that enables clean comparisons.

### Key Comparisons

| Comparison | What It Isolates |
|---|---|
| **B vs C** (primary) | Quality effect — same spacing, different model |
| **A vs C** (secondary) | Spacing/quantity effect — same model, different spacing |
| **A vs B** (exploratory) | Net business effect — overall combined impact |

---

## Calibration

Before launch, a calibration simulation is run on a representative sample of 100–200 content titles to find the minimum spacing value for Arms B and C that equates average ad breaks to Arm A.

Example output:
```
Old model @ 4 min → avg 5.2 breaks/content   ← Arm A baseline
New model @ 5 min → avg 6.8 breaks/content
New model @ 6 min → avg 5.8 breaks/content
New model @ 7 min → avg 5.1 breaks/content   ← Arm B target ✓
Old model @ 7 min → avg 4.9 breaks/content   ← Arm C target ✓
```

---

## User Assignment

Users are assigned to arms via hash-based randomization:

```
hash(user_id) % 100
  [0–39]  → Arm A (40%)
  [40–69] → Arm B (30%)
  [70–99] → Arm C (30%)
```

---

## Cue Point Selection Algorithm

When multiple cue points fall within a spacing window, the spacing enforcement algorithm selects which to use:

```python
last_break_time = 0
for cue_point in sorted_cue_points:
    if (cue_point.time - last_break_time) >= min_spacing:
        show_ad_break(cue_point)
        last_break_time = cue_point.time
```

**Selection strategies:**
- **First-available** — deterministic, simplest
- **Score-based** — uses model confidence score to pick highest-quality cue point in each window (preferred for Arm B)
- **Random** — unbiased but suboptimal

---

## Metrics

### Primary (B vs C — quality effect)
- Total Watch Time (TVT)
- Qualified View Days (QVD)
- Conversion rate
- Revenue Per User (RPU)

### Secondary
- Realized ad breaks per session
- Ad impressions per session
- Drop-off rate at/after ad breaks
- Inter-break watch time

### Diagnostic
- First break drop-off rate
- Break completion rate
- Content completion rate

---

## Statistical Analysis Plan

**Primary regression (B vs C):**
```
outcome ~ treatment + content_duration + genre + user_segment + realized_ad_breaks
```

**With interaction term for residual quantity differences:**
```
outcome ~ treatment + realized_ad_breaks + treatment × realized_ad_breaks + covariates
```

**Tests used:** Two-sample t-tests or Mann-Whitney U; chi-square for SRM detection.

**Subgroup analyses:** content type (short vs long-form), genre, user engagement tier, device, time of day.

---

## Required Logging Schema

Per session:
```
user_id, content_id, experiment_arm, cue_points_available, cue_points_shown,
min_spacing_policy, content_duration, watch_time, ad_impressions, revenue,
completion_rate, drop_off_points
```

---

## Success Criteria

| Tier | Signal |
|---|---|
| Strong success | B vs C: significant positive engagement AND revenue |
| Moderate success | B vs C: positive engagement, neutral/small negative revenue, positive net LTV |
| Inconclusive | B vs C: null or inconsistent — requires deeper investigation |
| Failure | B vs C: significant negative effect |

---

## Timeline

| Phase | Duration |
|---|---|
| Pre-experiment (calibration, setup) | 2–3 weeks |
| Experiment execution | 4–6 weeks |
| Analysis and reporting | 1–2 weeks |

---

## Key Data Asset

`impressions_2026-02-28.csv` — 1,000 sample ad impression records across 21 integration types (GENERIC_VAST, TRADE_DESK, DV360, INTERNAL, Amazon APS, etc.) used for baseline metrics and calibration.

---

## Open Questions (Pre-Launch)

- Does the new model output confidence/quality scores per cue point?
- What is the current baseline average ad breaks per content (by type)?
- What is the minimum detectable effect (MDE) for TVT and RPU?
- Are there policy/legal constraints on ad break frequency?
- Is there sufficient historical data for subgroup stratification?

---

## Pre-Launch Checklist

- [ ] Confirm new model output format (cue points + scores)
- [ ] Pull baseline metrics from historical data
- [ ] Run calibration simulation for Arm B/C spacing
- [ ] Define subgroups for heterogeneity analysis
- [ ] Set up experiment tracking dashboard and SRM monitoring
- [ ] Draft experiment launch checklist
- [ ] Schedule design review with stakeholders
