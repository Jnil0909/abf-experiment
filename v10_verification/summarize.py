import json, sys
V = json.load(open(sys.argv[1])); GB = json.load(open(sys.argv[2])); GT = json.load(open(sys.argv[3]))
H, R = V["head"], V["raw"]
f = lambda e: f"{e['l']:+.3f} [{e['lo']:+.3f},{e['hi']:+.3f}]{'*' if e['lo']>0 or e['hi']<0 else ' '}"
f2 = lambda e: f"{e['l']:+.2f}{'*' if e['lo']>0 or e['hi']<0 else ' '}"
print("n:", {p: H[p]["n"] for p in ("ITT", "Active", "ToT", "PV")})
print("ctrl means ITT:", {k: round(v, 4) for k, v in H["ITT"]["ctrl_mean"].items()})
for pop in ("ITT", "Active", "ToT", "NPV", "PV"):
    for m in (("revt", "revb", "revu", "impt", "impb", "impu", "tvt", "orevu", "oimpu", "otvt") if pop in ("ITT",) else ("revt", "revu", "tvt", "orevu", "otvt")):
        print(f"{pop:6} {m:6}", "  ".join(f"{g}:{f(H[pop][m][g])}" for g in ("v4", "v5b", "v6")))
for g in sorted(R):
    if g.startswith("band|"): continue
    if not g.startswith("band|"):
        print(f"{g:26}", "  ".join(f"{a}: rev {f2(R[g][a]['rev'])} tvt {f2(R[g][a]['tvt'])} imp {f2(R[g][a]['imps'])} n={R[g][a]['n']}" for a in ("v4", "v5b", "v6") if a in R[g]))
for nm, G in (("BASE", GB), ("TOL", GT)):
    c = {(x["tt"], x["band"], x["arm"]): x["sim_delta"] for x in G["cells"]}
    print(nm, "gate:", "; ".join(f"{t[0]}{b}:" + "/".join(str(c[(t, b, a)]) for a in ("v4", "v5b", "v6")) for t in ("Movie", "Episode") for b in ("4-6", "7-9", "10-12", "13+")))
    print(nm, "decomp:", G["episode_decomp"])
    print(nm, "first:", [(x["tt"], x["arm"], x["first_ctl"], x["first_srv"]) for x in G["first"]])
