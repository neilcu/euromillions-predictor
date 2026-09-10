"""Statistical analysis of EuroMillions draw history."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .data import Draw, MAIN_MAX, MAIN_MIN, STAR_MAX, STAR_MIN


@dataclass(frozen=True)
class NumberStats:
    number: int
    count: int
    draws_since_last: int


def _frequency(draws: list[Draw], pool: range, getter) -> Counter[int]:
    counts: Counter[int] = Counter({number: 0 for number in pool})
    for draw in draws:
        for number in getter(draw):
            counts[number] += 1
    return counts


def _draws_since_last(draws: list[Draw], pool: range, getter) -> dict[int, int]:
    gaps = {number: len(draws) for number in pool}
    for index, draw in enumerate(reversed(draws)):
        for number in getter(draw):
            if gaps[number] == len(draws):
                gaps[number] = index
    return gaps


def main_ball_stats(draws: list[Draw]) -> list[NumberStats]:
    pool = range(MAIN_MIN, MAIN_MAX + 1)
    counts = _frequency(draws, pool, lambda draw: draw.main)
    gaps = _draws_since_last(draws, pool, lambda draw: draw.main)
    return [
        NumberStats(number=number, count=counts[number], draws_since_last=gaps[number])
        for number in pool
    ]


def star_stats(draws: list[Draw]) -> list[NumberStats]:
    pool = range(STAR_MIN, STAR_MAX + 1)
    counts = _frequency(draws, pool, lambda draw: draw.stars)
    gaps = _draws_since_last(draws, pool, lambda draw: draw.stars)
    return [
        NumberStats(number=number, count=counts[number], draws_since_last=gaps[number])
        for number in pool
    ]


def top_numbers(stats: list[NumberStats], count: int, key) -> list[int]:
    ranked = sorted(stats, key=key, reverse=True)
    return [item.number for item in ranked[:count]]


def expected_frequency(draws: list[Draw], picks_per_draw: int, pool_size: int) -> float:
    if not draws:
        return 0.0
    return len(draws) * picks_per_draw / pool_size
