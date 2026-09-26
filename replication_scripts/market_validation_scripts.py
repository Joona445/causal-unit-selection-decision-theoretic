#!/usr/bin/env python3
"""
framework_validation.py — Independent validation of the causal unit-selection framework.

License: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)[cite: 1]

SINGLE FILE, NO INTERNAL DATA. Runs three validations to demonstrate that
the framework f(c) = W(c) + sigma·PNS(c) is applicable to decision auditing:
  1. TWINS (public dataset) — both potential outcomes are known
  2. Synthetic Market DGP   — transferring the mechanism to trading decisions
  3. Public Market Data     — yfinance (OPTIONAL: requires `pip install yfinance pandas`)

DEPENDENCIES: Python 3 standard library only (downloads via urllib).

Usage:
    python3 framework_validation.py            # All three (market data if yfinance is found)
    python3 framework_validation.py --twins    # TWINS only
    python3 framework_validation.py --synth    # Synthetic only
    python3 framework_validation.py --market   # Public market data only (yfinance)

TWINS is downloaded automatically from the CEVAE repo (AMLab-Amsterdam) to ./twins_cache/,
or uses a local copy if --twins-dir <path> is provided.
This file DOES NOT contain proprietary data and DOES NOT reference any internal systems.
"""

import sys, os, csv, urllib.request, collections, datetime
import argparse

# =====================================================================
# FRAMEWORK (inline — independent, no imports)
# =====================================================================
def sigma(benefit):
    b, g, t, d = benefit
    return b - g - t + d

def W(benefit, py1, py0):
    b, g, t, d = benefit
    return (g - d) * py1 + d * py0 + t * (1 - py0)

def benefit_interval(benefit, py1, py0):
    s = sigma(benefit)
    w = W(benefit, py1, py0)
    lo, up = (w + s, w) if s < 0 else (w, w + s)
    return lo, up, w, s

def decide_groups(groups, benefit):
    """T6: Safe if a group strictly dominates (interval entirely above others)."""
    names = list(groups)
    rows = {}
    for n in names:
        py1, py0 = groups[n]
        lo, up, w, s = benefit_interval(benefit, py1, py0)
        rows[n] = {"lo": lo, "up": up, "W": w}
    
    best = max(names, key=lambda n: rows[n]["W"])
    selectable = [A for A in names
                  if all(rows[A]["lo"] > rows[B]["up"] + 1e-12 for B in names if B != A)]
    return {"rows": rows, "point_best": best, "safe_decision": selectable,
            "decided": len(selectable) >= 1}

# =====================================================================
# COMMON UTILITIES
# =====================================================================
def _load_csv(path):
    with open(path) as f:
        return [dict(r) for r in csv.DictReader(f)]

def _type(y1, y0):
    if y1 == 1 and y0 == 0: return 'B'
    if y1 == 1 and y0 == 1: return 'A'
    if y1 == 0 and y0 == 0: return 'N'
    return 'H'

# =====================================================================
# 1. TWINS VALIDATION
# =====================================================================
TWINS_URLS = {
    "T": "https://raw.githubusercontent.com/AMLab-Amsterdam/CEVAE/master/datasets/TWINS/twin_pairs_T_3years_samesex.csv",
    "Y": "https://raw.githubusercontent.com/AMLab-Amsterdam/CEVAE/master/datasets/TWINS/twin_pairs_Y_3years_samesex.csv",
    "X": "https://raw.githubusercontent.com/AMLab-Amsterdam/CEVAE/master/datasets/TWINS/twin_pairs_X_3years_samesex.csv",
}

def _ensure_twins(twins_dir):
    """Returns (T,Y,X) paths; downloads if missing."""
    if twins_dir:
        return (f"{twins_dir}/twin_pairs_T_3years_samesex.csv",
                f"{twins_dir}/twin_pairs_Y_3years_samesex.csv",
                f"{twins_dir}/twin_pairs_X_3years_samesex.csv")
    
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

def run_twins(benefit, twins_dir=None, target=2.0):
    print("=" * 72)
    print("VALIDATION 1: TWINS (both potential outcomes known)")
    print("=" * 72)
    tpath, ypath, xpath = _ensure_twins(twins_dir)
    T = _load_csv(tpath); Y = _load_csv(ypath); X = _load_csv(xpath)
    
    def fget(x, k):
        v = x.get(k, "")
        try: return float(v)
        except: return None
        
    # Strata: gestation (<=5 risk vs >5) and preterm (1/0)
    strata_fns = [
        ("gestation <=5", lambda x: ("gest", 1 if (fget(x, "gestat10") or 99) <= 5 else 0)),
        ("preterm 1/0",   lambda x: ("preterm", fget(x, "preterm"))),
    ]
    
    for label, strata_fn in strata_fns:
        per = collections.defaultdict(lambda: collections.Counter())
        for t, y, x in zip(T, Y, X):
            try:
                w0, w1 = float(t["dbirwt_0"]), float(t["dbirwt_1"])
                m0, m1 = float(y["mort_0"]), float(y["mort_1"])
            except: continue
            
            # treatment = heavier twin survives
            if w1 > w0: y1, y0 = 1 - m1, 1 - m0
            else:       y1, y0 = 1 - m0, 1 - m1
            
            k = strata_fn(x)
            if k is not None and k[1] is not None:
                per[k][_type(y1, y0)] += 1
                
        print(f"\n  STRATA: {label}")
        print(f"  {'stratum':<10}{'n':>7}{'PNS':>7}{'P(H)':>7}{'naive a-b':>11}"
              f"{'TRUE-f':>8}{'interval [lo,up]':>18}  correct")
        
        for k, c in sorted(per.items()):
            s = sum(c.values())
            if s == 0: continue
            
            B, A, N, Hh = c['B'], c['A'], c['N'], c['H']
            a = (B + A) / s; b = (A + Hh) / s
            pns = B / s; h = Hh / s
            true_f = (benefit[0]*B + benefit[1]*A + benefit[2]*N + benefit[3]*Hh) / s
            
            lo, up, w, sg = benefit_interval(benefit, a, b)
            ok = "YES" if lo <= true_f <= up else "NO"
            print(f"  {str(k[1]):<10}{s:>7}{pns:>7.3f}{h:>7.3f}{a-b:>+11.3f}"
                  f"{true_f:>8.1f}{f'[{lo:.1f},{up:.1f}]':>18}  {ok}")
                  
    print("\n  NOTE: The interval should contain TRUE-f in every stratum (Theorem 5).\n")

# =====================================================================
# 2. SYNTHETIC MARKET DGP
# =====================================================================
def run_synthetic(benefit, n=200000):
    print("=" * 72)
    print("VALIDATION 2: Synthetic Market DGP (mechanism transfer)")
    print("=" * 72)
    
    def seg_low(nn):
        return {'B': int(.25*nn), 'A': int(.25*nn), 'N': int(.42*nn), 'H': int(.08*nn)}
    def seg_hi(nn):
        return {'B': int(.25*nn), 'A': int(.25*nn), 'N': int(.27*nn), 'H': int(.23*nn)}
        
    SEGS = {"low_risk": seg_low(n), "high_risk": seg_hi(n)}
    
    def stats(types):
        s = sum(types.values())
        B, A, N, H = types['B'], types['A'], types['N'], types['H']
        return dict(py1=(B+A)/s, py0=(A+H)/s, PNS=B/s, H=H/s,
                    true_f=(benefit[0]*B+benefit[1]*A+benefit[2]*N+benefit[3]*H)/s)
                    
    st = {k: stats(v) for k, v in SEGS.items()}
    
    print(f"\n  {'segment':<14}{'p_y1':>7}{'p_y0':>7}{'naive':>8}{'TRUE-f':>8}{'P(H)':>7}")
    for k, v in st.items():
        print(f"  {k:<14}{v['py1']:>7.3f}{v['py0']:>7.3f}{v['py1']-v['py0']:>+8.3f}"
              f"{v['true_f']:>8.1f}{v['H']:>7.3f}")
              
    # T6 Evaluation
    groups = {k: (v['py1'], v['py0']) for k, v in st.items()}
    r = decide_groups(groups, benefit)
    print(f"\n  T6: safe_decision = {r['safe_decision']}  (only clearly dominating named)")
    
    # Naive vs True Identity
    print("\n  Identity a-b = PNS - P(H):")
    for k, v in st.items():
        print(f"    {k:<14} a-b={v['py1']-v['py0']:+.3f} = PNS {v['PNS']:.3f} - H {v['H']:.3f}"
              f"{'  ✓' if abs((v['py1']-v['py0'])-(v['PNS']-v['H']))<1e-9 else '  ✗'}")
    print()

# =====================================================================
# 3. PUBLIC MARKET DATA (yfinance, optional)
# =====================================================================
def run_market(benefit, trail=21, fwd=21, start="2023-06-01", end=None, tickers=None):
    print("=" * 72)
    print("VALIDATION 3: Public Market Data (yfinance) — benchmark observable")
    print("=" * 72)
    
    try:
        import yfinance as yf
        import pandas as pd
    except ImportError:
        print("  [market data] yfinance/pandas not installed — skipping.")
        print("  Install via: pip install yfinance pandas")
        return
        
    if end is None:
        end = datetime.date.today().isoformat()
    bench = "^OMXH25"
    
    if tickers is None:
        tickers = ["NOKIA.HE","SAMPO.HE","KNEBV.HE","NESTE.HE","UPM.HE",
                   "FORTUM.HE","WRT1V.HE","KCR.HE","ELISA.HE","NDA-FI.HE"]
                   
    all_t = [bench] + tickers
    print(f"  Downloading {len(all_t)} series from {start} to {end} ...")
    raw = yf.download(all_t, start=start, end=end, interval="1d", progress=False)["Close"]
    
    if bench not in raw.columns:
        print(f"  [error] Benchmark {bench} not found in data.")
        return

    # Reconstruct the logic for market validation
    # Define outcomes based on forward returns
    records = []
    for tk in tickers:
        if tk not in raw.columns: continue
        for i in range(trail, len(raw) - fwd):
            # Benchmark outcome (y0): if benchmark is positive
            b_ret = raw[bench].iloc[i+fwd] / raw[bench].iloc[i] - 1
            y0 = 1 if b_ret > 0 else 0
            
            # Action outcome (y1): if stock is positive
            t_ret = raw[tk].iloc[i+fwd] / raw[tk].iloc[i] - 1
            y1 = 1 if t_ret > 0 else 0
            
            # Regime based on trailing benchmark return
            b_trail = raw[bench].iloc[i] / raw[bench].iloc[i-trail] - 1
            reg = "upward" if b_trail > 0 else "downward"
            
            records.append({"tk": tk, "reg": reg, "y1": y1, "y0": y0, "type": _type(y1, y0)})
            
    df = pd.DataFrame(records)
    print(f"  Units: {len(df)} ({df['tk'].nunique()} stocks)")
    
    print(f"\n  {'regime':<10}{'n':>6}{'p_y1':>7}{'p_y0':>7}{'naive':>8}{'TRUE-f':>8}"
          f"{'P(H)':>7}  interval")
          
    res = {}
    for reg in ["upward", "downward"]:
        sub = df[df.reg == reg]
        if len(sub) == 0: continue
        
        s = len(sub)
        p1 = sub.y1.mean()
        p0 = sub.y0.mean()
        types = sub["type"].value_counts().to_dict()
        
        B = types.get('B', 0); A = types.get('A', 0); N = types.get('N', 0); H = types.get('H', 0)
        true_f = (benefit[0]*B + benefit[1]*A + benefit[2]*N + benefit[3]*H) / s
        lo, up, w, sg = benefit_interval(benefit, p1, p0)
        
        res[reg] = dict(p1=p1, p0=p0, W=w, lo=lo, up=up, true_f=true_f, H=H/s)
        print(f"  {reg:<10}{s:>6}{p1:>7.3f}{p0:>7.3f}{p1-p0:>+8.3f}{true_f:>8.1f}"
              f"{H/s:>7.3f}  [{lo:.1f},{up:.1f}]")
              
    print("\n  Check: does the interval contain TRUE-f?")
    for reg, v in res.items():
        ok = "YES" if v['lo'] <= v['true_f'] <= v['up'] else "NO"
        print(f"    {reg:<10} [{v['lo']:.1f},{v['up']:.1f}] contains {v['true_f']:.1f} -> {ok}")
    print()

# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Independent framework validation (no internal data)")
    ap.add_argument("--twins", action="store_true", help="only TWINS")
    ap.add_argument("--synth", action="store_true", help="only synthetic")
    ap.add_argument("--market", action="store_true", help="only market data (yfinance)")
    ap.add_argument("--twins-dir", default=None, help="local TWINS directory")
    ap.add_argument("--benefit", default="100,30,-40,-120", 
                    help="utility (B,A,N,H), comma separated")
    
    args = ap.parse_args()
    b = tuple(float(x) for x in args.benefit.split(","))
    only = args.twins or args.synth or args.market
    
    print(f"benefit (B,A,N,H) = {b}   |sigma| = {abs(sigma(b)):.1f}   "
          f"(run {datetime.date.today().isoformat()})")
          
    if not only or args.twins:
        run_twins(b, twins_dir=args.twins_dir)
    if not only or args.synth:
        run_synthetic(b)
    if not only or args.market:
        run_market(b)
