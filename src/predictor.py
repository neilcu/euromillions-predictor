"""Prediction strategies based on historical draw patterns."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from .analysis import NumberStats, main_ball_stats, star_stats, top_numbers
from .data import Draw, MAIN_MAX, MAIN_MIN, STAR_MAX, STAR_MIN


class Strategy(str, Enum):
    HOT = "hot"
    COLD = "cold"
    DUE = "due"
    BALANCED = "balanced"
    RANDOM = "random"


@dataclass(frozen=True)
class Prediction:
    strategy: Strategy
    main: tuple[int, int, int, int, int]
    stars: tuple[int, int]
    rationale: str


def _pick_unique(numbers: list[int], count: int) -> list[int]:
    chosen: list[int] = []
    for number in numbers:
        if number not in chosen:
            chosen.append(number)
        if len(chosen) == count:
            break
    return sorted(chosen)


def _overdue_score(item: NumberStats, total_draws: int) -> float:
    """How overdue a number is relative to its typical appearance gap."""
    if item.count == 0:
        return float(item.draws_since_last)
    average_gap = total_draws / item.count
    return item.draws_since_last / average_gap


def _weighted_sample(
    stats,
    count: int,
    weight_key,
    rng: random.Random,
) -> list[int]:
    pool = list(stats)
    weights = [max(weight_key(item), 0.01) for item in pool]
    chosen: set[int] = set()
    while len(chosen) < count:
        pick = rng.choices(pool, weights=weights, k=1)[0]
        chosen.add(pick.number)
    return sorted(chosen)


def predict(
    draws: list[Draw],
    strategy: Strategy = Strategy.BALANCED,
    seed: int | None = None,
) -> Prediction:
    """Return a suggested line using the chosen strategy."""
    rng = random.Random(seed)
    main_stats = main_ball_stats(draws)
    star_stat_list = star_stats(draws)

    if strategy == Strategy.HOT:
        main = _pick_unique(
            top_numbers(main_stats, 12, key=lambda item: item.count),
            5,
        )
        stars = _pick_unique(
            top_numbers(star_stat_list, 6, key=lambda item: item.count),
            2,
        )
        rationale = "Picks the most frequently drawn main balls and lucky stars."

    elif strategy == Strategy.COLD:
        main = _pick_unique(
            top_numbers(main_stats, 12, key=lambda item: item.draws_since_last),
            5,
        )
        stars = _pick_unique(
            top_numbers(star_stat_list, 6, key=lambda item: item.draws_since_last),
            2,
        )
        rationale = "Picks numbers that have not appeared for the longest time."

    elif strategy == Strategy.DUE:
        total_draws = len(draws)
        main = _pick_unique(
            top_numbers(
                main_stats,
                12,
                key=lambda item: _overdue_score(item, total_draws),
            ),
            5,
        )
        stars = _pick_unique(
            top_numbers(
                star_stat_list,
                6,
                key=lambda item: _overdue_score(item, total_draws),
            ),
            2,
        )
        rationale = (
            "Picks numbers most overdue compared with how often they usually appear."
        )

    elif strategy == Strategy.RANDOM:
        main = sorted(rng.sample(range(MAIN_MIN, MAIN_MAX + 1), 5))
        stars = sorted(rng.sample(range(STAR_MIN, STAR_MAX + 1), 2))
        rationale = "Pure random selection (useful as a baseline)."

    elif strategy == Strategy.BALANCED:
        main = _weighted_sample(
            main_stats,
            5,
            weight_key=lambda item: item.count + (item.draws_since_last * 0.15),
            rng=rng,
        )
        stars = _weighted_sample(
            star_stat_list,
            2,
            weight_key=lambda item: item.count + (item.draws_since_last * 0.15),
            rng=rng,
        )
        rationale = (
            "Weighted mix of frequently drawn numbers and long-absent numbers."
        )

    else:
        raise ValueError(f"Unsupported strategy: {strategy}")

    while len(main) < 5:
        candidate = rng.randint(MAIN_MIN, MAIN_MAX)
        if candidate not in main:
            main.append(candidate)
    main = sorted(main)

    while len(stars) < 2:
        candidate = rng.randint(STAR_MIN, STAR_MAX)
        if candidate not in stars:
            stars.append(candidate)
    stars = sorted(stars)

    return Prediction(
        strategy=strategy,
        main=tuple(main),
        stars=tuple(stars),
        rationale=rationale,
    )
