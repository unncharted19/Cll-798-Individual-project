"""
Trophic-Asymmetric Bak-Sneppen (TABS) on food-web networks.
Core simulator module.
"""
import numpy as np
import networkx as nx

def build_network(topology, N, avg_k=4, seed=42):
    """Returns (neighbor_list, networkx_graph)."""
    rng = np.random.default_rng(seed)
    if topology == "1D_ring":
        nbrs = [[(i-1) % N, (i+1) % N] for i in range(N)]
        G = nx.cycle_graph(N)
    elif topology == "2D_lattice":
        L = int(round(np.sqrt(N))); assert L*L == N
        nbrs = []
        for i in range(N):
            r, c = i // L, i % L
            nbrs.append([((r-1)%L)*L+c, ((r+1)%L)*L+c, r*L+(c-1)%L, r*L+(c+1)%L])
        G = nx.grid_2d_graph(L, L, periodic=True)
        G = nx.convert_node_labels_to_integers(G)
    elif topology == "ER_random":
        G = nx.erdos_renyi_graph(N, p=avg_k/(N-1), seed=seed)
        if not nx.is_connected(G):
            comps = list(nx.connected_components(G))
            for i in range(len(comps)-1):
                G.add_edge(next(iter(comps[i])), next(iter(comps[i+1])))
        nbrs = [list(G.neighbors(i)) for i in range(N)]
    elif topology == "BA_scalefree":
        m = max(1, avg_k // 2)
        G = nx.barabasi_albert_graph(N, m=m, seed=seed)
        nbrs = [list(G.neighbors(i)) for i in range(N)]
    else:
        raise ValueError(topology)
    return nbrs, G

def assign_trophic_levels(G, N, n_levels=4):
    """Assign trophic levels 1..n_levels based on degree rank (hubs = apex predators)."""
    degs = np.array([G.degree(i) for i in range(N)])
    order = np.argsort(degs)  # ascending
    levels = np.zeros(N, dtype=np.int8)
    cut = N // n_levels
    for lvl in range(n_levels):
        lo = lvl*cut
        hi = (lvl+1)*cut if lvl < n_levels-1 else N
        levels[order[lo:hi]] = lvl + 1
    return levels

def run_tabs(topology, N=196, steps=300_000, burn_in=50_000,
             p_up=1.0, p_down=1.0, avg_k=4, seed=42, track_participation=False):
    """
    Trophic-asymmetric Bak-Sneppen.
    p_up   = prob. of perturbing a higher-trophic neighbour (predator) when prey dies
    p_down = prob. of perturbing a lower-trophic neighbour (prey) when predator dies
    p_up=p_down=1 reproduces standard Bak-Sneppen.
    """
    rng = np.random.default_rng(seed)
    nbrs, G = build_network(topology, N, avg_k=avg_k, seed=seed)
    trophic = assign_trophic_levels(G, N)
    fitness = rng.random(N)
    trace = np.empty(steps, dtype=np.float32)
    participation = np.zeros(N, dtype=np.int64) if track_participation else None

    for t in range(steps):
        i = int(np.argmin(fitness))
        trace[t] = fitness[i]
        fitness[i] = rng.random()
        ti = trophic[i]
        for j in nbrs[i]:
            tj = trophic[j]
            if tj > ti:   # j is a predator of i
                if rng.random() < p_up:
                    fitness[j] = rng.random()
            elif tj < ti: # j is prey of i
                if rng.random() < p_down:
                    fitness[j] = rng.random()
            else:         # same level -> always perturb
                fitness[j] = rng.random()

    post = trace[burn_in:]
    f_c = float(np.mean(post))
    f0 = float(np.percentile(post, 60))

    # Extract avalanches
    sizes = []; in_a = False; cur = 0; cur_set = set()
    # Second pass to track participation: re-run is expensive, so approximate
    # by recording species identities during avalanche runs — we do it here
    # from the trace alone (size only). Participation handled separately below.
    for x in post:
        if x < f0:
            cur = cur + 1 if in_a else 1
            in_a = True
        else:
            if in_a: sizes.append(cur); in_a = False
    if in_a: sizes.append(cur)

    # For participation tracking: do a lightweight re-run recording which
    # species was the min at each step during avalanche windows.
    if track_participation:
        rng2 = np.random.default_rng(seed)
        fitness2 = rng2.random(N)
        in_a = False
        for t in range(steps):
            i = int(np.argmin(fitness2))
            val = fitness2[i]
            fitness2[i] = rng2.random()
            ti = trophic[i]
            for j in nbrs[i]:
                tj = trophic[j]
                if tj > ti:
                    if rng2.random() < p_up: fitness2[j] = rng2.random()
                elif tj < ti:
                    if rng2.random() < p_down: fitness2[j] = rng2.random()
                else:
                    fitness2[j] = rng2.random()
            if t >= burn_in:
                if val < f0:
                    participation[i] += 1

    degs = np.array([G.degree(i) for i in range(N)])
    return dict(
        topology=topology, N=N, avg_k=avg_k, seed=seed,
        p_up=p_up, p_down=p_down,
        trace=trace, avalanches=np.array(sizes, dtype=np.int64),
        f_c=f_c, f0=f0, trophic=trophic, degrees=degs,
        participation=participation, graph=G,
    )
