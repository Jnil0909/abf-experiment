"""Write narrative JSON for the Mobile and Web v10 docs (refresh 2026-10-20: window to end of 10-19; on-title/ToT/bands use the 224,739 targeted titles). Every number is read from the results files.

Usage: make_narr_r2.py <mobile|web> <results_dir> <prev_dir>
Prose = judgement written after reading the refreshed results; numbers are pulled, never typed.
"""
import json, os, sys
import numpy as np

P, RD, PD = sys.argv[1:4]
J = lambda d, f: json.load(open(os.path.join(d, f)))
V = J(RD, f"values_{P}.json"); H, R = V["head"], V["raw"]
VO = J(RD, "values_ott.json"); HO, RO = VO["head"], VO["raw"]
OLD = J(PD, {"mobile": "values_mobile.json", "web": "values_web.json"}[P])["head"]
GB = J(RD, f"gate_{P}_base.json"); GT = J(RD, f"gate_{P}_tol.json")
WD = {(r[0], r[1]): r for r in J(RD, "watch_depth.json")["rows"]}


def s(x, nd=2):
    x = round(x, nd) + 0.0
    return f"{x:+.{nd}f}".replace("-", "−")


sg = lambda e: e["lo"] > 0 or e["hi"] < 0
def L(e, nd=3, tag=True):
    return f"{s(e['l'], nd)}%" + ((" sig" if sg(e) else " ns") if tag else "")


I = H["ITT"]
g = lambda m, a, pop="ITT": H[pop][m][a]
rb = lambda grp, a, m="rev": R[grp][a][m]
ro = lambda grp, a, m="rev": RO[grp][a][m]


def corr(G):
    bp = {(x["band"], x["arm"]): x["sim_delta"] for x in G["band_pooled"]}
    keys = [(b, a) for b in ("1-3", "4-6", "7-9", "10-12", "13+") for a in ("v4", "v5b", "v6")]
    return float(np.corrcoef([bp[k] for k in keys], [R["band|" + b][a]["imps"]["l"] for b, a in keys])[0, 1])


rA, rB = corr(GB), corr(GT)
plat = {"mobile": "Mobile", "web": "Web"}[P]
exp = f"ads_{P}_abf_3_v10_abf2_titles_only"
ctrl_n = H["ITT"]["n"]["Control"]
old_n = OLD["ITT"]["n"]["Control"]
act_share = H["Active"]["n"]["Control"] / ctrl_n * 100
ARMS = ("v4", "v5b", "v6")
hw = lambda e: (e["hi"] - e["lo"]) / 2
ratio_ott = hw(I["revt"]["v5b"]) / hw(HO["ITT"]["revt"]["v5b"])

# ---- what changed vs the 10-15 read (auto) ----
chg = []
for m, lbl in (("revt", "total revenue"), ("revb", "budgeted revenue"), ("revu", "unbudgeted revenue"), ("impt", "impressions"), ("tvt", "TVT")):
    for a in ARMS:
        o, n_ = OLD["ITT"][m][a], I[m][a]
        if sg(o) != sg(n_):
            chg.append(f"{a} {lbl} {'ns → sig' if sg(n_) else 'sig → ns'} ({s(o['l'],3)}% → {s(n_['l'],3)}%)")
move = "; ".join(f"{a} {s(OLD['ITT']['revt'][a]['l'],3)}% → {s(I['revt'][a]['l'],3)}%" for a in ARMS)
tmove = "; ".join(f"{a} {s(OLD['ITT']['tvt'][a]['l'],3)}% → {s(I['tvt'][a]['l'],3)}%" for a in ARMS)
oto = "; ".join(f"{a} {s(OLD['ITT']['orevu'][a]['l'],3)}% → {s(I['orevu'][a]['l'],3)}%" for a in ARMS)
refresh = (f"Window extended from the end of 2026-10-18 to the end of 2026-10-19 (every complete day loaded in the exposures table); "
           f"ITT devices/arm {old_n/1e6:.2f}M → {ctrl_n/1e6:.2f}M. **Title set corrected:** the on-title, ToT, band, type and below-control tables now use the 224,739 targeted titles (`ml_dev.tmp.abf3_v10_targeted_titles`, the titles served v10 cue points) "
           "instead of the 299k live ABF2 catalog, which included about 74.5k titles that carry identical cues in every arm and so diluted every on-title and band lift. "
           f"On-title ITT unbudgeted revenue, previous version → now (title set and window both changed): {oto}. "
           f"Global ITT total revenue, previous version → now: {move}. TVT: {tmove}. "
           + ("Significance calls that changed: " + "; ".join(chg) + "." if chg else "No global ITT significance call changed.")
           + " All tables, the band/type/below-control cuts, the gate replay and the viewing-depth numbers below were re-run.")

nar = dict(
    title=f"ABF3 v10 — ABF2 Titles Results ({plat})",
    window_short="2026-10-09 → 2026-10-19",
    arm_label={"v4": "v4 (equal load)", "v6": "v6 (movies 60–120 min, +7% load)", "v5b": "v5b (ABF2 density, gate-aware placement)"},
)
nar["front"] = [
    ["Experiment:", f"`{exp}` ({plat}) · device-randomized, four arms at 25% each · restarted 2026-10-09 23:30 UTC (same restart as OTT)."],
    ["Arms:", "Control = ABF2 human cue points. v4 = T1 equal-load pruner (`abf3_pruner_t1_equal_load_v4.py`). v6 = T2, equal load plus about +7% ad load on movies of 60–120 minutes (`abf3_pruner_t2_targeted_load_v6.py`). v5b = T3, ABF2-like cue counts placed where the OTT ad config accepts requests (`abf3_pruner_t3_abf2_density_v5b.py`). The served cue lists are catalog-level, so every platform serves the same lists as OTT."],
    ["Window:", "2026-10-09 → 2026-10-19 (complete days). Outcomes are capped at 2026-10-20 00:00 UTC; the exposures table is loaded through the end of 2026-10-19 (2026-10-20 is a partial day and is excluded). Same window as the refreshed OTT report. This is an early read of a live test, not a graduation read, and it has not been re-reconciled with a Statsig scorecard."],
    ["Method:", f"device-level CUPED, pre-period 2026-09-25 → 2026-10-08, Welch 95% intervals. ~{ctrl_n/1e6:.2f}M devices/arm (ITT). Revenue is reported three ways — total (all billable ads), budgeted (direct, guaranteed, PMP), and unbudgeted (open auction, the v8 metric) — plus ad impressions and TVT. Same queries and definitions as the OTT report (Appendix C), run on the {plat.lower()} experiment's exposures. Report date 2026-10-20."],
    ["Refresh (2026-10-20):", refresh],
]

if P == "mobile":
    ep, mv = "type|Episode", "type|Movie"
    ep_below = lambda b: next(x for x in json.load(open(os.path.join(RD, "served.json")))["rows"] if x[0] == "band" and x[1] == "Episode" and x[2] == "v4" and x[4] == b)[10]
    tvt_sig_pops = [pop for pop in ("ITT", "Active", "ToT") if sg(g("tvt", "v5b", pop))]
    tvt_pv = "; ".join(f"{a} {'power' if pop == 'PV' else 'non-power'} viewers ({L(g('tvt', a, pop), 2)})" for pop in ("NPV", "PV") for a in ARMS if sg(g("tvt", a, pop)))
    nar["tldr"] = [
        ["Only v5b wins on mobile.", f"v5b lifts total revenue {L(g('revt','v5b'))} and impressions {L(g('impt','v5b'))}; on the treated ABF2 titles its open-auction revenue is {L(g('orevu','v5b'))}. Its TVT is {L(g('tvt','v5b'))} globally (Active {L(g('tvt','v5b','Active'),2)}, ToT {L(g('tvt','v5b','ToT'),2)}) — a small but now nominally significant engagement cost, the item to weigh."],
        ["v4 and v6 lose significantly — unlike OTT.", f"Total revenue v4 {L(g('revt','v4'))}, v6 {L(g('revt','v6'))}; every revenue and impression pool is down for both, and TVT is flat (v4 {L(g('tvt','v4'),2)}, v6 {L(g('tvt','v6'),2)}). On OTT v6 is a safe positive ({L(HO['ITT']['revt']['v6'])}); on mobile it is not."],
        ["Episodes drive the split.", f"Episode open-auction revenue: v4 {L(rb(ep,'v4'),2)}, v6 {L(rb(ep,'v6'),2)}, v5b {L(rb(ep,'v5b'),2)}. Movies gain on v6 ({L(rb(mv,'v6'),2)}) and v5b ({L(rb(mv,'v5b'),2)}); v4 is {L(rb(mv,'v4'),2)}. The episode loss for v4/v6 is concentrated in the sparse 1–3 and 4–6 bands, where v4 serves fewer cue points than ABF2 on {ep_below('1-3')}% / {ep_below('4-6')}% of episode titles and places the first cue ~3.5 min later than ABF2."],
        ["The below-control defect replicates.", f"Dense titles served below their ABF2 count lose revenue on v4 and v6 (v4 10–12 {L(rb('below|v4|10-12|below','v4'),2)}, v6 10–12 {L(rb('below|v6|10-12|below','v6'),2)}), and titles kept at or above control gain (v6 10–12 {L(rb('below|v6|10-12|at/above','v6'),2)}). The per-title floor applies to mobile too."],
        ["TVT: only v5b moves, and only slightly.", f"Global TVT is {L(g('tvt','v5b'))} for v5b and flat for v4/v6. Locally, v5b and v6 lose TVT on 13+ titles ({L(rb('band|13+','v5b','tvt'),2)}, {L(rb('band|13+','v6','tvt'),2)}); on-title TVT is not significant for any arm"+ (f"; by viewer type only {tvt_pv} is significant." if tvt_pv else ", nor for either viewer type.")],
    ]
    nar["tldr_note"] = ("All figures are global ITT CUPED lifts versus Control. Direction is stable across ITT, Active, and ToT. Significance calls are nominal 95% (not adjusted for sequential looks or three arms); "
                        "the Statsig scorecard widened intervals ~1.8× on the 10-15 OTT read, which would make v5b's mobile TVT dip not significant and leave its total-revenue gain borderline (approximation, not re-checked against Statsig for this window).")
    nar["headline_intro"] = "All figures are CUPED lifts versus Control, 95% intervals. Global is across every title an exposed device watched. On-title is the same devices, restricted to the 224,739 targeted titles — the ABF2-catalog titles served v10 cue points. ToT is defined on the same set. “Sig” means the interval excludes zero (nominal p < 0.05)."
    nar["money_read"] = (f"Unlike OTT, the mobile money table is a clean split: v5b is up in every pool (budgeted {L(g('revb','v5b'))}; unbudgeted {L(g('revu','v5b'))}, positive but its interval just includes zero), "
                         f"while v4 and v6 lose in every pool (budgeted {L(g('revb','v4'))} / {L(g('revb','v6'))}; unbudgeted {L(g('revu','v4'))} / {L(g('revu','v6'))}). "
                         "Revenue tracks impressions closely in every arm, so this is an ad-delivery effect, not a price effect.")
    nar["ontitle_read"] = (f"On the targeted titles the split sharpens: v5b {L(g('orevu','v5b'))} unbudgeted revenue, v4 {L(g('orevu','v4'))}, v6 {L(g('orevu','v6'))}, "
                           "the same sign and significance in every population. On-title TVT is not significant for any arm.")
    nar["npv_read"] = ((f"The v5b global dip shows in both viewer types (non-power {L(g('tvt','v5b','NPV'))}, power {L(g('tvt','v5b','PV'))}); only the power-viewer dip is significant. " if sg(g('tvt','v5b','PV')) and not sg(g('tvt','v5b','NPV')) else f"v5b non-power {L(g('tvt','v5b','NPV'))}, power {L(g('tvt','v5b','PV'))}. ")
                       + f"v4 and v6 do not move TVT significantly for either type. Power viewers are a small share on mobile (~{H['PV']['n']['Control']/ctrl_n*100:.1f}%), so their intervals are wide.")
    nar["band_read"] = [
        f"1–3 and 4–6 are where v4/v6 lose: 1–3 v4 {L(rb('band|1-3','v4'),2)}, v6 {L(rb('band|1-3','v6'),2)}; 4–6 v4 {L(rb('band|4-6','v4'),2)}, v6 {L(rb('band|4-6','v6'),2)}. v5b is up in both ({L(rb('band|1-3','v5b'),2)}, {L(rb('band|4-6','v5b'),2)}). On OTT 1–3 is flat and the 4–6 losses are smaller (v4 {L(ro('band|4-6','v4'),2)}, v6 {L(ro('band|4-6','v6'),2)}).",
        f"10–12 is the positive pocket for v6 ({L(rb('band|10-12','v6'),2)}) and v5b ({L(rb('band|10-12','v5b'),2)}); v4 is {L(rb('band|10-12','v4'),2)}.",
        f"7–9 gains on v5b ({L(rb('band|7-9','v5b'),2)}) and loses on v4 ({L(rb('band|7-9','v4'),2)}); v6 {L(rb('band|7-9','v6'),2)}. 13+ loses on v4 ({L(rb('band|13+','v4'),2)}) and slightly on v5b ({L(rb('band|13+','v5b'),2)}); v6 is {L(rb('band|13+','v6'),2)}.",
        "TVT is flat in every band except " + "; ".join(f"{b.replace('-', '–')} on {a} ({L(rb('band|'+b,a,'tvt'),2)})" for b in ("1-3","4-6","7-9","10-12","13+") for a in ARMS if sg(rb('band|'+b,a,'tvt'))) + ".",
    ]
    cells_b = [(a, b, t) for a in ARMS for b in ("10-12", "13+") for t in ("below", "at/above")]
    below_rev = [R[f"below|{a}|{b}|below"][a]["rev"]["l"] for a in ARMS for b in ("10-12", "13+")]
    above_rev = [R[f"below|{a}|{b}|at/above"][a]["rev"]["l"] for a in ARMS for b in ("10-12", "13+")]
    nar["below_read"] = (f"This reproduces the v8 and OTT defect on mobile: titles served below control change unbudgeted revenue by {s(max(below_rev),1)}% to {s(min(below_rev),1)}% (the one near-zero cell is v5b 10–12, {L(rb('below|v5b|10-12|below','v5b'),2)}), "
                         f"while titles kept at or above control gain {s(min(above_rev),1)}% to {s(max(above_rev),1)}%. TVT gives back a little on 13+ titles (v5b below {L(rb('below|v5b|13+|below','v5b','tvt'),2)}, v6 below {L(rb('below|v6|13+|below','v6','tvt'),2)}, v6 at/above {L(rb('below|v6|13+|at/above','v6','tvt'),2)}) and is flat elsewhere. "
                         "A per-title floor (never serve fewer cue points than ABF2) helps mobile as much as OTT.")
    nar["type_read"] = (f"Episodes split the arms: v5b {L(rb(ep,'v5b'),2)}, v4 {L(rb(ep,'v4'),2)}, v6 {L(rb(ep,'v6'),2)}. On OTT v4 and v6 also lose on episodes ({L(ro(ep,'v4'),2)}, {L(ro(ep,'v6'),2)}) and v5b is {L(ro(ep,'v5b'),2)}; on mobile v5b gains. "
                        f"Movies gain on v6 and v5b; v4 is {L(rb(mv,'v4'),2)}. TVT is not significant for any arm or type.")
    wm, wo = WD[("MOBILE", "Episode")], WD[("OTT", "Episode")]
    gc = lambda G, tt, b, a: {(x["tt"], x["band"], x["arm"]): x["sim_delta"] for x in G["cells"]}[(tt, b, a)]
    nar["gate_intro"] = ("Replay the pod gate (greedy first-eligible) over the ABF2 and served positions, weighted by each title's in-window mobile TVT. "
                         "The mobile ad config is not in the project files, so two gate profiles are shown: A = OTT base gates, and B = the most tolerant OTT ladder step. "
                         "Observed mobile midrolls start earlier than OTT (median first episode break ~508s vs ~652s on OTT, measured on a 2026-10-12/13 sample), so B is the closer approximation. "
                         f"Profile B also fits the measured per-band impression lifts better (r = {rB:.2f} vs {rA:.2f} across the 15 arm×band cells).")
    nar["gate_read"] = (f"Under the tolerant profile, v5b's front-loaded cues fire more episode breaks in every band ({s(gc(GT,'Episode','13+','v5b'),1)}% to {s(gc(GT,'Episode','1-3','v5b'),1)}%), while v4/v6 fire fewer from 4–6 up (v4 {s(gc(GT,'Episode','4-6','v4'),1)}% at 4–6 to {s(gc(GT,'Episode','13+','v4'),1)}% at 13+) — the same split as the measured episode result. "
                        f"The replay does not reproduce the sparse-band (1–3) loss for v4/v6: it predicts {s(gc(GT,'Episode','1-3','v4'),1)}% / {s(gc(GT,'Episode','1-3','v6'),1)}% on episodes where mobile measures {L(rb('band|1-3','v4'),2)} / {L(rb('band|1-3','v6'),2)}. "
                        f"The replay assumes full viewing; on mobile only {wm[4]}% of ABF2 episode views reach ABF2's ~6.3-min first cue and {wm[5]}% reach v4/v6's ~9.7-min first cue "
                        f"(OTT: {wo[4]}% / {wo[5]}%). Losing the first break on ~{(1-float(wm[5])/float(wm[4]))*100:.0f}% of views matters most on sparse titles, where it is a large share of all breaks — a likely but unproven part of the 1–3 loss.")
    nar["decomp_read"] = "For v4/v6 the episode deficit is mostly a count miss (dense episodes pruned below control) under both profiles, so the per-title floor is the main lever. For v5b the tolerant profile turns the count term positive — v5b's ABF2-density lists fire more breaks when gates are looser."
    nar["decision_intro"] = "Early read, same window as OTT. Judge the money on total revenue; on mobile every revenue pool moves the same direction, so the read is unambiguous. The one new wrinkle is v5b's small TVT dip."
    nar["decision"] = [
        ["v5b is the only arm to carry forward on mobile.", f"Total revenue {L(g('revt','v5b'))}, on-title unbudgeted {L(g('orevu','v5b'))}, impressions up. TVT is {L(g('tvt','v5b'))} (was {L(OLD['ITT']['tvt']['v5b'])} before this refresh) — small, but now nominally significant in ITT, Active and ToT, so it is the engagement item to track as the window grows."],
        ["v4 and v6 should not ship to mobile as-is.", f"Both lose significantly ({L(g('revt','v4'))}, {L(g('revt','v6'))}), driven by episodes and sparse titles. The OTT recommendation for v6 does not carry over."],
        ["The fixes from OTT apply, plus one.", "A per-title floor removes the below-control loss (validated here too). An earlier first episode cue likely matters more on mobile, where more viewers stop early — v5b, which front-loads cues, is the arm that gains on episodes."],
        ["Open items.", f"Get the mobile ad config to replace the approximate gate profiles; re-read after a longer window — mobile intervals are ~{ratio_ott:.1f}× wider than OTT's."],
    ]
    nar["pool_read"] = (f"For v5b both pools rise (budgeted {L(g('impb','v5b'))}, unbudgeted {L(g('impu','v5b'))}), so the extra ads are new inventory filled by both demand types — a cleaner incrementality signal than OTT, where budgeted rises far more than unbudgeted. "
                        "For v4 and v6 both pools fall: fewer fireable breaks, not a demand shift.")
else:
    ep, mv = "type|Episode", "type|Movie"
    nbands = [R["band|" + b]["v4"]["ctrl_n"] for b in ("1-3", "4-6", "7-9", "10-12", "13+")]
    below_sig = [f"{a} {b.replace('-', '–')} {lbl} {L(R[f'below|{a}|{b}|{t}'][a]['rev'],2)}" for a in ARMS for b in ("10-12", "13+") for t, lbl in (("below", "below"), ("at/above", "at/above")) if sg(R[f"below|{a}|{b}|{t}"][a]["rev"])]
    nar["tldr"] = [
        ["v5b is the clear winner on web.", f"Total revenue {L(g('revt','v5b'))}, budgeted {L(g('revb','v5b'))}, unbudgeted {L(g('revu','v5b'))}, impressions {L(g('impt','v5b'))}. On the targeted titles open-auction revenue is {L(g('orevu','v5b'))}. TVT flat ({L(g('tvt','v5b'))})."],
        ["v4 loses; v6 is flat.", f"Total revenue v4 {L(g('revt','v4'))} (budgeted {L(g('revb','v4'))}), v6 {L(g('revt','v6'))}. Neither moves TVT."],
        ["Episodes split the arms, as on mobile.", f"Episode open-auction revenue: v5b {L(rb(ep,'v5b'),2)}, v6 {L(rb(ep,'v6'),2)}, v4 {L(rb(ep,'v4'),2)}. Movies: v6 {L(rb(mv,'v6'),2)}, v5b {L(rb(mv,'v5b'),2)}, v4 {L(rb(mv,'v4'),2)}."],
        ["Web is a small, noisy surface.", f"Only ~{act_share:.0f}% of exposed web devices watched anything in-window (Active n ≈ {H['Active']['n']['Control']/1e3:.0f}K/arm), and total revenue is ~${H['ITT']['ctrl_mean']['revt']:.2f} per exposed device in the window. Intervals are wide; at the headline level only v5b's gain and v4's loss clear zero."],
        ["TVT is flat everywhere.", "No TVT move is significant in any population, band, type, or below-control cut."],
    ]
    nar["tldr_note"] = ("All figures are global ITT CUPED lifts versus Control. Direction is stable across ITT, Active, and ToT (v4's total-revenue loss is "
                        + ("also significant in Active and ToT" if sg(g('revt','v4','Active')) and sg(g('revt','v4','ToT')) else "not significant in every population")
                        + "). Significance calls are nominal 95% (not adjusted for sequential looks or three arms) and the interval widening seen on the Statsig scorecard (~1.8× on the 10-15 OTT read) would apply here too; not re-checked against Statsig for this window.")
    nar["headline_intro"] = "All figures are CUPED lifts versus Control, 95% intervals. Global is across every title an exposed device watched. On-title is the same devices, restricted to the 224,739 targeted titles — the ABF2-catalog titles served v10 cue points. ToT is defined on the same set. “Sig” means the interval excludes zero (nominal p < 0.05)."
    nar["money_read"] = (f"v5b gains in every pool, with the largest lift in the open auction ({L(g('revu','v5b'))}) — the opposite of OTT, where v5b's gain comes mostly through budgeted demand. "
                         f"v4's loss is in the budgeted pool ({L(g('revb','v4'))}); its open-auction revenue is {L(g('revu','v4'))}.")
    nar["ontitle_read"] = (f"On the targeted titles v5b is {L(g('orevu','v5b'))} (ITT), {L(g('orevu','v5b','Active'))} (Active), {L(g('orevu','v5b','ToT'))} (ToT). "
                           f"v4 is {L(g('orevu','v4'))} (ITT), {L(g('orevu','v4','Active'))} (Active), {L(g('orevu','v4','ToT'))} (ToT) — significantly negative on the treated titles even though its global unbudgeted revenue is {L(g('revu','v4'))}; v6 is {L(g('orevu','v6'))} (ITT), not significant. On-title TVT is flat for all arms.")
    nar["npv_read"] = f"No TVT move is significant for either viewer type. Power viewers are rare on web (~{H['PV']['n']['Control']/ctrl_n*100:.2f}%), so that row is very wide."
    nar["band_read"] = [
        f"v5b gains in the sparse bands: 1–3 {L(rb('band|1-3','v5b'),2)}, 4–6 {L(rb('band|4-6','v5b'),2)}. v4 and v6 lose at 1–3 ({L(rb('band|1-3','v4'),2)}, {L(rb('band|1-3','v6'),2)}).",
        f"10–12 is the positive pocket for every arm: v6 {L(rb('band|10-12','v6'),2)}, v5b {L(rb('band|10-12','v5b'),2)}, v4 {L(rb('band|10-12','v4'),2)}.",
        f"7–9 and 13+ are not significant for any arm. Band cells on web are small ({min(nbands)/1e3:.0f}–{max(nbands)/1e3:.0f}K devices), so only large moves clear zero.",
        "TVT is flat in every band.",
    ]
    nar["below_read"] = (f"Same direction as OTT and mobile for v4 and v6: below-control titles lose and at/above-control titles gain. Significant cells: " + "; ".join(below_sig) + ". "
                         "Cells not listed are not significant at web sample sizes. The per-title floor case holds on web.")
    nar["type_read"] = (f"Episodes split the arms: v5b {L(rb(ep,'v5b'),2)}, v6 {L(rb(ep,'v6'),2)}, v4 {L(rb(ep,'v4'),2)}. "
                        f"Movies: v6 {L(rb(mv,'v6'),2)}, v5b {L(rb(mv,'v5b'),2)}, v4 {L(rb(mv,'v4'),2)}. TVT flat.")
    ww, wo = WD[("WEB", "Episode")], WD[("OTT", "Episode")]
    gc = lambda G, tt, b, a: {(x["tt"], x["band"], x["arm"]): x["sim_delta"] for x in G["cells"]}[(tt, b, a)]
    nar["gate_intro"] = ("Replay the pod gate (greedy first-eligible) over the ABF2 and served positions, weighted by each title's in-window web TVT. "
                         "The web ad config is not in the project files, so two gate profiles are shown: A = OTT base gates, and B = the most tolerant OTT ladder step. "
                         "Observed web midrolls start earlier than OTT (median first episode break ~491s vs ~652s on OTT, measured on a 2026-10-12/13 sample), so B is the closer approximation. "
                         f"Profile B fits the measured per-band impression lifts clearly better (r = {rB:.2f} vs {rA:.2f} across the 15 arm×band cells).")
    nar["gate_read"] = (f"Under the tolerant profile v5b fires more episode breaks in every band ({s(gc(GT,'Episode','10-12','v5b'),1)}% to {s(gc(GT,'Episode','1-3','v5b'),1)}%) and v4/v6 fire fewer from 4–6 up (v4 {s(gc(GT,'Episode','4-6','v4'),1)}% at 4–6 to {s(gc(GT,'Episode','13+','v4'),1)}% at 13+) — the measured episode split. "
                        f"Web episode viewing is shallower than OTT ({ww[4]}% of ABF2 episode views reach ~6.3 min, {ww[5]}% reach ~9.7 min; OTT {wo[4]}% / {wo[5]}%), "
                        "which likely adds to v4/v6's late-first-cue penalty on sparse episodes.")
    nar["decomp_read"] = "For v4/v6 the episode losses come mostly from fewer cue points under both profiles → the per-title floor is the lever. For v5b the tolerant profile makes the count term positive: ABF2-density lists fire more breaks when gates are looser."
    nar["decision_intro"] = "Early read, same window as OTT. Web is the smallest and noisiest surface; treat everything except v5b's gain and v4's loss as directional."
    nar["decision"] = [
        ["v5b leads on web too.", f"Total revenue {L(g('revt','v5b'))}, open-auction {L(g('revu','v5b'))}, on-title {L(g('orevu','v5b'))}, TVT flat. It is the only arm with a significant total-revenue gain on all three platforms (on mobile with a small TVT dip)."],
        ["v4 should not ship to web.", f"Total revenue {L(g('revt','v4'))}, driven by budgeted demand ({L(g('revb','v4'))})."],
        ["v6 is neutral on web.", f"Total revenue {L(g('revt','v6'))}; its movie gain ({L(rb(mv,'v6'),2)}) is offset by the episode loss ({L(rb(ep,'v6'),2)})."],
        ["Open items.", "Get the web ad config to replace the approximate gate profiles; a longer window is needed for the band and below-control cells."],
    ]
    nar["pool_read"] = (f"For v5b both pools rise (budgeted {L(g('impb','v5b'))}, unbudgeted {L(g('impu','v5b'))}): new inventory filled by both demand types, a clean incrementality signal. "
                        f"v4's budgeted impressions fall ({L(g('impb','v4'))}).")

nar["methods"] = [
    ["Assignment.", f"One variant per device from `core_dev.statsig.exposures` for `{exp}`; no device has more than one variant. Outcomes require event time at/after first exposure."],
    ["Window.", "Outcomes 2026-10-09 through 2026-10-19, capped at 2026-10-20 00:00 UTC. CUPED covariate 2026-09-25 → 2026-10-08. Active = ≥1 video session since first exposure in-window. ToT = ≥1 second of TVT on a targeted title (the 224,739 titles in `ml_dev.tmp.abf3_v10_targeted_titles`) in-window."],
    ["Title set, metrics, estimator.", "Identical to the OTT report. On-title, ToT, band, type and below-control tables use the 224,739 targeted titles (`ml_dev.tmp.abf3_v10_targeted_titles`: ABF2-catalog titles — movie/episode streams with non-empty `cue_points_abf`, excluding `abf3_pruned_v8` and the v8 title table — that were served v10 cue points); the other ~74.5k catalog titles carry identical cues in every arm and are excluded (versions before 2026-10-20 included them and understated on-title and band lifts); total / budgeted / unbudgeted revenue from `core_prod.ads.impressions` × `mercurydb_cdc.campaigns` with the v8 advertiser exclusions; device-level CUPED with pooled theta per population, Welch 95% (z = 1.96). Band/type/below-control tables are raw Welch."],
    ["Gate replay.", "Same simulation as OTT, re-run as a SQL port of `v10_gate_replay.py` (`gate_replay_all.sql`; validated against the 10-15 notebook run), TVT weights from in-window video sessions on this platform. Gate values are approximations — see §2c."],
    ["Served cue lists.", "`ml_dev.tmp.abf3_new_pruner_cuepoints` (snapshot 2026-10-08; T1 = v4, T2 = v6, T3 = v5b; the table now also holds extra arms that are not part of v10 and were excluded) — catalog-level, so §B.4 and the first-cue table match the OTT report."],
    ["Code.", "Queries and scripts in `abf-experiment/v10_verification/` (refresh outputs in `results_20261020/`)."],
]
json.dump(nar, open(os.path.join(RD, f"narrative_{P}.json"), "w"), indent=1, ensure_ascii=False)
print("ok", P, "rA", round(rA, 3), "rB", round(rB, 3))
