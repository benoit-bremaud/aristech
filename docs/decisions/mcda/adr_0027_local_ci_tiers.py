"""MCDA totals and sensitivity checks for ADR-0027 (local CI tiers, issue #109).

Run with any Python 3: ``python docs/decisions/mcda/adr_0027_local_ci_tiers.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

DECISIONS = {
    "D1 hook runner and toolchain": (
        ["same_checks_everywhere", "pinned_reproducible", "speed", "simplicity", "cross_project_fit"],
        [30, 25, 15, 15, 15],
        {
            "A just + lefthook + mise": [5, 5, 4, 4, 5],
            "B pre-commit framework (install the existing config)": [3, 4, 3, 4, 2],
            "C Makefile targets + hand-written git hooks": [3, 1, 4, 3, 2],
        },
        [[20, 15, 15, 35, 15], [40, 30, 10, 10, 10]],
    ),
    "D2 Semgrep when the rule registry is unreachable": (
        ["no_false_green", "works_offline", "simplicity"],
        [50, 30, 20],
        {
            "A WARNING not run, check goes on": [4, 5, 4],
            "B fail the check": [5, 0, 5],
            "C vendor the p/python rules in the repo": [5, 5, 1],
        },
        [[30, 50, 20], [70, 15, 15]],
    ),
}


def total(weights: list[int], scores: list[int]) -> int:
    """Weighted sum of 0-5 scores, out of 500."""
    return sum(w * s for w, s in zip(weights, scores, strict=True))


def main() -> None:
    """Print each decision's totals best first, then its sensitivity scenarios."""
    for name, (criteria, weights, options, variants) in DECISIONS.items():
        assert sum(weights) == 100, name
        assert all(len(s) == len(criteria) for s in options.values()), name
        print(f"## {name}  ({', '.join(criteria)})")
        for label, scores in sorted(options.items(), key=lambda kv: -total(weights, kv[1])):
            print(f"  {total(weights, scores):>4}  {label}")
        for alt in variants:
            assert sum(alt) == 100, name
            ranked = sorted(options.items(), key=lambda kv: -total(alt, kv[1]))
            print(
                f"  sensitivity {alt}: " + ", ".join(f"{k[0]} {total(alt, v)}" for k, v in ranked)
            )


if __name__ == "__main__":
    main()
