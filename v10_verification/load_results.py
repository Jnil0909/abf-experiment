"""Parse the 2026-10-19 refresh outputs (results_20261019/*.tsv) into the JSON shapes the doc builders use.

Writes, per platform P in (ott, mobile, web):
  values_{P}.json   {head: {pop: {n:{arm:int}, ctrl_mean:{..}, metric:{arm:{l,lo,hi}}}}, raw: {grp: {arm: {n, ctrl_n, rev, tvt, imps}}}}
  gate_{P}_base.json / gate_{P}_tol.json   {cells, band_pooled, episode_decomp, first}   (OTT: base only, all-platform TVT weights)
Usage: python3 load_results.py <results_dir>
"""
import json, sys, os

D = sys.argv[1]
ARMS = ("v4", "v5b", "v6")


def tsv(name):
    return [l.rstrip("\n").split("\t") for l in open(os.path.join(D, name)) if l.strip()]


def lift3(s, sep="|"):
    l, lo, hi = (float(x) for x in s.split(sep))
    return dict(l=l, lo=lo, hi=hi)


# ---- headline ----
head = {}
for plat, pop, m, s in tsv("headline.tsv"):
    P = head.setdefault(plat, {}).setdefault(pop, {"n": {}, "ctrl_mean": {}})
    if m == "n":
        P["n"] = {kv.split(":")[0]: int(kv.split(":")[1]) for kv in s.split(";")}
    elif m == "cm":
        P["ctrl_mean"] = {kv.split(":")[0]: float(kv.split(":")[1]) for kv in s.split(";")}
    else:
        P[m] = {kv.split(":")[0]: lift3(kv.split(":")[1]) for kv in s.split(";")}

# ---- bands / type / below (raw Welch) ----
raw = {}
for plat, grp, s in tsv("bands.tsv"):
    for part in s.split(";"):
        arm, rest = part.split(":", 1)
        nn, rev, tvt, imps = rest.split("|")
        n, cn = nn.split("/")
        raw.setdefault(plat, {}).setdefault(grp, {})[arm] = dict(
            n=int(n), ctrl_n=int(cn), rev=lift3(rev, ","), tvt=lift3(tvt, ","), imps=lift3(imps, ","))

# ---- gate replay ----
gate = {}
for k, prof, wset, tt, band, s in tsv("gate.tsv"):
    G = gate.setdefault((prof, wset), dict(cells=[], band_pooled=[], episode_decomp=[], first=[]))
    for part in s.split(";"):
        arm, rest = part.split(":", 1)
        if k == "cell":
            G["cells"].append(dict(tt=tt, band=band, arm=arm, sim_delta=float(rest)))
        elif k == "pooled":
            G["band_pooled"].append(dict(band=band, arm=arm, sim_delta=float(rest)))
        elif k == "decomp":
            t, f, p, g = (float(x) for x in rest.split("|"))
            G["episode_decomp"].append(dict(arm=arm, total=t, from_fewer=f, from_placement=p, from_gains=g))
        elif k == "first":
            fc, fs, ufc, ufs = (float(x) for x in rest.split("|"))
            G["first"].append(dict(tt=tt, arm=arm, first_ctl=fc, first_srv=fs, unw_first_ctl=ufc, unw_first_srv=ufs))

for plat in ("OTT", "MOBILE", "WEB"):
    p = plat.lower()
    json.dump(dict(head=head[plat], raw=raw[plat]), open(os.path.join(D, f"values_{p}.json"), "w"), indent=1)
    json.dump(gate[("A", "ALL" if plat == "OTT" else plat)], open(os.path.join(D, f"gate_{p}_base.json"), "w"), indent=1)
    if plat != "OTT":
        json.dump(gate[("B", plat)], open(os.path.join(D, f"gate_{p}_tol.json"), "w"), indent=1)
print("ok", sorted(gate))
