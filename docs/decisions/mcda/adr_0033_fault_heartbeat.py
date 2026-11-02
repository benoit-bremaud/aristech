"""MCDA totals and weight sensitivity for ADR-0033 (fault and heartbeat pushes)."""

import itertools

STUDIES = {
    "heartbeat period": (
        ["liveness latency", "noise", "battery and data", "simplicity"],
        [35, 35, 15, 15],
        {"A. hourly": [5, 1, 2, 5], "B. every 6 h": [4, 3, 4, 5], "C. daily": [2, 5, 5, 5]},
    ),
    "faults covered": (
        ["coverage", "false alarms", "feasible without the Pi", "simplicity"],
        [40, 20, 20, 20],
        {
            "A. loop error only": [2, 5, 5, 5],
            "B. loop error + live source ended": [4, 5, 5, 4],
            "C. B + disk, temperature, battery": [5, 3, 1, 2],
        },
    ),
    "rate limiting": (
        ["no flood", "no lost fault", "simplicity", "testability"],
        [35, 30, 20, 15],
        {
            "A. none": [1, 5, 5, 5],
            "B. one push per fault kind per cool-down": [5, 4, 4, 5],
            "C. global token bucket": [4, 3, 2, 3],
        },
    ),
}


def total(weights, scores):
    return sum(w * s for w, s in zip(weights, scores, strict=True))


def study(criteria, weights, options):
    for option, scores in options.items():
        print(f"  {option}: {total(weights, scores)}")
    for i, name in enumerate(criteria):
        for delta in (-10, 10):
            shifted = list(weights)
            shifted[i] += delta
            totals = {o: total(shifted, s) for o, s in options.items()}
            print(f"    {name} {delta:+d}: first {max(totals, key=totals.get)}")
    wins = dict.fromkeys(options, 0)
    vectors = 0
    for vector in itertools.product(range(0, 101, 5), repeat=len(weights)):
        if sum(vector) != 100:
            continue
        vectors += 1
        totals = {o: total(vector, s) for o, s in options.items()}
        best = max(totals.values())
        for option, value in totals.items():
            wins[option] += value == best
    print("  first in:", {o: f"{100 * c / vectors:.0f}%" for o, c in wins.items()})


def main():
    for title, (criteria, weights, options) in STUDIES.items():
        print(title)
        study(criteria, weights, options)


if __name__ == "__main__":
    main()
