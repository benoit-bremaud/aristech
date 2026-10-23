"""MCDA totals and sensitivity checks for ADR-0024 (pre-field model training, issue #95 PR 4).

Run with any Python 3: ``python docs/decisions/mcda/adr_0024_prefield_training.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

DECISIONS = {
    "D1 RF-DETR size": (
        ["small_object_accuracy", "fits_8gb", "training_time", "edge_path", "licence"],
        [30, 25, 20, 15, 10],
        {
            "A Nano (384 px)": [2, 5, 5, 5, 5],
            "B Small (512 px)": [4, 4, 4, 4, 5],
            "C Medium": [5, 3, 3, 3, 5],
        },
        [[45, 20, 15, 10, 10], [25, 20, 15, 30, 10], [25, 40, 15, 10, 10]],
    ),
    "D2 scoring path": (
        ["same_yardstick", "dry", "reusable_later", "effort"],
        [35, 25, 20, 20],
        {
            "A RFDETRDetector adapter + UC3 harness": [5, 5, 5, 3],
            "B metrics inside the training script": [3, 1, 1, 4],
            "C rfdetr built-in COCO mAP only": [1, 4, 1, 5],
        },
        [[30, 20, 10, 40], [40, 30, 0, 30]],
    ),
    "D3 human box spot check": (
        ["label_trust", "owner_time", "delay", "traceability"],
        [40, 30, 20, 10],
        {
            "A contact sheet of 30 images": [4, 4, 4, 4],
            "B no check": [2, 5, 5, 2],
            "C review all 282": [5, 1, 2, 5],
        },
        [[60, 20, 10, 10], [30, 50, 10, 10]],
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
