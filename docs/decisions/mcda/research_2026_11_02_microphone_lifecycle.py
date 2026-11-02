"""MCDA totals and sensitivity checks for the ICS-43434 lifecycle note (issue #84).

Run with any Python 3:
``python docs/decisions/mcda/research_2026_11_02_microphone_lifecycle.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

CRITERIA = ["band_fidelity", "available_now", "longevity", "pi5_integration", "cost"]
WEIGHTS = [30, 25, 15, 20, 10]
OPTIONS = {
    "A keep ICS-43434 (Adafruit 6049) + spares": [4, 5, 1, 5, 5],
    "B SPH0645 (Adafruit 3421)": [3, 3, 1, 5, 5],
    "C T5848 + 1.8 V level shifter": [4, 2, 5, 1, 2],
}
SCENARIOS = [[25, 15, 35, 15, 10], [30, 10, 15, 35, 10], [40, 25, 10, 15, 10]]


def total(scores: list[int], weights: list[int]) -> int:
    """Weighted sum of 0-5 scores, out of 500."""
    return sum(s * w for s, w in zip(scores, weights, strict=True))


def main() -> None:
    """Print the totals, then each sensitivity scenario."""
    print(f"== microphones {CRITERIA} {WEIGHTS}")
    for option, scores in OPTIONS.items():
        print(f"  {option}: {total(scores, WEIGHTS)}")
    for scenario in SCENARIOS:
        assert sum(scenario) == 100, scenario
        results = {o: total(s, scenario) for o, s in OPTIONS.items()}
        print(f"  sensitivity {scenario}: {results}")


if __name__ == "__main__":
    main()
