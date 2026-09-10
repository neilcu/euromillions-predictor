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

function heatColor(count, max) {
  const ratio = max === 0 ? 0 : count / max;
  const alpha = 0.15 + ratio * 0.75;
  return `rgba(79, 140, 255, ${alpha})`;
}

function renderHeatmap(items) {
  const max = Math.max(...items.map((item) => item.count));
  mainHeatmap.innerHTML = items
    .map(
      (item) =>
        `<div class="heat-cell" style="background:${heatColor(item.count, max)}" title="${item.count} draws">${item.number}</div>`
    )
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
