# ABF3 v8 — Full ABF1 Catalog Results (MOBILE)

**Experiment:** `ads_mobile_abf_3_v8` (iOS, Android) · device-randomized 50/50 · launched 2026-07-23 · **top-up of 38,116 titles added 2026-08-11** → full treated set = **192,464 ABF1 titles** (title-level serving change, shared across platforms).
**Main analysis window (this report):** **2026-08-12 → 2026-08-20** (post-top-up, 9 complete days). Pre-add "Window A" and A/B comparisons are in the appendices. Companion reports: [OTT](https://docs.google.com/document/d/1z70VEKZ0sfDJTuslRZ_wLacBaXaBFVcwLtzfR_M7E88/edit), [Web](https://docs.google.com/document/d/1u5RN6dlFRf1UBr0JkyYIpB7njVs10bezViUP6yikSH0/edit) (same structure).
**Method:** device-level CUPED (clean pre-period 2026-07-09 → 07-22), Welch CIs; populations ITT / Active / ToT (Appendix C). Report date 2026-08-21.

## TL;DR

- **Mobile is the strongest platform in the program: TOTAL mobile revenue +2.96%, TOTAL mobile TVT flat — across all devices and ALL titles (treated and untreated), measured at catalog scale (15.9M devices/arm).**

| | Global (all-titles) revenue | Global (all-titles) TVT |
|---|---|---|
| **v8 MEASURED (global topline, ITT)** | **+2.957%** [+2.597, +3.316] | **−0.168%** [−0.492, +0.156] **ns — flat** |
| Projected from the v7 sample XP (matching pruner config) | +2.42% [+1.53, +3.31] | −0.4% to −0.6% |
| Projected from the v6 sample XP (lighter pruner) | +3.19% [+2.45, +3.94] | −0.34% to −0.70% |

- **Mobile OVER-delivers its projection** (+2.96% vs +2.42%) — the opposite of OTT (~65% of projection) — **and the projected TVT cost did not materialize.** Mobile was the sample era's worst engagement platform (on-title TVT −0.90% sig in v6/v7); at catalog scale TVT is flat on every lens and in every density band. Caveat: the global TVT CI [−0.49, +0.16] cannot yet fully exclude a v6-sized −0.4% cost.
- Robust to population definition: ITT +2.96%, Active +2.91%, ToT +3.36% revenue; TVT ns on all three.
- **The trade decomposes cleanly and additively:** original 154K batch = +1.16% global (Window A) at flat TVT; the top-up adds ≈ +1.78pp (its banded contribution) at flat TVT — 1.16 + 1.78 ≈ the measured +2.96%.
- **Defect check on mobile:** the below-control dense over-prune **replicates** (13+ below-control −6.3% vs at/above +1.6%; 10–12: −5.1% vs +6.5%) — the per-title floor fix is validated on mobile too. The OTT series/gate-alignment defect is **largely absent on mobile**: series are strongly positive in sparse bands (+11.8% at 1–3), flat at 7–12, negative only at 13+ — consistent with mobile's different ad-config gates not binding ABF3's placement the way OTT episode gates do.
- Caveats: 9-day post-add read; ITT n includes late-exposed zero-outcome devices (does not affect % lifts).

## 1. Headline (Window B: 08-12 → 08-20)

Two scopes: **global** = total revenue/TVT across ALL titles watched by exposed devices (the platform topline); **on-title** = effect on the 192,464 treated titles.

**Global (all titles, all exposed devices):**

| Population | n/arm | Revenue | TVT |
|---|---|---|---|
| **ITT** | 15.87M | **+2.957%** [+2.597, +3.316] p=2e-58 | −0.168% [−0.492, +0.156] p=0.31 |
| Active (≥1 session since exposure) | 6.58M | +2.913% [+2.557, +3.269] p=7e-58 | −0.192% p=0.24 |
| ToT | 2.46M | +3.361% [+3.002, +3.720] p=4e-75 | −0.259% p=0.11 |

**On-title (treated titles):** ITT **+8.132%** [+7.639, +8.625] p=2e-229 revenue / −0.094% TVT p=0.67; ToT +7.966% p=2e-257 / −0.242% p=0.23. Impressions: global ITT +3.363% p=9e-79; on-title ITT +9.337% p<1e-300.

**NPV_TVT — non-power-viewer TVT (Statsig metric), Window B:** power flag from the latest `device_okr_daily` snapshot on/before first exposure (≥8 visit-days last-28d AND >4 hrs/visit-day; absent = non-power); share balanced (0.678% both arms). **NPV_TVT −0.237% [−0.585, +0.111] p=0.18 ns** (15.76M/arm); power viewers +0.109% [−0.663, +0.881] p=0.78 (108K/arm). Flat on both subpopulations, matching mobile's overall TVT.

## 2. Where the lift lives

### 2a. By ABF1 density band (Window B, all treated ∩ ABF1 universe)

| Band | Revenue lift | TVT | n/arm |
|---|---|---|---|
| 1–3 | **+11.90%** [+10.38, +13.42] | −0.24% ns | 488K |
| 4–6 | +7.07% [+5.69, +8.46] | +0.78% ns | 596K |
| 7–9 | **+12.69%** [+12.07, +13.31] | −0.04% ns | 1.57M |
| 10–12 | +4.19% [+3.57, +4.80] | +0.20% ns | 1.39M |
| 13+ | **−2.24%** [−3.26, −1.23] | +0.07% ns | 514K |

Banded set = **35.7% of mobile revenue** (platform-scoped); treated-wide rev-weighted lift **+8.16%**; **banded global contribution ≈ +2.92pp**. (Band 0's huge % lift is a near-zero-baseline artifact; negligible weight.) Unlike OTT, the lift is broad and strong across sparse AND mid bands, and **no band shows a TVT cost**.

### 2b. Defect 1 — below-control over-prune: replicates on mobile

| Cut | Revenue |
|---|---|
| 10–12 served ≥ control | **+6.48%** |
| 10–12 served < control | **−5.13%** |
| 13+ served ≥ control | **+1.61%** |
| 13+ served < control | **−6.25%** |

Same signature as OTT — dense titles kept at/above control gain, titles pruned below control lose. The per-title floor fix applies platform-wide.

### 2c. The series picture — the OTT gate-alignment defect is largely absent on mobile

| Band | MOVIE revenue | SERIES revenue |
|---|---|---|
| 1–3 | +24.6% | **+11.8%** ✅ |
| 4–6 | +16.2% | **+5.2%** ✅ |
| 7–9 | +13.2% | +0.8% ns |
| 10–12 | +4.2% | +3.5% ns |
| 13+ | −1.5% | −9.7%\* |

On OTT, series lose revenue in every band ≥4 cp (placement × episode-gate misalignment, proven by gate simulation). On mobile, series are *positive* where they carry the most TVT and flat in the dense-mid bands — consistent with mobile's ad-config gates (different initial-slot/spacing values) not exposing ABF3's late-start/tight-spacing signature the way OTT's episode gates do. \*The 13+ series negative persists — that band is dominated by the below-control **count** defect (the floor's territory), not placement.

### 2d. Cohorts (Window B)

| Cohort, on-title (ITT) | Revenue | TVT |
|---|---|---|
| Original 154,348 titles | +7.58% [+6.87, +8.29] | +0.34% ns |
| Top-up 38,116 titles (bands aggregate) | **+8.79%** treated-wide | flat in all bands |

Top-up banded contribution ≈ **+1.78pp** of mobile global (banded share 20.2%). Unlike OTT — where the top-up carries a real TVT cost — mobile shows **no engagement cost on either cohort**.

## 3. Decision frame (on revenue and TVT lift directly)

- **Mobile at the current config is close to a pure win:** +2.96% platform revenue at TVT flat on every lens and band. The one reservation is CI width — the global TVT bound (−0.49%) cannot yet exclude a v6-sized cost; more runtime tightens it.
- **The floor fix has clear mobile upside** (13+/10–12 below-control drags −5 to −6%); the series placement fix is an OTT matter — on mobile there is little series deficit to recover outside 13+ (which the floor addresses).
- **Re-measure any changed pruner config (Window C) before graduating its numbers** — same guardrail as OTT.

---

## Appendix A — Window A (pre-top-up, 07-23 → 08-10)

**Headline:** global ITT revenue **+1.161%** [+0.876, +1.446], TVT +0.05% ns; on-title ITT +6.925% [+6.348, +7.501] / −0.176% ns; ToT on-title +6.805% / −0.232% ns; Active global +1.107%.

**Bands (original set):** 1–3 +9.16%, 4–6 +5.36%, 7–9 +10.12%, 10–12 +2.62%, 13+ **−3.59%**; TVT ns everywhere. Dense split: 10–12 at/above +4.66 vs below −4.62; 13+ at/above +2.20 vs below −5.96. Series positive at 1–6 (+9.1/+2.4), 7–9 −3.0, 13+ −6.2. Treated-wide +6.43%; banded share 15.5% (platform-scoped) → banded contribution ≈ +1.00pp.

**Projection calibration:** Window A measured +1.16% global at ~15.5% banded revenue coverage. The v7 projection (+2.42% at ~40% universe share) scale-adjusted to that coverage ≈ +0.94% — **mobile tracked its projection almost exactly pre-add**, then over-delivered as the dense/movie-heavy top-up landed on a platform where those titles carry no TVT cost.

## Appendix B — Window A vs B & checks

- Global revenue +1.16% → +2.96%: the delta ≈ the top-up's banded contribution (+1.78pp) — internally consistent.
- Original-set Window B on-title: +7.58% / +0.34% ns — no moderation, no TVT emergence on the original cohort.
- TVT flat in both windows, both cohorts, all bands — the OTT top-up TVT cost has **no mobile counterpart**.
- Carryover: verified ≈nil on OTT (fresh vs veteran devices, design-level property of the shared title-level serving change); not re-run per platform.
- Top-up verification, activation date (08-11, impressions test/control ratio step), and durable cue-point snapshot are shared with OTT (title-level; see OTT report Appendix B.4).

## Appendix C — Methods

Identical to the OTT report (windows: A = 07-23→08-10, add day 08-11 excluded, B = 08-12→08-20; CUPED pre 07-09→07-22; populations ITT / Active-since-exposure / ToT; unbudgeted programmatic revenue, TVT from video_session; estimators unchanged from the v6/v7 suite). Platform scoping: device-level cuts are scoped by the experiment's exposures (device_id is platform-specific); the banded revenue-share denominator is scoped to mobile platforms (android/iphone/ipad/firetablet/android_samsung). Artifacts: runs archived as `…mobile…__run_2026-08-21_OUTPUT` in `/Users/bpulikkal@tubi.tv/ABF_3/`; results JSON in project `.v8_refresh_results/`.
