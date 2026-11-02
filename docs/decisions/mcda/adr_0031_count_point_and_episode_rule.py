"""MCDA totals and weight sensitivity for ADR-0031 (COUNT point target, episode rule)."""

import itertools


def run(name, weights, options):
    print(name)
    for option, scores in options.items():
        print(f"  {option}: {sum(w * s for w, s in zip(weights, scores, strict=True))}")
    wins = dict.fromkeys(options, 0)
    vectors = 0
    for vector in itertools.product(range(0, 101, 5), repeat=len(weights)):
        if sum(vector) != 100:
            continue
        vectors += 1
        totals = {o: sum(w * s for w, s in zip(vector, sc, strict=True)) for o, sc in options.items()}
        best = max(totals.values())
        for option, total in totals.items():
            wins[option] += total == best
    print("  first in:", {o: f"{100 * c / vectors:.0f}%" for o, c in wins.items()}, vectors)


run(
    "COUNT target [recall 35, false-count noise 25, ADR consistency 25, simplicity 15]",
    [35, 25, 25, 15],
    {
        "A keep P>=0.95 (infeasible)": [0, 5, 1, 3],
        "B P>=0.80 -> 0.15": [5, 3, 4, 4],
        "C P>=0.85 -> 0.40": [4, 4, 4, 4],
        "D COUNT=ACT 0.45": [4, 4, 2, 5],
    },
)
run(
    "Episode rule [FP robustness 35, attack sensitivity 30, simplicity 20, spec fit 15]",
    [35, 30, 20, 15],
    {
        "E1 N hit frames in sliding W open, T quiet closes": [4, 4, 4, 5],
        "E2 first hit opens, T quiet closes": [1, 5, 5, 2],
        "E3 N consecutive hit frames open": [5, 2, 4, 3],
    },
)
