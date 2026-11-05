"""MCDA totals and sensitivity checks for the M5 models and free-GPU survey (issue #168).

Run with any Python 3: ``python docs/decisions/mcda/research_2026_11_05_m5_models_free_gpus.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

DECISIONS = {
    "D1 base detector": (
        ["licence", "small_data_accuracy", "hailo_path", "training_effort", "maturity"],
        [30, 25, 20, 15, 10],
        {
            "A RF-DETR Small/Medium": [5, 5, 2, 5, 4],
            "B D-FINE / DEIM": [4, 4, 1, 2, 3],
            "C RT-DETRv2 / v4": [4, 4, 1, 2, 4],
            "D YOLOX-S": [4, 3, 5, 3, 3],
        },
        [[30, 25, 30, 10, 5], [25, 20, 40, 10, 5], [40, 25, 15, 10, 10]],
    ),
    "D2 training compute": (
        ["zero_cost", "vram_throughput", "terms_fit", "session_reliability", "setup_friction"],
        [25, 25, 20, 15, 15],
        {
            "A local RTX 4070 Laptop 8 GB": [5, 3, 5, 5, 5],
            "B Kaggle (30 h/week, 12 h sessions)": [5, 4, 3, 4, 3],
            "C Modal (30 $/month credit)": [3, 5, 3, 4, 3],
            "D Colab free": [5, 4, 3, 1, 4],
        },
        [[20, 45, 15, 10, 10], [25, 60, 5, 5, 5]],
    ),
}


def total(scores: list[int], weights: list[int]) -> int:
    """Weighted sum of 0-5 scores, out of 500."""
    return sum(s * w for s, w in zip(scores, weights, strict=True))


def main() -> None:
    """Print each decision's totals, then its sensitivity scenarios."""
    for name, (criteria, weights, options, scenarios) in DECISIONS.items():
        assert sum(weights) == 100 and all(sum(s) == 100 for s in scenarios)
        assert all(len(s) == len(criteria) for s in options.values())
        print(name)
        for option, scores in sorted(options.items(), key=lambda kv: -total(kv[1], weights)):
            print(f"  {total(scores, weights):3d}  {option}")
        for scenario in scenarios:
            ranked = sorted(options.items(), key=lambda kv: -total(kv[1], scenario))
            line = ", ".join(f"{o.split()[0]} {total(s, scenario)}" for o, s in ranked)
            print(f"  sensitivity {scenario}: {line}")


if __name__ == "__main__":
    main()
