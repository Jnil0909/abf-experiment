import json, math, sys

d = json.load(open(sys.argv[1]))
cols = d["columns"]
rows = [dict(zip(cols, r)) for r in d["rows"]]
S = {}
for r in rows:
    S[(r["grp"], r["variant"])] = {k: float(v) for k, v in r.items() if k not in ("grp", "variant")}


def lift(t, c, m):
    mt = t["s_" + m] / t["n"]; mc = c["s_" + m] / c["n"]
    vt = (t["ss_" + m] - t["n"] * mt * mt) / (t["n"] - 1)
    vc = (c["ss_" + m] - c["n"] * mc * mc) / (c["n"] - 1)
    se = math.sqrt(vt / t["n"] + vc / c["n"]); diff = mt - mc
    lo, hi = 100 * (diff - 1.96 * se) / mc, 100 * (diff + 1.96 * se) / mc
    return f"{100*diff/mc:+6.2f}% [{lo:+.2f}, {hi:+.2f}] {'sig' if lo > 0 or hi < 0 else 'ns '}"


grps = sorted({g for g, _ in S})
for g in grps:
    c = S.get((g, "Control"))
    for arm in ("v4", "v5b", "v6"):
        t = S.get((g, arm))
        if not t or not c:
            continue
        print(f"{g:28} {arm:4} n={int(t['n']):>9,} ctrl_n={int(c['n']):>9,}  rev {lift(t,c,'rev')}  tvt {lift(t,c,'tvt')}  imps {lift(t,c,'imps')}")
