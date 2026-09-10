"""Fetch and load EuroMillions historical draw data."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import requests

DATA_URL = (
    "https://raw.githubusercontent.com/daowa89/lottery-archive/main/"
    "eu/euromillions/results.csv"
)
DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "results.csv"

MAIN_MIN, MAIN_MAX = 1, 50
STAR_MIN, STAR_MAX = 1, 12


@dataclass(frozen=True)
class Draw:
    draw_date: date
    main: tuple[int, int, int, int, int]
    stars: tuple[int, int]


def fetch_data(dest: Path = DEFAULT_DATA_PATH) -> Path:
    """Download the latest draw history CSV and save it locally."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(DATA_URL, timeout=30)
    response.raise_for_status()
    dest.write_text(response.text, encoding="utf-8")
    return dest


def load_draws(path: Path = DEFAULT_DATA_PATH) -> list[Draw]:
    """Load draws from a local CSV file."""
    if not path.exists():
        fetch_data(path)

    draws: list[Draw] = []
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            draws.append(
                Draw(
                    draw_date=date.fromisoformat(row["date"]),
                    main=(
                        int(row["n1"]),
                        int(row["n2"]),
                        int(row["n3"]),
                        int(row["n4"]),
                        int(row["n5"]),
                    ),
                    stars=(int(row["s1"]), int(row["s2"])),
                )
            )

    draws.sort(key=lambda draw: draw.draw_date)
    return draws
