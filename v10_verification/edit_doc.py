"""Apply the verified v10 numbers to the ABF3 v10 OTT results doc (in place, formatting preserved)."""
import json, sys, docx

SRC, VALS, GATE, OUT = sys.argv[1:5]
V = json.load(open(VALS)); H = V["head"]; R = V["raw"]
G = json.load(open(GATE)); CORR = float(sys.argv[5])
d = docx.Document(SRC)
ARMS = ("v4", "v5b", "v6")
MISSES = []


def s(x, nd):
    x = round(x, nd) + 0.0
    t = f"{x:+.{nd}f}" if x != 0 else f"{0:+.{nd}f}"
    return t.replace("-", "−")


def sig(e):
    return "sig" if e["lo"] > 0 or e["hi"] < 0 else "ns"


def full(e, nd=3, tag=True):
    t = f"{s(e['l'], nd)}% [{s(e['lo'], nd)}, {s(e['hi'], nd)}]"
    return t + (" " + sig(e) if tag else "")


def short(e, nd=2):
    return f"{s(e['l'], nd)}% {sig(e)}"


def tvt_cell(e, nd=2):
    # doc convention in 2b: show the interval only when significant
    return full(e, nd) if sig(e) == "sig" else short(e, nd)


def setcell(cell, text):
    runs = [r for p in cell.paragraphs for r in p.runs]
    if not runs:
        cell.paragraphs[0].add_run(text); return
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""


def rep(old, new, count_expected=None):
    """Replace text inside single runs across all paragraphs + table cells."""
    hits = 0
    pars = list(d.paragraphs) + [p for t in d.tables for row in t.rows for c in row.cells for p in c.paragraphs]
    for p in pars:
        for r in p.runs:
            if old in r.text:
                r.text = r.text.replace(old, new); hits += 1
    if hits == 0:
        MISSES.append(old)
    return hits


n = lambda x: f"{x:,}"

# ---------------- tables ----------------
T = d.tables
# T0 TL;DR + T1 revenue three ways
for i, g in enumerate(ARMS):
    row0 = {"v4": 1, "v6": 2, "v5b": 3}[g]
    I = H["ITT"]
    setcell(T[0].rows[row0].cells[1], full(I["revt"][g]))
    setcell(T[0].rows[row0].cells[2], short(I["revb"][g], 3))
    setcell(T[0].rows[row0].cells[3], short(I["revu"][g], 3))
    setcell(T[0].rows[row0].cells[4], short(I["impt"][g], 3))
    setcell(T[0].rows[row0].cells[5], short(I["tvt"][g], 3))
    row1 = {"v4": 1, "v5b": 2, "v6": 3}[g]
    for ci, m in enumerate(("revt", "revb", "revu", "impt"), start=1):
        setcell(T[1].rows[row1].cells[ci], full(I[m][g]))

# T2 global unbudgeted detail, T3 on-title
for bi, pop in enumerate(("ITT", "Active", "ToT")):
    for ai, g in enumerate(ARMS):
        r = 1 + 3 * bi + ai
        P = H[pop]
        setcell(T[2].rows[r].cells[2], n(P["n"][g]))
        setcell(T[2].rows[r].cells[3], full(P["revu"][g]))
        setcell(T[2].rows[r].cells[4], full(P["impu"][g]))
        setcell(T[2].rows[r].cells[5], full(P["tvt"][g]))
        setcell(T[3].rows[r].cells[2], full(P["orevu"][g]))
        setcell(T[3].rows[r].cells[3], full(P["oimpu"][g]))
        setcell(T[3].rows[r].cells[4], full(P["otvt"][g]))

# T4 NPV / PV TVT
for bi, pop in enumerate(("NPV", "PV")):
    for ai, g in enumerate(ARMS):
        r = 1 + 3 * bi + ai; e = H[pop]["tvt"][g]
        setcell(T[4].rows[r].cells[2], n(H[pop]["n"][g]))
        setcell(T[4].rows[r].cells[3], full(e, 3, tag=False))
        setcell(T[4].rows[r].cells[4], "Yes" if sig(e) == "sig" else "No")

# T5 bands
for bi, b in enumerate(("1-3", "4-6", "7-9", "10-12", "13+")):
    for ai, g in enumerate(ARMS):
        r = 1 + 3 * bi + ai; x = R["band|" + b][g]
        setcell(T[5].rows[r].cells[2], full(x["rev"], 2))
        setcell(T[5].rows[r].cells[3], short(x["tvt"]))
        setcell(T[5].rows[r].cells[4], full(x["imps"], 2))
        setcell(T[5].rows[r].cells[5], n(x["n"]))

# T6 below vs at/above (row order: 10-12 below v4,v5b,v6; 10-12 at/above; 13+ below; 13+ at/above)
r = 1
for b in ("10-12", "13+"):
    for tag in ("below", "at/above"):
        for g in ARMS:
            x = R[f"below|{g}|{b}|{tag}"][g]
            setcell(T[6].rows[r].cells[3], full(x["rev"], 2))
            setcell(T[6].rows[r].cells[4], tvt_cell(x["tvt"]))
            r += 1

# T7 movies vs episodes
for ti, tt in enumerate(("Movie", "Episode")):
    for ai, g in enumerate(ARMS):
        r = 1 + 3 * ti + ai; x = R["type|" + tt][g]
        setcell(T[7].rows[r].cells[2], full(x["rev"], 2))
        setcell(T[7].rows[r].cells[3], short(x["tvt"]))
        setcell(T[7].rows[r].cells[4], short(x["imps"]))
        setcell(T[7].rows[r].cells[5], n(x["n"]))

# T9 gate replay type x band; T10 episode decomposition (from the Databricks gate run)
cell = {(c["tt"], c["band"], c["arm"]): c["sim_delta"] for c in G["cells"]}
for row in T[9].rows[1:]:
    tt, b = row.cells[0].text.strip(), row.cells[1].text.strip().replace("–", "-")
    for ci, g in enumerate(ARMS, start=2):
        setcell(row.cells[ci], f"{s(cell[(tt, b, g)], 1)}%")
dec = {x["arm"]: x for x in G["episode_decomp"]}
for row in T[10].rows[1:]:
    g = row.cells[0].text.strip()
    setcell(row.cells[1], f"{s(dec[g]['total'], 1)}%")
    setcell(row.cells[2], f"{s(dec[g]['from_fewer'], 1)}%")
    setcell(row.cells[3], f"{s(dec[g]['from_placement'], 1)}%")
# add the missing "gains" column so the parts sum to the total
from copy import deepcopy
grid = T[10]._tbl.tblGrid
grid.append(deepcopy(grid.gridCol_lst[-1]))
for ri, row in enumerate(T[10].rows):
    tc = deepcopy(row.cells[3]._tc); row._tr.append(tc)
    newc = row.cells[-1]
    setcell(newc, "from gains (at/above titles)" if ri == 0 else f"{s(dec[row.cells[0].text.strip()]['from_gains'], 1)}%")


# ---------------- text ----------------
cn = lambda g: n(R[g]["v4"]["ctrl_n"])
rep("10:00 EST (14:00 UTC)", "10:00 EDT (14:00 UTC)")
rep("10:00 EST)", "10:00 EDT)")
e = H["ITT"]["tvt"]["v5b"]; pv = H["PV"]["tvt"]["v5b"]
rep("(−0.189% global, −0.278% on power viewers)", f"({s(e['l'],3)}% global, {s(pv['l'],3)}% on power viewers)")
mv, ep = R["type|Movie"], R["type|Episode"]
rep("v5b +1.39%, v6 +2.54%", f"v5b {s(mv['v5b']['rev']['l'],2)}%, v6 {s(mv['v6']['rev']['l'],2)}%")
rep("(v4 −1.20%, v5b −0.43%, v6 −1.65%", f"(v4 {s(ep['v4']['rev']['l'],2)}%, v5b {s(ep['v5b']['rev']['l'],2)}%, v6 {s(ep['v6']['rev']['l'],2)}%")
cm = H["ITT"]["ctrl_mean"]
rep("total revenue 0.586, budgeted 0.173, all-ad impressions 50.2",
    f"total revenue {cm['revt']:.3f}, budgeted {cm['revb']:.3f}, all-ad impressions {cm['impt']:.1f}")
rep("Active 4,057,913 · ToT 3,252,581", f"Active {n(H['Active']['n']['Control'])} · ToT {n(H['ToT']['n']['Control'])}")
pvs = H["PV"]["n"]["Control"] / H["ITT"]["n"]["Control"] * 100
rep("(~14.1% per arm)", f"(~{pvs:.1f}% per arm)")
rep("v4 non-power +0.30%", f"v4 non-power {s(H['NPV']['tvt']['v4']['l'],2)}%")
rep("v5b power −0.28%", f"v5b power {s(H['PV']['tvt']['v5b']['l'],2)}%")
rep("1–3 1,026,361 · 4–6 1,339,950 · 7–9 1,358,016 · 10–12 1,435,468 · 13+ 1,891,700",
    " · ".join(f"{b.replace('-', '–')} {cn('band|'+b)}" for b in ("1-3", "4-6", "7-9", "10-12", "13+")))
b10 = R["band|10-12"]; b13 = R["band|13+"]
rep("(+3.70%) then v5b (+2.86%)", f"({s(b10['v6']['rev']['l'],2)}%) then v5b ({s(b10['v5b']['rev']['l'],2)}%)")
rep(" (−1.65%, −0.85%); v6 is a small significant positive.",
    f" ({s(b13['v4']['rev']['l'],2)}%, {s(b13['v5b']['rev']['l'],2)}%); v6 is roughly flat ({s(b13['v6']['rev']['l'],2)}%, interval just includes zero).")
rep("1–3 is flat.", f"1–3 is flat on revenue (v5b impressions {s(R['band|1-3']['v5b']['imps']['l'],2)}%, just significant).")
rep("movies 2,494,085 · episodes 1,833,836", f"movies {cn('type|Movie')} · episodes {cn('type|Episode')}")
rep("Across the 15 arm×band cells", "Across the 15 arm×band cells (3 arms × 5 ABF2 bands, movies and episodes pooled)")
rep("r = 0.55", f"r = {CORR:.2f}")
f = {(x["tt"], x["arm"]): x for x in G["first"]}
fe = lambda a, k="first_srv": f"~{f[('Episode', a)][k]:.0f}s"
rep(" episodes ABF2 ~620s; v4 ~658s, v6 ~656s (later), v5b ~596s (earlier). Movies ~1097s control; all arms within ~20s.",
    f" episodes ABF2 {fe('v4','first_ctl')}; v4 {fe('v4')}, v6 {fe('v6')} (slightly later), v5b {fe('v5b')} (earlier). "
    f"Movies ~{f[('Movie','v4')]['first_ctl']:.0f}s control; v4 {s(f[('Movie','v4')]['first_srv']-f[('Movie','v4')]['first_ctl'],0)}s, "
    f"v6 {s(f[('Movie','v6')]['first_srv']-f[('Movie','v6')]['first_ctl'],0)}s, v5b {s(f[('Movie','v5b')]['first_srv']-f[('Movie','v5b')]['first_ctl'],0)}s vs control. "
    f"Unweighted title averages show a bigger episode gap (ABF2 {fe('v4','unw_first_ctl')}, v4 {fe('v4','unw_first_srv')}, v6 {fe('v6','unw_first_srv')}, v5b {fe('v5b','unw_first_srv')}), "
    f"so the late first break sits mostly in lower-TVT titles.")
rep("Episode deficit — count vs position (TVT-weighted, pooled over episodes):",
    "Episode deficit — count vs position (TVT-weighted, pooled over episodes; total = fewer cue points + placement + gains on titles kept at/above control):")

# verification note, appended after the last Appendix C bullet
last = d.paragraphs[-1]
for p in d.paragraphs:
    if p.text.startswith("Still omitted."):
        last = p
newp = deepcopy(last._p); last._p.addnext(newp)
from docx.text.paragraph import Paragraph
vp = Paragraph(newp, last._parent)
vp.runs[0].text = "Verification (2026-10-15)."
vp.runs[1].text = (" Every table was re-derived from the raw tables on Databricks with the definitions above, and the gate replay was re-run "
    "(all-platform in-window TVT weights; OTT-only weights move no reported cell by more than ~0.6pp). "
    "Lifts reproduced to rounding. Updated in this version: Control per-device means; Active/ToT and band/type device counts "
    "(now applying the full 14:00 UTC cap; the earlier counts matched a cutoff a few hours earlier, which moved those lifts by ≤0.15pp); "
    "power-viewer share; first-fireable-break timing (now TVT-weighted as labelled); two significance calls (13+ v6 revenue is now ns; 1–3 v5b impressions now just sig); "
    "the episode-deficit table (added the gains column so the parts sum to the total); EST → EDT.")
for r in vp.runs[2:]:
    r.text = ""

json.dump(MISSES, open(OUT + ".misses.json", "w"))
d.save(OUT)
print("saved", OUT, "misses:", MISSES)
