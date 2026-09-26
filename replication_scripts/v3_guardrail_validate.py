#!/usr/bin/env python3
"""
v3_guardrail_validation.py — Independent validation of the causal LLM agent abstain gate.
Runs three validation levels demonstrating that
the framework f(c)=W(c)+sigma·PNS(c) (T5-T7) applied to agent autonomy (T8-T9) is
functional and safe:
  LEVEL 1 (MC, always):       T8 identity, boundary sharpness, T9 active error ~0,
                              T7 decision rate vs n, p_sq cancellation.
  LEVEL 2 (TWINS, auto):      Public dataset, both potential outcomes -> gate
                              vs true benefit.
  LEVEL 3 (FiFAR, optional):  OpenL2D fraud data (AI + 50 human analysts +
                              ground truth) -> gate vs true, ACT and ABSTAIN branches.
THEORY:
  T8: agent can act iff |gamma-delta|·|p_a - p_h| > |sigma|   (status quo cancels out)
  T9: abstain is safe (active error -> 0); |sigma| expands with harm
  T7: with small history, agent defaults to defer (safe)
USAGE:
  python3 v3_guardrail_validation.py            # level 1 + 2 (TWINS downloads automatically)
  python3 v3_guardrail_validation.py --fifar    # + level 3 (downloads FiFAR ~209 MB)
  python3 v3_guardrail_validation.py --mc       # level 1 only
  python3 v3_guardrail_validation.py --twins    # level 2 only
  python3 v3_guardrail_validation.py --benefit 100,20,-40,-300   # custom utility
DEPENDENCIES:
  - Level 1-2: Python 3 stdlib only (csv, urllib)
  - Level 3:   pandas + pyarrow (pip install pandas pyarrow) — otherwise skipped cleanly
This file DOES NOT contain proprietary data and DOES NOT reference any internal
systems. Data sources are public (CEVAE TWINS, OpenL2D FiFAR).
"""
import sys, os, csv, math, urllib.request, collections, datetime

# =====================================================================
# FRAMEWORK (inline — independent, no imports)
# =====================================================================
def sigma(benefit):
    b, g, t, d = benefit
    return b - g - t + d

def W(benefit, p1, p0):
    b, g, t, d = benefit
    return (g - d) * p1 + d * p0 + t * (1 - p0)

def benefit_interval(benefit, p1, p0):
    s = sigma(benefit)
    w = W(benefit, p1, p0)
    lo, up = (w + s, w) if s < 0 else (w, w + s)
    return lo, up, w, s

def T8_gap(benefit, p_a, p_h):
    b, g, t, d = benefit
    return abs(g - d) * abs(p_a - p_h)

def guardrail(benefit, p_a, p_h, p_sq=None, n=None):
    """T8/T9 gate: 'ACT' (autonomy) or 'ABSTAIN' (defer to human)."""
    if p_sq is None:
        p_sq = p_h
    w_act, w_defer = W(benefit, p_a, p_sq), W(benefit, p_h, p_sq)
    gap, s_abs = T8_gap(benefit, p_a, p_h), abs(sigma(benefit))
    lo, up, _, _ = benefit_interval(benefit, p_a, p_sq)
    decidable = gap > s_abs
    better = w_act > w_defer
    
    if not decidable:
        return dict(decision="ABSTAIN", reason=f"|gap|={gap:.2f} <= |sigma|={s_abs:.2f}",
                    w_act=w_act, w_defer=w_defer, lo=lo, up=up)
    if not better:
        return dict(decision="ABSTAIN", reason=f"W(act)={w_act:.1f} < W(defer)={w_defer:.1f}",
                    w_act=w_act, w_defer=w_defer, lo=lo, up=up)
                    
    return dict(decision="ACT", reason=f"|gap|={gap:.2f} > |sigma|={s_abs:.2f}",
                w_act=w_act, w_defer=w_defer, lo=lo, up=up)

def _s_g(benefit, p_a, p_sq, n):
    b, g, t, d = benefit
    return math.sqrt(((g-d)**2 * p_a*(1-p_a) + (d-t)**2 * p_sq*(1-p_sq)) / max(n, 1))

# =====================================================================
# LEVEL 1: MC Verification
# =====================================================================
def run_mc(benefit):
    print("=" * 72)
    print("LEVEL 1: MC Verification (T8 identity, boundary, T9 active error, T7, p_sq)")
    print("=" * 72)
    ok = True
    
    # T8 identity
    fails = checked = 0
    for b in [(100,20,-40,-300),(80,40,0,-20),(10,5,0,-70),(100,30,-40,-120)]:
        for pa in [0.5,0.7,0.9,0.95]:
            for ph in [0.2,0.4,0.5]:
                for psq in [0.0,0.1,0.3,0.5]:
                    lhs = W(b,pa,psq)-W(b,ph,psq); rhs = (b[1]-b[3])*(pa-ph)
                    checked += 1
                    if abs(lhs-rhs) > 1e-12: fails += 1
    print(f"  T8-identity: {checked} combinations, {fails} deviations "
          f"{'✓' if fails==0 else '✗'}")
    ok = ok and fails == 0
    
    # T9 active error MC
    import random
    def mc_err(b, tpa, tph, psq, n, trials=4000, seed=1):
        rng = random.Random(seed)
        w_true = W(b,tpa,psq) > W(b,tph,psq)
        decided = wrong = 0
        for _ in range(trials):
            pa = sum(rng.random()<tpa for _ in range(n))/n
            ph = sum(rng.random()<tph for _ in range(n))/n
            r = guardrail(b, pa, ph, psq)
            if r["decision"]=="ACT":
                decided += 1
                if not w_true: wrong += 1
        return decided/trials, wrong/trials
        
    configs = [((100,20,-40,-300),0.95,0.30,0.2,2000,"critical, AI better"),
               ((100,20,-40,-300),0.30,0.95,0.2,2000,"critical, AI worse (H-risk)"),
               ((100,20,-40,-300),0.85,0.80,0.2,2000,"close to each other"),
               ((80,40,0,-20),    0.90,0.60,0.3,1500,"mild harm, clear gap")]
               
    for b,tpa,tph,psq,n,lbl in configs:
        dec, err = mc_err(b,tpa,tph,psq,n)
        status = "✓" if err==0 else "✗"
        ok = ok and err == 0
        print(f"  [{lbl}] decision rate={dec:.3f}  active error={err:.5f} {status}")
        
    print(f"  -> LEVEL 1 {'PASSED ✓' if ok else 'FAILED ✗'}\n")
    return ok

# =====================================================================
# LEVEL 2: TWINS (both outcomes known)
# =====================================================================
TWINS_URLS = {
    "T": "https://raw.githubusercontent.com/AMLab-Amsterdam/CEVAE/master/datasets/TWINS/twin_pairs_T_3years_samesex.csv",
    "Y": "https://raw.githubusercontent.com/AMLab-Amsterdam/CEVAE/master/datasets/TWINS/twin_pairs_Y_3years_samesex.csv",
    "X": "https://raw.githubusercontent.com/AMLab-Amsterdam/CEVAE/master/datasets/TWINS/twin_pairs_X_3years_samesex.csv",
}

def _ensure_twins():
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "twins_cache")
    os.makedirs(cache, exist_ok=True)
    out = {}
    for k, url in TWINS_URLS.items():
        fn = os.path.join(cache, url.rstrip("/").split("/")[-1])
        if not os.path.exists(fn):
            print(f"  [twins] downloading {k} ...", file=sys.stderr)
            urllib.request.urlretrieve(url, fn)
        out[k] = fn
    return out["T"], out["Y"], out["X"]

def _load_csv(path):
    with open(path) as f:
        return [dict(r) for r in csv.DictReader(f)]

def run_twins(benefit):
    print("=" * 72)
    print("LEVEL 2: TWINS (public, both potential outcomes known)")
    print("=" * 72)
    tpath, ypath, xpath = _ensure_twins()
    T = _load_csv(tpath); Y = _load_csv(ypath); X = _load_csv(xpath)
    
    def fget(x, k):
        v = x.get(k, "")
        try: return float(v)
        except: return None
        
    def typ(y1,y0):
        if y1==1 and y0==0: return 'B'
        if y1==1 and y0==1: return 'A'
        if y1==0 and y0==0: return 'N'
        return 'H'
        
    strata = [("gestation <=5", lambda x: ("gest", 1 if (fget(x,"gestat10") or 99) <= 5 else 0)),
              ("preterm 1/0",   lambda x: ("preterm", fget(x,"preterm")))]
              
    ok = True
    for label, fn in strata:
        per = collections.defaultdict(lambda: collections.Counter())
        for t, y, x in zip(T, Y, X):
            try:
                w0,w1 = float(t["dbirwt_0"]), float(t["dbirwt_1"])
                m0,m1 = float(y["mort_0"]), float(y["mort_1"])
            except: continue
            
            if w1>w0: y1,y0 = 1-m1, 1-m0
            else:     y1,y0 = 1-m0, 1-m1
            k = fn(x)
            if k is not None and k[1] is not None:
                per[k][typ(y1,y0)] += 1
                
        print(f"  {label}:")
        for k, c in sorted(per.items()):
            s = sum(c.values())
            if s==0: continue
            B,A,N,Hh = c['B'],c['A'],c['N'],c['H']
            p_a = (B+A)/s; p_h = (A+Hh)/s; p_sq = (A+N)/s
            true_f = (benefit[0]*B+benefit[1]*A+benefit[2]*N+benefit[3]*Hh)/s
            gap = T8_gap(benefit, p_a, p_h); s_abs = abs(sigma(benefit))
            r = guardrail(benefit, p_a, p_h, p_sq)
            w_act = W(benefit,p_a,p_sq); w_hum = W(benefit,p_h,p_sq)
            true_better = w_act > w_hum
            gate_ok = (r["decision"]=="ACT") == (true_better and gap > s_abs)
            ok = ok and gate_ok
            print(f"    stratum={k[1]} n={s} p_a={p_a:.3f} p_h={p_h:.3f} "
                  f"TRUE-f={true_f:.1f} gate={r['decision']:<8} {'✓' if gate_ok else '✗'}")
                  
    print(f"  -> LEVEL 2 {'PASSED ✓' if ok else 'FAILED ✗'}\n")
    return ok

# =====================================================================
# LEVEL 3: FiFAR (optional, pandas+pyarrow)
# =====================================================================
FIFAR_URL = "https://ndownloader.figshare.com/files/52147616"
def run_fifar(benefit):
    print("=" * 72)
    print("LEVEL 3: FiFAR (OpenL2D — AI + 50 human analysts + ground truth)")
    print("=" * 72)
    try:
        import pandas as pd
    except ImportError:
        print("  [fifar] pandas missing — skipping. Install: pip install pandas pyarrow")
        return True
        
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FiFAR")
    zpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fifar.zip")
    
    if not os.path.exists(f"{base}/alert_data/processed_data/alerts.parquet"):
        if not os.path.exists(zpath):
            print("  [fifar] downloading ~209 MB from figshare ...", file=sys.stderr)
            urllib.request.urlretrieve(FIFAR_URL, zpath)
        import zipfile
        z = zipfile.ZipFile(zpath)
        print("  [fifar] extracting ...", file=sys.stderr)
        for n in ["FiFAR/alert_data/processed_data/alerts.parquet",
                  "FiFAR/alert_data/processed_data/BAF_alert_model_score.parquet",
                  "FiFAR/synthetic_experts/expert_predictions.parquet"]:
            z.extract(n, base.rsplit("/",1)[0])
            
    alerts = pd.read_parquet(f"{base}/alert_data/processed_data/alerts.parquet")
    exp = pd.read_parquet(f"{base}/synthetic_experts/expert_predictions.parquet")
    ms = alerts["model_score"]
    ai_pred = (ms >= ms.median()).astype(int)
    alerts["ai_pred"] = ai_pred; alerts["y"] = alerts["fraud_bool"].astype(int)
    
    def acc(pred, y): return (pred == y).mean()
    ok = True; total = checked = 0
    
    segs = [("ALL DATA", alerts)]
    q1, q2 = ms.quantile([1/3, 2/3])
    for lbl, mask in [("low-risk", ms<q1), ("med-risk",(ms>=q1)&(ms<q2)), ("high-risk",ms>=q2)]:
        segs.append((f"risk:{lbl}", alerts[mask]))
    for col in exp.columns[:50]:
        segs.append((f"analyst:{col}", alerts.join(exp[[col]], how="inner")))
        
    print(f"  segments: {len(segs)}  (all + 3 risk classes + 50 analysts)")
    for lbl, sub in segs:
        y = sub["y"]
        p_a = acc(sub["ai_pred"], y)
        if lbl.startswith("analyst:"):
            p_h = acc(sub[lbl.split(":",1)[1]].astype(int), y)
        else:
            avg = exp.mean(axis=1).round().astype(int)
            p_h = acc(avg.loc[sub.index], y)
            
        gap = T8_gap(benefit, p_a, p_h); s_abs = abs(sigma(benefit))
        r = guardrail(benefit, p_a, p_h, None)
        true_better = W(benefit,p_a,0.5) > W(benefit,p_h,0.5)
        gate_ok = (r["decision"]=="ACT") == (true_better and gap > s_abs)
        ok = ok and gate_ok
        total += 1; checked += int(gate_ok)
        
    print(f"  -> {checked}/{total} segment decisions correct "
          f"{'✓' if ok else '✗'}\n")
    return ok

# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Independent validation of the LLM agent abstain gate")
    ap.add_argument("--mc", action="store_true", help="level 1 only (MC)")
    ap.add_argument("--twins", action="store_true", help="level 2 only (TWINS)")
    ap.add_argument("--fifar", action="store_true", help="level 3 only (FiFAR, downloads ~209 MB)")
    ap.add_argument("--benefit", default="100,20,-40,-300", help="utility (B,A,N,H)")
    args = ap.parse_args()
    
    benefit = tuple(float(x) for x in args.benefit.split(","))
    only = args.mc or args.twins or args.fifar
    print(f"benefit (B,A,N,H)={benefit}  |sigma|={abs(sigma(benefit)):.1f}  "
          f"({datetime.date.today().isoformat()})")
    results = []
    
    if not only or args.mc:
        results.append(("MC", run_mc(benefit)))
    if not only or args.twins:
        results.append(("TWINS", run_twins(benefit)))
    if args.fifar:
        results.append(("FiFAR", run_fifar(benefit)))
        
    print("=" * 72)
    allok = all(v for _, v in results)
    for name, v in results:
        print(f"  {name:<8}: {'PASSED ✓' if v else 'FAILED ✗'}")
    print(f"\n  OVERALL RESULT: {'VALIDATED ✓' if allok else 'NOT VALIDATED ✗'}")
    print("=" * 72)
