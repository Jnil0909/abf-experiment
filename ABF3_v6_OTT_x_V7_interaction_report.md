# ABF3 v6 (OTT) × V7 MTML/XGBoost — TVT & Revenue Interaction Analysis

**Question:** ABF3 v6 (OTT) ran concurrently with a second ad-load experiment, `dynamic_ads_tolerance_mtml_device_xgboost_session` ("V7", Bing Wang). Many devices were exposed to both. Did the interaction between the two experiments **better or worsen** ABF3's TVT effect — or was there no interaction? Unbudgeted revenue analyzed alongside TVT.

**Experiments**
- **ABF3** = `ads_abf_3_v6` (OTT): ABF1 control vs ABF3 test, 1,084 titles, ABF3 pruned to ~ABF2 density. Launched 2026-05-29.
- **V7** = `dynamic_ads_tolerance_mtml_device_xgboost_session`: reduces `min_time_spacing_between_breaks` (→ **more ad breaks**) for tolerant/stable devices via ML targeting. 1 control + 10 treatment arms (~1.5M devices/arm). Ran 2026-05-21 → 2026-06-02. Targeted all OTT platforms **except Roku** (+ Web/Amazon), per its setup doc.
- Both push the **same lever** (more ad breaks), so a TVT interaction is mechanistically plausible.

**Design & method**
- **2×2 factorial** on devices co-exposed to both experiments. Factor A = ABF3 (Control/Test); Factor B = V7 (Control / any-treatment-arm pooled).
- **Window: 2026-05-29 → 2026-06-02** — the only period both experiments were live.
- **Scope:** ABF3 titles only, **ToT** (device watched ≥1 ABF3 title), device-level — matches the v6 OTT headline (−0.33% TVT) the analysis is investigating.
- **CUPED**-adjusted (pooled θ; covariate = device's pre-period same-metric value over a **clean joint pre-period 2026-05-07 → 05-20**, before *both* launches so neither treatment leaks into the covariate). Welch t-test for simple effects; analytic SE for the interaction (independent cells).
- **Part B — Roku natural control:** V7 never served on Roku and Tubi `device_id` is platform-specific, so **0 Roku devices appear in V7**. ABF3's effect measured on Roku-platform sessions is therefore the pure ABF3 effect at **zero V7 exposure** — a large (1.56M devices/arm) triangulation against the small co-exposed V7-control cell.
- Notebook: `/Users/bpulikkal@tubi.tv/ABF_3/abf_v6_v7_interaction` (serverless run 2026-06-10).

## Key Takeaways

> **⚠️ Updated 2026-06-11 — conclusion reversed by a clean post-V7 follow-up (see §6).** V7 ended 2026-06-02 while ABF3 v6 OTT kept running, opening a high-powered, V7-free window (06-03→06-10). It directly tests the interaction hypothesis below — and **refutes it.** The Key Takeaways now reflect that follow-up; the **Detailed Summary and §1–§5 are the original 2026-06-10 co-exposure analysis, kept for history** (its "likely-real interaction" lean is now superseded).

**Q: Did the concurrent V7 experiment interact with ABF3 — better or worsen its TVT/revenue effect?**

1. **No — there is no V7 interaction. ABF3's TVT cost is standalone and platform-driven, not a V7 artifact.** In the clean V7-free window, removing V7 from the platforms where it had operated (non-Roku OTT) left ABF3's TVT effect **unchanged**: −0.60% (V7 on) → −0.76% (V7 off), temporal DiD **+0.0%, p=0.97** (ToT), confirmed by the randomization-preserving ITT cut (+0.05%, p=0.75). The CI rules out the −1.3% to −1.6% interaction the original analysis hypothesized.
2. **The original "dose gradient" was platform heterogeneity in disguise.** The Roku-vs-non-Roku gap that looked like a V7 dose effect **persists with V7 gone**: Roku stays flat (+0.01% → −0.19%), non-Roku stays negative (−0.60% → −0.76%). This matches the already-known platform split (web −0.17%, OTT −0.33%, mobile −0.90%). The earlier analysis used Roku as its "zero-V7" anchor and mis-read a platform difference as a V7 interaction — exactly the confound §5 had flagged.
3. **ABF3 DOES carry a genuine standalone TVT cost** — present and stable in a fully V7-free window: −0.53% all-OTT on-title ToT (−0.76% non-Roku, flat on Roku). The v6 OTT −0.33% headline is real and **not** inflated by V7.
4. **Revenue stays strongly positive everywhere regardless of V7** (+5.4% to +6.0% on-title ToT in the V7-free window). A mild P1→P2 softening appears on *all* platforms incl. Roku → ordinary runtime/seasonality drift, not V7.
5. **Implication:** the graduation trade (≈+2.2% global revenue for a small, platform-varying TVT cost) **stands on its own and does not depend on V7's status** (whether V7 stays off or is re-run). If stakeholders want to buy down the TVT cost on the high-cost platforms (mobile/non-Roku), further density pruning is now a legitimate lever — but it is *not* needed to neutralize a V7 interaction, because there is none.

---

## Detailed Summary

> *Historical — original 2026-06-10 co-exposure analysis. Its "likely-real interaction" conclusion is **superseded by §6** (post-V7 clean window), which shows no interaction. Retained unchanged for traceability.*

**There is likely a real, mild interaction on TVT — we are underpowered to prove it, not able to rule it out.** The interaction misses 95% significance (ITT TVT p=0.092, ToT p=0.17), but this is a **power problem, not a clean null**: V7 ran 10 treatment arms against 1 control, starving the off-V7 reference cell, and the CI comfortably permits a meaningful negative interaction. The balance of evidence — a significant −0.70% ABF3 TVT cost on V7-treated devices, a *precisely-measured* flat effect off V7 (Roku +0.01% [−0.31%, +0.33%]), and a coherent dose gradient — **leans toward V7 deepening ABF3's TVT cost.** Do **not** read "not significant" as "no interaction." (Revenue shows no independent interaction — it tracks TVT mechanically; see below.)

The v6 OTT −0.33% TVT headline is therefore **not *provably* an artifact of V7, but the data lean toward V7 carrying part of it** — ABF3's standalone TVT cost is likely somewhat smaller than −0.33%.

- The interaction term is identical under both framings (symmetric, as it must be): **TVT −1.60% [−3.87%, +0.67%], p=0.17**; **revenue −1.16% [−3.23%, +0.91%], p=0.27**. Both CIs straddle zero.
- **One TVT signal worth monitoring — but it is not a proven interaction.** Two distinct questions are in play, and only one has a confident answer:
  - *Does ABF3 cost TVT on devices that also got V7?* **Yes** — **−0.70% [−1.18%, −0.22%], p=0.0045** (all-titles ITT). This is a **simple effect measured inside the V7-treated cell**; it stands on its own.
  - *Is ABF3's TVT cost genuinely **larger** on V7 devices than off them?* **Can't confirm.** That comparison — the difference *between* cells — **is** the interaction, and it misses 95% (p=0.092 ITT, p=0.17 ToT). The point estimates do line up in a suggestive gradient — Roku/zero-V7 **+0.01% [−0.31%, +0.33%]**, V7-control **+0.61%**, V7-treated **−0.70%** — but the off-V7 cells are imprecise (Roku is confounded with platform; the V7-control cell is small and noisy), so the −0.70% **cannot be shown to be reliably different from them.**
  - **Why a significant cell but no significant interaction:** the difference between a sharply-measured number (−0.70%, n≈1.18M) and a fuzzily-measured one (+0.61%, noisy V7-control) is itself fuzzy — so the formal interaction test can't clear 95% even though the underlying effect looks real. This is a **power failure, not evidence of no effect.** The two cleaner data points both point the same way: the significant −0.70% on V7-treated devices, and the *precise* Roku off-V7 estimate (+0.01%, tight CI) confirming the off-V7 effect really is flat — not just noisily flat. Together they make the compounding story (V7's extra ad load deepens ABF3's TVT cost) the **most likely reading**; the only thing missing is power in the starved V7-control arm to stamp it significant. **Treat as a likely-real effect to confirm with more data, not as established or as ruled out.**
- **Revenue rises strongly on every device — V7 or not (+5.1% to +6.3% ToT); it is never dampened in absolute terms (no "revenue drop" anywhere).** The intuitive "more ads → more money" effect is real and shows up exactly where it should — in **revenue per watch-hour: +5.3% (V7-control) vs +5.7% (V7-treated) — essentially identical** (ITT: +1.5% vs +1.8%). So V7 does not change *how* ABF3 monetizes. The only reason *total* revenue lift is a touch smaller on V7-treated devices (+5.13% vs +6.32%) is that on those devices ad load also costs some watch-time (the TVT interaction), so the unchanged per-hour rate applies to slightly fewer hours: `total rev% ≈ rev/hour% + TVT%` → V7-control +5.3% + 1.0% = +6.3%; V7-treated +5.7% − 0.6% = +5.1%. One lever (ad load), two readouts (+rev/hour, −hours); the slightly smaller total lift is the arithmetic of fewer hours, not a monetization penalty. Revenue confirms the TVT story; it is not independent evidence of an interaction.
- **No gap clears significance for the full interaction** — the co-exposed V7-control cell is small (~40k devices/arm ToT, ~131k ITT; V7 ran 10 treatment arms against 1 control), so the interaction SE is large.

**Verdict: a TVT interaction is likely real but cannot be proven at 95% — this is an underpowered result, not a clean null, and "not significant" must not be read as "no interaction." The evidence leans toward V7 deepening ABF3's TVT cost: (1) a significant simple effect — on V7-treated devices ABF3 costs −0.70% TVT [−1.18%, −0.22%], p=0.0045; (2) a *precisely-measured* flat effect off V7 (Roku +0.01% [−0.31%, +0.33%]), confirming the off-V7 baseline genuinely is flat, not just noisily flat; (3) a coherent dose gradient (flat off V7 → negative on V7). The formal interaction test misses significance (ITT p=0.092, ToT p=0.17) only because V7 starved its control arm 10-to-1, leaving the off-V7 cell too noisy — the CI still permits a meaningful negative interaction. Implication: ABF3's standalone TVT cost is likely somewhat smaller than the v6 OTT −0.33% headline, with part of it attributable to V7 co-exposure. Confirm with more data / a cleaner V7-control arm; do not treat as ruled out. Revenue is not independently affected — ABF3's per-watch-hour monetization lift is unchanged by V7; the slightly smaller total-revenue lift on V7 devices is just the mechanical consequence of less watch time.**

## 1. Co-exposure & validity

| Quantity | Value |
|---|---|
| Devices in ABF3 (overlap window) | 19.70M |
| Devices in V7 (overlap window) | 4.28M |
| **Co-exposed (both)** | **2.62M** |

**Randomizations are independent (no cross-experiment SRM):** among ABF3-test devices 90.01% are V7-treated vs 89.98% among ABF3-control — balanced. ABF3 assignment is balanced within the co-exposed set (1,310,959 control / 1,310,914 test). The 2×2 is valid.

**ToT cell sizes (devices that watched ≥1 ABF3 title):**

| | V7 control | V7 treated |
|---|---|---|
| **ABF3 control** | 40,350 | 363,039 |
| **ABF3 test** | 40,291 | 362,391 |

The V7-control column is the small/noisy reference (V7 pooled 10 treatment arms vs 1 control), which dominates the interaction SE.

## 2. Part A — 2×2 interaction, both framings (CUPED, on-title ToT)

**Cell means (CUPED TVT, minutes):**

| | V7 control | V7 treated |
|---|---|---|
| **ABF3 control** | 102.66 | 103.04 |
| **ABF3 test** | 103.71 | 102.45 |

### 2a. ABF3-side framing — "does V7 change ABF3's effect?"

| Metric | ABF3 effect in V7-**control** | ABF3 effect in V7-**treated** | Interaction (95% CI), p |
|---|---|---|---|
| TVT | +1.02% (p=0.35) | −0.58% (p=0.11) | **−1.60%** [−3.87%, +0.67%], p=0.17 |
| Revenue | +6.32% (p≈3e-10) | +5.13% (p≈2e-53) | **−1.16%** [−3.23%, +0.91%], p=0.27 |

### 2b. V7-side framing — "does ABF3 change V7's effect?"

| Metric | V7 effect in ABF3-**control** | V7 effect in ABF3-**treated** | Interaction (95% CI), p |
|---|---|---|---|
| TVT | +0.37% [−1.22%, +1.96%], p=0.65 | −1.22% [−2.82%, +0.39%], p=0.14 | **−1.60%** [−3.87%, +0.67%], p=0.17 |
| Revenue | +0.68% [−0.73%, +2.10%], p=0.34 | −0.45% [−1.87%, +0.97%], p=0.54 | **−1.16%** [−3.23%, +0.91%], p=0.27 |

**The interaction term is byte-for-byte identical across both framings** (−1.64 min TVT; −0.0013 revenue) — confirming algebraic symmetry: testing "V7's effect differs by ABF3 arm" *is* testing "ABF3's effect differs by V7 arm." This is one claim, proven once.

- **TVT:** V7 is mildly positive on ABF3-control devices (+0.37%, ns) and mildly negative on ABF3-test devices (−1.22%, ns). Equivalently, ABF3 is +1.02% on V7-control and −0.58% on V7-treated. Interaction ns (p=0.17).
- **Revenue:** V7 mildly positive on ABF3-control (+0.68%, ns), mildly negative on ABF3-test (−0.45%, ns). Interaction ns (p=0.27).
- Raw vs CUPED are nearly identical here (variance reduction is modest for on-title ToT, as in v6).

## 3. Part B — Roku natural control (ABF3 effect at zero V7)

Roku = the **largest OTT platform** and carries **0 V7 devices** → ABF3's effect on Roku is uncontaminated by V7. High-powered: **1.56M devices/arm**.

| Metric | ABF3 effect on Roku (zero V7) | 95% CI | p |
|---|---|---|---|
| **TVT** | **+0.01%** | [−0.31%, +0.33%] | 0.95 (dead flat) |
| **Revenue** | **+6.96%** | [+6.61%, +7.30%] | ≈0 |

Laying the three V7-dose levels side by side:

| ABF3 effect by V7 "dose" | n/arm | TVT | Revenue |
|---|---|---|---|
| **Zero V7** (Roku) | 1.56M | **+0.01%** (flat, tight) | **+6.96%** |
| **V7 present, control arm** | 40k | +1.02% | +6.32% |
| **V7 treated** | 363k | −0.58% | +5.13% |

- **TVT is exactly flat where V7 is absent** (+0.01% ±0.33%); the −0.58% is confined to V7-treated devices. This is the robust signal.
- **Total revenue lift stays strongly positive at every dose level** (+6.96% → +6.32% → +5.13%) — it merely shrinks slightly; there is no revenue drop. Do not read the shrink as ABF3 monetizing less under V7. Revenue ≈ watch-time × revenue-per-hour; ABF3's revenue lift **per watch-hour** is essentially flat across dose (≈+6.9% Roku, +5.3% V7-control, +5.7% V7-treated on the ToT cut). The decline in *total* lift tracks the TVT decline (same per-hour rate × fewer hours), not a change in per-hour monetization. The combination — flat per-hour revenue gain + larger TVT cost on higher-ad-load devices — is exactly what a convex annoyance curve predicts (extra breaks hurt more when baseline ad load is already high). One lever (ad load), two metrics.

## 3b. All-titles ITT 2×2 (higher power)

To tighten the interval, the same 2×2 was re-run as **all-titles ITT**: all assigned co-exposed devices (no ToT filter), outcomes summed over all titles. This ~3× the V7-control cell (131,296 / 130,996 devices per ABF3 arm, vs ~40k in ToT). CUPED, same covariate.

### ABF3-side framing
| Metric | ABF3 in V7-**control** | ABF3 in V7-**treated** | Interaction (95% CI), p |
|---|---|---|---|
| **TVT** | +0.61% (p=0.41, ns) | **−0.70% [−1.18%, −0.22%], p=0.0045 (sig)** | **−1.32% [−2.85%, +0.21%], p=0.092** |
| **Revenue** | +2.12% [+0.92%, +3.32%] (p=0.0005) | +1.12% [+0.72%, +1.51%] (p≈3e-8) | −0.99% [−2.26%, +0.27%], p=0.123 |

### V7-side framing (same interaction)
| Metric | V7 in ABF3-**control** | V7 in ABF3-**treated** | Interaction p |
|---|---|---|---|
| TVT | +0.71% (p=0.20, ns) | −0.60% (p=0.27, ns) | 0.092 |
| Revenue | +0.76% (p=0.10, ns) | −0.23% (p=0.61, ns) | 0.123 |

(Revenue *levels* differ from the on-title cut because all-titles outcomes are diluted by non-ABF3 titles; the ABF3 all-titles revenue lift ~+1.1–2.1% is the expected diluted figure.)

**What higher power changes:**
- The interaction is **still not significant at 95%**, but TVT tightens to **marginal (p=0.092)**, up from p=0.17 in ToT — same direction, similar magnitude (−1.32% vs −1.60%).
- The decisive new result: **ABF3's TVT effect among V7-treated devices is now significantly negative, −0.70% [−1.18%, −0.22%], p=0.0045** — resolved cleanly from zero by the larger cell. Among V7-control devices it is +0.61% (ns, flat-to-positive). The interaction misses significance only because the V7-control arm remains the noisy one.

### ABF3's TVT effect by V7 dose — full triangulation

| V7 dose | n/arm | ABF3 TVT effect | Significance |
|---|---|---|---|
| **Zero V7** (Roku) | 1.56M | **+0.01%** | flat, tight (p=0.95) |
| **V7-control** (ITT) | 131k | **+0.61%** | ns |
| **V7-treated** (ITT) | 1.18M | **−0.70%** | **sig (p=0.0045)** |

ABF3's TVT goes from flat/positive without V7 to significantly negative where V7 is active — a monotone, coherent gradient across three independent dose levels.

## 4. Interpretation

1. **The interaction misses 95% significance — but this is a power failure, not a clean null.** On-title ToT TVT p=0.17, higher-powered all-titles ITT TVT p=0.092 (marginal), revenue p=0.27 / 0.12. Crucially, the CIs are wide and *permit a meaningful negative interaction* — "not significant" here means "couldn't resolve from zero with a starved control arm," NOT "no effect." Do not read this as proof the two experiments don't interact.
2. **The v6 OTT −0.33% TVT headline is not *provably* an artifact of V7 — but the evidence leans toward V7 carrying part of it.** The clean within-co-exposure 2×2 can't reach significance (underpowered), while the simple effect (−0.70% on V7-treated) and the precise Roku off-V7 flat reading both point to a real compounding component. ABF3's standalone TVT cost is therefore likely somewhat smaller than −0.33%.
3. **A likely-real interaction, statistically unproven — distinct from the (confident) simple effect.** Confident: on V7-treated devices ABF3 costs **−0.70% TVT (p=0.0045, ITT)**. Likely real but unproven at 95%: that this cost is *larger than* ABF3's cost off V7 (the interaction). The case for it is strong — a coherent dose gradient (Roku/zero-V7 +0.01% → V7-control +0.61% → V7-treated −0.70%), with the off-V7 end *precisely* measured flat on Roku (not just noisily flat) and a clear mechanism (both treatments add ad breaks → compounding engagement cost). The only thing missing is power: V7 starved its control arm 10-to-1, so the difference-of-differences lands at p=0.092 despite the underlying effect looking real. Confirm with more data; do not rule out.
4. **Revenue is a follower of TVT, not an independent signal — and it never drops.** ABF3's revenue lift is strongly positive on every device (+5.13% V7-treated, +6.32% V7-control, ToT); there is no "revenue drop" anywhere. The "more ads → more money" intuition is correct and shows up in **revenue per watch-hour, which is unchanged by V7** (≈+5.3% V7-control vs +5.7% V7-treated, ToT; implied per-hour interaction ≈0). The slightly smaller *total* revenue lift on V7-treated devices is purely arithmetic: `total rev% ≈ rev/hour% + TVT%`, and the same per-hour rate applies to slightly fewer hours because ad load also costs some watch-time there. **Crucially this is NOT a contradiction with the TVT cost** — higher ad load *simultaneously* lifts per-hour revenue (more impressions) and trims hours (annoyance); total revenue is their product and stays strongly positive. The TVT cost being larger on V7-treated devices despite an identical per-hour revenue gain reflects a **convex annoyance curve**: V7 already raised baseline ad load, so ABF3's extra breaks land closer to users' tolerance and extract more lost time per identical impression. One lever (ad load), two readouts; revenue confirms the TVT story rather than corroborating it independently.
5. **Practical read:** the small ABF3 TVT cost in the v6 OTT headline appears **concentrated on devices also receiving V7's extra ad load** — partly a consequence of stacking two ad-increasing treatments, not intrinsic to ABF3 alone. ABF3's standalone engagement cost is **likely smaller** than the on-title ToT **−0.33%** [−0.54%, −0.08%] headline implies, with part of that cost attributable to V7 co-exposure. (For reference, the v6 OTT report's TVT figures are: on-title ToT −0.33%; all-titles CUPED −0.165% ITT / −0.201% ToT; and the topline/global graduation figure **−0.05% to −0.40%**. The −0.33% is the on-title ToT number this analysis investigates, not the global figure.) The formal interaction test misses 95% only for lack of power (starved V7-control arm), so treat this as a likely-real effect to confirm with more data — not as a proven effect, but equally not as ruled out.

## 5. Caveats

- **Power, not signal, is the binding constraint.** The co-exposed V7-control cell is ~40k devices/arm (V7 ran 10 treatment arms vs 1 control), so the ABF3-in-V7-control estimate is noisy (±2pp TVT) and dominates the interaction SE. A −1.6% TVT interaction is real-world meaningful but unresolvable from zero at this n.
- **Roku is corroborating, not confirmatory.** The Roku "zero-V7 = flat TVT" result is confounded with **platform** (Roku ≠ the V7-eligible platforms; different device/content mix). The clean causal test of interaction is the within-co-exposure 2×2 (Part A), which is ns. Roku triangulates the direction, it does not prove the interaction.
- **V7 "treatment" pools all 10 non-control arms**, including `DGSpacingIncrease20Pct` (which *increases* spacing → fewer ads, opposite to ABF3) and `PreQvd`. Pooling tests "any concurrent V7 vs V7-baseline"; it slightly mutes the spacing-decrease signal. A spacing-decrease-only definition would be a cleaner mechanistic test (not run here).
- **Two scopes run:** on-title ToT (§2) and all-titles ITT (§3b). ITT has ~3× the V7-control cell and tightens the TVT interaction to marginal (p=0.092) with the V7-treated ABF3 effect significant — but even ITT's V7-control cell (~131k) remains the precision-limiting arm, so the full interaction still misses 95%.
- **Single time window** (5 overlap days); estimates can move with runtime.

---

## 6. Post-V7 clean-window follow-up (2026-06-11) — the interaction is refuted

**Why this section exists.** The original analysis (§1–§5) leaned toward a "likely-real" V7 interaction but could never clear significance, because the co-exposed V7-control cell was tiny and the only large off-V7 reference (Roku) was confounded with platform. A clean test became available: **V7 ended 2026-06-02, while ABF3 v6 OTT kept running.** That opens a high-powered, fully V7-free window in which to re-measure ABF3's effect on the *same non-Roku platforms* where V7 had operated. If V7 was contributing to ABF3's TVT cost, removing it should make the cost shrink.

**Design.**
- **P1_withV7** = 2026-05-29→06-02 (V7 live). **P2_postV7** = 2026-06-03→06-10 (V7 off; confirmed in `core_dev.statsig.exposures` — V7 has zero exposures after 06-02).
- Per period: ABF3 Test-vs-Control, on-title ToT, device-level, CUPED (same clean pre-window 05-07→05-20). Periods defined **independently** (a device may fall in both; assignment is fixed by randomization, so each within-period contrast is a clean RCT — we do **not** cohort on first-exposure timing, which would condition on a post-randomization outcome).
- **Platform falsification cut** (device_id is platform-specific → Roku and non-Roku are disjoint device sets): **non-Roku** = where V7 operated (expect TVT cost to shrink P1→P2 if V7 was the cause); **Roku** = placebo, V7 never present in either period (expect no change; if it moves too, the change is time drift, not V7).
- Notebook `/Users/bpulikkal@tubi.tv/ABF_3/abf_v6_prepost_v7` (serverless run 2026-06-11; output archived `__run_2026-06-11_OUTPUT`).

**Per-period ABF3 effect (on-title ToT, CUPED):**

| Platform | P1: V7 **on** — TVT | P2: V7 **off** — TVT | Temporal DiD (P2−P1), p | Revenue P1 → P2 |
|---|---|---|---|---|
| **all-OTT** | −0.32% (p=0.005) | −0.53% (p=0.004) | **+0.01%, p=0.60** | +5.75% → +5.40% |
| **non-Roku** (V7 lived here) | −0.60% (p=1e-4) | −0.76% (p=0.002) | **−0.01%, p=0.97** | +4.75% → +5.03% |
| **Roku** (placebo, never V7) | +0.01% (p=0.95) | −0.19% (p=0.52) | −0.15%, p=0.58 | +6.96% → +5.98% |

n/arm: all-OTT 3.34M (P1) / 1.68M (P2); non-Roku 1.78M / 0.97M; Roku 1.56M / 0.71M — well powered. The P1 all-OTT figure (−0.32%) reproduces the v6 headline −0.33%, confirming the pipeline ties out.

**Robustness — all-titles ITT, same platform split (randomization-preserving).** ToT conditions on a post-randomization outcome (watching ≥1 ABF3 title), and the *set* of watchers differs P1 vs P2, so a DiD could in principle absorb composition change. ITT (all assigned devices, outcomes over all titles) removes that — it preserves randomization at the cost of dilution (~5–6× smaller effect), which the large n easily affords. The verdict is identical:

| Platform | P1: V7 **on** — TVT | P2: V7 **off** — TVT | Temporal DiD (P2−P1), p |
|---|---|---|---|
| all-OTT | −0.16% (p=0.010) | −0.23% (p=0.032) | **+0.01%, p=0.94** |
| **non-Roku** (V7 lived here) | −0.32% (p=4e-4) | −0.36% (p=0.014) | **+0.05%, p=0.75** |
| **Roku** (placebo, never V7) | +0.01% (p=0.94) | −0.05% (p=0.76) | −0.04%, p=0.78 |

The decisive non-Roku cell — **DiD +0.05%, p=0.75** — matches the ToT non-Roku DiD (p=0.97): removing V7 from the platforms where it operated changed ABF3's TVT effect by essentially zero, under **both** estimands. (ITT also sharpens the runtime-drift read: revenue DiD is significantly negative on *all three* platforms incl. Roku — non-Roku −0.44% p=0.003, Roku −0.55% p=7e-5 — confirming the P1→P2 revenue softening is general drift, not V7, since V7 never touched Roku.)

**Result — no interaction; the TVT cost is standalone and platform-driven.**
1. **Removing V7 did not shrink ABF3's TVT cost.** On the platforms where V7 had operated (non-Roku), the cost was −0.60% with V7 and −0.76% without it — **DiD +0.0%, p=0.97** (ToT), CI [−0.50%, +0.48%]; the randomization-preserving ITT cut agrees (DiD +0.05%, p=0.75). That interval **rules out** the −1.3% to −1.6% interaction the original analysis hypothesized. The interaction prediction was tested directly, at power, under both estimands, and failed.
2. **The "dose gradient" was platform heterogeneity, not a V7 dose.** Roku stays flat and non-Roku stays negative *with V7 entirely absent* — so the Roku-vs-non-Roku gap the original read interpreted as Zero-V7→V7-treated dosing is just the platform difference we already see across the v6 platform reports (web −0.17%, OTT −0.33%, mobile −0.90%). The original analysis anchored on Roku as "zero V7" and mistook a **platform** contrast for a **V7** contrast — precisely the confound §5's second caveat warned about.
3. **ABF3 has a real standalone TVT cost.** It is present and stable in a fully V7-free window (−0.53% all-OTT; −0.76% non-Roku; flat Roku). The v6 OTT −0.33% headline is genuine and not inflated by co-exposure.
4. **The mild P1→P2 softening is runtime drift, not V7.** Both metrics soften slightly in P2 across *all* platforms, including Roku where V7 never ran (revenue +6.96%→+5.98%; TVT +0.01%→−0.19%, p=0.58 — not significant). A uniform, mostly-non-significant cross-platform drift is the signature of novelty/runtime moderation or seasonality, not of V7 leaving.

**Bottom line (supersedes §1–§5's lean):** there is **no detectable ABF3 × V7 interaction.** ABF3's small TVT cost is intrinsic to ABF3 and varies by platform; it is unchanged by V7's presence or absence. The graduation trade therefore does not depend on V7's status — reassuring whether V7 stays retired or is modified and re-run. Further density pruning remains a *possible* lever to reduce the TVT cost on high-cost platforms (mobile/non-Roku), but is not required to neutralize any interaction, because none exists.
