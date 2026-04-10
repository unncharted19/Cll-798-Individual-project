"""Run all experiments for the project."""
import sys, os, pickle, warnings
sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore")
import numpy as np
import powerlaw
from tabs import run_tabs, build_network, assign_trophic_levels
import networkx as nx

OUT = "/home/claude/project/results"
os.makedirs(OUT, exist_ok=True)

def fit_pl(sizes):
    """MLE power-law fit with likelihood ratio vs exponential."""
    sizes = np.asarray(sizes)
    sizes = sizes[sizes >= 1]
    if len(sizes) < 30:
        return dict(tau=np.nan, xmin=np.nan, R=np.nan, p=np.nan, n=len(sizes))
    try:
        fit = powerlaw.Fit(sizes, discrete=True, verbose=False)
        R, p = fit.distribution_compare('power_law', 'exponential', normalized_ratio=True)
        return dict(tau=float(fit.alpha), xmin=float(fit.xmin),
                    R=float(R), p=float(p), n=int(len(sizes)))
    except Exception as e:
        return dict(tau=np.nan, xmin=np.nan, R=np.nan, p=np.nan, n=len(sizes))

# =============================================================
# Experiment 1: Connectivity sweep
# =============================================================
print("="*60); print("EXP 1: Connectivity sweep"); print("="*60)
TOPOS = ["1D_ring", "2D_lattice", "ER_random", "BA_scalefree"]
KS    = [2, 3, 4, 6, 8]
SEEDS = [42, 123, 999]
STEPS = 300_000
N = 196

sweep = {}
for top in TOPOS:
    for k in KS:
        if top == "1D_ring" and k != 2: continue
        if top == "2D_lattice" and k != 4: continue
        for seed in SEEDS:
            key = (top, k, seed)
            r = run_tabs(top, N=N, steps=STEPS, avg_k=k, seed=seed)
            fit = fit_pl(r["avalanches"])
            sweep[key] = dict(f_c=r["f_c"], n_av=len(r["avalanches"]),
                              max_av=int(r["avalanches"].max()) if len(r["avalanches"]) else 0,
                              tau=fit["tau"], R=fit["R"], p=fit["p"],
                              avalanches=r["avalanches"])
            print(f"  {top:14s} k={k} seed={seed}  f_c={r['f_c']:.3f}  "
                  f"#av={len(r['avalanches']):5d}  tau={fit['tau']:.2f}  R={fit['R']:.1f}")

# =============================================================
# Experiment 2: Finite-size scaling on BA
# =============================================================
print("="*60); print("EXP 2: Finite-size scaling"); print("="*60)
fss = {}
for N_fss in [64, 144, 256, 400]:
    r = run_tabs("BA_scalefree", N=N_fss, steps=300_000, avg_k=4, seed=42)
    fit = fit_pl(r["avalanches"])
    fss[N_fss] = dict(avalanches=r["avalanches"], tau=fit["tau"], f_c=r["f_c"])
    print(f"  N={N_fss:4d}  f_c={r['f_c']:.3f}  tau={fit['tau']:.2f}  "
          f"max_av={r['avalanches'].max()}  #av={len(r['avalanches'])}")

# =============================================================
# Experiment 3: Trophic asymmetry sweep (the novelty)
# =============================================================
print("="*60); print("EXP 3: Trophic asymmetry"); print("="*60)
ASYM = [(1.0, 1.0), (0.5, 1.0), (1.0, 0.5), (0.3, 1.0), (1.0, 0.3)]
asym_res = {}
for (pu, pd) in ASYM:
    r = run_tabs("BA_scalefree", N=196, steps=300_000, avg_k=4, seed=42,
                 p_up=pu, p_down=pd)
    fit = fit_pl(r["avalanches"])
    asym_res[(pu, pd)] = dict(avalanches=r["avalanches"], tau=fit["tau"],
                              f_c=r["f_c"], R=fit["R"])
    print(f"  p_up={pu}  p_down={pd}  f_c={r['f_c']:.3f}  tau={fit['tau']:.2f}")

# =============================================================
# Experiment 4: Dynamic extinction-risk vs static centrality
# =============================================================
print("="*60); print("EXP 4: Extinction risk vs centrality"); print("="*60)
r_ks = run_tabs("BA_scalefree", N=196, steps=500_000, avg_k=4, seed=42,
                track_participation=True)
G = r_ks["graph"]
part = r_ks["participation"]
deg = np.array([G.degree(i) for i in range(196)])
betw = nx.betweenness_centrality(G)
betw_arr = np.array([betw[i] for i in range(196)])
pr = nx.pagerank(G)
pr_arr = np.array([pr[i] for i in range(196)])
troph = r_ks["trophic"]
from scipy.stats import spearmanr
corr = {}
for name, arr in [("degree", deg), ("betweenness", betw_arr),
                  ("pagerank", pr_arr), ("trophic", troph)]:
    rho, pval = spearmanr(part, arr)
    corr[name] = (float(rho), float(pval))
    print(f"  {name:12s}  rho={rho:+.3f}  p={pval:.2e}")

keystone = dict(participation=part, degree=deg, betweenness=betw_arr,
                pagerank=pr_arr, trophic=troph, corr=corr)

# =============================================================
# Save everything
# =============================================================
with open(f"{OUT}/all_results.pkl", "wb") as f:
    pickle.dump(dict(sweep=sweep, fss=fss, asym=asym_res, keystone=keystone),
                f, protocol=4)
print("\nAll experiments complete. Saved to all_results.pkl")
