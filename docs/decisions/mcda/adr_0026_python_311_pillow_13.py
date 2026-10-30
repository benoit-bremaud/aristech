"""MCDA totals and sensitivity checks for ADR-0026 (Python >= 3.11 for Pillow 13, issue #111).

Run with any Python 3: ``python docs/decisions/mcda/adr_0026_python_311_pillow_13.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

DECISIONS = {
    "D1 Pillow 13 needs Python >= 3.11": (
        [
            "closes_vulnerabilities",
            "runtime_risk",
            "scope_effort",
            "simplicity",
            "python_support_breadth",
        ],
        [35, 25, 15, 15, 10],
        {
            "A Python >= 3.11 + Pillow 13": [5, 4, 2, 5, 4],
            "B markers: Pillow 13 on >= 3.11, 12.3 on 3.10": [3, 3, 3, 1, 5],
            "C keep Pillow 12.3 under a time-boxed waiver": [2, 5, 5, 4, 5],
        },
        [[15, 25, 35, 15, 10], [50, 20, 10, 10, 10]],
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
