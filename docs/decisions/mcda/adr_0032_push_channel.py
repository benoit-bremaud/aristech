"""MCDA totals and weight sensitivity for ADR-0032 (attack alert push channel)."""

import itertools

CRITERIA = ["privacy", "reliability", "simplicity", "phone", "cost", "secrets"]
WEIGHTS = [25, 20, 20, 15, 10, 10]
OPTIONS = {
    "A. Telegram bot": [3, 4, 5, 5, 4, 4],
    "B. ntfy self-hosted": [5, 3, 4, 4, 3, 4],
    "C. Email (SMTP)": [3, 3, 3, 2, 4, 3],
}


def total(weights, scores):
    return sum(w * s for w, s in zip(weights, scores, strict=True))


def main():
    for option, scores in OPTIONS.items():
        print(f"{option}: {total(WEIGHTS, scores)}")
    for i, name in enumerate(CRITERIA):
        for delta in (-10, 10):
            weights = list(WEIGHTS)
            weights[i] += delta
            totals = {o: total(weights, s) for o, s in OPTIONS.items()}
            print(f"  {name} {delta:+d}: first {max(totals, key=totals.get)} {totals}")
    wins = dict.fromkeys(OPTIONS, 0)
    vectors = 0
    for vector in itertools.product(range(0, 101, 5), repeat=len(WEIGHTS)):
        if sum(vector) != 100:
            continue
        vectors += 1
        totals = {o: total(vector, s) for o, s in OPTIONS.items()}
        best = max(totals.values())
        for option, value in totals.items():
            wins[option] += value == best
    print("first in:", {o: f"{100 * c / vectors:.0f}%" for o, c in wins.items()}, vectors)


if __name__ == "__main__":
    main()
