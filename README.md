# Trophic-Asymmetric Extinction Cascades: SOC in a Toy Food Web

**Course project — CLL798 Complexity Science in Chemical Industry, IIT Delhi, April 2026**
**Author:** Ayush Bhanderiya (2023CH10584)

## What this project is about

This project investigates whether a minimal model of an ecological food web exhibits **Self-Organized Criticality (SOC)** — the property that small perturbations trigger cascades of every size, following a power law, without any parameter tuning. SOC is the statistical fingerprint that unifies earthquakes, neuronal avalanches, forest fires, and power-grid blackouts. Here we ask: do toy food webs join that club?

We extend the classical Bak–Sneppen (BS) evolution model by introducing **trophic asymmetry**: each species is assigned a trophic level (producer → apex predator), and the update rule treats predator and prey perturbations *differently*. We call this the **Trophic-Asymmetric Bak–Sneppen (TABS)** model. To our knowledge this extension has not been published.

## Key findings

1. **Universal SOC.** On 4 network topologies (1D ring, 2D lattice, Erdős–Rényi, Barabási–Albert) and 5 mean degrees, the avalanche-size distribution is a clean power law with exponent **τ ≈ 2.8 ± 0.1**, robust across seeds and connectivity.
2. **Finite-size scaling** at N ∈ {64, 144, 256, 400} confirms universal small-avalanche behaviour — the canonical SOC signature.
3. **Novelty result — predator shielding collapses the exponent.** Setting the predator-perturbation probability p_up = 0.3 (while leaving prey perturbation at 1.0) drops τ from ~2.88 to ~1.73 — a dramatically heavier tail. Shielding prey instead leaves τ unchanged. **Ecological meaning:** insulating apex predators from the collapse of their prey does not make ecosystems safer — it concentrates extinction risk into rare, catastrophic events.
4. **Hidden keystones.** Betweenness centrality predicts dynamic extinction risk better (Spearman ρ = 0.61) than trophic level (0.44) or PageRank (0.31), but all static metrics leave most of the variance unexplained, implying that simulation-based vulnerability analysis reveals information topology alone cannot.

## Repository structure
```
.
├── README.md                  # this file
├── src/
│   ├── tabs.py                # TABS simulator (the model)
│   ├── run_experiments.py     # runs all 4 experiments
│   ├── make_figures.py        # generates all 7 figures
│   └── summarize.py           # prints the results table
├── results/
│   ├── all_results.pkl        # raw simulation output
│   └── summary.md             # human-readable summary table
├── figures/
│   ├── fig1_foodweb.png       # schematic food web
│   ├── fig2_pdfs.png          # avalanche PDFs across topologies
│   ├── fig3_tau_vs_k.png      # connectivity sweep
│   ├── fig4_fss.png           # finite-size scaling
│   ├── fig5_asymmetry.png     # THE novelty result
│   ├── fig6_keystones.png     # extinction risk vs centrality
│   └── fig7_minfit.png        # min-fitness self-organization
└── report/
    ├── report.tex             # LaTeX manuscript
    └── report.pdf             # compiled 12-page PDF
```

## Reproducing the results

```bash
# 1. Install dependencies
pip install numpy networkx matplotlib scipy powerlaw

# 2. Run the four experiments (~3 minutes on a modern laptop)
python src/run_experiments.py

# 3. Generate all figures
python src/make_figures.py

# 4. Print summary
python src/summarize.py

# 5. Compile the report (optional, requires pdflatex)
cd report && pdflatex report.tex && pdflatex report.tex
```

Random seeds (42, 123, 999) are hard-coded for bit-for-bit reproducibility.

## Acknowledgements

Developed with assistance from Claude (Anthropic) for scoping, code drafting, debugging, figure design, and manuscript drafting. All code was executed and every quantitative claim was verified against simulation output before being included. The full list of prompts used is in Appendix A of the report.

Thanks to Prof. Rajesh for the CLL798 project framing.
