"""MCDA totals and sensitivity checks for ADR-0023 (iNaturalist fetch, issue #95 PR 3).

Run with any Python 3: ``python docs/decisions/mcda/adr_0023_inaturalist_fetch.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

CRITERIA = ["traceability", "licence_safety", "dependencies_kiss", "effort"]
WEIGHTS = [35, 25, 20, 20]
OPTIONS = {
    "A stdlib script on API v1, per-photo attribution": [5, 5, 4, 3],
    "B manual website export": [2, 4, 5, 3],
    "C pyinaturalist library": [5, 5, 2, 4],
}
SCENARIOS = [[25, 25, 30, 20], [30, 20, 20, 30], [25, 25, 20, 30], [35, 15, 30, 20]]


def total(scores: list[int], weights: list[int]) -> int:
    """Weighted sum of 0-5 scores, out of 500."""
    return sum(s * w for s, w in zip(scores, weights, strict=True))


def main() -> None:
    """Print the totals, then each sensitivity scenario."""
    assert sum(WEIGHTS) == 100
    assert all(sum(s) == 100 for s in SCENARIOS)
    for option, scores in sorted(OPTIONS.items(), key=lambda kv: -total(kv[1], WEIGHTS)):
        print(f"{total(scores, WEIGHTS):3d}  {option}")
    for scenario in SCENARIOS:
        ranked = sorted(OPTIONS.items(), key=lambda kv: -total(kv[1], scenario))
        line = ", ".join(f"{o.split()[0]} {total(s, scenario)}" for o, s in ranked)
        print(f"sensitivity {scenario}: {line}")


if __name__ == "__main__":
    main()
