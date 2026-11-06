"""MCDA totals and sensitivity checks for the bench acceptance spec (issue #171).

Run with any Python 3:
``python docs/decisions/mcda/spec_2026_11_06_bench_acceptance.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

DECISIONS = {
    "D1 where the bench criteria live": {
        "criteria": ["traceability_clarity", "single_source_of_truth", "scope_fit", "effort"],
        "weights": [30, 25, 25, 20],
        "options": {
            "A new spec bench-acceptance.md": [5, 4, 5, 3],
            "B section in capture-rig.md": [3, 4, 2, 5],
            "C criteria spread over four specs": [2, 5, 4, 2],
        },
        "scenarios": [[25, 20, 15, 40], [20, 40, 20, 20]],
    },
    "D2 detection latency threshold on the Pi 5 CPU": {
        "criteria": ["fits_need", "achievable_without_hailo", "testable", "keeps_m6_honest"],
        "weights": [35, 25, 20, 20],
        "options": {
            "A p95 <= 1 s, >= 1 FPS": [4, 5, 5, 3],
            "B p95 <= 200 ms, >= 5 FPS": [5, 2, 5, 5],
            "C p95 <= 500 ms, >= 2 FPS": [5, 4, 5, 4],
            "D measure only, no threshold": [1, 5, 3, 2],
        },
        "scenarios": [[30, 40, 15, 15], [30, 20, 15, 35]],
    },
}


def total(scores: list[int], weights: list[int]) -> int:
    """Weighted sum of 0-5 scores, out of 500."""
    return sum(s * w for s, w in zip(scores, weights, strict=True))


def main() -> None:
    """Print the totals of each decision, then each sensitivity scenario."""
    for name, decision in DECISIONS.items():
        weights = decision["weights"]
        assert sum(weights) == 100, weights
        print(f"== {name} {decision['criteria']} {weights}")
        for option, scores in decision["options"].items():
            print(f"  {option}: {total(scores, weights)}")
        for scenario in decision["scenarios"]:
            assert sum(scenario) == 100, scenario
            results = {o[:1]: total(s, scenario) for o, s in decision["options"].items()}
            print(f"  sensitivity {scenario}: {results}")


if __name__ == "__main__":
    main()
