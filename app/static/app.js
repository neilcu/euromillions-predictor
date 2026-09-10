const drawCount = document.getElementById("draw-count");
const drawRange = document.getElementById("draw-range");
const topMain = document.getElementById("top-main");
const topStars = document.getElementById("top-stars");
const mainHeatmap = document.getElementById("main-heatmap");
const predictions = document.getElementById("predictions");
const disclaimer = document.getElementById("disclaimer");
const predictForm = document.getElementById("predict-form");
const refreshBtn = document.getElementById("refresh-btn");

function renderLeaderboard(container, items) {
  container.innerHTML = items
    .map(
      (item) =>
        `<li><span>${String(item.number).padStart(2, "0")}</span><span>${item.count} draws</span></li>`
    )
    .join("");
}

const HEAT_STOPS = [
  { pos: 0.0, color: [30, 64, 175] },
  { pos: 0.25, color: [14, 165, 233] },
  { pos: 0.5, color: [99, 102, 241] },
  { pos: 0.75, color: [249, 115, 22] },
  { pos: 1.0, color: [239, 68, 68] },
];

function normalize(value, min, max) {
  if (max === min) {
    return 0.5;
  }
  return (value - min) / (max - min);
}

function interpolateColor(score) {
  const clamped = Math.min(1, Math.max(0, score));
  let lower = HEAT_STOPS[0];
  let upper = HEAT_STOPS[HEAT_STOPS.length - 1];

  for (let index = 0; index < HEAT_STOPS.length - 1; index += 1) {
    if (clamped >= HEAT_STOPS[index].pos && clamped <= HEAT_STOPS[index + 1].pos) {
      lower = HEAT_STOPS[index];
      upper = HEAT_STOPS[index + 1];
      break;
    }
  }

  const span = upper.pos - lower.pos || 1;
  const ratio = (clamped - lower.pos) / span;
  const rgb = lower.color.map((start, index) =>
    Math.round(start + (upper.color[index] - start) * ratio)
  );
  return `rgb(${rgb.join(", ")})`;
}

function heatLabel(score) {
  if (score >= 0.8) return "Very hot";
  if (score >= 0.6) return "Hot";
  if (score >= 0.4) return "Neutral";
  if (score >= 0.2) return "Cool";
  return "Cold";
}

function computeHeatScore(item, bounds) {
  const frequency = normalize(item.count, bounds.minCount, bounds.maxCount);
  const recency = 1 - normalize(item.draws_since_last, bounds.minGap, bounds.maxGap);
  return frequency * 0.55 + recency * 0.45;
}

function heatTextColor(score) {
  return score >= 0.45 ? "#fff8ef" : "#e8f2ff";
}

function renderHeatmap(items) {
  const bounds = {
    minCount: Math.min(...items.map((item) => item.count)),
    maxCount: Math.max(...items.map((item) => item.count)),
    minGap: Math.min(...items.map((item) => item.draws_since_last)),
    maxGap: Math.max(...items.map((item) => item.draws_since_last)),
  };

  mainHeatmap.innerHTML = items
    .map((item) => {
      const score = computeHeatScore(item, bounds);
      const background = interpolateColor(score);
      const label = heatLabel(score);
      const title = [
        `Ball ${String(item.number).padStart(2, "0")}`,
        `${label} (${Math.round(score * 100)}%)`,
        `${item.count} total draws`,
        `${item.draws_since_last} draws since last appearance`,
      ].join(" · ");

      return `<div
        class="heat-cell${score >= 0.8 ? " heat-cell-glow" : ""}"
        style="background:${background};color:${heatTextColor(score)};border-color:${background}"
        title="${title}"
      >${item.number}</div>`;
    })
    .join("");
}

function renderPredictions(data) {
  disclaimer.textContent = data.disclaimer;
  predictions.innerHTML = data.lines
    .map(
      (line) => `
        <article class="prediction-card">
          <div class="prediction-header">
            <span>Line ${line.line}</span>
            <span>${line.strategy}</span>
          </div>
          <div class="ball-row">
            ${line.main.map((n) => `<span class="ball">${String(n).padStart(2, "0")}</span>`).join("")}
            <span class="stars-label">Stars</span>
            ${line.stars.map((n) => `<span class="star">${String(n).padStart(2, "0")}</span>`).join("")}
          </div>
          <p class="panel-note">${line.rationale}</p>
        </article>`
    )
    .join("");
}

async function loadStats() {
  const response = await fetch("/api/stats");
  if (!response.ok) {
    throw new Error("Failed to load stats");
  }
  const stats = await response.json();
  drawCount.textContent = `${stats.total_draws.toLocaleString()} draws`;
  drawRange.textContent = `${stats.first_draw} to ${stats.last_draw}`;
  renderLeaderboard(topMain, stats.top_main);
  renderLeaderboard(topStars, stats.top_stars);
  renderHeatmap(stats.main_frequency);
}

predictForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const strategy = document.getElementById("strategy").value;
  const lines = document.getElementById("lines").value;
  const response = await fetch(`/api/predict?strategy=${strategy}&lines=${lines}`);
  if (!response.ok) {
    predictions.innerHTML = "<p class='placeholder'>Could not generate predictions.</p>";
    return;
  }
  renderPredictions(await response.json());
});

refreshBtn.addEventListener("click", async () => {
  refreshBtn.disabled = true;
  refreshBtn.textContent = "Refreshing…";
  try {
    await fetch("/api/refresh", { method: "POST" });
    await loadStats();
  } finally {
    refreshBtn.disabled = false;
    refreshBtn.textContent = "Refresh data";
  }
});

loadStats().catch(() => {
  drawCount.textContent = "Unavailable";
  drawRange.textContent = "Could not load draw history.";
});
