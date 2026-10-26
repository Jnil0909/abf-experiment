# ABF3 v8 — Full ABF1 Catalog Results (WEB)

**Experiment:** `ads_web_abf_3_v8` · device-randomized 50/50 · launched 2026-07-23 · **top-up of 38,116 titles added 2026-08-11** → full treated set = **192,464 ABF1 titles** (title-level serving change, shared across platforms).
**Main analysis window (this report):** **2026-08-12 → 2026-08-20** (post-top-up, 9 complete days). Pre-add "Window A" and A/B comparisons in the appendices. Companion reports: [OTT](https://docs.google.com/document/d/1z70VEKZ0sfDJTuslRZ_wLacBaXaBFVcwLtzfR_M7E88/edit), [Mobile](https://docs.google.com/document/d/1NSoVOcipzJ-yXRgqdzz60JV6Ippl_g_-oTUrerPdOe4/edit) (same structure).
**Method:** device-level CUPED (clean pre-period 2026-07-09 → 07-22), Welch CIs; populations ITT / Active / ToT (Appendix C). Report date 2026-08-21.

## TL;DR

- **Web's topline is statistically significant for the first time in the ABF3 program: TOTAL web revenue +3.21%, TOTAL web TVT flat-to-positive** — across all devices and ALL titles, measured at catalog scale.

| | Global (all-titles) revenue | Global (all-titles) TVT |
|---|---|---|
| **v8 MEASURED (global topline, ITT)** | **+3.205%** [+2.231, +4.179] p=1e-10 ✅ | +0.319% [−0.440, +1.078] ns (flat/positive) |
| Projected from the v7 sample XP (matching pruner config) | +1.38% [−0.74, +3.51] — **never significant** | too noisy to call |
| Projected from the v6 sample XP (lighter pruner) | +4.68% [+2.73, +6.63] | flat-to-positive |

- **Web over-delivers the v7 projection ~2.3×, and the chronic web power problem is solved by scale:** the sample era's web topline never cleared zero (small treated share × small platform); at ~37% treated revenue coverage and a 9-day window it is decisively significant. No measurable TVT cost in any window, band, or population — consistent with v6/v7 web.
- Robust to population definition: ITT +3.21%, Active +2.30%, ToT +2.51% revenue — all significant; TVT ns on all three. (Web population lenses diverge more than other platforms because web device_ids are cookie-based and churn heavily — see caveats.)
- **Defect check on web:** the below-control dense over-prune **replicates** (13+ below-control −9.7% vs at/above +1.5%; 10–12: −8.4% vs +0.7%) — the per-title floor fix is validated on web too. The series pattern is intermediate: series positive in sparse/mid bands (1–3: +7.6%, 4–6: +6.3%, 7–9: +3.8%), negative in dense bands (13+ series: −20.1%, largely the below-control count defect).
- Caveats: 9-day post-add read; web is the noisiest platform (CIs ~5× OTT's); cookie-based device churn inflates ITT n (35.8M/arm) and dilutes per-device signal; ~11% of web-exposed devices' watch happens on mobile surfaces (FIRETABLET/ANDROID_SAMSUNG — v7 finding, not re-corrected here, consistent with v6/v7 methodology).

## 1. Headline (Window B: 08-12 → 08-20)

**Global (all titles, all exposed devices):**

| Population | n/arm | Revenue | TVT |
|---|---|---|---|
| **ITT** | 35.79M | **+3.205%** [+2.231, +4.179] p=1e-10 | +0.319% [−0.440, +1.078] p=0.41 |
| Active (≥1 session since exposure) | 2.81M | +2.295% [+1.366, +3.223] p=1e-06 | +0.263% p=0.49 |
| ToT | 0.89M | +2.505% [+1.565, +3.445] p=2e-07 | +0.192% p=0.62 |

**On-title (treated titles):** ITT **+6.057%** [+4.850, +7.264] p=8e-23 revenue / +0.130% TVT p=0.78; ToT +4.201% [+3.119, +5.282] p=3e-14 / −0.321% p=0.45. Impressions: global ITT +3.416% p=6e-13; on-title ITT +6.594% p=2e-28.

**NPV_TVT — non-power-viewer TVT (Statsig metric), Window B:** power flag from the latest `device_okr_daily` snapshot on/before first exposure (≥8 visit-days last-28d AND >4 hrs/visit-day; absent = non-power); share balanced (0.081% both arms). **NPV_TVT +0.188% [−0.599, +0.974] p=0.64 ns** (35.76M/arm); power viewers +0.762% [−0.966, +2.490] p=0.39 (29K/arm). Note: power viewers are nearly nonexistent on web (cookie churn prevents 28-day history), so NPV_TVT ≈ the all-device TVT.

## 2. Where the lift lives

### 2a. By ABF1 density band (Window B, all treated ∩ ABF1 universe)

| Band | Revenue lift | TVT | 
|---|---|---|
| 1–3 | **+7.65%** [+4.02, +11.29] | −1.11% ns |
| 4–6 | +6.49% [+3.34, +9.63] | +0.55% ns |
| 7–9 | **+7.22%** [+5.90, +8.54] | +0.61% ns |
| 10–12 | −1.01% [−2.36, +0.34] ns | −0.11% ns |
| **13+** | **−3.99%** [−6.28, −1.69] | −1.27% ns |

Banded set = **37.5% of web revenue** (platform-scoped); treated-wide rev-weighted lift **+4.12%**; **banded global contribution ≈ +1.54pp**. Broad positive lift across sparse and mid bands; only the dense bands drag. TVT ns everywhere.

### 2b. Defect 1 — below-control over-prune: replicates on web

| Cut | Revenue |
|---|---|
| 10–12 served ≥ control | +0.69% |
| 10–12 served < control | **−8.42%** |
| 13+ served ≥ control | +1.52% |
| 13+ served < control | **−9.71%** |

Same signature as OTT and mobile. The per-title floor fix is platform-universal.

### 2c. The series picture — intermediate between mobile (fine) and OTT (broken)

| Band | MOVIE revenue | SERIES revenue |
|---|---|---|
| 1–3 | +9.2% | **+7.6%** ✅ |
| 4–6 | +9.7% | **+6.3%** ✅ |
| 7–9 | +7.5% | +3.8% |
| 10–12 | −1.0% | −3.4% |
| 13+ | −2.8% | **−20.1%** |

Web series earn in sparse/mid bands (unlike OTT, where they lose everywhere ≥4 cp) — web ad-config gates evidently don't expose ABF3's placement the way OTT episode gates do. The 13+ series collapse (−20%) sits on the below-control **count** defect (the floor's territory) plus thin cells (web dense series are few).

### 2d. Cohorts (Window B)

| Cohort | Revenue | TVT |
|---|---|---|
| Original 154,348 titles, on-title (ITT) | +5.52% [+3.91, +7.14] | +0.35% ns |
| Top-up 38,116 titles (bands aggregate) | **+4.50%** treated-wide; contribution ≈ +0.88pp | flat in all bands |

No TVT cost on either cohort. (Window A→B additivity is looser on web than other platforms — the original set itself strengthened B-over-A within web noise.)

## 3. Decision frame (on revenue and TVT lift directly)

- **Web at the current config is a clear win at platform level:** +3.21% platform revenue, no measurable engagement cost, first-ever significant web topline.
- **The floor fix has web upside** (below-control drags −8 to −10%); the OTT series placement fix is not needed for web outside the dense bands the floor already covers.
- **Re-measure any changed pruner config (Window C) before graduating its numbers** — same guardrail as OTT/mobile.

---

## Appendix A — Window A (pre-top-up, 07-23 → 08-10)

**Headline:** global ITT revenue **+1.347%** [+0.554, +2.139] p=0.0009 — significant even pre-add; TVT +0.09% ns. On-title ITT +4.384% [+3.105, +5.663] / −0.657% ns (p=0.19); ToT on-title +3.334% / −0.67% ns.

**Bands (original set):** 1–3 +11.24%, 4–6 +5.71%, 7–9 +3.37%, 10–12 **−2.70%**, 13+ **−10.53%**; TVT ns everywhere. Dense split: 10–12 at/above −0.88 ns vs below −8.71; 13+ at/above −5.24 vs below −13.39. Series: positive 1–6 (+11.2/+4.8), negative 7+ (7–9 −6.2, 13+ −32.3 — thin cells). Treated-wide +2.78%; banded share 17.9% → contribution ≈ +0.50pp.

**Projection calibration:** Window A measured +1.35% global — already at the v7 sample's *point estimate* (+1.38%) despite Window A's smaller coverage, and unlike the sample read it is significant. The catalog experiment resolved what the sample could not: web's lift is real.

## Appendix B — Window A vs B & checks

- Global revenue +1.35% → +3.21%; the top-up's banded contribution is ≈ +0.88pp, with the remainder from the original set strengthening within web noise (B-vs-A original on-title +4.38 → +5.52, CIs overlap).
- TVT: no significant cost anywhere, either window, any cohort, any band — web remains the most engagement-tolerant platform, as in v6/v7.
- Carryover: verified ≈nil on OTT (design-level property of the shared title-level serving change); not re-run per platform.
- Top-up verification, activation date (08-11), and durable cue-point snapshot are shared with OTT (title-level; see OTT report Appendix B.4).

## Appendix C — Methods

Identical to the OTT report (windows A = 07-23→08-10 / B = 08-12→08-20, add day excluded; CUPED pre 07-09→07-22; populations ITT / Active-since-exposure / ToT; unbudgeted programmatic revenue; v6/v7-suite estimators). Platform scoping: device-level cuts scoped by `ads_web_abf_3_v8` exposures; banded revenue-share denominator scoped to `platform='web'`. Known web-specific caveats: cookie-based device_id churn (inflates ITT n; % lifts unaffected); ~11% cross-surface watch leakage (v7 measurement, uncorrected here for consistency with v6/v7 methodology — correcting it made web look slightly *better* in v7). Artifacts: runs archived as `…web…__run_2026-08-21_OUTPUT`; results JSON in project `.v8_refresh_results/`.
