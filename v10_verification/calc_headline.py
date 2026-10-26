import json, math, sys

d = json.load(open(sys.argv[1]))
cols = d["columns"]
rows = [dict(zip(cols, r)) for r in d["rows"]]
for r in rows:
    for k, v in r.items():
        if k not in ("pop", "variant"):
            r[k] = float(v)

# metric -> covariate
MET = {"tvt": "tvt", "otvt": "tvt", "revt": "revt", "revb": "revb", "impt": "impt", "impb": "impb",
       "revu": "revu", "impu": "impu", "orevu": "revu", "oimpu": "impu"}


def lifts(pop):
    arms = {r["variant"]: r for r in rows if r["pop"] == pop}
    N = sum(a["n"] for a in arms.values())
    out = {}
    for m, x in MET.items():
        # pooled theta across arms in this population
        sx = sum(a["sx_" + x] for a in arms.values()); sxx = sum(a["sxx_" + x] for a in arms.values())
        sy = sum(a["sy_" + m] for a in arms.values()); sxy = sum(a["sxy_" + m] for a in arms.values())
        vx = (sxx - sx * sx / N) / (N - 1); cxy = (sxy - sx * sy / N) / (N - 1)
        th = cxy / vx if vx > 0 else 0.0
        xbar = sx / N
        st = {}
        for g, a in arms.items():
            n = a["n"]
            my = a["sy_" + m] / n; mx = a["sx_" + x] / n
            vy = (a["syy_" + m] - n * my * my) / (n - 1)
            vxa = (a["sxx_" + x] - n * mx * mx) / (n - 1)
            cv = (a["sxy_" + m] - n * mx * my) / (n - 1)
            st[g] = dict(n=n, raw_m=my, raw_v=vy, adj_m=my - th * (mx - xbar), adj_v=vy - 2 * th * cv + th * th * vxa)
        c = st["Control"]
        for g in ("v4", "v5b", "v6"):
            t = st[g]
            res = {}
            for kind in ("adj", "raw"):
                diff = t[kind + "_m"] - c[kind + "_m"]
                se = math.sqrt(t[kind + "_v"] / t["n"] + c[kind + "_v"] / c["n"])
                base = c[kind + "_m"]
                res[kind] = (100 * diff / base, 100 * (diff - 1.96 * se) / base, 100 * (diff + 1.96 * se) / base)
            out[(g, m)] = dict(n=t["n"], ctrl_mean=c["raw_m"], ctrl_n=c["n"], **res)
    return out


for pop in ("ITT", "Active", "ToT", "NPV", "PV"):
    o = lifts(pop)
    print(f"\n=== {pop}  (Control n={int(o[('v4','tvt')]['ctrl_n']):,})")
    print("arm  metric   n          ctrl_mean   CUPED lift [95% CI]            raw lift")
    for g in ("v4", "v5b", "v6"):
        for m in MET:
            r = o[(g, m)]
            a = r["adj"]; w = r["raw"]
            sig = "sig" if (a[1] > 0 or a[2] < 0) else "ns"
            print(f"{g:4} {m:6} {int(r['n']):>10,} {r['ctrl_mean']:10.4f}  {a[0]:+7.3f}% [{a[1]:+.3f}, {a[2]:+.3f}] {sig:3}   {w[0]:+7.3f}%")
