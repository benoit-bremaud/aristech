"""MCDA totals and sensitivity checks for ADR-0025 (branching and promotion model, issue #112).

Run with any Python 3: ``python docs/decisions/mcda/adr_0025_branching_model.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

DECISIONS = {
    "D1 branching model": (
        [
            "main_field_ready",
            "contributors_long_experiments",
            "local_ci_actions_prod_only",
            "simplicity_no_drift_hotfix",
            "qa_before_users",
            "convention_conformance",
            "traceability_of_field_commit",
        ],
        [20, 20, 10, 15, 15, 10, 10],
        {
            "A git-flow dev -> staging -> main": [5, 5, 5, 1, 5, 1, 3],
            "B main + short branches, staging env, signed tag": [4, 3, 5, 5, 5, 5, 5],
            "C B + dev integration branch": [5, 5, 5, 3, 5, 2, 4],
        },
        [[20, 30, 10, 5, 15, 10, 10], [30, 10, 10, 20, 15, 5, 10]],
    ),
}


def total(weights: list[int], scores: list[int]) -> int:
    return sum(w * s for w, s in zip(weights, scores, strict=True))


def main() -> None:
    for name, (criteria, weights, options, variants) in DECISIONS.items():
        assert sum(weights) == 100, name
        print(f"## {name}  ({', '.join(criteria)})")
        for label, scores in options.items():
            print(f"  {total(weights, scores):>4}  {label}")
        for alt in variants:
            assert sum(alt) == 100, name
            ranked = sorted(options.items(), key=lambda kv: -total(alt, kv[1]))
            print(
                f"  sensitivity {alt}: " + ", ".join(f"{k[0]} {total(alt, v)}" for k, v in ranked)
            )


if __name__ == "__main__":
    main()
