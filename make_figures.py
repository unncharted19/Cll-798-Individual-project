"""Generate all 7 figures for the manuscript."""
import pickle, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from tabs import build_network, assign_trophic_levels

plt.rcParams.update({"font.size": 11, "figure.dpi": 130, "savefig.dpi": 150,
                     "axes.grid": True, "grid.alpha": 0.3})
FIG = "/home/claude/project/figures"
os.makedirs(FIG, exist_ok=True)
with open("/home/claude/project/results/all_results.pkl","rb") as f:
    R = pickle.load(f)

TOPO_LABEL = {"1D_ring":"1D Ring","2D_lattice":"2D Lattice",
              "ER_random":"ER Random","BA_scalefree":"BA Scale-free"}
COLORS = {"1D_ring":"#1f77b4","2D_lattice":"#2ca02c",
          "ER_random":"#ff7f0e","BA_scalefree":"#d62728"}

def logbin(data, nbins=22):
    data = np.asarray(data); data = data[data >= 1]
    if len(data) < 5: return np.array([]), np.array([])
    edges = np.logspace(0, np.log10(data.max()+1), nbins+1)
    c, _ = np.histogram(data, bins=edges)
    w = np.diff(edges); cent = np.sqrt(edges[:-1]*edges[1:])
    pdf = c / (c.sum()*w)
    m = c > 0
    return cent[m], pdf[m]

# ============ FIG 1: Food web schematic ============
nbrs, G = build_network("BA_scalefree", 60, avg_k=4, seed=7)
troph = assign_trophic_levels(G, 60)
pos = nx.spring_layout(G, seed=3, k=0.6)
# override y by trophic level
for i in range(60):
    pos[i] = (pos[i][0], troph[i] + 0.3*np.random.default_rng(i).standard_normal())
fig, ax = plt.subplots(figsize=(8, 5.5))
tcols = ["#2ca02c","#ffd92f","#ff7f0e","#d62728"]
for lvl in [1,2,3,4]:
    ns = [i for i in range(60) if troph[i]==lvl]
    nx.draw_networkx_nodes(G, pos, nodelist=ns, node_color=tcols[lvl-1],
                           node_size=[60+25*G.degree(i) for i in ns],
                           edgecolors="black", linewidths=0.5, ax=ax,
                           label=f"Trophic level {lvl}")
nx.draw_networkx_edges(G, pos, alpha=0.25, width=0.6, ax=ax)
ax.set_title("Toy food web: scale-free network with assigned trophic levels")
ax.set_ylabel("Trophic level"); ax.set_xlabel("")
ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
ax.set_xticks([]); ax.grid(False)
fig.tight_layout(); fig.savefig(f"{FIG}/fig1_foodweb.png", bbox_inches="tight")
plt.close(fig); print("fig1 done")

# ============ FIG 2: Avalanche PDFs for 4 topologies at k=4 ============
fig, ax = plt.subplots(figsize=(7.5, 5.2))
sweep = R["sweep"]
for top in ["1D_ring","2D_lattice","ER_random","BA_scalefree"]:
    k = 2 if top=="1D_ring" else 4
    all_av = np.concatenate([sweep[(top, k, s)]["avalanches"] for s in [42,123,999] if (top,k,s) in sweep])
    x, y = logbin(all_av)
    taus = [sweep[(top,k,s)]["tau"] for s in [42,123,999] if (top,k,s) in sweep]
    taum = np.nanmean(taus); taus_sd = np.nanstd(taus)
    ax.loglog(x, y, "o-", ms=6, color=COLORS[top],
              label=f"{TOPO_LABEL[top]} (τ={taum:.2f}±{taus_sd:.2f})", alpha=0.85)
ax.set_xlabel("Avalanche size $s$"); ax.set_ylabel("Probability density $P(s)$")
ax.set_title("Avalanche-size distributions at $\\langle k \\rangle = 4$")
ax.legend(fontsize=9, loc="lower left")
fig.tight_layout(); fig.savefig(f"{FIG}/fig2_pdfs.png", bbox_inches="tight")
plt.close(fig); print("fig2 done")

# ============ FIG 3: tau vs k (connectivity sweep) ============
fig, ax = plt.subplots(figsize=(7, 4.8))
for top in ["ER_random","BA_scalefree"]:
    ks, taum, taus = [], [], []
    for k in [2,3,4,6,8]:
        vals = [sweep[(top,k,s)]["tau"] for s in [42,123,999] if (top,k,s) in sweep
                and not np.isnan(sweep[(top,k,s)]["tau"])]
        if vals:
            ks.append(k); taum.append(np.mean(vals)); taus.append(np.std(vals))
    ax.errorbar(ks, taum, yerr=taus, marker="o", ms=8, capsize=4, lw=1.5,
                color=COLORS[top], label=TOPO_LABEL[top])
# add ring and lattice as single points
for top in ["1D_ring","2D_lattice"]:
    k = 2 if top=="1D_ring" else 4
    vals = [sweep[(top,k,s)]["tau"] for s in [42,123,999]]
    ax.errorbar([k], [np.mean(vals)], yerr=[np.std(vals)], marker="s", ms=10,
                capsize=4, color=COLORS[top], label=TOPO_LABEL[top])
ax.set_xlabel("Mean degree $\\langle k \\rangle$")
ax.set_ylabel("Power-law exponent $\\tau$")
ax.set_title("Connectivity sweep: SOC exponent across topologies")
ax.legend(fontsize=9); ax.set_ylim(1.3, 3.3)
fig.tight_layout(); fig.savefig(f"{FIG}/fig3_tau_vs_k.png", bbox_inches="tight")
plt.close(fig); print("fig3 done")

# ============ FIG 4: Finite-size scaling ============
fig, ax = plt.subplots(figsize=(7, 4.8))
fss = R["fss"]
cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(fss)))
for (N_, c) in zip(sorted(fss.keys()), cmap):
    x, y = logbin(fss[N_]["avalanches"])
    ax.loglog(x, y, "o-", ms=6, color=c, label=f"$N={N_}$ (τ={fss[N_]['tau']:.2f})")
ax.set_xlabel("Avalanche size $s$"); ax.set_ylabel("$P(s)$")
ax.set_title("Finite-size scaling (BA scale-free, $\\langle k \\rangle = 4$)")
ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(f"{FIG}/fig4_fss.png", bbox_inches="tight")
plt.close(fig); print("fig4 done")

# ============ FIG 5: Trophic asymmetry (the novelty) ============
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
asym = R["asym"]
labels = {(1.0,1.0):"Symmetric (standard BS)",
          (0.5,1.0):"$p_{up}=0.5$ (predators shielded)",
          (1.0,0.5):"$p_{down}=0.5$ (prey shielded)",
          (0.3,1.0):"$p_{up}=0.3$ (strong pred. shield)",
          (1.0,0.3):"$p_{down}=0.3$ (strong prey shield)"}
colors_a = plt.cm.coolwarm(np.linspace(0.1, 0.9, 5))
for (key, c) in zip([(1.0,1.0),(0.5,1.0),(0.3,1.0),(1.0,0.5),(1.0,0.3)], colors_a):
    x, y = logbin(asym[key]["avalanches"])
    axes[0].loglog(x, y, "o-", ms=5, color=c,
                   label=f"{labels[key]} (τ={asym[key]['tau']:.2f})", alpha=0.85)
axes[0].set_xlabel("Avalanche size $s$"); axes[0].set_ylabel("$P(s)$")
axes[0].set_title("Effect of trophic asymmetry on avalanche tails")
axes[0].legend(fontsize=8, loc="lower left")

# bar of taus
keys_ord = [(1.0,1.0),(1.0,0.5),(1.0,0.3),(0.5,1.0),(0.3,1.0)]
taus_ord = [asym[k]["tau"] for k in keys_ord]
xtick = ["sym\n(1,1)","prey\nshield\n(1,0.5)","prey\nstrong\n(1,0.3)",
         "pred\nshield\n(0.5,1)","pred\nstrong\n(0.3,1)"]
bars = axes[1].bar(range(5), taus_ord, color=colors_a[[0,3,4,1,2]], edgecolor="black")
axes[1].set_xticks(range(5)); axes[1].set_xticklabels(xtick, fontsize=9)
axes[1].set_ylabel("Fitted exponent $\\tau$")
axes[1].set_title("Shielding predators produces heavy tails")
axes[1].axhline(asym[(1.0,1.0)]["tau"], ls="--", color="gray", lw=1,
                label="Symmetric baseline")
axes[1].legend(fontsize=9); axes[1].set_ylim(1.3, 3.3)
for b, t in zip(bars, taus_ord):
    axes[1].text(b.get_x()+b.get_width()/2, t+0.05, f"{t:.2f}",
                 ha="center", fontsize=9)
fig.tight_layout(); fig.savefig(f"{FIG}/fig5_asymmetry.png", bbox_inches="tight")
plt.close(fig); print("fig5 done")

# ============ FIG 6: Extinction risk vs centrality ============
ks = R["keystone"]
part = ks["participation"]
metrics = [("Degree", ks["degree"]), ("Betweenness", ks["betweenness"]),
           ("PageRank", ks["pagerank"]), ("Trophic level", ks["trophic"])]
fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
for ax, (name, arr) in zip(axes, metrics):
    ax.scatter(arr, part, alpha=0.55, s=26, color="#1f77b4", edgecolor="k", lw=0.3)
    key = name.lower().split()[0]
    key = "betweenness" if "betw" in key else key
    rho, pval = ks["corr"][key if key in ks["corr"] else name.lower()]
    ax.set_xlabel(name); ax.set_ylabel("Participation count" if ax is axes[0] else "")
    ax.set_title(f"{name}\nρ={rho:.2f}, p={pval:.1e}", fontsize=10)
fig.suptitle("Dynamic extinction risk vs static centrality (BA, N=196)", y=1.02)
fig.tight_layout(); fig.savefig(f"{FIG}/fig6_keystones.png", bbox_inches="tight")
plt.close(fig); print("fig6 done")

# ============ FIG 7: Min-fitness time series ============
# Rerun short for trace plots
from tabs import run_tabs
fig, axes = plt.subplots(2, 2, figsize=(11, 6.5), sharey=True)
for ax, top in zip(axes.flat, ["1D_ring","2D_lattice","ER_random","BA_scalefree"]):
    k = 2 if top=="1D_ring" else 4
    r = run_tabs(top, N=196, steps=80_000, burn_in=10_000, avg_k=k, seed=42)
    tr = r["trace"][::100]
    ax.plot(np.arange(len(tr))*100, tr, lw=0.3, color=COLORS[top])
    ax.axhline(r["f_c"], color="k", ls="--", lw=1)
    ax.set_title(f"{TOPO_LABEL[top]}  ($f_c$={r['f_c']:.3f})")
    ax.set_ylim(0,1)
for ax in axes[-1]: ax.set_xlabel("Time step")
for ax in axes[:,0]: ax.set_ylabel("Min fitness")
fig.suptitle("Self-organization of minimum fitness", y=1.01)
fig.tight_layout(); fig.savefig(f"{FIG}/fig7_minfit.png", bbox_inches="tight")
plt.close(fig); print("fig7 done")

print("\nAll figures generated.")
