"""Auction assignment: Part 1 (second price), Part 2 (first price), Part 3 (VCG path).
Run: python auctions.py   -> prints results, saves PNGs to ./plots
"""
import os, itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
OUT = "plots"
os.makedirs(OUT, exist_ok=True)
N_SIM = 100_000
BIDS = np.round(np.arange(0, 1.001, 0.01), 2)
VALUES = [0.2, 0.5, 0.8]
STRATS = ["truthful", "half", "random"]


# ---------------------------------------------------------------- Part 1
def rival_bids(strategy, size):
    """Draw rival value ~ U[0,1] and return its bid under the strategy."""
    v = rng.random(size)
    if strategy == "truthful":
        return v
    if strategy == "half":
        return v / 2
    if strategy == "random":
        return rng.random(size)  # ignores its value
    raise ValueError(strategy)


def avg_utility(v, b, strategy, n_rivals, n=N_SIM):
    """Mean utility of bidder 1 (value v, bid b) in a 2nd-price auction."""
    bids = np.stack([rival_bids(strategy, n) for _ in range(n_rivals)])
    top = bids.max(axis=0)               # highest rival bid = price if 1 wins
    return np.where(b > top, v - top, 0.0).mean()   # ties have prob. 0


def part_a_or_c(n_rivals, tag):
    print(f"\n=== Part 1{tag}: {n_rivals} rival(s), bids 0.00..1.00, {N_SIM} auctions/bid ===")
    fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharex=True)
    for i, v in enumerate(VALUES):
        for j, s in enumerate(STRATS):
            u = np.array([avg_utility(v, b, s, n_rivals) for b in BIDS])
            best = BIDS[u.argmax()]
            # plateau of near-optimal bids (within Monte-Carlo noise)
            near = BIDS[u >= u.max() - 0.002]
            print(f"v={v} rival={s:8s}: max utility {u.max():.4f}; best bid {best:.2f}; "
                  f"near-optimal range [{near.min():.2f}, {near.max():.2f}]; "
                  f"U(b=v)={u[int(round(v*100))]:.4f}")
            ax = axes[i, j]
            ax.plot(BIDS, u)
            ax.axvline(v, color="r", ls="--", lw=1, label="b = v")
            ax.set_title(f"v={v}, rival: {s}")
            if i == 2: ax.set_xlabel("bidder 1's bid")
            if j == 0: ax.set_ylabel("avg utility")
            ax.legend(fontsize=8)
    fig.suptitle(f"Second-price auction, {n_rivals} rival(s)")
    fig.tight_layout()
    fig.savefig(f"{OUT}/part1{tag}_{n_rivals}rivals.png", dpi=120)
    plt.close(fig)


def part_b(rival_sets):
    """Rival bids are fixed; check b=v maximises utility (deterministic)."""
    print("\n=== Part 1B: fixed rival bids ===")
    for rb in rival_sets:
        price = max(rb)
        for v in VALUES:
            u = np.array([(v - price) if b > price else 0.0 for b in BIDS])
            uv = u[int(round(v * 100))]
            print(f"rival bids {rb}, v={v}: U(b=v)={uv:.2f}, max over grid={u.max():.2f}, "
                  f"b=v optimal? {uv >= u.max() - 1e-12}")


# ---------------------------------------------------------------- Part 2
KS = np.round(np.arange(0.1, 2.0001, 0.1), 2)


def part2(n, n_sim=N_SIM):
    eq = (n - 1) / n
    util, regret_frac, gap = [], [], []
    for k in KS:
        vals = rng.random((n_sim, n))
        bids = vals * eq
        bids[:, 0] = vals[:, 0] * k          # bidder 1 deviates
        order = np.sort(bids, axis=1)
        top, second = order[:, -1], order[:, -2]
        win1 = bids[:, 0] == top
        util.append(np.where(win1, vals[:, 0] - bids[:, 0], 0).mean())
        # winner (any bidder) could have paid less and still won: bid > 2nd highest
        regret_frac.append((top > second).mean())
        gap.append((top - second).mean())     # avg money left on the table
    return np.array(util), np.array(regret_frac), np.array(gap)


def run_part2():
    print("\n=== Part 2: first-price auction ===")
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for c, n in enumerate([2, 3, 4]):
        u, rf, gap = part2(n)
        eq = (n - 1) / n
        k_best = KS[u.argmax()]
        print(f"n={n}: equilibrium k={eq:.3f}; best k on grid={k_best:.1f} "
              f"(U={u.max():.4f}); U at k=eq(nearest grid {KS[np.abs(KS-eq).argmin()]:.1f})="
              f"{u[np.abs(KS-eq).argmin()]:.4f}")
        for k, a, b_, g in zip(KS, u, rf, gap):
            print(f"   k={k:.1f} U1={a:.4f} frac(winner could pay less)={b_:.3f} avg gap={g:.4f}")
        axes[0, c].plot(KS, u); axes[0, c].axvline(eq, color="r", ls="--", label="equilibrium k")
        axes[0, c].set_title(f"n={n}: bidder 1 expected utility"); axes[0, c].set_xlabel("k"); axes[0, c].legend()
        axes[1, c].plot(KS, rf); axes[1, c].axvline(eq, color="r", ls="--")
        axes[1, c].set_title(f"n={n}: fraction winner could pay less"); axes[1, c].set_xlabel("k")
    fig.tight_layout(); fig.savefig(f"{OUT}/part2_first_price.png", dpi=120); plt.close(fig)


# ---------------------------------------------------------------- Part 3
# NOTE: edit COSTS if your copy of Figure 7.3 differs. These costs reproduce the
# payments stated in the text (AB=4, BE=2, EF=3, others 0).
COSTS = {("A", "B"): 3, ("B", "E"): 1, ("E", "F"): 2,
         ("A", "C"): 2, ("C", "D"): 3, ("D", "F"): 2}
SRC, DST = "A", "F"


def all_paths(costs, src, dst):
    adj = {}
    for (u, v) in costs:
        adj.setdefault(u, []).append(v)
    out = []
    def dfs(node, path):
        if node == dst:
            out.append(list(path)); return
        for nxt in adj.get(node, []):
            if nxt not in path:
                path.append(nxt); dfs(nxt, path); path.pop()
    dfs(src, [src])
    return [[(p[i], p[i + 1]) for i in range(len(p) - 1)] for p in out]


def cheapest(costs, exclude=None):
    best, best_c = None, float("inf")
    for p in all_paths(costs, SRC, DST):
        if exclude in p:
            continue
        c = sum(costs[e] for e in p)
        if c < best_c:
            best, best_c = p, c
    return best, best_c


def vcg(costs):
    path, cost = cheapest(costs)
    pay = {}
    for e in costs:
        if e in path:
            _, c_without = cheapest(costs, exclude=e)
            pay[e] = c_without - (cost - costs[e])   # VCG payment
        else:
            pay[e] = 0.0
    return path, cost, pay


def run_part3():
    print("\n=== Part 3: VCG cheapest path ===")
    path, cost, pay = vcg(COSTS)
    print("chosen path:", "".join(e[0] for e in path) + path[-1][1], "cost", cost)
    for e, p in pay.items():
        print(f"  edge {e[0]}{e[1]} cost {COSTS[e]} paid {p}")
    grid = np.arange(0, 10.001, 0.5)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, edge in zip(axes, [("B", "E"), ("C", "D")]):
        on = edge in path
        truth = COSTS[edge]
        us = []
        for r in grid:
            rep = dict(COSTS); rep[edge] = r
            p, _, pay_r = vcg(rep)
            us.append(pay_r[edge] - truth if edge in p else 0.0)   # utility w/ TRUE cost
        us = np.array(us)
        print(f"edge {edge[0]}{edge[1]} ({'on' if on else 'off'} path, true cost {truth}): "
              f"truthful utility {us[list(grid).index(truth)] if truth in grid else 'n/a'}, "
              f"max utility {us.max()} at report(s) {grid[us == us.max()]}")
        for r, u in zip(grid, us): print(f"    report {r:4.1f} -> utility {u:.1f}")
        ax.step(grid, us, where="mid"); ax.axvline(truth, color="r", ls="--", label="true cost")
        ax.set_title(f"Edge {edge[0]}{edge[1]} ({'on' if on else 'off'} chosen path)")
        ax.set_xlabel("reported cost"); ax.set_ylabel("utility"); ax.legend()
    fig.tight_layout(); fig.savefig(f"{OUT}/part3_vcg.png", dpi=120); plt.close(fig)


if __name__ == "__main__":
    part_a_or_c(1, "A")
    part_b([(0.1,), (0.4,), (0.9,)])
    part_a_or_c(2, "C")                 # two rivals, same strategy
    part_b([(0.1, 0.4), (0.4, 0.9), (0.1, 0.9)])   # Part B with two rivals
    run_part2()
    run_part3()
