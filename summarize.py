"""Dump a summary markdown table of all key results."""
import pickle, numpy as np
with open("/home/claude/project/results/all_results.pkl","rb") as f:
    R = pickle.load(f)

lines = ["# Results summary\n"]
lines.append("## Connectivity sweep (N=196, 300k steps, 3 seeds)\n")
lines.append("| Topology | <k> | f_c | τ (mean±sd) | # avalanches | max avalanche |")
lines.append("|---|---|---|---|---|---|")
sweep = R["sweep"]
rows = []
for top in ["1D_ring","2D_lattice","ER_random","BA_scalefree"]:
    for k in [2,3,4,6,8]:
        keys = [(top,k,s) for s in [42,123,999] if (top,k,s) in sweep]
        if not keys: continue
        taus = [sweep[kk]["tau"] for kk in keys]
        fcs  = [sweep[kk]["f_c"] for kk in keys]
        nav  = [sweep[kk]["n_av"] for kk in keys]
        mxa  = [sweep[kk]["max_av"] for kk in keys]
        rows.append(f"| {top} | {k} | {np.mean(fcs):.3f} | "
                    f"{np.nanmean(taus):.2f}±{np.nanstd(taus):.2f} | "
                    f"{int(np.mean(nav))} | {int(np.mean(mxa))} |")
lines += rows

lines.append("\n## Finite-size scaling (BA, k=4)")
lines.append("| N | f_c | τ | max avalanche |")
lines.append("|---|---|---|---|")
for N_ in sorted(R["fss"].keys()):
    d = R["fss"][N_]
    lines.append(f"| {N_} | {d['f_c']:.3f} | {d['tau']:.2f} | {int(d['avalanches'].max())} |")

lines.append("\n## Trophic asymmetry (BA, N=196, k=4)")
lines.append("| p_up | p_down | f_c | τ | interpretation |")
lines.append("|---|---|---|---|---|")
interp = {(1.0,1.0):"symmetric baseline",(0.5,1.0):"predators shielded",
          (1.0,0.5):"prey shielded",(0.3,1.0):"predators strongly shielded",
          (1.0,0.3):"prey strongly shielded"}
for key in [(1.0,1.0),(1.0,0.5),(1.0,0.3),(0.5,1.0),(0.3,1.0)]:
    d = R["asym"][key]
    lines.append(f"| {key[0]} | {key[1]} | {d['f_c']:.3f} | {d['tau']:.2f} | {interp[key]} |")

lines.append("\n## Extinction risk correlations (BA, N=196, 500k steps)")
lines.append("| Static metric | Spearman ρ | p-value |")
lines.append("|---|---|---|")
for name, (rho, p) in R["keystone"]["corr"].items():
    lines.append(f"| {name} | {rho:+.3f} | {p:.2e} |")

txt = "\n".join(lines)
with open("/home/claude/project/results/summary.md","w") as f:
    f.write(txt)
print(txt)
