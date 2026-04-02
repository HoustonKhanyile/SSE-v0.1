const detailEl = document.getElementById("detail");
const reflectionEl = document.getElementById("reflection");
const deepDiveEl = document.getElementById("deep-dive");

function itemIdFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id") || "";
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function fetchItem(id) {
  const response = await fetch(`/api/queries/${encodeURIComponent(id)}`);
  if (!response.ok) {
    return null;
  }
  return response.json();
}

function metricRow(label, value) {
  return `<div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`;
}

function renderItem(item) {
  if (!item || item.error) {
    detailEl.innerHTML = "<p>Saved forecast not found.</p>";
    return;
  }

  const prediction = item.prediction || {};
  const dailyUse = prediction.daily_use || {};
  const metrics = dailyUse.forecast_metrics || {};
  detailEl.innerHTML = `
    <p class="kicker">Situation summary</p>
    <h2>${escapeHtml(dailyUse.situation_summary || item.situation)}</h2>
    <p class="copy">${escapeHtml(dailyUse.likely_outcome_direction || prediction.predicted_outcome?.label || "")}</p>
    <div class="metrics">
      ${metricRow("Stability", metrics.situation_stability?.label || "n/a")}
      ${metricRow("Escalation Risk", metrics.escalation_risk ? `${metrics.escalation_risk.score}% (${metrics.escalation_risk.label})` : "n/a")}
      ${metricRow("Receptiveness", metrics.receptiveness_score ? `${metrics.receptiveness_score.score}% (${metrics.receptiveness_score.label})` : "n/a")}
      ${metricRow("Trust Fragility", metrics.trust_fragility?.label || "n/a")}
      ${metricRow("Pressure Index", metrics.pressure_index ? `${metrics.pressure_index.score} (${metrics.pressure_index.label})` : "n/a")}
      ${metricRow("Timing Quality", metrics.timing_quality || "n/a")}
    </div>
    <p><strong>Recommended posture:</strong> ${escapeHtml((dailyUse.recommended_posture || []).join(" + "))}</p>
    <p><strong>Why this forecast:</strong> ${escapeHtml(dailyUse.reasoning_summary || prediction.explanation || "")}</p>
    <p><strong>Next step:</strong> ${escapeHtml(dailyUse.next_step_suggestion || "")}</p>
    <p><strong>Saved:</strong> ${escapeHtml(item.created_at || "")}</p>
  `;

  if (item.reflection) {
    reflectionEl.innerHTML = `
      <h2>Outcome reflection</h2>
      <p><strong>Action taken:</strong> ${escapeHtml(item.reflection.action_taken || "")}</p>
      <p><strong>Outcome summary:</strong> ${escapeHtml(item.reflection.outcome_summary || "")}</p>
      <p><strong>Forecast accuracy:</strong> ${escapeHtml(item.reflection.forecast_accuracy || "")}</p>
      <p><strong>Reflective comparison:</strong> ${escapeHtml(item.reflection.reflective_comparison || "")}</p>
      <p><strong>Trust recap:</strong> ${escapeHtml(item.reflection.trust_building_recap || "")}</p>
      <p><strong>Learning insight:</strong> ${escapeHtml(item.reflection.learning_insight || "")}</p>
    `;
    reflectionEl.classList.remove("hidden");
  }

  deepDiveEl.innerHTML = `
    <h2>Deep dive</h2>
    <p><strong>Feature type:</strong> ${escapeHtml(dailyUse.feature_type || "situation_check")}</p>
    <p><strong>Engine explanation:</strong> ${escapeHtml(prediction.explanation || "")}</p>
    <p><strong>Mode / Horizon:</strong> ${escapeHtml(prediction.mode || "n/a")} / ${escapeHtml(prediction.horizon || "n/a")}</p>
    <p><strong>Timestamp:</strong> ${escapeHtml(prediction.timestamp || "")}</p>
    <p><strong>Factors:</strong> ${escapeHtml((prediction.factors || []).map((factor) => factor.name).join(", ") || "none")}</p>
    <p><strong>Alternatives:</strong> ${escapeHtml((prediction.alternatives || []).map((alt) => alt.label).join(" | ") || "none")}</p>
  `;
  deepDiveEl.classList.remove("hidden");
}

async function init() {
  const id = itemIdFromQuery();
  if (!id) {
    detailEl.innerHTML = "<p>Missing query id.</p>";
    return;
  }
  renderItem(await fetchItem(id));
}

init();
