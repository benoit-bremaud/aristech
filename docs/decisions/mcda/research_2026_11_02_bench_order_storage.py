"""MCDA totals and sensitivity checks for the bench order storage choice (issue #132).

Run with any Python 3:
``python docs/decisions/mcda/research_2026_11_02_bench_order_storage.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

CRITERIA = ["cost", "capacity", "fits_head", "adr_0017_conformity", "available_now", "endurance"]
WEIGHTS = [25, 20, 20, 10, 15, 10]
OPTIONS = {
    "A M.2 HAT+ + Kingston NV3 2230 1 TB (284 EUR)": [1, 5, 5, 5, 4, 4],
    "B Pimoroni NVMe Base + Kingston NV3 2280 1 TB (208 EUR)": [3, 5, 3, 3, 5, 4],
    "C M.2 HAT+ + SK hynix 2230 512 GB (160 EUR)": [4, 3, 5, 4, 4, 3],
    "D official SSD kit 512 GB with M.2 HAT+ (165 EUR, pre-order)": [4, 3, 5, 4, 1, 3],
}
SCENARIOS = [
    [40, 15, 15, 10, 10, 10],
    [15, 35, 15, 10, 15, 10],
    [20, 15, 35, 10, 10, 10],
]


def total(scores: list[int], weights: list[int]) -> int:
    """Weighted sum of 0-5 scores, out of 500."""
    return sum(s * w for s, w in zip(scores, weights, strict=True))


def main() -> None:
    """Print the totals, then each sensitivity scenario."""
    print(f"== storage {CRITERIA} {WEIGHTS}")
    for option, scores in OPTIONS.items():
        print(f"  {option}: {total(scores, WEIGHTS)}")
    for scenario in SCENARIOS:
        assert sum(scenario) == 100, scenario
        results = {o[:1]: total(s, scenario) for o, s in OPTIONS.items()}
        print(f"  sensitivity {scenario}: {results}")


if __name__ == "__main__":
    main()
