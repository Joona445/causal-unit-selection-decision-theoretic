#!/usr/bin/env python3
"""
unit_selection_theorems.py — A SINGLE standalone file containing the theory (T5–T7)
AND its validation calculations. 

AUTHOR: Eskelinen J.M.E
REFERENCE: "A Decision-Theoretic Extension of Causal Unit Selection"

LICENSE: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
This code is freely available for academic research, peer review, and non-commercial 
development. Any commercial use, proprietary integration, or for-profit application 
requires explicit written permission from the copyright holder.

Purpose: anyone can run this script 
(python3 unit_selection_theorems.py) to reproduce all theorem verifications, 
or import the theory structure (sigma, W, benefit_interval, decide_groups) 
into their own code. No external dependencies (uses standard math/random).

Theorems (derived & proven; see manuscript):
  f(c) = W(c) + sigma·PNS(c),        sigma = beta - gamma - theta + delta
  W(c) = (gamma-delta)·py1 + delta·py0 + theta·(1-py0)

  T5: f is point-identifiable from effects iff sigma == 0.
  T6: two groups are strictly decidable from effects alone iff |W1-W0| > |sigma|.
  T7: under estimation, decision rate P(ghat>|sigma|) = 1-Phi(-D/s_g), n*~1/D^2, 
      abstaining yields no active error.
  Epsilon bounds: |f(c) - (W(c)+sigma/2)| <= |sigma|/2, tight (PNS=0/1 achieves this).
"""

import math, random

# ============================================================ CORE (Theory)
def sigma(benefit):
    b, g, t, d = benefit
    return b - g - t + d

def W(benefit, py1, py0):
    """W(c) = (gamma-delta)·py1 + delta·py0 + theta·(1-py0)."""
    b, g, t, d = benefit
    return (g - d) * py1 + d * py0 + t * (1 - py0)

def benefit_interval(benefit, py1, py0, pns_bounds=None):
    """Returns (lo, up, W_value, sigma). Interval narrows if pns_bounds (L,U) are given."""
    s = sigma(benefit); w = W(benefit, py1, py0)
    if pns_bounds is None:
        lo, up = w + min(0.0, s), w + max(0.0, s)
    else:
        L, U = pns_bounds
        if s >= 0:
            lo, up = w + s * L, w + s * U
        else:
            lo, up = w + s * U, w + s * L
    return lo, up, w, s

def _pair(score):
    if isinstance(score, dict): return score["py1"], score["py0"]
    return score[0], score[1]

def decide_groups(groups, benefit, pns_bounds_map=None):
    """Decision (T6): safe if one group dominates (interval strictly above others);
    otherwise abstain. Point recommendation = argmax W (eps-optimal)."""
    names = list(groups); rows = {}
    for n in names:
        py1, py0 = _pair(groups[n])
        pns = pns_bounds_map.get(n) if pns_bounds_map else None
        lo, up, w, s = benefit_interval(benefit, py1, py0, pns)
        rows[n] = {"lo": lo, "up": up, "W": w, "center": w + s / 2.0}
        
    best_w = max(names, key=lambda n: rows[n]["W"])
    selectable = [A for A in names if all(rows[A]["lo"] > rows[B]["up"] + 1e-12 for B in names if B != A)]
    return {"rows": rows, "point_best": best_w, "safe_decision": selectable,
            "decided": len(selectable) >= 1}

# ============================================================ T5: Identifiability iff sigma=0
# Types: 0=Benefited(1,0), 1=Always(1,1), 2=Never(0,0), 3=Harmed/Defier(0,1)
_T_Y0 = {0:0, 1:1, 2:0, 3:1}
_T_Y1 = {0:1, 1:1, 2:0, 3:0}

def _effects_from_types(t):
    tB, tA, tN, tD = t
    pyx = tB + tA               # P(y_x)   = complier + always
    pyxp = tA + tD              # P(y_x')  = always + defier
    return (pyx, pyxp, 1 - pyxp)

def _benefit_from_types(t, benefit):
    return sum(benefit[i] * t[i] for i in range(4))

def check_T5():
    """Construction: identical effects (P(y_x),P(y_x')), PNS shifted by Δ.
    -> benefit difference = sigma·Δ. If sigma==0, diff is 0 (point-identifiable); else ≠0."""
    results = []
    for benefit, name in [((100,-60,0,-140), "sigma=20"), ((10,5,0,-5), "sigma=0")]:
        s = sigma(benefit); passed_tests = []
        t0 = [0.3, 0.2, 0.3, 0.2]
        eff0 = _effects_from_types(t0)
        
        for delta in (0.1, 0.15):
            t1 = [t0[0]+delta, t0[1]-delta, t0[2], t0[3]+delta]
            eff1 = _effects_from_types(t1)
            same_effects = all(abs(eff0[k]-eff1[k]) < 1e-12 for k in range(3))
            pns_diff = t1[0]-t0[0]
            fdiff = _benefit_from_types(t1, benefit) - _benefit_from_types(t0, benefit)
            
            # Theory: fdiff == sigma·Δ and ≠0 iff sigma≠0
            ok = same_effects and abs(fdiff - s*pns_diff) < 1e-9
            if s != 0:
                ok = ok and abs(fdiff) > 1e-9
            else:
                ok = ok and abs(fdiff) < 1e-9
            passed_tests.append(ok)
        results.append((name, s, all(passed_tests), t0))
    return all(r[2] for r in results), results

# ============================================================ T6: Decision criterion |ΔW|>|σ|
def check_T6():
    b = (100,-60,0,-140); s = sigma(b); eps = abs(s); rows = []
    for G in (eps-0.3, eps*1.0, eps+0.3):
        g, d = b[1], b[3]
        py1a, py0a, py0b = 0.3, 0.1, 0.1
        py1b = py1a + G/(g-d)
        
        Wa = W(b, py1a, py0a); Wb = W(b, py1b, py0b)
        gap = Wb - Wa
        loa, upa = Wa+min(0,s), Wa+max(0,s)
        lob, upb = Wb+min(0,s), Wb+max(0,s)
        
        decidable = (lob > upa+1e-9) or (loa > upb+1e-9)
        predict = abs(gap) > eps
        rows.append((gap, decidable, predict, decidable == predict))
    return all(r[3] for r in rows), rows

# ============================================================ T7: Decision rate / Abstain
def var_W(b, p1, p0, n1, n0):
    g, th, d = b[1], b[2], b[3]
    return (g-d)**2 * p1*(1-p1)/n1 + (d-th)**2 * p0*(1-p0)/n0

def _binom(rng, p, n):
    return sum(rng.random() < p for _ in range(n))/n

def _sim_decision(seed, b, effects, n, trials):
    W1 = W(b, effects[1][0], effects[1][1]); W0 = W(b, effects[0][0], effects[0][1])
    star = abs(sigma(b)); true_gap = W1-W0
    rng = random.Random(seed); decided = wrong = 0
    for _ in range(trials):
        p10h=_binom(rng,effects[0][0],n); p00h=_binom(rng,effects[0][1],n)
        p11h=_binom(rng,effects[1][0],n); p01h=_binom(rng,effects[1][1],n)
        ghat = W(b,p11h,p01h)-W(b,p10h,p00h)
        if ghat > star+1e-12:
            decided += 1
        elif ghat < -star-1e-12:
            wrong += 1
    return decided/trials, wrong/trials

def _gauss_ok(D, s_g):
    return 0.5*math.erfc(D/(math.sqrt(2)*s_g))   # = P(ghat < |sig|) = indecisive+wrong

def check_T7():
    b = (100,-60,0,-140); star = abs(sigma(b))
    p10, p00, p01 = 0.30, 0.10, 0.10
    rows_all = []
    for D in (0.5, 2.0, 5.0):
        G = star + D
        p11 = 0.30 + G/(b[1]-b[3])
        effects = [(p10,p00),(p11,p01)]
        for n in (50, 200, 800, 2000):
            s_g = math.sqrt(var_W(b,p10,p00,n,n) + var_W(b,p11,p01,n,n))
            pred = 1 - _gauss_ok(D, s_g)             # P(decided correctly)
            mc, acterr = _sim_decision(7, b, effects, n, 4000)
            
            # Theory: mc ≈ pred, and abstain yields no active error => acterr ≈ 0
            ok = abs(mc-pred) < 0.05 and acterr < 0.01
            rows_all.append((D, n, mc, pred, acterr, ok))
    return all(r[5] for r in rows_all), rows_all

# ============================================================ Epsilon bounds & Tightness
def _scm(rng):
    ptp = {(c,u): (lambda w: [x/sum(w) for x in w])([rng.random() for _ in range(4)])
           for c in (0,1) for u in (0,1)}
    return {"pu":0.5, "x1":rng.uniform(0.5,0.95), "x0":rng.uniform(0.05,0.5), "ptp":ptp}

def _causal_effect(scm, c, x):
    p = [0.0]*4
    for u in (0,1):
        pu = scm["pu"] if u==1 else 1-scm["pu"]
        for t in range(4): p[t] += pu*scm["ptp"][(c,u)][t]
    p = [v/sum(p) for v in p]
    return sum(p[t]*(_T_Y1[t] if x==1 else _T_Y0[t]) for t in range(4))

def _true_pns(scm, c):
    p = [0.0]*4 
    for u in (0,1):
        pu = scm["pu"] if u==1 else 1-scm["pu"]
        for t in range(4): p[t] += pu*scm["ptp"][(c,u)][t]
    return p[0]/sum(p)

def check_epsilon_and_decision(n_scm=1500, benefit=(100,-60,0,-140)):
    rng = random.Random(1); s = sigma(benefit); eps = abs(s)/2
    violations = agreements = 0
    for _ in range(n_scm):
        scm = _scm(rng)
        f = lambda c: W(benefit, _causal_effect(scm,c,1), _causal_effect(scm,c,0)) + s*_true_pns(scm,c)
        ctr = lambda c: W(benefit, _causal_effect(scm,c,1), _causal_effect(scm,c,0)) + s/2
        
        if abs(f(0)-ctr(0)) > eps+1e-9: violations += 1
        if abs(f(1)-ctr(1)) > eps+1e-9: violations += 1
        agreements += int((f(1) > f(0)) == (ctr(1) > ctr(0)))
    return {"viol": violations, "total": 2*n_scm, "agree": agreements, "n_scm": n_scm}

def check_tightness(benefit=(100,-60,0,-140)):
    """Tightness: Constructions where PNS(c)=0 and PNS(c)=1 achieve exactly |sigma|/2."""
    s = sigma(benefit); eps = abs(s)/2
    scm = {"pu":0.5,"x1":0.85,"x0":0.25,
           "ptp":{(0,0):[0,0,1,0],(0,1):[0,0,1,0],(1,0):[1,0,0,0],(1,1):[1,0,0,0]}}
           
    def err(c):
        w = W(benefit, _causal_effect(scm,c,1), _causal_effect(scm,c,0))
        cig = w + s*_true_pns(scm,c); ctr = w + s/2
        return abs(cig-ctr)
        
    e0, e1 = err(0), err(1)
    return {"e0":e0,"e1":e1,"eps":eps,"tight": abs(e0-eps)<1e-9 and abs(e1-eps)<1e-9}

# ============================================================ RUN / Validation
def _fmt_pass(ok): return "OK" if ok else "FAIL"

def main():
    print("unit_selection_theorems — T5/T6/T7 + epsilon validation (single file)\n")
    all_passed = True 
    
    # T5
    ok5, results5 = check_T5()
    s_str = "; ".join(f"{name}(sigma={s}): {'OK' if OK else 'FAIL'}" for name, s, OK, _ in results5)
    print(f"[T5] Identifiability iff sigma=0: {_fmt_pass(ok5)}   {s_str}")
    all_passed &= ok5
    
    # T6
    ok6, rows6 = check_T6()
    r6 = "; ".join(f"gap={g:+.1f}->decide^{d and p}" for g, d, p, ok in rows6)
    print(f"[T6] Decision criterion |ΔW|>|σ|: {_fmt_pass(ok6)}   {r6}")
    all_passed &= ok6
    
    # T7
    ok7, rows7 = check_T7()
    print(f"[T7] Sample size MC (~1/D²) + abstain-no-error: {_fmt_pass(ok7)}")
    for D, n, mc, pred, ae, ok in rows7[:8]:
        print(f"       D={D}: n={n} MC={mc:.4f} pred={pred:.4f} acterr={ae:.5f} {_fmt_pass(ok)}")
    all_passed &= ok7
    
    # Epsilon + Decision Stats
    for bv, lab in [((100,-60,0,-140),"carwash"), ((100,-20,-40,-100),"skewed"),
                    ((10,5,0,-5),"sigma=0"), ((100,-30,-40,-30),"σ=140")]:
        r = check_epsilon_and_decision(1500, bv)
        t = check_tightness(bv)
        okE = r["viol"] == 0 and t["tight"]
        print(f"[ε] {lab} (σ={sigma(bv)}): bounds-broken={r['viol']}/{r['total']}, "
              f"tightness={t['tight']} ({t['e0']:.3f}={t['eps']:.3f}), "
              f"eps-center==oracle={100*r['agree']/r['n_scm']:.1f}%  {_fmt_pass(okE)}")
        all_passed &= okE
        
    print("\n" + ("ALL CHECKS PASSED." if all_passed else "SOME CHECKS FAILED."))
    return all_passed

if __name__ == "__main__":
    main()