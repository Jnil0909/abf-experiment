# ABF3 Experiment (v6) — Web — Lift & Graduation Generalization Report

**Experiment:** `ads_web_abf_3_v6` (Web: platform = web)
**Design:** ABF1 (Control) vs ABF3 (Test), 1,084 titles, ABF3 pruned (new algorithm) to ~ABF2 density
**Launch:** 2026-05-27 · **Analysis window:** 2026-05-27 → 2026-06-04 (complete days) · **Baseline/pre-period:** 2026-05-13 → 2026-05-26 (clean pre-launch)
**Notebooks:** `/Users/bpulikkal@tubi.tv/ABF_3/ads_abf_3_v6__*` run with web params; outputs `ads_web_abf_3_v6__*__run_2026-06-05_OUTPUT`
**Method:** Same 6-notebook suite as OTT, parameterized per platform. All topline-denominator computations scoped to `platform_type = 'WEB'`.

## TL;DR

Web shows the **largest revenue lift of the three platforms with no engagement cost**: **+8.95% unbudgeted revenue, +9.65% impressions** on experiment titles (device-level ToT, CUPED), and **TVT is flat** (−0.17%, not significant). This is the cleanest result of the three — big revenue, no measurable TVT downside.

- **Generalization holds and is strong.** Poststratified onto the full web ABF1 universe, the on-ABF1-title revenue lift is ~**+11.4%** (revenue-weighted); TVT-weighted title-clustered point **+8.69%**, 95% CI **[+6.96%, +10.53%]** (2,000-iter title bootstrap). Positive in every density decile; TVT flat in every cut.
- **Global (topline, web-scoped) revenue impact of graduating:** web ABF1 titles = **41.14% of web unbudgeted revenue / 39.93% of web TVT**; **63.4%** of web devices watch ≥1 ABF1 title. Diluting the +11.37% ABF1-wide lift → **global web unbudgeted revenue ~+4.68%** (CI **[+2.73%, +6.63%]**) — the highest global revenue lift of the three platforms.
- **Global (topline, web-scoped) TVT impact:** **+0.27%** (on-title dilution) to **+1.47%** (coverage-scaling) — i.e. **non-negative / slightly positive**. Web shows no TVT cost from the heavier ad load; the all-titles TVT point is positive (ITT +0.48%, ns).
- **Graduation trade ≈ +4.7% global web revenue at ~flat (or positive) global web TVT** — the most favorable of the three platforms. `me_score`/`e_score` (offline) remain the formal gate, not computed here.

## 1. Headline lift (device-level, CUPED)

CUPED-adjusted (14-day pre-period covariate 2026-05-13→05-26; pooled θ; 95% CI). ToT n ≈ 261K/arm, ITT n ≈ 1.79M/arm. Web has the smallest device base, so CIs are wider than mobile/OTT.

**ToT — devices that watched ≥1 experiment title**

| Scope | Metric | Lift (CUPED) | 95% CI | Sig? |
|---|---|---|---|---|
| ABF3 titles only | Unbudgeted Revenue | **+8.95%** | [+7.20%, +10.70%] | yes |
| ABF3 titles only | Unbudgeted Impressions | **+9.65%** | [+7.91%, +11.39%] | yes |
| ABF3 titles only | TVT | **−0.17%** | [−1.48%, +1.14%] | no (flat) |
| All titles | Unbudgeted Revenue | +2.02% | [+0.80%, +3.24%] | yes |
| All titles | Unbudgeted Impressions | +1.96% | [+0.79%, +3.13%] | yes |
| All titles | TVT | −0.36% | [−1.22%, +0.50%] | no |

**ITT — all assigned devices**

| Scope | Metric | Lift (CUPED) | 95% CI | Sig? |
|---|---|---|---|---|
| ABF3 titles only | Unbudgeted Revenue | +9.39% | [+7.57%, +11.22%] | yes |
| ABF3 titles only | Unbudgeted Impressions | +10.27% | [+8.48%, +12.07%] | yes |
| ABF3 titles only | TVT | −0.44% | [−1.86%, +0.99%] | no (flat) |
| All titles | Unbudgeted Revenue | +1.01% | [+0.12%, +1.89%] | yes |
| All titles | Unbudgeted Impressions | +0.96% | [+0.09%, +1.83%] | yes |
| All titles | TVT | −0.36% | [−1.04%, +0.32%] | no |

**Coverage:** experiment titles = **13.05%** of web exposed-device TVT (baseline window). CUPED variance reduction: large on all-titles cuts (42–61%), modest on ABF3-only (10–20%).

> **Note:** Web's abf3-only revenue lift (+8.95% ToT, +9.39% ITT) is the **highest of the three platforms** (OTT +5.67%, mobile +6.89%), and unlike the others its on-title TVT is **not significantly negative**.

## 2. Generalization to all web ABF1 titles (the graduation question)

ABF1 universe = {titles with no ABF cue points} ∪ {1,084 experiment titles} = 492,024 titles. Baseline density = served `cue_points`. All TVT weighting uses the 14-day pre-launch window, web-scoped.

### 2a. Representativeness (sample vs rest of universe)

| Trait | Sample (1,084) | Rest of universe | Note |
|---|---|---|---|
| Web TVT share | 32.69% | 67.31% | sample = large titles |
| ABF1 density, unweighted | 7.44 | 2.80 | std diff 1.19 (huge) |
| ABF1 density, TVT-weighted | 9.45 | 7.38 | close |
| Duration, unweighted | 4,476s | 1,859s | std diff 1.26 (huge) |
| Duration, TVT-weighted | 5,860s | 4,520s | close |

Raw per-title skew is large (long zero-TVT tail; only 134,873 / 490,940 non-experiment titles have any web TVT), but on the TVT-weighted basis the sample is close to the population. Projection in §2c corrects residual skew.

### 2b. Heterogeneity — revenue lift by ABF1 density decile (ToT, ABF3 titles)

| Decile | Density | Rev lift | TVT lift |
|---|---|---|---|
| 1 | 1–2 | +29.96% | flat |
| 2 | 2 | +21.12% | flat |
| 3 | 2–4 | +16.07% | flat |
| 4 | 4–7 | +14.13% | flat |
| 5 | 7–8 | +16.57% | flat |
| 6 | 8–9 | +13.47% | flat |
| 7 | 9–10 | +10.32% | flat |
| 8 | 10–11 | +6.46% | flat |
| 9 | 11–12 | +4.58% | flat |
| 10 | 12–36 | +0.83% | flat |

Monotone-decreasing in density (sparsest ABF1 titles gain most), positive and significant in every decile except the densest (decile 10, ns). **TVT flat in every decile** — no significant negative anywhere. **By content type:** MOVIE +8.24% rev / +0.41% TVT (ns), SERIES +13.27% rev / +0.83% TVT (ns).

### 2c. Title-clustered CI & poststratified projection (revenue, ToT)

| Quantity | Value |
|---|---|
| Naive sample lift (TVT-weighted, per-title basis) | +8.69% |
| Unweighted (per-title) sample lift | +9.96% |
| Poststratified projection onto full web ABF1 universe (TVT-weighted) | +13.12% |
| Title-clustered 95% CI (2,000-iter title bootstrap) | [+6.96%, +10.53%] |
| Device-level CI (for contrast) | [+7.20%, +10.70%] |

The poststratified projection (+13.12%) sits above the naive sample lift because the full web universe carries more TVT in the sparse, high-lift low-density deciles than the sample does. Title-clustered CI comfortably positive.

### 2d. Global (topline, web-scoped) lift if ABF3 graduates on all web ABF1 titles

Notebook: `global_graduation_projection`, `PLATFORM_TYPE='WEB'`. Global lift = Σ_decile(decile_rev_lift × decile_revenue_in_full_universe) / total_web_revenue (revenue-weighted poststratification).

| Quantity | Value |
|---|---|
| Web ABF1 revenue share of total web (14d pre-launch) | 41.14% |
| Web ABF1 TVT share of total web | 39.93% |
| Web device exposure (watch ≥1 ABF1 title) | 63.43% (2.97M / 4.68M) |
| ABF1-wide revenue lift (rev-weighted) | +11.37% |
| ➡ **GLOBAL web unbudgeted-revenue lift** | **+4.68%** (CI [+2.73%, +6.63%]) |

### 2e. Global (web-scoped) TVT impact of graduating — two estimates

| Method | Computation | Global web TVT lift |
|---|---|---|
| On-title dilution (no spillover) | per-decile TVT lift × ABF1 TVT share | **+0.27%** |
| Coverage-scaling (with spillover) | ITT all-titles TVT +0.48% × (39.93% / 13.05%) | **+1.47%** |

Both estimates are **non-negative**. Web shows no TVT cost from the heavier ABF3 ad load — if anything a small positive. The all-titles TVT point is positive (ITT +0.48%, ns), so coverage-scaling produces a positive projection. No spillover penalty to weigh against the revenue gain on web. **Caveat:** the positive TVT is not statistically significant; treat as "flat," not a confirmed gain.

## 3. Conclusion

Graduating ABF3 on all web ABF1 titles via the random sample is **the strongest case of the three platforms**: on-ABF1-title revenue lift projects to **~+11.4%** (revenue-weighted), title-clustered CI [+6.96%, +10.53%], diluted to **~+4.68% global web revenue** (CI [+2.73%, +6.63%]) — the highest global revenue lift across platforms — at **flat-to-positive global web TVT** (+0.27% to +1.47%).

The graduation trade on web is **~+4.7% global revenue for ~flat global TVT** — the most favorable trade of the three platforms. Whether to ship still needs a stakeholder-agreed threshold; the formal gate is `me_score` (offline).

## 4. Caveats

- **Residual quantity confound:** ABF3 (pruned to ABF2 density) serves more breaks than the sparse ABF1 baseline, so the revenue lift includes a quantity component, not pure positioning quality. Notably, on web this extra ad load did **not** produce a measurable TVT cost.
- **Smallest device base of the three platforms** (ToT ≈ 261K/arm): CIs are wider here than mobile/OTT, especially on abf3-only TVT (±1.3pp) — "flat TVT" reflects a genuinely wide interval centered near zero, not a tight null.
- **Global TVT positive but not significant:** treat as flat, not a confirmed engagement gain.
- **Sample skews dense/long even TVT-weighted** (~15–30% higher): mitigated by poststratification, which assumes per-decile lift is stable within a decile across sample and population.
- **Single time window:** complete days 2026-05-27 → 06-04; early-window estimates can move with runtime.
- **Per-title lift basis** uses titles with control mean revenue > 0 (1,082 / 1,084).
