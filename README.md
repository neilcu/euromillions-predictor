# EuroMillions Predictor

A containerised tutorial project that downloads every historical EuroMillions draw, analyses number frequencies, and suggests the "most likely" next numbers through a simple web UI.

## Disclaimer

Lottery draws are independent random events. **No strategy can genuinely improve your odds of winning.** This project is for learning data analysis and containerised web apps, not gambling advice.

## Features

- Web UI with strategy picker, frequency leaders, and a main-ball heatmap
- REST API (`/api/stats`, `/api/predict`, `/api/refresh`)
- CLI tool for terminal use
- Docker image for local runs or deployment

## Quick start with Docker

```bash
git clone https://github.com/neilcu/euromillions-predictor.git
cd euromillions-predictor
docker compose up --build
```

Open [http://localhost:8080](http://localhost:8080).

Stop the stack:

```bash
docker compose down
```

## Local development (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

CLI usage:

```bash
python predict.py --refresh --stats
python predict.py --strategy hot --lines 5
```

## API examples

```bash
curl http://localhost:8080/api/stats
curl "http://localhost:8080/api/predict?strategy=balanced&lines=3"
curl -X POST http://localhost:8080/api/refresh
```

## Project layout

```
euromillions-predictor/
  app/
    main.py              # FastAPI app
    templates/           # Web UI
    static/              # CSS + JS
  src/
    data.py              # Download and parse draws
    analysis.py          # Frequency calculations
    predictor.py         # Prediction strategies
  data/results.csv       # Cached draw history
  predict.py             # CLI entry point
  Dockerfile
  docker-compose.yml
```

## Strategies

| Strategy   | Idea |
|-----------|------|
| `hot`     | Most frequently drawn numbers |
| `due`     | Numbers most overdue vs their usual appearance gap |
| `cold`    | Numbers absent the longest (raw gap) |
| `balanced`| Weighted mix of hot and overdue numbers |
| `random`  | Pure random baseline |

## Data source

Draw history is downloaded from the open [lottery-archive](https://github.com/daowa89/lottery-archive) project on GitHub.

## Publish to GitHub

```bash
cd euromillions-predictor
git init
git add .
git commit -m "Add containerised EuroMillions predictor web app"
gh repo create euromillions-predictor --public --source=. --push
```
