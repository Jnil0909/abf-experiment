"""Turn the v10 Databricks sufficient-stats outputs into lift dicts (JSON) for the doc edit."""
import json, math, sys

ARMS = ("v4", "v5b", "v6")


def load(p):
    d = json.load(open(p))
    return [dict(zip(d["columns"], r)) for r in d["rows"]]


def welch(mt, vt, nt, mc, vc, nc):
    diff = mt - mc; se = math.sqrt(vt / nt + vc / nc)
    return dict(l=100 * diff / mc, lo=100 * (diff - 1.96 * se) / mc, hi=100 * (diff + 1.96 * se) / mc)


# ---- headline (CUPED) ----
MET = {"tvt": "tvt", "otvt": "tvt", "revt": "revt", "revb": "revb", "impt": "impt", "impb": "impb",
       "revu": "revu", "impu": "impu", "orevu": "revu", "oimpu": "impu"}
rows = load(sys.argv[1])
for r in rows:
    for k in list(r):
        if k not in ("pop", "variant"):
            r[k] = float(r[k])
head = {}
for pop in ("ITT", "Active", "ToT", "NPV", "PV"):
    arms = {r["variant"]: r for r in rows if r["pop"] == pop}
    N = sum(a["n"] for a in arms.values())
    head[pop] = {"n": {g: int(a["n"]) for g, a in arms.items()},
                 "ctrl_mean": {m: arms["Control"]["sy_" + m] / arms["Control"]["n"] for m in MET}}
    for m, x in MET.items():
        sx = sum(a["sx_" + x] for a in arms.values()); sxx = sum(a["sxx_" + x] for a in arms.values())
        sy = sum(a["sy_" + m] for a in arms.values()); sxy = sum(a["sxy_" + m] for a in arms.values())
        th = ((sxy - sx * sy / N) / (N - 1)) / ((sxx - sx * sx / N) / (N - 1)); xbar = sx / N
        st = {}
        for g, a in arms.items():
            n = a["n"]; my = a["sy_" + m] / n; mx = a["sx_" + x] / n
            vy = (a["syy_" + m] - n * my * my) / (n - 1); vx = (a["sxx_" + x] - n * mx * mx) / (n - 1)
            cv = (a["sxy_" + m] - n * mx * my) / (n - 1)
            st[g] = (my - th * (mx - xbar), vy - 2 * th * cv + th * th * vx, n)
        c = st["Control"]
        for g in ARMS:
            head[pop].setdefault(m, {})[g] = welch(*st[g], *c)

# ---- bands / type / below (raw Welch) ----
S = {}
for r in load(sys.argv[2]):
    S[(r["grp"], r["variant"])] = {k: float(v) for k, v in r.items() if k not in ("grp", "variant")}
raw = {}
for (g, v), t in S.items():
    if v == "Control":
        continue
    c = S[(g, "Control")]
    out = {"n": int(t["n"]), "ctrl_n": int(c["n"])}
    for m in ("rev", "tvt", "imps"):
        def mv(s):
            mu = s["s_" + m] / s["n"]; return mu, (s["ss_" + m] - s["n"] * mu * mu) / (s["n"] - 1), s["n"]
        out[m] = welch(*mv(t), *mv(c))
    raw.setdefault(g, {})[v] = out

json.dump(dict(head=head, raw=raw), open(sys.argv[3], "w"), indent=1)
print("ok", sys.argv[3])
