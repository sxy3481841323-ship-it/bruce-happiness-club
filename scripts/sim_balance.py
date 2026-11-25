#!/usr/bin/env python3
"""Monte Carlo balance & Meaning-A probability verifier for Bruce Happiness Club."""

import json
import random

CONTENT_PATH = "/Users/alex/.gemini/antigravity/scratch/bruce-happiness-club/data/content.json"


def meaning_a_pick(higher_ranked_count: int, rng: random.Random) -> int:
    """higher_ranked_count = K; returns chosen rank in 1..K with weight = rank."""
    ranks = list(range(1, higher_ranked_count + 1))
    weights = ranks[:]  # weight = rank => #1 lowest prob, #K highest prob
    return rng.choices(ranks, weights=weights, k=1)[0]


def simulate_meaning_a(trials: int = 20000, k: int = 6):
    rng = random.Random(42)
    counts = {r: 0 for r in range(1, k + 1)}
    for _ in range(trials):
        counts[meaning_a_pick(k, rng)] += 1
    probs = {r: counts[r] / trials for r in range(1, k + 1)}
    monotonic = all(probs[r] < probs[r + 1] for r in range(1, k))
    print(f"[Meaning-A Verification] K={k} higher players, {trials} trials:")
    for r in range(1, k + 1):
        expected = r / (k * (k + 1) / 2)
        print(f"  Rank #{r}: observed={probs[r]:.4f}, theory={expected:.4f}")
    assert monotonic, "Meaning-A probabilities are not strictly increasing from top to bottom!"
    print("  -> PASS: Probability strictly increases from rank #1 to rank #K.\n")


def simulate_treats_and_loop(treats: list, trials: int = 10000):
    rng = random.Random(2026)
    print("[Treat Rescue & Video Recovery Simulation]")
    for start_score in (78, 65, 40, 20):
        rescued = 0
        video_needed = 0
        avg_steps = 0
        for _ in range(trials):
            score = start_score
            steps = 0
            while score < 80:
                affordable = [t for t in treats if t["cost"] <= score]
                if not affordable:
                    video_needed += 1
                    score = 80
                    break
                # Pick highest affordable mid-tier or greedy safe tier
                pick = affordable[-1] if len(affordable) <= 2 else affordable[min(len(affordable) - 1, 3)]
                score -= pick["cost"]
                steps += 1
                if rng.random() < pick["prob"]:
                    score = pick["target"]
                    rescued += 1
                    break
            avg_steps += steps
        print(
            f"  Start<{80} at {start_score:2d}: treat_rescue={rescued/trials:.1%}, "
            f"bankrupt_to_video={video_needed/trials:.1%}, avg_buys={avg_steps/trials:.2f}"
        )


def main():
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    simulate_meaning_a(20000, k=6)
    simulate_treats_and_loop(data["treats"], 10000)


if __name__ == "__main__":
    main()
