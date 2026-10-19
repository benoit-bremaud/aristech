"""MCDA totals and sensitivity checks for ADR-0018 to ADR-0022 (annotation pipeline, issue #95).

Run with any Python 3: ``python docs/decisions/mcda/adr_0018_0022_annotation_pipeline.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

MATRICES = {
    "ADR-0018 annotation tool + label format": (
        ["licence", "pre_annotation", "setup", "format_fit", "longevity"],
        [15, 25, 20, 25, 15],
        {
            "A CVAT + YOLO txt": [5, 4, 2, 5, 5],
            "B Label Studio + COCO JSON": [5, 3, 3, 3, 4],
            "C X-AnyLabeling + YOLO txt": [4, 5, 5, 5, 3],
            "D labelImg + YOLO txt": [5, 0, 5, 4, 0],
        },
        [[15, 15, 15, 25, 30], [30, 20, 15, 20, 15], [15, 35, 10, 25, 15]],
    ),
    "ADR-0019 dataset storage + licence register": (
        ["licence_compliance", "reproducibility", "simplicity", "scale_to_c1"],
        [30, 25, 25, 20],
        {
            "A Committed CSV manifest + register, pixels git-ignored": [5, 4, 5, 3],
            "B DVC with a private remote": [4, 5, 2, 5],
            "C Git LFS in the repository": [0, 5, 3, 2],
        },
        [[20, 25, 15, 40], [30, 40, 15, 15]],
    ),
    "ADR-0020 frozen test-set policy": (
        ["no_leakage", "stability", "field_relevance", "simplicity"],
        [35, 25, 20, 20],
        {
            "A Group-keyed, hash-listed, versioned (test-vN, append-only)": [5, 5, 4, 4],
            "B Random image hold-out": [1, 3, 2, 5],
            "C Whole-source hold-out": [5, 4, 2, 4],
        },
        [[25, 25, 20, 30], [35, 15, 40, 10]],
    ),
    "ADR-0021 public sets": (
        ["licence_certainty", "class_coverage", "entrance_context", "effort"],
        [35, 25, 20, 20],
        {
            "A Roboflow hornet-behavior + Sledevic bees + iNaturalist CC BY/CC0": [5, 5, 3, 2],
            "B Roboflow hornet-behavior + Sledevic bees only": [5, 3, 3, 4],
            "C A + unverified Roboflow sets after licence check": [3, 5, 3, 3],
        },
        [[35, 35, 15, 15], [35, 15, 20, 30], [25, 30, 25, 20]],
    ),
    "ADR-0022 base detector": (
        ["licence", "small_data_accuracy", "hailo_path", "training_effort", "maturity"],
        [30, 25, 20, 15, 10],
        {
            "A RF-DETR Small/Medium (Apache-2.0 code + weights)": [5, 5, 2, 4, 4],
            "B YOLOX-S (Apache-2.0 code, COCO weights)": [4, 3, 5, 3, 3],
            "C RT-DETR (Apache-2.0)": [4, 4, 2, 3, 4],
            "D torchvision Faster R-CNN (BSD-3)": [4, 3, 1, 4, 5],
        },
        [[30, 20, 30, 10, 10], [20, 25, 35, 10, 10], [40, 30, 10, 10, 10]],
    ),
}


def total(scores: list[int], weights: list[int]) -> int:
    """Weighted sum of 0-5 scores, out of 500."""
    return sum(s * w for s, w in zip(scores, weights, strict=True))


def main() -> None:
    """Print every matrix's totals, then each sensitivity scenario."""
    for name, (criteria, weights, options, scenarios) in MATRICES.items():
        assert sum(weights) == 100, name
        assert all(sum(s) == 100 for s in scenarios), name
        print(f"\n{name}  ({', '.join(f'{c} {w}' for c, w in zip(criteria, weights))})")
        for option, scores in sorted(options.items(), key=lambda kv: -total(kv[1], weights)):
            print(f"  {total(scores, weights):3d}  {option}")
        for scenario in scenarios:
            ranked = sorted(options.items(), key=lambda kv: -total(kv[1], scenario))
            line = ", ".join(f"{o.split()[0]} {total(s, scenario)}" for o, s in ranked)
            print(f"  sensitivity {scenario}: {line}")


if __name__ == "__main__":
    main()
