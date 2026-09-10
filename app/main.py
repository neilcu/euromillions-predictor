"""EuroMillions predictor web application."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.analysis import expected_frequency, main_ball_stats, star_stats, top_numbers
from src.data import DEFAULT_DATA_PATH, fetch_data, load_draws
from src.predictor import Strategy, predict

APP_DIR = Path(__file__).resolve().parent
DATA_PATH = DEFAULT_DATA_PATH

app = FastAPI(title="EuroMillions Predictor", version="1.0.0")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


def _get_draws() -> list:
    draws = load_draws(DATA_PATH)
    if not draws:
        raise HTTPException(status_code=503, detail="No draw data available")
    return draws


def _stats_payload(draws: list) -> dict:
    main = main_ball_stats(draws)
    stars = star_stats(draws)
    return {
        "total_draws": len(draws),
        "first_draw": draws[0].draw_date.isoformat(),
        "last_draw": draws[-1].draw_date.isoformat(),
        "expected_main_frequency": round(expected_frequency(draws, 5, 50), 1),
        "expected_star_frequency": round(expected_frequency(draws, 2, 12), 1),
        "top_main": [
            asdict(next(item for item in main if item.number == number))
            for number in top_numbers(main, 10, key=lambda item: item.count)
        ],
        "top_stars": [
            asdict(next(item for item in stars if item.number == number))
            for number in top_numbers(stars, 5, key=lambda item: item.count)
        ],
        "main_frequency": [asdict(item) for item in main],
        "star_frequency": [asdict(item) for item in stars],
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/stats")
async def stats() -> dict:
    return _stats_payload(_get_draws())


@app.post("/api/refresh")
async def refresh() -> dict:
    fetch_data(DATA_PATH)
    draws = _get_draws()
    return {
        "message": "Draw data refreshed",
        "stats": _stats_payload(draws),
    }


@app.get("/api/predict")
async def predict_numbers(
    strategy: Strategy = Query(default=Strategy.BALANCED),
    lines: int = Query(default=3, ge=1, le=10),
    seed: int | None = Query(default=None),
) -> dict:
    draws = _get_draws()
    predictions = []
    for index in range(lines):
        line_seed = None if seed is None else seed + index
        result = predict(draws, strategy=strategy, seed=line_seed)
        predictions.append(
            {
                "line": index + 1,
                "main": list(result.main),
                "stars": list(result.stars),
                "strategy": result.strategy.value,
                "rationale": result.rationale,
            }
        )

    return {
        "strategy": strategy.value,
        "lines": predictions,
        "disclaimer": (
            "Lottery draws are random. Past results do not affect future draws."
        ),
    }
