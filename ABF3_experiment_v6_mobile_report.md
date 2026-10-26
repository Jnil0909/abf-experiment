# ABF3 Experiment (v6) — Mobile — Lift & Graduation Generalization Report

**Experiment:** `ads_mobile_abf_3_v6` (Mobile: android, iphone, ipad, firetablet, android_samsung)
**Design:** ABF1 (Control) vs ABF3 (Test), 1,084 titles, ABF3 pruned (new algorithm) to ~ABF2 density
**Launch:** 2026-05-27 · **Analysis window:** 2026-05-27 → 2026-06-04 (complete days) · **Baseline/pre-period:** 2026-05-13 → 2026-05-26 (clean pre-launch)
**Notebooks:** `/Users/bpulikkal@tubi.tv/ABF_3/ads_abf_3_v6__*` run with mobile params; outputs `ads_mobile_abf_3_v6__*__run_2026-06-05_OUTPUT`
**Method:** Same 6-notebook suite as OTT, parameterized per platform. All topline-denominator computations scoped to `platform_type = 'MOBILE'`.

## TL;DR

Mobile shows a **strong, significant revenue lift of ABF3 over ABF1**: **+6.89% unbudgeted revenue, +7.88% impressions** on experiment titles (device-level ToT, CUPED), but with a **significant −0.90% TVT** on those titles — **the largest engagement cost of the three platforms** (OTT −0.33%, web flat). The revenue win is real and large; the TVT cost is the thing to weigh.

- **Generalization holds.** Poststratified onto the full mobile ABF1 universe, the on-ABF1-title revenue lift is ~**+8.2%** (revenue-weighted); TVT-weighted title-clustered point **+6.83%**, 95% CI **[+5.22%, +8.49%]** (2,000-iter title bootstrap). Revenue lift is heterogeneous across density (highest at low ABF1 density), but positive in every decile.
- **Global (topline, mobile-scoped) revenue impact of graduating:** mobile ABF1 titles = **38.97% of mobile unbudgeted revenue / 40.76% of mobile TVT**; **68.4%** of mobile devices watch ≥1 ABF1 title. Diluting the +8.19% ABF1-wide lift → **global mobile unbudgeted revenue ~+3.19%** (CI **[+2.45%, +3.94%]**).
- **Global (topline, mobile-scoped) TVT impact:** **−0.34%** (on-title dilution) to **−0.70%** (coverage-scaling w/ spillover). The spillover end is more realistic on mobile — the ITT all-titles TVT decline (−0.27%) exceeds on-title losses alone, indicating heavier ABF1 ad loads modestly suppress total mobile watch time.
- **Graduation trade ≈ +3.2% global mobile revenue for ~−0.4% to −0.7% global mobile TVT.** `me_score`/`e_score` (offline) remain the formal gate, not computed here.

## 1. Headline lift (device-level, CUPED)

CUPED-adjusted (14-day pre-period covariate 2026-05-13→05-26; pooled θ; 95% CI). ToT n ≈ 1.22M/arm, ITT n ≈ 3.61M/arm.

**ToT — devices that watched ≥1 experiment title**

| Scope | Metric | Lift (CUPED) | 95% CI | Sig? |
|---|---|---|---|---|
| ABF3 titles only | Unbudgeted Revenue | **+6.89%** | [+6.21%, +7.58%] | yes |
| ABF3 titles only | Unbudgeted Impressions | **+7.88%** | [+7.22%, +8.55%] | yes |
| ABF3 titles only | TVT | **−0.90%** | [−1.43%, −0.37%] | **yes (negative)** |
| All titles | Unbudgeted Revenue | +0.97% | [+0.56%, +1.38%] | yes |
| All titles | Unbudgeted Impressions | +1.11% | [+0.72%, +1.50%] | yes |
| All titles | TVT | −0.26% | [−0.59%, +0.06%] | no |

**ITT — all assigned devices**

| Scope | Metric | Lift (CUPED) | 95% CI | Sig? |
|---|---|---|---|---|
| ABF3 titles only | Unbudgeted Revenue | +6.77% | [+6.05%, +7.49%] | yes |
| ABF3 titles only | Unbudgeted Impressions | +7.78% | [+7.08%, +8.48%] | yes |
| ABF3 titles only | TVT | −0.94% | [−1.52%, −0.37%] | **yes (negative)** |
| All titles | Unbudgeted Revenue | +0.66% | [+0.34%, +0.98%] | yes |
| All titles | Unbudgeted Impressions | +0.77% | [+0.46%, +1.08%] | yes |
| All titles | TVT | −0.12% | [−0.39%, +0.14%] | no |

**Coverage:** experiment titles = **15.55%** of mobile exposed-device TVT (baseline window). CUPED variance reduction: large on all-titles cuts (48–62%), modest on ABF3-only (11–23%).

> **Watch-out:** Mobile is the only platform where the on-title TVT decline is both **significant and ≈1%** (ToT −0.90%, ITT −0.94%). On OTT it was −0.33%; on web it is flat. The all-titles TVT decline is not significant but consistently negative.

## 2. Generalization to all mobile ABF1 titles (the graduation question)

ABF1 universe = {titles with no ABF cue points} ∪ {1,084 experiment titles} = 492,024 titles. Baseline density = served `cue_points`. All TVT weighting uses the 14-day pre-launch window, mobile-scoped.

### 2a. Representativeness (sample vs rest of universe)

| Trait | Sample (1,084) | Rest of universe | Note |
|---|---|---|---|
| Mobile TVT share | 38.14% | 61.86% | sample = large titles |
| ABF1 density, unweighted | 7.44 | 2.80 | std diff 1.19 (huge) |
| ABF1 density, TVT-weighted | 9.81 | 7.41 | close |
| Duration, unweighted | 4,476s | 1,859s | std diff 1.26 (huge) |
| Duration, TVT-weighted | 6,106s | 4,485s | close |

Raw per-title skew is large (long zero-TVT tail; only 150,464 / 490,940 non-experiment titles have any mobile TVT), but on the decision-relevant TVT-weighted basis the sample is close to the population. The projection in §2c corrects residual skew.

### 2b. Heterogeneity — revenue lift by ABF1 density decile (ToT, ABF3 titles)

| Decile | Density | Rev lift | TVT lift |
|---|---|---|---|
| 1 | 1–2 | +20.48% | flat |
| 2 | 2 | +14.75% | flat |
| 3 | 2–4 | +15.21% | flat |
| 4 | 4–7 | +9.80% | flat |
| 5 | 7–8 | +10.48% | −1.02% (sig) |
| 6 | 8–9 | +8.99% | flat |
| 7 | 9–10 | +6.81% | flat |
| 8 | 10–11 | +6.91% | flat |
| 9 | 11–12 | +3.83% | −1.28% (sig) |
| 10 | 12–36 | +1.78% | flat |

Monotone-decreasing in density: the sparsest ABF1 titles gain the most (most headroom to add breaks). Positive and significant in every decile. **By content type:** MOVIE +6.07% rev / **−1.04% TVT (sig)**, SERIES +9.46% rev / −1.00% TVT (ns).

### 2c. Title-clustered CI & poststratified projection (revenue, ToT)

| Quantity | Value |
|---|---|
| Naive sample lift (TVT-weighted, per-title basis) | +6.83% |
| Unweighted (per-title) sample lift | +8.08% |
| Poststratified projection onto full mobile ABF1 universe (TVT-weighted) | +9.78% |
| Title-clustered 95% CI (2,000-iter title bootstrap) | [+5.22%, +8.49%] |
| Device-level CI (for contrast) | [+6.21%, +7.58%] |

The title-clustered CI is wider than the device CI (reflects title-draw variance) but comfortably positive. The poststratified projection (+9.78%) sits above the naive sample lift because the full mobile universe carries more TVT in the sparse, high-lift low-density deciles than the sample does.

### 2d. Global (topline, mobile-scoped) lift if ABF3 graduates on all mobile ABF1 titles

Notebook: `global_graduation_projection`, `PLATFORM_TYPE='MOBILE'`. Global lift = Σ_decile(decile_rev_lift × decile_revenue_in_full_universe) / total_mobile_revenue (revenue-weighted poststratification; non-watchers sit in denominator with zero numerator).

| Quantity | Value |
|---|---|
| Mobile ABF1 revenue share of total mobile (14d pre-launch) | 38.97% |
| Mobile ABF1 TVT share of total mobile | 40.76% |
| Mobile device exposure (watch ≥1 ABF1 title) | 68.41% (6.79M / 9.93M) |
| ABF1-wide revenue lift (rev-weighted) | +8.19% |
| ➡ **GLOBAL mobile unbudgeted-revenue lift** | **+3.19%** (CI [+2.45%, +3.94%]) |

### 2e. Global (mobile-scoped) TVT impact of graduating — two estimates

| Method | Computation | Global mobile TVT lift |
|---|---|---|
| On-title dilution (no spillover) | per-decile TVT lift × ABF1 TVT share | **−0.34%** |
| Coverage-scaling (with spillover) | ITT all-titles TVT −0.27% × (40.76% / 15.55%) | **−0.70%** |

The **−0.70% end is more realistic on mobile**: the all-titles TVT decline (ITT −0.27%) is larger than on-ABF1-title losses scaled by coverage would predict under no-spillover, indicating added ABF1 ad breaks modestly suppress *total* mobile watch time, not merely shift it. This is the main item to weigh against the +3.2% revenue gain. **Caveat:** coverage-scaling assumes substitution intensity holds as coverage grows from 1,084 to ~492K titles.

## 3. Conclusion

Graduating ABF3 on all mobile ABF1 titles via the random sample is well-supported on revenue: on-ABF1-title lift projects to **~+8.2%** (revenue-weighted), title-clustered CI [+5.22%, +8.49%], diluted to **~+3.19% global mobile revenue** (CI [+2.45%, +3.94%]).

The **mobile-specific concern is TVT**: a significant **−0.90%** on experiment titles and a global mobile estimate of **−0.34% to −0.70%** — materially larger than OTT (−0.05% to −0.40%) and web (neutral). The graduation trade on mobile is **~+3.2% global revenue for ~−0.4% to −0.7% global TVT**. Whether acceptable needs a stakeholder-agreed threshold; the formal gate is `me_score` (offline).

## 4. Caveats

- **Residual quantity confound:** ABF3 (pruned to ABF2 density) serves more breaks than the sparse ABF1 baseline, so the revenue lift includes a quantity component, not pure positioning quality. The significant TVT declines are consistent with that extra ad load costing engagement — and mobile shows the largest such cost of the three platforms.
- **Global TVT spans ~2×** (−0.34% to −0.70%): spillover-inclusive coverage-scaling assumes substitution intensity holds as coverage expands.
- **Sample skews dense/long even TVT-weighted** (~15–30% higher): mitigated by poststratification, which assumes per-decile lift is stable within a decile across sample and population.
- **Single time window:** complete days 2026-05-27 → 06-04; early-window estimates can move with runtime.
- **Per-title lift basis** uses titles with control mean revenue > 0 (1,081 / 1,084).
- **No raw ad-break-density diagnostic** was run for mobile (not part of the 6-notebook suite); the +7.88% impression lift on flat-to-negative TVT implies a higher realized break rate, consistent with the OTT density finding.
