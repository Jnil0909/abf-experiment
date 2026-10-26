# ABF3 v8 — Full ABF1 Catalog Results (OTT)

**Experiment:** `ads_abf_3_v8` (OTT incl. Roku) · device-randomized 50/50 · launched 2026-07-23 · **top-up of 38,116 titles added 2026-08-11** → full treated set = **192,464 ABF1 titles**.
**Main analysis window (this report):** **2026-08-12 → 2026-08-20** (post-top-up, 9 complete days) — the catalog as it now runs. Pre-add "Window A" results and all A/B comparisons are in the appendices.
**Method:** device-level CUPED (clean pre-period 2026-07-09 → 07-22), Welch CIs; populations ITT / Active / ToT (definitions in Appendix C). Report date 2026-08-21 (refreshed; first published 2026-08-19 on the 7-day window). Companion reports: [Mobile](https://docs.google.com/document/d/1NSoVOcipzJ-yXRgqdzz60JV6Ippl_g_-oTUrerPdOe4/edit), [Web](https://docs.google.com/document/d/1u5RN6dlFRf1UBr0JkyYIpB7njVs10bezViUP6yikSH0/edit) (same structure).

## TL;DR

- **Measured global (topline) impact of serving ABF3 on the treated ABF1 catalog: TOTAL unbudgeted revenue +0.88%, TOTAL TVT −0.16% — across all devices and ALL titles (treated and untreated), not just on the treated titles.** Both statistically significant at catalog scale (65M devices/arm), measured, not projected from a sample. (The on-title effect on the treated titles themselves is +2.4% revenue / −0.30% TVT — §1.)

| | Global (all-titles) revenue | Global (all-titles) TVT |
|---|---|---|
| **v8 MEASURED (global topline, ITT)** | **+0.877%** [+0.768, +0.986] | **−0.161%** [−0.275, −0.047] |
| Projected from the v7 sample XP (matching pruner config, comparable ~35% revenue coverage) | +1.36% [+1.13, +1.59] | ~flat (−0.09% to +0.04%) |
| Projected from the v6 sample XP (lighter pruner — not the config v8 shipped) | +2.2% [+1.99, +2.38] | −0.05% to −0.40% |

- **v8 delivered ~65% of the projected revenue.** The shortfall is composition, not noise, and is fully accounted for by two fixable defects (below): the sample's sparse-title gains didn't generalize (catalog sparse band = short series, not long movies), series lose revenue at every density, and the floorless pruner turns dense titles negative. Sample→catalog projection machinery: directionally right, ~1.5× optimistic.
- The measured result is robust to population definition: ITT +0.877%, Active +0.847%, ToT +0.950% revenue; TVT −0.16% to −0.19% across all three.
- **NPV_TVT (Statsig non-power-viewer TVT): −0.27% (p=1e-4) vs power viewers +0.01% ns — the TVT cost is carried entirely by casual viewers** (§1); power viewers absorb ABF3 with no measurable engagement change.
- **The trade decomposes cleanly by cohort:** the original 154K batch delivers +2.0% on-title revenue at **zero** TVT cost; the 38K top-up (dense, movie-heavy rotating-window titles) adds strong revenue (+2.6% on-title) but carries the entire TVT cost (−0.48% on-title). The engagement cost is config-intrinsic (present for freshly exposed devices; not carryover) and title-driven (not temporal).
- **Two systematic, fixable defects are suppressing revenue:**
  1. **Dense titles pruned below their ABF1 control lose 4–8% revenue**; identical-band titles kept at/above control gain +1.4–2.4%. A per-title pruner floor (never serve fewer cue points than control) is directly validated by this contrast.
  2. **Long-form series content loses revenue in every band ≥4 cue points (down to −9.7%)** despite being served *more* candidates than control — proven (gate simulation, r=0.962 vs observed) to be a placement×gate-alignment problem: ABF3's type-blind placement lands just under the episode gate's spacing and misses its early slot, so fewer breaks fire. Typical short episodes are unaffected (flat-to-positive). Fix: make the pruner gate-aware (keep the earliest eligible candidate, target spacing at gate+margin) or hold series bands 4+ on control cue points.
- **Decision frame (on revenue and TVT lift directly):** +0.88% global revenue for −0.16% global TVT is a genuine revenue-for-engagement trade — the TVT cost is significant at 63M devices/arm, robust to population definition, localized to exactly the titles producing the new revenue (original 154K stay flat; top-up carries all of it), present for freshly exposed devices, and mechanistically coupled to the revenue (both come from more realized breaks on long movies; v6/v7 dose-response showed the cost can't be pruned away without giving up the revenue ~1:1).
- **Fixing the two defects would raise revenue; the engagement side differs by fix.** Floor-to-control is TVT-neutral *by construction* (floored titles serve identical cue points to control → no contrast; it removes the −4 to −8% drags and gives back only a negligible under-serving TVT bonus, ~+0.005pp global). Serving dense titles *above* control, or fixing series under-firing, raises ad load above today's treatment and should be expected to carry the usual small TVT price (e.g. series 4–6, where ABF3 already fires more, shows −0.95% TVT). Measured support for the upside: same-band at/above-control titles earn +1.4–2.4% at flat TVT — contemporaneous but not config-randomized. **Any fixed pruner config should be re-measured (Window C) before its numbers are used for graduation.**
- Caveats: 9-day post-add read; CUPED variance reduction weaker than usual (pre-period is 3+ weeks before the window). Mobile and web have their own reports; both show stronger revenue at flat TVT.

## 1. Headline (Window B: 08-12 → 08-20)

All figures CUPED lifts, Test vs Control, 95% CIs. Two scopes: **global** = total revenue/TVT across ALL titles watched by exposed devices (treated + untreated — the business topline); **on-title** = the effect on the 192,464 treated titles only.

**Global (all titles, all exposed devices — the topline):**

| Population | n/arm | Unbudgeted revenue | Impressions | TVT |
|---|---|---|---|---|
| **ITT (all exposed)** | 65.49M | **+0.877%** [+0.768, +0.986] p=4e-56 | +1.084% [+0.974, +1.195] p=3e-82 | **−0.161%** [−0.275, −0.047] p=0.006 |
| **Active** (≥1 session since exposure) | 23.32M | +0.847% [+0.740, +0.955] p=6e-54 | +1.054% p=5e-80 | −0.176% [−0.288, −0.064] p=0.002 |
| ToT (watched ≥1 treated title in window) | 10.86M | +0.950% [+0.846, +1.055] p=4e-71 | +1.189% p=2e-106 | −0.190% [−0.298, −0.081] p=0.0006 |

**On-title (the 192,464 treated titles):**

| Population | Revenue | Impressions | TVT |
|---|---|---|---|
| ITT | **+2.376%** [+2.234, +2.519] p=2e-235 | +2.910% p<1e-300 | **−0.295%** [−0.446, −0.145] p=0.0001 |
| ToT | +2.304% [+2.175, +2.433] p=6e-269 | +2.840% p<1e-300 | −0.315% [−0.451, −0.179] p=6e-06 |

**NPV_TVT — non-power-viewer TVT (Statsig metric), Window B:** TVT restricted to devices that were NOT power viewers at first exposure (power = ≥8 visit-days in last 28d AND >4 watch-hrs/visit-day, from the latest `device_okr_daily` snapshot on/before first exposure; devices absent from the table = non-power). Pre-exposure classification → valid population cut; power-viewer share balanced across arms (2.549% vs 2.546%).

| Subpopulation | n/arm | TVT (CUPED) | p |
|---|---|---|---|
| **Non-power viewers (NPV_TVT)** | 63.82M | **−0.272%** [−0.411, −0.133] | **0.00013** |
| Power viewers (contrast) | 1.67M | +0.010% [−0.178, +0.199] | 0.92 |

**The OTT TVT cost lands entirely on non-power (casual) viewers** — deeper than the all-device −0.161%, while power viewers are unaffected (the all-device figure is the TVT-weighted blend of the two). This sharpens the engagement concern toward the casual/marginal audience segment most relevant to retention.

## 2. Where the lift (and the cost) lives

### 2a. By ABF1 density band (all treated ∩ ABF1 universe; device-level per-band lifts)

| ABF1 band | Revenue lift | TVT lift | n/arm (devices) |
|---|---|---|---|
| 0 (no control cue points) | +145.3% [+137.9, +152.8] | −16.2% [−19.8, −12.6] | 43K |
| 1–3 | −0.38% [−0.82, +0.05] ns | +0.48% (sig +) | 2.29M |
| 4–6 | +0.70% [+0.28, +1.12] | −0.29% ns | 2.65M |
| **7–9** | **+7.06%** [+6.90, +7.23] | −0.47% (sig −) | 7.12M |
| 10–12 | +0.66% [+0.51, +0.82] | −0.41% (sig −) | 6.53M |
| **13+** | **−3.71%** [−3.97, −3.46] | +0.04% ns | 2.64M |

The banded set covers **35.0% of total business revenue** (vs 14.3% before the top-up); its net global contribution is **≈ +0.83pp**. The mid-dense 7–9 band is the engine. Band 0 monetizes spectacularly (ads where none existed) but at a −15% TVT cost to those viewers; its reach is tiny.

### 2b. Defect 1 — the below-control over-prune (dense bands split by served-vs-control count)

| Cut | Revenue | TVT |
|---|---|---|
| 10–12, served ≥ control | **+1.75%** | −0.46% |
| 10–12, served < control | **−3.37%** | −0.08% ns |
| 13+, served ≥ control | **+1.35%** | −0.05% ns |
| 13+, served < control | **−7.33%** | +0.20% ns |

Same band, same window — the only difference is whether the pruner kept at least the control count. The dense-band revenue drag is *entirely* the below-control subset. This replicated identically on the fresh top-up titles (at/above +1.75%, below −6.72%), so it is a systematic pruner property. **Fix: per-title floor (serve ≥ ABF1 control count).** Context: the v8 pruner realizes ~6.5 cue points/hr vs actual ABF2 density ~8.2 (−17 to −21%) — more aggressive than its stated ABF2 target (Appendix B.4).

### 2c. Defect 2 — series lose revenue at every density (movies win everywhere except 13+)

| Band | MOVIE revenue | SERIES revenue |
|---|---|---|
| 1–3 | +4.04% | −0.40% ns |
| 4–6 | **+11.12%** | −1.18% |
| 7–9 | **+7.67%** | **−6.41%** |
| 10–12 | +0.81% | −5.88% |
| 13+ | −2.91% | **−9.78%** |

Series serve *more* candidate cue points than control in most losing bands (e.g. 4–6: 5.19 vs 4.63), yet realize **fewer actual breaks** (realized density −0.6% to −12.7%, tracking revenue ~1:1), while movies realize +2 to +14% more.

**Mechanism PROVEN by deterministic simulation (no behavioral data):** we replayed the pod-placement gate (initial-ad-slot + min-time-between-breaks, greedy first-eligible) over both arms' actual served cue point positions for all ~193K titles. The simulated Test−Control fireable-break delta reproduces the observed realized pattern across all 10 band×type cells with **correlation r = 0.962**. The failure mode is visible directly in the positions — **on dense series, ABF3 serves no early cue points**:

| Series band | First fireable break: ABF1 → ABF3 | Unused tail: ABF1 → ABF3 |
|---|---|---|
| 1–3 / 4–6 | ~595s → ~635s (+40s) | ~equal |
| 7–9 | 599s → **806s (+3.5 min)** | 737s → 950s |
| 10–12 | 591s → **936s (+5.8 min)** | 877s → 1072s |
| 13+ | 585s → **997s (+6.9 min)** | 811s → 1126s |

The ABF3 break train starts 3.5–7 minutes later *and* ends further from the credits — the fireable window is compressed from both ends, so fewer spacing slots fit (4,268 series titles fire fewer simulated breaks despite having MORE cue points). Real sessions being partial amplifies the penalty (later breaks under-realize further), and under the tighter gate profiles that tolerant/low-fill traffic segments receive, simulated series deficits deepen to −5 to −15% — matching observed magnitudes.

**Worked examples (real titles, positions in minutes; "fires" = gate replay at 7-min initial / 10-min spacing):**

- *Columbo S03:E03* (98 min, 32K hrs/14d): ABF1 has 9 points [8.8, 17.9, 26.5, 35.0, 51.3, 62.6, 72.1, 81.1, 91.1] → **fires 6** (8.8…91.1). ABF3 has 10 points [17.9, 23.9, 31.6, 38.1, 44.9, 51.3, 59.5, 66.8, 73.4, 81.0] → **fires 5** (17.9…73.4). One MORE cue point, one FEWER break: the first point comes 9 min later, the mid-episode points sit 6–8 min apart (under the 10-min gate, so every other one is skipped), and the last 25 minutes are ad-free.
- *The Temptations Pt.1* (87 min, 270K hrs/14d): ABF1 24 points → fires 6 (from 7.8 min); ABF3 10 points → fires 5 (from 11.2 min).
- Contrast — typical short episode, *Shooter S01:E01* (42 min, 554K hrs/14d — the #1 TVT series title): ABF1 4 points → fires 2; ABF3 6 points → **fires 3**. On short sparse episodes ABF3's extra candidates fill ABF1's gaps — the sparse band is flat-to-positive. **The damage is specifically long-form series content** (miniseries, multi-hour episodes) — movie-length bodies governed by episode gates.

**Why movies win where series lose (same placement policy, opposite gate alignment):** gates are set by content TYPE, not duration — movies 15-min initial / 12-min spacing; episodes 7-min / 10-min. ABF1's human reviewers implicitly tuned placement to each type's gate: episode points start ~7–9 min (right where the gate opens) and spread 10–12 min (*just above* the gate → nearly every point fires). ABF3 + the pruner apply one type-blind policy — avoid the first ~10–15 min, keep ~6.4 points/hr (~9-min spread). Under the **movie** gate this is invisible or helpful: the late start is hidden behind the 15-min gate, and the ~9-min spread tracks the 12-min grid *better* than ABF1's ~11.6-min spread (which sits just under 12 min and overshoots to ~23-min effective cadence) → movies fire +16–26% more. Under the **episode** gate the same policy fails twice: the 7-min slot ABF1 always hit is lost, and the ~9-min spread sits *just under* the 10-min gate → every other point is skipped (~18-min effective cadence vs ABF1's 10–12). Spacing just above the gate = every point fires; just below = half fire. ABF3 landed on the right side of the movie gate and the wrong side of the episode gate.

**Prevalence — the issue is series-concentrated by 5–10× where it matters (share of TVT where ABF3 fires fewer / equal / more than ABF1):**

| | Fewer | Equal | More |
|---|---|---|---|
| SERIES (all) | **10.6%** | 70.0% | 19.4% |
| MOVIE (all) | 5.2% | 43.3% | **51.5%** |
| SERIES 7–9 / 13+ | **23.8% / 54.6%** | — | 16.5% / 3.2% |
| MOVIE 7–9 / 13+ | 2.5% / 11.1% | — | 58.4% / 48.7% |

Movies are mostly winners (51.5% of TVT gains breaks) with few losers; series are mostly no-ops (the gate pins short episodes at ~2 breaks) with a concentrated loser pocket in the dense bands. Severity per affected title is ~1.0 lost break in both types — but one lost break is −33% of an episode's ad load vs −17% of a movie's.

**Aggregate series cost — and the ad-load discount buys no engagement back (pooled across all bands, device-level on-title):**

| OTT, all treated titles of type | Revenue | TVT |
|---|---|---|
| SERIES, Window B (3.31M devices/arm) | **−1.31%** [−1.63, −0.99] | **+0.20% [−0.12, +0.53] ns** |
| SERIES, Window A | −1.63% [−1.98, −1.27] | +0.14% ns |
| MOVIE, Window B (9.23M/arm) | +3.66% [+3.51, +3.80] | −0.48% [−0.63, −0.32] |

Series lose ~1.3–1.6% of revenue while gaining a statistically-zero ~+0.2% of TVT — the flat TVT dose-response again (a few percent of ad load moves TVT by almost nothing). The scattered per-band series TVT significances (7–9 negative, 13+ positive) cancel in this pooled cut — multiplicity noise around a flat truth, not per-break placement harm. **Consequence: the series under-firing is a pure loss, and fixing it is nearly free — restoring series ad load recovers the ~1.3% revenue at a giveback bounded by the non-significant +0.2% TVT.**

**The deficit splits by band:** in 13+ series it is mostly **count** (below-control pruning: −7.2pp of the −8.2pp simulated deficit) → the per-title floor helps there; in 7–9/10–12 it is mostly **position** (missing early candidates) → the floor does NOT help. Fix options: make the pruner **gate-aware per content type** — always keep the earliest gate-eligible candidate (~7–10 min on episodes) and target kept spacing at *gate + margin* (~11 min episodes / ~12.5 min movies) instead of a flat per-hour density (+ the per-title floor); or hold series bands 4+ on their control cue points. All are selection-time constraints — no model re-run. Whether the missing early positions are the model's (never generated) or the pruner's (dropped) is testable against the unpruned candidate set (`product_ai_ad_breakfinder`) — pending an asset↔content mapping.

### 2d. Cohorts — original batch vs top-up (same window)

| Cohort, on-title (ITT) | Revenue | TVT |
|---|---|---|
| Original 154,348 titles | +2.07% [+1.86, +2.29] | **−0.04% [−0.25, +0.18] ns — flat** |
| Top-up 38,116 titles (all devices) | +2.57% [+2.40, +2.73] | **−0.48% [−0.66, −0.30] sig** |
| Top-up, freshly exposed devices only | +4.58% [+4.20, +4.95] | −0.54% sig |

The original catalog remains a **TVT-free** revenue product. The top-up — precisely the long, dense rotating-window movies where ABF3's cadence cost lives — delivers the strongest revenue but carries the entire engagement cost. The cost is identical for fresh and veteran devices (config-intrinsic, not exposure fatigue); the fresh-device revenue premium is novelty/composition (Appendix B.3).

## 3. Decision frame

The graduation decision for this project is made on the **measured revenue and TVT lifts** directly.

- **The original 154K catalog is arguably graduation-ready on its own:** +2% on-title revenue, +0.37% global (its Window A read), zero measurable TVT cost at 63M-device power.
- **The top-up poses the real trade:** ~+0.5pp additional global revenue for ~−0.16pp global TVT. Whether that exchange rate is acceptable is a stakeholder call; a pre-agreed threshold (X% revenue per Y% TVT) is the clean way to make it.
- **Both defects have upside independent of that decision:** floor-to-control removes the dense-band drag (worth roughly +0.1–0.2pp global) and is TVT-neutral by construction (identical serving to control; only a negligible ~+0.005pp under-serving bonus is given back). The series fix is **nearly free by the pooled measurement (§2c)**: series currently lose −1.31% revenue for a non-significant +0.20% TVT, so restoring series load to control recovers the revenue at a giveback bounded by that ns +0.2%; going *above* control would carry the usual small trade. Holding series on control is the zero-risk fallback. **Re-measure any changed pruner config (Window C) before using its numbers for graduation.**
- Mobile and web replications of this analysis are pending; v6/v7 experience says platform differences can be material.

---

## Appendix A — Window A (pre-top-up, 07-23 → 08-10): validation & mechanism

### A.1 Headline (original 154,348 titles)

| Cut (CUPED) | Revenue | Impressions | TVT |
|---|---|---|---|
| ITT all-titles (global) | **+0.365%** [+0.279, +0.452] | +0.431% | **−0.041% [−0.130, +0.049] ns** |
| ITT on-title | +2.222% [+2.051, +2.392] | +2.557% | −0.036% ns |
| ToT on-title (10.70M/arm) | +2.146% [+1.984, +2.308] | +2.486% | −0.073% ns |
| Active all-titles (18.62M/arm) | +0.351% [+0.268, +0.434] | +0.416% | −0.059% ns |

Global TVT was precisely flat at enormous power — the CI even excludes v6's −0.17% global spillover cost. At this pruning level on the original batch, OTT engagement cost ≈ zero.

### A.2 Projection calibration (why Window A matters)

Window A is the only at-scale test of the v6/v7 sample→catalog projection machinery. Scale-adjusting the v7 projection (+1.36% global at the full 37% ABF1 revenue share) to Window A's actual treated share (~14–16%) predicts +0.55–0.59%; measured was **+0.365% ≈ ⅔ of projection**. The shortfall decomposes into the two defects of §2: the sample's sparse-band gains (+20–30% in v6/v7 decile 1 — long sparse *movies*) did not generalize to the catalog's sparse band (mostly short series, null), and the below-control dense titles turned negative. Sample-based projections were directionally right, ~1.6× optimistic in magnitude.

### A.3 Realized-break density — the mechanism table (Window A)

Non-empty ad pods per TVT-hour, Control → Test:

| Band | MOVIE (Δ) | MOVIE rev | SERIES (Δ) | SERIES rev |
|---|---|---|---|---|
| 1–3 | 2.97→3.15 (+6.1%) | +4.6% | 3.49→3.47 (−0.7%) | −0.4% |
| 4–6 | 3.40→3.87 (+13.9%) | +11.2% | 4.27→4.25 (−0.6%) | −1.8% |
| 7–9 | 3.60→3.89 (+8.0%) | +6.4% | 4.43→4.12 (−6.9%) | −5.9% |
| 10–12 | 3.78→3.86 (+2.0%) | +1.2% | 1.84→1.78 (−3.5%) | −3.5% |
| 13+ | 4.46→4.23 (−5.1%) | −4.8% | 4.46→3.89 (−12.7%) | −9.7% |

Revenue tracks realized ad load ~1:1 in every cell (CPM flat) — consistent with all v6/v7 mechanism work. Series realize fewer breaks despite more candidates → placement×gating, not count.

### A.4 Window A band lifts (original set)

0: +163.9% rev / −14.9% TVT · 1–3: −0.33% ns / +0.69% · 4–6: +0.97% / −0.75% · 7–9: +5.62% / −0.27% · 10–12: +0.95% / −0.14% ns · 13+: −6.50% / +0.38% ns. Dense below-control split: 10–12 at/above +2.40% vs below −4.21%; 13+ at/above +0.28% ns vs below −8.19%.

## Appendix B — Window A vs B comparisons & causal checks

### B.1 What changed A→B

| | Window A | Window B | Read |
|---|---|---|---|
| Global revenue | +0.365% | +0.877% | Top-up ≈ tripled banded revenue coverage (14.3%→35.0%) |
| Global TVT | −0.04% ns | −0.16% sig | Entirely top-up-driven (B.2) |
| On-title rev (orig. titles) | +2.22% | +2.07% | Mild moderation, consistent with v6/v7 runtime pattern |

### B.2 The TVT cost is title-driven, not temporal

Original 154K set measured *within Window B*: on-title TVT −0.035% [−0.252, +0.182] ns — reproduces its Window A value (−0.036%) exactly. Meanwhile the combined set is −0.30% sig and the top-up cohort −0.49% sig in the same period. No drift; the cost entered with the top-up titles.

### B.3 Carryover check (guardrail)

Devices first exposed on/after 08-12 (zero prior ABF3 history, 8.86M/arm) show the top-up TVT cost at the same magnitude as veterans (−0.54% vs −0.49%) → the cost is config-intrinsic, not cumulative-exposure fatigue. Their revenue lift is higher (+4.58% vs +2.59%) — a novelty/early-exposure and device-mix effect (same moderation-over-runtime pattern as v6/v7), not contamination; steady-state (all-device) numbers are the graduation-relevant ones.

### B.4 Top-up verification & pruner density

- Top-up landed 2026-08-11 (verified: test/control impression ratio on the added titles flat ≈1.000 through 08-10, +2.9% on 08-11, ~+3.1% steady after). 38,116 of 40,766 reconciliation candidates live, including all INCLUDE buckets, the 888 Gemini-ready titles (21.6M hrs), and the partner-metadata set.
- Served cue points snapshotted durably: `core_dev.dsa.temp_bp_abf_v8_topup_cuepoints` (with control counts and reconciliation buckets).
- The pruner was **unchanged** for the top-up: floorless, and realizing ~6.5 kept cue points/hr vs actual ABF2 ~8.2 (−17 to −21%, uniform across movies/episodes) — i.e., more aggressive than the stated "ABF2-density" target, closer to v7's level. This predicts (and Window B confirms) v7-like rather than v6-like lifts.

## Appendix C — Methods

- **Windows:** A = 07-23→08-10 (original config); add day 08-11 excluded; B = 08-12→08-20 (report refreshed 2026-08-21; the fresh-cohort figures in B.3 are from the initial 08-12→08-18 window). Never quote the Statsig dashboard across the 08-11 boundary (it blends configs); all numbers here are windowed offline analyses. CUPED pre-period 07-09→07-22 (clean, pre-launch) for both windows; variance reduction 35–42% in B (vs 55–62% in A — the covariate is further from the window).
- **Population semantics:** exposure fires on title *load*; ~64% of exposed devices never watch anything afterwards. Populations: ITT = all exposed; **Active = ≥1 video session since first exposure** (treatment-independent by construction — a never-watcher never experienced treatment; empirically balanced 35.6687% vs 35.6707%); ToT = watched ≥1 treated title in-window. A window-scoped Active variant and a "≥1 ad break" filter were evaluated and rejected: the former conditions on post-treatment churn (empirically balanced here, 20.828% vs 20.824%, but unsafe by construction), the latter is treatment-dependent (measured +0.021pp Test tilt, z≈2.2). Relative lifts are invariant to including zero-outcome devices, so ITT/Active agree; Active is reported for interpretable per-device magnitudes.
- **Metrics:** unbudgeted revenue/impressions = unbudgeted programmatic (`budget IS NULL`, PROGRAMMATIC_OPEN/DIRECT, standard advertiser exclusions, billable); TVT from `video_session`; realized breaks = distinct non-empty ad pods. Estimators identical to the v6/v7 suite (device-level Welch + CUPED; per-band device-pooled lifts as in `abf_v7_decile_concentration`).
- **Sanity:** SRM clean (63,277,285 vs 63,270,264); arm balance verified on Active definitions; top-up activation verified empirically.
- **Artifacts:** notebooks `ads_abf_3_v8__cuped_stat_sig`, `abf_v8_winA_bands` in `/Users/bpulikkal@tubi.tv/ABF_3/`; 12 archived output runs `…__run_2026-08-19_OUTPUT`; tables `core_dev.dsa.temp_bp_abf_v8_{titles,all_titles,topup_titles,topup_cuepoints}`, `temp_bp_v8_topup_buckets`. Full running history: `ABF_BACKGROUND.md`.
