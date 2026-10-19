"""MCDA totals and sensitivity checks for ADR-0017 (capture-rig hardware).

Run with any Python 3: ``python docs/decisions/mcda/adr_0017_capture_rig_hardware.py``.
Scores are 0-5, weights sum to 100, totals are out of 500.
"""

MATRICES = {
    "board": (
        ["capture", "power", "cost", "m6_path", "supply"],
        [30, 20, 20, 15, 15],
        {
            "A Pi 5 8 GB": [5, 2, 3, 5, 5],
            "B Pi 4 4 GB": [4, 3, 4, 2, 4],
            "C Pi Zero 2 W": [2, 5, 5, 0, 3],
            "D Jetson Orin Nano": [4, 1, 1, 4, 3],
        },
        [[30, 35, 15, 10, 10], [20, 20, 30, 15, 15], [30, 20, 20, 0, 30]],
    ),
    "camera": (
        ["px_on_hornet", "motion_blur", "cost", "fits_head", "low_light"],
        [30, 20, 15, 20, 15],
        {
            "A Camera Module 3": [4, 3, 5, 5, 3],
            "B Camera Module 3 Wide": [2, 3, 5, 5, 3],
            "C HQ + 6 mm": [5, 3, 2, 2, 5],
            "D Global Shutter + 6 mm": [3, 5, 2, 2, 3],
        },
        [[20, 35, 15, 15, 15], [40, 15, 10, 15, 20], [30, 20, 15, 5, 30]],
    ),
    "mics": (
        ["band_fidelity", "one_clock", "cable_run", "cost", "simplicity"],
        [30, 30, 15, 10, 15],
        {
            "A 2x ICS-43434 one I2S bus": [4, 5, 3, 5, 4],
            "B 2x SPH0645 one I2S bus": [3, 5, 3, 5, 4],
            "C USB audio + 2 analog mics": [4, 2, 5, 3, 3],
        },
        [[30, 15, 30, 10, 15], [40, 20, 15, 10, 15]],
    ),
    "storage": (
        ["endurance", "capacity", "power", "cost", "simplicity"],
        [30, 25, 15, 15, 15],
        {
            "A microSD HE 256 GB": [2, 1, 5, 5, 5],
            "B USB 3 SSD 1 TB": [4, 5, 3, 3, 4],
            "C NVMe HAT 1 TB": [5, 5, 3, 3, 3],
        },
        [[20, 25, 15, 15, 25], [40, 25, 15, 10, 10]],
    ),
}


def total(scores: list[int], weights: list[int]) -> int:
    """Weighted sum of 0-5 scores, out of 500."""
    return sum(s * w for s, w in zip(scores, weights, strict=True))


def main() -> None:
    """Print every matrix's totals, then each sensitivity scenario."""
    for name, (criteria, weights, options, scenarios) in MATRICES.items():
        print(f"== {name} {criteria} {weights}")
        for option, scores in options.items():
            print(f"  {option}: {total(scores, weights)}")
        for scenario in scenarios:
            assert sum(scenario) == 100, scenario
            results = {o: total(s, scenario) for o, s in options.items()}
            print(f"  sensitivity {scenario}: {results}")


if __name__ == "__main__":
    main()
