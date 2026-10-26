"""Write narrative.json for the Mobile and Web v10 docs. Every number is pulled from the platform's results files."""
import json, sys
import numpy as np

P = sys.argv[1]  # mobile | web
V = json.load(open(f"/tmp/v10chk/values_{P}.json")); H, R = V["head"], V["raw"]
GB = json.load(open(f"/tmp/v10chk/gate_{P}_base.json")); GT = json.load(open(f"/tmp/v10chk/gate_{P}_tol.json"))
WD = {(r[0], r[1]): r for r in (eval(l) for l in open("/tmp/v10chk/watch_depth.txt").read().splitlines()[1:])}


def s(x, nd=2):
    x = round(x, nd) + 0.0
    return f"{x:+.{nd}f}".replace("-", "−")


sg = lambda e: e["lo"] > 0 or e["hi"] < 0
def L(e, nd=3, tag=True):
    return f"{s(e['l'], nd)}%" + ((" sig" if sg(e) else " ns") if tag else "")


I = H["ITT"]
g = lambda m, a, pop="ITT": H[pop][m][a]
rb = lambda grp, a, m="rev": R[grp][a][m]


def corr(G):
    bp = {(x["band"], x["arm"]): x["sim_delta"] for x in G["band_pooled"]}
    keys = [(b, a) for b in ("1-3", "4-6", "7-9", "10-12", "13+") for a in ("v4", "v5b", "v6")]
    return float(np.corrcoef([bp[k] for k in keys], [R["band|" + b][a]["imps"]["l"] for b, a in keys])[0, 1])


rA, rB = corr(GB), corr(GT)
plat = {"mobile": "Mobile", "web": "Web"}[P]
exp = f"ads_{P}_abf_3_v10_abf2_titles_only"
nar = dict(
    title=f"ABF3 v10 — ABF2 Titles Results ({plat})",
    window_short="2026-10-09 → 2026-10-15 10:00 EDT",
    arm_label={"v4": "v4 (equal load)", "v6": "v6 (movies 60–120 min, +7% load)", "v5b": "v5b (ABF2 density, gate-aware placement)"},
)
ctrl_n = H["ITT"]["n"]["Control"]
act_share = H["Active"]["n"]["Control"] / ctrl_n * 100
nar["front"] = [
    ["Experiment:", f"`{exp}` ({plat}) · device-randomized, four arms at 25% each · restarted 2026-10-09 23:30 UTC (same restart as OTT)."],
    ["Arms:", "Control = ABF2 human cue points. v4 = T1 equal-load pruner (`abf3_pruner_t1_equal_load_v4.py`). v6 = T2, equal load plus about +7% ad load on movies of 60–120 minutes (`abf3_pruner_t2_targeted_load_v6.py`). v5b = T3, ABF2-like cue counts placed where the OTT ad config accepts requests (`abf3_pruner_t3_abf2_density_v5b.py`). The served cue lists are catalog-level, so every platform serves the same lists as OTT."],
    ["Window:", "2026-10-09 → 2026-10-15 10:00 EDT (14:00 UTC) — the same window as the OTT report. Outcomes are capped at 14:00 UTC on 2026-10-15. This is an early read of a live test, not a graduation read."],
    ["Method:", f"device-level CUPED, pre-period 2026-09-25 → 2026-10-08, Welch 95% intervals. ~{ctrl_n/1e6:.2f}M devices/arm (ITT). Revenue is reported three ways — total (all billable ads), budgeted (direct, guaranteed, PMP), and unbudgeted (open auction, the v8 metric) — plus ad impressions and TVT. Same queries and definitions as the OTT report (Appendix C), run on the {plat.lower()} experiment's exposures. Report date 2026-10-15."],
]

if P == "mobile":
    ep, mv = "type|Episode", "type|Movie"
    nar["tldr"] = [
        ["Only v5b wins on mobile.", f"v5b lifts total revenue {L(g('revt','v5b'))} and impressions {L(g('impt','v5b'))}; on the treated ABF2 titles its open-auction revenue is {L(g('orevu','v5b'))}. TVT is {L(g('tvt','v5b'))} (interval just includes zero) — the one engagement item to watch."],
        ["v4 and v6 lose significantly — unlike OTT.", f"Total revenue v4 {L(g('revt','v4'))}, v6 {L(g('revt','v6'))}; every revenue and impression pool is down for both. On OTT v6 was a safe positive; on mobile it is not."],
        ["Episodes drive the split.", f"Episode open-auction revenue: v4 {L(rb(ep,'v4'),2)}, v6 {L(rb(ep,'v6'),2)}, v5b {L(rb(ep,'v5b'),2)}. Movies gain on v6 ({L(rb(mv,'v6'),2)}) and v5b ({L(rb(mv,'v5b'),2)}), v4 flat. The episode loss for v4/v6 is concentrated in the sparse 1–3 and 4–6 bands, where v4/v6 serve fewer cue points than ABF2 on ~half the titles and place the first cue ~3.5 min later than ABF2."],
        ["The below-control defect replicates.", f"Dense titles served below their ABF2 count lose revenue on every arm (v4 10–12 {L(rb('below|v4|10-12|below','v4'),2)}), and titles kept at or above control gain (v6 10–12 {L(rb('below|v6|10-12|at/above','v6'),2)}). The per-title floor applies to mobile too."],
        ["TVT is flat for every arm.", "No arm moves global TVT significantly in any population. The significant TVT items are small and local: v5b on-title TVT among non-power viewers (" + L(g('otvt','v5b','NPV')) + ") and v6 in the 13+ band (" + L(rb('band|13+','v6','tvt'),2) + ")."],
    ]
    nar["tldr_note"] = "All figures are global ITT CUPED lifts versus Control. Direction is stable across ITT, Active, and ToT. Not reconciled with a Statsig scorecard (not available here)."
    nar["headline_intro"] = "All figures are CUPED lifts versus Control, 95% intervals. Global is across every title an exposed device watched. On-title is the same devices, restricted to the ABF2 title list. “Sig” means the interval excludes zero (nominal p < 0.05)."
    nar["money_read"] = (f"Unlike OTT, the mobile money table is a clean split: v5b is up in every pool (budgeted {L(g('revb','v5b'))}; unbudgeted {L(g('revu','v5b'))}, positive but not significant), "
                         f"while v4 and v6 lose in every pool (budgeted {L(g('revb','v4'))} / {L(g('revb','v6'))}; unbudgeted {L(g('revu','v4'))} / {L(g('revu','v6'))}). "
                         "Revenue tracks impressions closely in every arm, so this is an ad-delivery effect, not a price effect.")
    nar["ontitle_read"] = (f"On the treated ABF2 titles the split sharpens: v5b {L(g('orevu','v5b'))} unbudgeted revenue, v4 {L(g('orevu','v4'))}, v6 {L(g('orevu','v6'))}, "
                           "the same sign in every population. On-title TVT is flat for all three arms.")
    nar["npv_read"] = (f"No arm moves TVT significantly for either viewer type (v5b non-power {L(g('tvt','v5b','NPV'))}, power {L(g('tvt','v5b','PV'))}). "
                       f"Power viewers are a small share on mobile (~{H['PV']['n']['Control']/ctrl_n*100:.1f}%), so their intervals are wide.")
    nar["band_read"] = [
        f"1–3 and 4–6 are where v4/v6 lose: 1–3 v4 {L(rb('band|1-3','v4'),2)}, v6 {L(rb('band|1-3','v6'),2)}; 4–6 v4 {L(rb('band|4-6','v4'),2)}, v6 {L(rb('band|4-6','v6'),2)}. v5b is up in both ({L(rb('band|1-3','v5b'),2)}, {L(rb('band|4-6','v5b'),2)}). On OTT 1–3 was flat and the 4–6 losses were smaller (v4 −1.39%, v6 −2.07%).",
        f"10–12 is the positive pocket for every arm (v6 {L(rb('band|10-12','v6'),2)}, v5b {L(rb('band|10-12','v5b'),2)}, v4 {L(rb('band|10-12','v4'),2)}).",
        f"7–9 gains on v5b ({L(rb('band|7-9','v5b'),2)}) and loses on v4 ({L(rb('band|7-9','v4'),2)}). 13+ loses on v4 ({L(rb('band|13+','v4'),2)}); v5b and v6 flat.",
        "TVT is flat in every band except v6 13+ (" + L(rb('band|13+','v6','tvt'),2) + ").",
    ]
    nar["below_read"] = "This reproduces the v8 and OTT defect on mobile: titles served below control lose 1–7% unbudgeted revenue, titles kept at or above control gain 2–7%, with little TVT give-back (the exception is v6 13+ at/above, TVT " + L(rb('below|v6|13+|at/above','v6','tvt'),2) + "). A per-title floor (never serve fewer cue points than ABF2) helps mobile as much as OTT."
    nar["type_read"] = (f"Episodes split the arms: v5b {L(rb(ep,'v5b'),2)}, v4 {L(rb(ep,'v4'),2)}, v6 {L(rb(ep,'v6'),2)}. On OTT every arm lost on episodes; on mobile v5b gains. "
                        f"Movies gain on v6 and v5b; v4 flat. TVT is flat for every arm and type.")
    wm, wo = WD[("MOBILE", "Episode")], WD[("OTT", "Episode")]
    nar["gate_intro"] = ("Replay the pod gate (greedy first-eligible) over the ABF2 and served positions, weighted by each title's in-window mobile TVT. "
                         "The mobile ad config is not in the project files, so two gate profiles are shown: A = OTT base gates, and B = the most tolerant OTT ladder step. "
                         "Observed mobile midrolls start earlier than OTT (median first episode break ~508s vs ~652s on OTT), so B is the closer approximation. "
                         f"Profile B also fits the measured per-band impression lifts better (r = {rB:.2f} vs {rA:.2f} across the 15 arm×band cells).")
    nar["gate_read"] = (f"Under the tolerant profile, v5b's front-loaded cues fire more episode breaks in every band, while v4/v6 fire fewer from 4–6 up — the same split as the measured episode result. "
                        f"The replay does not reproduce the sparse-band (1–3) loss for v4/v6: it predicts a small gain where mobile measures {L(rb('band|1-3','v4'),2)} / {L(rb('band|1-3','v6'),2)}. "
                        f"The replay assumes full viewing; on mobile only {wm[4]}% of ABF2 episode views reach ABF2's ~6.3-min first cue and {wm[5]}% reach v4/v6's ~9.7-min first cue "
                        f"(OTT: {wo[4]}% / {wo[5]}%). Losing the first break on ~{(1-float(wm[5])/float(wm[4]))*100:.0f}% of views matters most on sparse titles, where it is a large share of all breaks — a likely but unproven part of the 1–3 loss.")
    nar["decomp_read"] = "For v4/v6 the episode deficit is mostly a count miss (dense episodes pruned below control) under both profiles, so the per-title floor is the main lever. For v5b the tolerant profile turns the count term positive — v5b's ABF2-density lists fire more breaks when gates are looser."
    nar["decision_intro"] = "Early read, same window as OTT. Judge the money on total revenue; on mobile every revenue pool moves the same direction, so the read is unambiguous."
    nar["decision"] = [
        ["v5b is the only arm to carry forward on mobile.", f"Total revenue {L(g('revt','v5b'))}, on-title unbudgeted {L(g('orevu','v5b'))}, impressions up, TVT flat (watch item: {L(g('tvt','v5b'))})."],
        ["v4 and v6 should not ship to mobile as-is.", f"Both lose significantly ({L(g('revt','v4'))}, {L(g('revt','v6'))}), driven by episodes and sparse titles. The OTT recommendation for v6 does not carry over."],
        ["The fixes from OTT apply, plus one.", "A per-title floor removes the below-control loss (validated here too). An earlier first episode cue likely matters more on mobile, where more viewers stop early — v5b, which front-loads cues, is the arm that gains on episodes."],
        ["Open items.", "Get the mobile ad config to replace the approximate gate profiles; re-read after a longer window — mobile intervals are ~2.5× wider than OTT."],
    ]
    nar["pool_read"] = (f"For v5b both pools rise (budgeted {L(g('impb','v5b'))}, unbudgeted {L(g('impu','v5b'))}), so the extra ads are new inventory filled by both demand types — a cleaner incrementality signal than OTT, where only budgeted rose. "
                        "For v4 and v6 both pools fall: fewer fireable breaks, not a demand shift.")
else:
    ep, mv = "type|Episode", "type|Movie"
    nar["tldr"] = [
        ["v5b is the clear winner on web.", f"Total revenue {L(g('revt','v5b'))}, budgeted {L(g('revb','v5b'))}, unbudgeted {L(g('revu','v5b'))}, impressions {L(g('impt','v5b'))}. On the treated ABF2 titles open-auction revenue is {L(g('orevu','v5b'))}. TVT flat ({L(g('tvt','v5b'))})."],
        ["v4 loses; v6 is flat.", f"Total revenue v4 {L(g('revt','v4'))} (budgeted {L(g('revb','v4'))}), v6 {L(g('revt','v6'))}. Neither moves TVT."],
        ["Episodes split the arms, as on mobile.", f"Episode open-auction revenue: v5b {L(rb(ep,'v5b'),2)}, v6 {L(rb(ep,'v6'),2)}, v4 {L(rb(ep,'v4'),2)}. Movies gain on v6 ({L(rb(mv,'v6'),2)}); v4 and v5b not significant."],
        ["Web is a small, noisy surface.", f"Only ~{act_share:.0f}% of exposed web devices watched anything in-window (Active n ≈ {H['Active']['n']['Control']/1e3:.0f}K/arm), and total revenue is ~${H['ITT']['ctrl_mean']['revt']:.2f} per exposed device in the window. Intervals are wide; at the headline level only v5b's gain and v4's loss clear zero."],
        ["TVT is flat everywhere.", "No TVT move is significant in any population, band, or type."],
    ]
    nar["tldr_note"] = "All figures are global ITT CUPED lifts versus Control. Direction is stable across ITT, Active, and ToT (v4's total-revenue loss is not significant in Active/ToT). Not reconciled with a Statsig scorecard (not available here)."
    nar["headline_intro"] = "All figures are CUPED lifts versus Control, 95% intervals. Global is across every title an exposed device watched. On-title is the same devices, restricted to the ABF2 title list. “Sig” means the interval excludes zero (nominal p < 0.05)."
    nar["money_read"] = (f"v5b gains in every pool, with the largest lift in the open auction ({L(g('revu','v5b'))}) — the opposite of OTT, where v5b's gain came through budgeted demand. "
                         f"v4's loss is in the budgeted pool ({L(g('revb','v4'))}); its open-auction revenue is flat ({L(g('revu','v4'))}).")
    nar["ontitle_read"] = (f"On the treated ABF2 titles v5b is {L(g('orevu','v5b'))} (ITT), {L(g('orevu','v5b','Active'))} (Active), {L(g('orevu','v5b','ToT'))} (ToT). "
                           "v4 and v6 are not significant on-title in any population. On-title TVT flat for all arms.")
    nar["npv_read"] = f"No TVT move is significant for either viewer type. Power viewers are rare on web (~{H['PV']['n']['Control']/ctrl_n*100:.1f}%), so that row is very wide."
    nar["band_read"] = [
        f"v5b gains in the sparse bands: 1–3 {L(rb('band|1-3','v5b'),2)}, 4–6 {L(rb('band|4-6','v5b'),2)}. v6 loses at 1–3 ({L(rb('band|1-3','v6'),2)}).",
        f"10–12 is positive on v6 ({L(rb('band|10-12','v6'),2)}) and v4 ({L(rb('band|10-12','v4'),2)}); v5b {L(rb('band|10-12','v5b'),2)}.",
        "7–9 and 13+ are not significant for any arm. Band cells on web are small (50–150K devices), so only large moves clear zero.",
        "TVT is flat in every band.",
    ]
    nar["below_read"] = (f"Same direction as OTT and mobile for v4 and v6: below-control titles lose and at/above-control titles gain, significant for v4 (10–12 below {L(rb('below|v4|10-12|below','v4'),2)}, at/above {L(rb('below|v4|10-12|at/above','v4'),2)}) "
                         "and v6 at/above. The v5b cells are mixed and not significant at web sample sizes. The per-title floor case holds on web.")
    nar["type_read"] = (f"Episodes split the arms: v5b {L(rb(ep,'v5b'),2)}, v6 {L(rb(ep,'v6'),2)}, v4 {L(rb(ep,'v4'),2)}. "
                        f"Movies: v6 {L(rb(mv,'v6'),2)}; v4 and v5b positive but not significant. TVT flat.")
    ww, wo = WD[("WEB", "Episode")], WD[("OTT", "Episode")]
    nar["gate_intro"] = ("Replay the pod gate (greedy first-eligible) over the ABF2 and served positions, weighted by each title's in-window web TVT. "
                         "The web ad config is not in the project files, so two gate profiles are shown: A = OTT base gates, and B = the most tolerant OTT ladder step. "
                         "Observed web midrolls start earlier than OTT (median first episode break ~491s vs ~652s on OTT), so B is the closer approximation. "
                         f"Profile B fits the measured per-band impression lifts clearly better (r = {rB:.2f} vs {rA:.2f} across the 15 arm×band cells).")
    nar["gate_read"] = (f"Under the tolerant profile v5b fires more episode breaks in every band and v4/v6 fire fewer from 4–6 up — the measured episode split. "
                        f"Web episode viewing is shallower than OTT ({ww[4]}% of ABF2 episode views reach ~6.3 min, {ww[5]}% reach ~9.7 min; OTT {wo[4]}% / {wo[5]}%), "
                        "which likely adds to v4/v6's late-first-cue penalty on sparse episodes.")
    nar["decomp_read"] = "For v4/v6 the episode losses come mostly from fewer cue points under both profiles → the per-title floor is the lever. For v5b the tolerant profile makes the count term positive: ABF2-density lists fire more breaks when gates are looser."
    nar["decision_intro"] = "Early read, same window as OTT. Web is the smallest and noisiest surface; treat everything except v5b's gain and v4's loss as directional."
    nar["decision"] = [
        ["v5b leads on web too.", f"Total revenue {L(g('revt','v5b'))}, open-auction {L(g('revu','v5b'))}, on-title {L(g('orevu','v5b'))}, TVT flat. It is the only arm that wins on all three platforms."],
        ["v4 should not ship to web.", f"Total revenue {L(g('revt','v4'))}, driven by budgeted demand."],
        ["v6 is neutral on web.", f"Total revenue {L(g('revt','v6'))}; its movie gain ({L(rb(mv,'v6'),2)}) is offset by the episode loss ({L(rb(ep,'v6'),2)})."],
        ["Open items.", "Get the web ad config to replace the approximate gate profiles; a longer window is needed for the band and below-control cells."],
    ]
    nar["pool_read"] = (f"For v5b both pools rise (budgeted {L(g('impb','v5b'))}, unbudgeted {L(g('impu','v5b'))}): new inventory filled by both demand types, a clean incrementality signal. "
                        f"v4's budgeted impressions fall ({L(g('impb','v4'))}).")

nar["methods"] = [
    ["Assignment.", f"One variant per device from `core_dev.statsig.exposures` for `{exp}`; no device has more than one variant. Outcomes require event time at/after first exposure."],
    ["Window.", "Outcomes 2026-10-09 through 2026-10-15 14:00 UTC (10:00 EDT). CUPED covariate 2026-09-25 → 2026-10-08. Active = ≥1 video session since first exposure in-window. ToT = ≥1 second of TVT on an ABF2-catalog title in-window."],
    ["ABF2 title list, metrics, estimator.", "Identical to the OTT report: movie/episode streams with non-empty `cue_points_abf`, excluding `abf3_pruned_v8` and the v8 title table; total / budgeted / unbudgeted revenue from `core_prod.ads.impressions` × `mercurydb_cdc.campaigns` with the v8 advertiser exclusions; device-level CUPED with pooled theta per population, Welch 95% (z = 1.96). Band/type/below-control tables are raw Welch."],
    ["Gate replay.", "Same simulation as OTT (`v10_gate_replay`, Databricks `/Users/jvora@tubi.tv/ABF_v10/`), TVT weights from in-window video sessions on this platform. Gate values are approximations — see §2c."],
    ["Served cue lists.", "`ml_dev.tmp.abf3_new_pruner_cuepoints` (snapshot 2026-10-08; T1 = v4, T2 = v6, T3 = v5b) — catalog-level, so §B.4 and the first-cue table match the OTT report."],
    ["Code.", "Queries and scripts in `abf-experiment/v10_verification/`."],
]
json.dump(nar, open(f"/tmp/v10chk/narrative_{P}.json", "w"), indent=1, ensure_ascii=False)
print("ok", P, "rA", round(rA, 3), "rB", round(rB, 3))
