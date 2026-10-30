"""MCDA totals and sensitivity checks for ADR-0028 (remove the GitHub check workflows, issue #110).

Run with any Python 3: ``python docs/decisions/mcda/adr_0028_remove_check_workflows.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

DECISIONS = {
    "D1 what to do with ci.yml": (
        ["adr_0025_conformance", "safety_net", "simplicity", "one_toolchain", "cost_time"],
        [30, 25, 20, 15, 10],
        {
            "A remove ci.yml": [5, 1, 5, 5, 5],
            "B reduce to mise-action + just check": [2, 4, 3, 5, 3],
            "C keep as is": [1, 3, 2, 1, 3],
        },
        [[15, 45, 15, 15, 10], [40, 15, 25, 10, 10]],
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
