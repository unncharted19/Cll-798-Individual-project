# Results summary

## Connectivity sweep (N=196, 300k steps, 3 seeds)

| Topology | <k> | f_c | τ (mean±sd) | # avalanches | max avalanche |
|---|---|---|---|---|---|
| 1D_ring | 2 | 0.217 | 2.84±0.01 | 56109 | 28 |
| 2D_lattice | 4 | 0.123 | 2.67±0.00 | 52479 | 34 |
| ER_random | 2 | 0.150 | 2.91±0.01 | 51221 | 42 |
| ER_random | 3 | 0.121 | 2.84±0.03 | 50174 | 42 |
| ER_random | 4 | 0.100 | 2.79±0.02 | 49321 | 45 |
| ER_random | 6 | 0.073 | 2.83±0.11 | 48194 | 49 |
| ER_random | 8 | 0.058 | 2.90±0.12 | 48007 | 42 |
| BA_scalefree | 2 | 0.116 | 2.52±0.57 | 37358 | 65 |
| BA_scalefree | 3 | 0.116 | 2.52±0.57 | 37358 | 65 |
| BA_scalefree | 4 | 0.078 | 2.91±0.03 | 39942 | 54 |
| BA_scalefree | 6 | 0.059 | 2.79±0.12 | 40705 | 51 |
| BA_scalefree | 8 | 0.049 | 2.86±0.09 | 41802 | 51 |

## Finite-size scaling (BA, k=4)
| N | f_c | τ | max avalanche |
|---|---|---|---|
| 64 | 0.091 | 2.83 | 41 |
| 144 | 0.077 | 2.80 | 72 |
| 256 | 0.070 | 2.98 | 75 |
| 400 | 0.066 | 1.73 | 68 |

## Trophic asymmetry (BA, N=196, k=4)
| p_up | p_down | f_c | τ | interpretation |
|---|---|---|---|---|
| 1.0 | 1.0 | 0.074 | 2.88 | symmetric baseline |
| 1.0 | 0.5 | 0.083 | 2.99 | prey shielded |
| 1.0 | 0.3 | 0.089 | 2.88 | prey strongly shielded |
| 0.5 | 1.0 | 0.085 | 1.72 | predators shielded |
| 0.3 | 1.0 | 0.092 | 1.73 | predators strongly shielded |

## Extinction risk correlations (BA, N=196, 500k steps)
| Static metric | Spearman ρ | p-value |
|---|---|---|
| degree | +0.603 | 8.81e-21 |
| betweenness | +0.609 | 2.58e-21 |
| pagerank | +0.311 | 9.24e-06 |
| trophic | +0.438 | 1.44e-10 |