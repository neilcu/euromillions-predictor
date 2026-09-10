#!/usr/bin/env python3
"""EuroMillions number predictor CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.analysis import expected_frequency, main_ball_stats, star_stats, top_numbers
from src.data import DEFAULT_DATA_PATH, load_draws
from src.predictor import Prediction, Strategy, predict


def format_line(prediction: Prediction) -> str:
    main = " ".join(f"{number:02d}" for number in prediction.main)
    stars = " ".join(f"{number:02d}" for number in prediction.stars)
    return f"{main}  |  Stars: {stars}"


def print_stats(draws) -> None:
    main_stats = main_ball_stats(draws)
    star_stat_list = star_stats(draws)

    print(f"\nDataset: {len(draws)} draws")
    print(f"From {draws[0].draw_date} to {draws[-1].draw_date}")
    print(
        "Expected main-ball frequency: "
        f"{expected_frequency(draws, 5, 50):.1f} appearances"
    )
    print(
        "Expected star frequency: "
        f"{expected_frequency(draws, 2, 12):.1f} appearances"
    )

    print("\nTop 10 main balls (most frequent):")
    for number in top_numbers(main_stats, 10, key=lambda item: item.count):
        item = next(stat for stat in main_stats if stat.number == number)
        print(f"  {number:02d}  drawn {item.count:4d} times")

    print("\nTop 5 lucky stars (most frequent):")
    for number in top_numbers(star_stat_list, 5, key=lambda item: item.count):
        item = next(stat for stat in star_stat_list if stat.number == number)
        print(f"  {number:02d}  drawn {item.count:4d} times")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze EuroMillions history and suggest numbers using "
            "frequency-based strategies."
        )
    )
    parser.add_argument(
        "--strategy",
        choices=[strategy.value for strategy in Strategy],
        default=Strategy.BALANCED.value,
        help="Prediction strategy to use",
    )
    parser.add_argument(
        "--lines",
        type=int,
        default=1,
        help="Number of suggested lines to generate",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible balanced/random picks",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show frequency summary before predictions",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Download the latest draw data before predicting",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to local draw CSV",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.refresh:
        from src.data import fetch_data

        fetch_data(args.data)
        print(f"Updated data at {args.data}")

    draws = load_draws(args.data)
    if not draws:
        print("No draw data found.", file=sys.stderr)
        return 1

    if args.stats:
        print_stats(draws)

    strategy = Strategy(args.strategy)
    print(f"\nStrategy: {strategy.value}")
    print("Disclaimer: lottery draws are random. Past results do not affect future draws.\n")

    for index in range(args.lines):
        line_seed = None if args.seed is None else args.seed + index
        prediction = predict(draws, strategy=strategy, seed=line_seed)
        print(f"Line {index + 1}: {format_line(prediction)}")
        if index == 0:
            print(f"  -> {prediction.rationale}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
