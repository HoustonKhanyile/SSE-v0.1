const featureTabs = [...document.querySelectorAll(".feature-tab")];
const exampleChips = [...document.querySelectorAll(".chip")];
const accuracyButtons = [...document.querySelectorAll(".accuracy-btn")];
const workspaceModeButtons = [...document.querySelectorAll(".mini-menu-btn")];

const elements = {
  situation: document.getElementById("situation"),
  roleTags: document.getElementById("role-tags"),
  urgency: document.getElementById("urgency"),
  intendedMove: document.getElementById("intended-move"),
  intendedTiming: document.getElementById("intended-timing"),
  desiredOutcome: document.getElementById("desired-outcome"),
  forecastWorkspace: document.getElementById("forecast-workspace"),
  generalWorkspace: document.getElementById("general-workspace"),
  moveFields: document.getElementById("move-fields"),
  timingFields: document.getElementById("timing-fields"),
  framingFields: document.getElementById("framing-fields"),
  modeDescription: document.getElementById("mode-description"),
  run: document.getElementById("run"),
  output: document.getElementById("output"),
  summaryTitle: document.getElementById("summary-title"),
  confidenceNote: document.getElementById("confidence-note"),
  metricGrid: document.getElementById("metric-grid"),
  recommendedPosture: document.getElementById("recommended-posture"),
  likelyOutcome: document.getElementById("likely-outcome"),
  reasoningSummary: document.getElementById("reasoning-summary"),
  nextStep: document.getElementById("next-step"),
  warningBanner: document.getElementById("warning-banner"),
  warningLabel: document.getElementById("warning-label"),
  warningText: document.getElementById("warning-text"),
  featureOutput: document.getElementById("feature-output"),
  featureOutputLabel: document.getElementById("feature-output-label"),
  featureOutputBody: document.getElementById("feature-output-body"),
  explanation: document.getElementById("explanation"),
  factors: document.getElementById("factors"),
  alternatives: document.getElementById("alternatives"),
  meta: document.getElementById("meta"),
  reflectionPanel: document.getElementById("reflection-panel"),
  actionTaken: document.getElementById("action-taken"),
  outcomeSummary: document.getElementById("outcome-summary"),
  saveReflection: document.getElementById("save-reflection"),
  reflectionOutput: document.getElementById("reflection-output"),
  queryMenuButton: document.getElementById("query-menu-btn"),
  querySidebar: document.getElementById("query-sidebar"),
  queryClose: document.getElementById("query-close"),
  querySearch: document.getElementById("query-search"),
  queryHistoryList: document.getElementById("query-history-list"),
  queryHistoryEmpty: document.getElementById("query-history-empty"),
  reputationButton: document.getElementById("reputation-btn"),
  reputationSidebar: document.getElementById("reputation-sidebar"),
  reputationClose: document.getElementById("reputation-close"),
  reputationSummary: document.getElementById("reputation-summary"),
  repCount: document.getElementById("rep-count"),
  repAccuracy: document.getElementById("rep-accuracy"),
  reputationDimensions: document.getElementById("reputation-dimensions"),
  scrim: document.getElementById("scrim"),
  generalSituation: document.getElementById("general-situation"),
  generalQueryMode: document.getElementById("general-query-mode"),
  generalHint: document.getElementById("general-hint"),
  generalRun: document.getElementById("general-run"),
  generalCompareToggle: document.getElementById("general-compare-toggle"),
  generalTimelineToggle: document.getElementById("general-timeline-toggle"),
  generalSemanticsToggle: document.getElementById("general-semantics-toggle"),
  generalTrackSituation: document.getElementById("general-track-situation"),
  generalComparePanel: document.getElementById("general-compare-panel"),
  generalTimelinePanel: document.getElementById("general-timeline-panel"),
  generalSemanticsPanel: document.getElementById("general-semantics-panel"),
  generalVariantSituation: document.getElementById("general-variant-situation"),
  generalRunCompare: document.getElementById("general-run-compare"),
  generalTimelineAdd: document.getElementById("general-timeline-add"),
  generalRunTimeline: document.getElementById("general-run-timeline"),
  generalTimelineRows: document.getElementById("general-timeline-rows"),
  generalSemanticsRows: document.getElementById("general-semantics-rows"),
  generalOutput: document.getElementById("general-output"),
  generalOutputTitle: document.getElementById("general-output-title"),
  generalModeLabel: document.getElementById("general-mode-label"),
  generalOutcome: document.getElementById("general-outcome"),
  generalExplanation: document.getElementById("general-explanation"),
  generalHorizon: document.getElementById("general-horizon"),
  generalConfidence: document.getElementById("general-confidence"),
  generalFactors: document.getElementById("general-factors"),
  generalAlternatives: document.getElementById("general-alternatives"),
  generalTrace: document.getElementById("general-trace"),
  generalBreakdown: document.getElementById("general-breakdown"),
  generalBreakdownBody: document.getElementById("general-breakdown-body"),
  generalCompareOutput: document.getElementById("general-compare-output"),
  generalCompareDelta: document.getElementById("general-compare-delta"),
  generalCompareBase: document.getElementById("general-compare-base"),
  generalCompareVariant: document.getElementById("general-compare-variant"),
  generalCompareFactors: document.getElementById("general-compare-factors"),
  generalTimelineOutput: document.getElementById("general-timeline-output"),
  generalTimelineTrend: document.getElementById("general-timeline-trend"),
  generalTimelineSteps: document.getElementById("general-timeline-steps"),
  generalTimelineInflections: document.getElementById("general-timeline-inflections"),
};

const featureConfig = {
  situation_check: {
    description: "Fast forecast for a described scenario.",
    button: "Check SSE",
  },
  move_evaluator: {
    description: "Test a proposed move or message before you send it.",
    button: "Evaluate Move",
  },
  timing_checker: {
    description: "Assess whether you should act now, wait, or prepare further.",
    button: "Check Timing",
  },
  framing_optimizer: {
    description: "Find the framing, tone, and posture most likely to land well.",
    button: "Optimize Framing",
  },
};

let currentFeature = "situation_check";
let currentAccuracy = "accurate";
let lastSavedQueryId = "";
let lastPrediction = null;
let workspaceMode = "forecast";
let timelineState = [{ label: "T1", situation: "" }];
let lastGeneralPrediction = null;

function setFeature(feature) {
  currentFeature = feature;
  featureTabs.forEach((button) => {
    button.classList.toggle("active", button.dataset.feature === feature);
  });
  elements.modeDescription.textContent = featureConfig[feature].description;
  elements.run.textContent = featureConfig[feature].button;
  elements.moveFields.classList.toggle("hidden", !["move_evaluator", "framing_optimizer"].includes(feature));
  elements.timingFields.classList.toggle("hidden", feature === "situation_check" || feature === "move_evaluator");
  elements.framingFields.classList.toggle("hidden", feature !== "framing_optimizer");
}

function setWorkspaceMode(mode) {
  workspaceMode = mode;
  workspaceModeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.workspaceMode === mode);
  });
  const forecastView = mode === "forecast";
  elements.forecastWorkspace.classList.toggle("hidden", !forecastView);
  elements.generalWorkspace.classList.toggle("hidden", forecastView);
  elements.output.classList.toggle("hidden", !forecastView || elements.output.classList.contains("hidden"));
  elements.reflectionPanel.classList.toggle("hidden", !forecastView || !lastPrediction);
  elements.generalOutput.classList.toggle("hidden", forecastView || elements.generalOutput.classList.contains("hidden"));
  elements.generalCompareOutput.classList.toggle("hidden", forecastView || elements.generalCompareOutput.classList.contains("hidden"));
  elements.generalTimelineOutput.classList.toggle("hidden", forecastView || elements.generalTimelineOutput.classList.contains("hidden"));
  elements.modeDescription.textContent = forecastView
    ? featureConfig[currentFeature].description
    : "Original simulator-style SSE controls with general, phenomenon, compare, timeline, and semantics tools.";
}

function selectedRoleTags() {
  return (elements.roleTags.value || "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function renderMetricCard(label, value, tone = "") {
  const card = document.createElement("article");
  card.className = `metric-card ${tone}`.trim();
  card.innerHTML = `<p>${label}</p><strong>${value}</strong>`;
  return card;
}

function renderList(target, items, formatter) {
  target.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.textContent = "No additional items.";
    target.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = formatter(item);
    target.appendChild(li);
  });
}

function openDrawer(which) {
  const isHistory = which === "history";
  elements.querySidebar.classList.toggle("open", isHistory);
  elements.reputationSidebar.classList.toggle("open", !isHistory);
  elements.scrim.classList.remove("hidden");
}

function closeDrawers() {
  elements.querySidebar.classList.remove("open");
  elements.reputationSidebar.classList.remove("open");
  elements.scrim.classList.add("hidden");
}

function renderFeatureSpecific(dailyUse) {
  let label = "";
  let items = [];
  if (currentFeature === "move_evaluator") {
    label = "Move evaluator";
    items = [
      `Likely reception: ${dailyUse.move_evaluator.likely_reception}`,
      `Posture rating: ${dailyUse.move_evaluator.posture_rating}`,
      `Recommended modification: ${dailyUse.move_evaluator.recommended_modifications}`,
    ];
  } else if (currentFeature === "timing_checker") {
    label = "Timing checker";
    items = [
      `Timing quality: ${dailyUse.timing_checker.timing_quality}`,
      `Time-sensitivity note: ${dailyUse.timing_checker.time_sensitivity_note}`,
      `Recommended timing posture: ${dailyUse.timing_checker.recommended_timing_posture}`,
    ];
  } else if (currentFeature === "framing_optimizer") {
    label = "Framing optimizer";
    items = [
      `Suggested framing angle: ${dailyUse.framing_optimizer.suggested_framing_angle}`,
      `Tone recommendation: ${dailyUse.framing_optimizer.tone_recommendation}`,
      `Posture refinement: ${dailyUse.framing_optimizer.posture_refinement}`,
      `Language guidance: ${dailyUse.framing_optimizer.revised_language_guidance}`,
    ];
  }

  if (!items.length) {
    elements.featureOutput.classList.add("hidden");
    return;
  }

  elements.featureOutputLabel.textContent = label;
  elements.featureOutputBody.innerHTML = items.map((item) => `<p>${item}</p>`).join("");
  elements.featureOutput.classList.remove("hidden");
}

function renderForecast(payload) {
  const dailyUse = payload.daily_use;
  const metrics = dailyUse.forecast_metrics;
  elements.summaryTitle.textContent = dailyUse.situation_summary;
  elements.confidenceNote.textContent = dailyUse.confidence_note;
  elements.metricGrid.innerHTML = "";
  elements.metricGrid.appendChild(
    renderMetricCard("Stability", metrics.situation_stability.label),
  );
  elements.metricGrid.appendChild(
    renderMetricCard("Escalation Risk", `${metrics.escalation_risk.score}% (${metrics.escalation_risk.label})`, metrics.escalation_risk.label === "High" ? "danger" : ""),
  );
  elements.metricGrid.appendChild(
    renderMetricCard("Receptiveness", `${metrics.receptiveness_score.score}% (${metrics.receptiveness_score.label})`),
  );
  elements.metricGrid.appendChild(
    renderMetricCard("Trust Fragility", metrics.trust_fragility.label, metrics.trust_fragility.label === "High" ? "danger" : ""),
  );
  elements.metricGrid.appendChild(
    renderMetricCard("Pressure Index", `${metrics.pressure_index.score} (${metrics.pressure_index.label})`, metrics.pressure_index.label === "Heavy" ? "danger" : ""),
  );
  elements.metricGrid.appendChild(
    renderMetricCard("Timing Quality", metrics.timing_quality),
  );

  elements.recommendedPosture.textContent = dailyUse.recommended_posture.join(" + ");
  elements.likelyOutcome.textContent = dailyUse.likely_outcome_direction;
  elements.reasoningSummary.textContent = dailyUse.reasoning_summary;
  elements.nextStep.textContent = dailyUse.next_step_suggestion;
  if (dailyUse.warning) {
    elements.warningLabel.textContent = dailyUse.warning.label;
    elements.warningText.textContent = `${dailyUse.warning.explanation} Safer alternative: ${dailyUse.warning.safer_alternative_posture}.`;
    elements.warningBanner.classList.remove("hidden");
  } else {
    elements.warningBanner.classList.add("hidden");
  }

  renderFeatureSpecific(dailyUse);
  elements.explanation.textContent = payload.explanation || "No explanation available.";
  renderList(elements.factors, payload.factors || [], (factor) => `${factor.name}: ${factor.role}`);
  renderList(elements.alternatives, payload.alternatives || [], (alt) => `${alt.label} (${alt.confidence})`);
  elements.meta.textContent = `Mode ${payload.mode} | Horizon ${payload.horizon} | Source ${payload.source} | ${payload.timestamp || ""}`;
  elements.output.classList.remove("hidden");
  elements.reflectionPanel.classList.remove("hidden");
}

function renderGeneralSemantics(payload) {
  const rows = [
    `Mode: ${payload.mode || "-"}`,
    `Domain: ${payload.domain || "-"}`,
    `Conflict: ${payload.conflict}`,
    `Actors: ${(payload.actors || []).join(", ") || "none"}`,
    `Institutions: ${(payload.institutions || []).join(", ") || "none"}`,
  ];
  if (payload.query_mode === "phenomenon") {
    rows.push(`Phenomenon tag: ${payload.phenomenon_tag || "missing"}`);
    if (payload.phenomenon?.summary) {
      rows.push(`Phenomenon summary: ${payload.phenomenon.summary}`);
    }
  }
  elements.generalSemanticsRows.innerHTML = rows.map((row) => `<article class="metric-card compact-row"><strong>${row}</strong></article>`).join("");
  elements.generalSemanticsPanel.classList.remove("hidden");
}

function renderGeneralPrediction(payload) {
  lastGeneralPrediction = payload;
  const isPhenomenon = payload.query_mode === "phenomenon";
  elements.generalOutputTitle.textContent = isPhenomenon ? "Breakdown" : "PredictionResult";
  elements.generalModeLabel.textContent = `Mode ${payload.mode} | ${isPhenomenon ? "Phenomenon" : "General"}`;
  elements.generalOutcome.textContent = payload.predicted_outcome?.label || "No outcome";
  elements.generalExplanation.textContent = payload.explanation || "";
  elements.generalHorizon.textContent = payload.horizon || "n/a";
  elements.generalConfidence.textContent = String(payload.predicted_outcome?.confidence ?? "n/a");
  renderList(elements.generalFactors, payload.factors || [], (factor) => `${factor.name}: ${factor.role}`);
  renderList(elements.generalAlternatives, payload.alternatives || [], (alt) => `${alt.label} (${alt.confidence})`);
  elements.generalTrace.textContent = payload.trace || "";
  if (isPhenomenon && payload.phenomenon) {
    elements.generalBreakdownBody.innerHTML = `
      <p>Module: @${payload.phenomenon.module}</p>
      <p>Question: ${payload.phenomenon.query}</p>
      <p>Summary: ${payload.phenomenon.summary}</p>
      <p>Hypotheses: ${(payload.phenomenon.hypotheses || []).join(" | ") || "none"}</p>
    `;
    elements.generalBreakdown.classList.remove("hidden");
  } else {
    elements.generalBreakdown.classList.add("hidden");
    elements.generalBreakdownBody.innerHTML = "";
  }
  elements.generalOutput.classList.remove("hidden");
}

async function trackGeneralSituation() {
  if (!lastGeneralPrediction) {
    return;
  }
  const situation = elements.generalSituation.value.trim();
  if (!situation) {
    return;
  }
  const response = await fetch("/api/tracking", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      situation,
      prediction: lastGeneralPrediction,
    }),
  });
  if (!response.ok) {
    return;
  }
  const created = await response.json();
  elements.generalTrace.textContent = `${lastGeneralPrediction.trace || ""} Tracking: saved (${created.id}).`;
}

function renderTimelineRows() {
  elements.generalTimelineRows.innerHTML = "";
  timelineState.forEach((row, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "timeline-row";
    wrapper.innerHTML = `
      <input class="timeline-label" type="text" value="${row.label}" readonly aria-readonly="true" />
      <input class="timeline-situation" type="text" value="${row.situation}" placeholder="Describe checkpoint situation update..." />
    `;
    wrapper.querySelector(".timeline-situation").addEventListener("input", (event) => {
      timelineState[index].situation = event.target.value;
    });
    elements.generalTimelineRows.appendChild(wrapper);
  });
}

async function saveQuery(payload) {
  const response = await fetch("/api/queries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      situation: elements.situation.value.trim(),
      query_mode: payload.query_mode || "general",
      prediction: payload,
    }),
  });
  if (!response.ok) {
    return;
  }
  const saved = await response.json();
  lastSavedQueryId = saved.id || "";
}

async function runForecast() {
  const situation = elements.situation.value.trim();
  if (!situation) {
    return;
  }

  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      situation,
      query_mode: "general",
      alternatives: true,
      feature_type: currentFeature,
      intended_move: elements.intendedMove ? elements.intendedMove.value.trim() : "",
      intended_timing: elements.intendedTiming ? elements.intendedTiming.value.trim() : "",
      desired_outcome: elements.desiredOutcome ? elements.desiredOutcome.value.trim() : "",
      role_tags: selectedRoleTags(),
      urgency: elements.urgency.value,
    }),
  });

  if (!response.ok) {
    return;
  }
  const payload = await response.json();
  lastPrediction = payload;
  renderForecast(payload);
  await saveQuery(payload);
  await loadHistory();
  await loadReputation();
}

function getGeneralQueryMode() {
  return elements.generalQueryMode.value || "general";
}

function getPhenomenonTag(text) {
  const match = (text || "").match(/@([A-Za-z0-9_-]+)/);
  return match ? match[1].toLowerCase() : "";
}

function updateGeneralHint() {
  elements.generalHint.textContent = getGeneralQueryMode() === "phenomenon"
    ? "Phenomenon mode: use @language, @trend, or @behavior, then ask why or how the pattern exists."
    : "General mode: optional profile tags, for example @city_commuters.";
}

async function runGeneralPrediction() {
  const situation = elements.generalSituation.value.trim();
  if (!situation) {
    return;
  }
  const response = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      situation,
      query_mode: getGeneralQueryMode(),
      depth: "default",
      alternatives: true,
    }),
  });
  if (!response.ok) {
    return;
  }
  renderGeneralPrediction(await response.json());
}

async function runGeneralCompare() {
  const response = await fetch("/api/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      base_situation: elements.generalSituation.value.trim(),
      variant_situation: elements.generalVariantSituation.value.trim(),
      query_mode: getGeneralQueryMode(),
      depth: "default",
      alternatives: true,
    }),
  });
  if (!response.ok) {
    return;
  }
  const payload = await response.json();
  elements.generalCompareDelta.textContent = `Delta ${payload.comparison.confidence_delta}`;
  elements.generalCompareBase.textContent = `${payload.base.predicted_outcome.label} | Mode ${payload.base.mode} | Horizon ${payload.base.horizon}`;
  elements.generalCompareVariant.textContent = `${payload.variant.predicted_outcome.label} | Mode ${payload.variant.mode} | Horizon ${payload.variant.horizon}`;
  elements.generalCompareFactors.textContent = `Added: ${payload.comparison.added_factors.join(", ") || "none"} | Removed: ${payload.comparison.removed_factors.join(", ") || "none"} | Shared: ${payload.comparison.shared_factors.join(", ") || "none"}`;
  elements.generalCompareOutput.classList.remove("hidden");
}

async function runGeneralTimeline() {
  const checkpoints = timelineState
    .map((row) => ({ label: row.label, situation: (row.situation || "").trim() }))
    .filter((row) => row.situation);
  const response = await fetch("/api/timeline", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      base_situation: elements.generalSituation.value.trim(),
      checkpoints,
      query_mode: getGeneralQueryMode(),
      depth: "default",
      alternatives: true,
    }),
  });
  if (!response.ok) {
    return;
  }
  const payload = await response.json();
  elements.generalTimelineTrend.textContent = `Trend ${payload.confidence_trend.join(" -> ")}`;
  elements.generalTimelineSteps.innerHTML = payload.steps
    .map((step) => {
      const delta = step.delta
        ? `Delta ${step.delta.confidence_delta}; outcome_changed=${step.delta.outcome_changed}; mode_changed=${step.delta.mode_changed}`
        : "Baseline step";
      return `
        <article class="insight-block">
          <p class="label">${step.label}</p>
          <p>${step.situation}</p>
          <p>${step.prediction.predicted_outcome.label}</p>
          <p>Mode ${step.prediction.mode} | Horizon ${step.prediction.horizon} | Confidence ${step.prediction.predicted_outcome.confidence}</p>
          <p>${delta}</p>
        </article>
      `;
    })
    .join("");
  elements.generalTimelineInflections.textContent = payload.inflections.length
    ? payload.inflections.map((item) => `${item.at_step}: ${item.reason} (${item.from_outcome} -> ${item.to_outcome})`).join(" ; ")
    : "No inflection points detected.";
  elements.generalTimelineOutput.classList.remove("hidden");
}

async function loadGeneralSemantics() {
  const response = await fetch("/api/semantics", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      situation: elements.generalSituation.value.trim(),
      query_mode: getGeneralQueryMode(),
    }),
  });
  if (!response.ok) {
    return;
  }
  renderGeneralSemantics(await response.json());
}

function renderHistory(items) {
  elements.queryHistoryList.innerHTML = "";
  elements.queryHistoryEmpty.classList.toggle("hidden", items.length > 0);
  items.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "history-item";
    const dailyUse = item.prediction?.daily_use;
    const posture = dailyUse?.recommended_posture?.join(" + ") || "No posture";
    const outcome = dailyUse?.likely_outcome_direction || item.prediction?.predicted_outcome?.label || "No forecast";
    button.innerHTML = `
      <strong>${dailyUse?.situation_summary || item.situation}</strong>
      <span>${posture}</span>
      <small>${outcome}</small>
    `;
    button.addEventListener("click", () => {
      window.location.href = `/static/query.html?id=${encodeURIComponent(item.id)}`;
    });
    const li = document.createElement("li");
    li.appendChild(button);
    elements.queryHistoryList.appendChild(li);
  });
}

async function loadHistory() {
  const query = (elements.querySearch.value || "").trim();
  const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
  const response = await fetch(`/api/queries${suffix}`);
  if (!response.ok) {
    renderHistory([]);
    return;
  }
  renderHistory(await response.json());
}

async function loadReputation() {
  const response = await fetch("/api/reputation");
  if (!response.ok) {
    return;
  }
  const payload = await response.json();
  elements.reputationSummary.textContent = payload.public_summary;
  elements.repCount.textContent = String(payload.cases_reflected);
  elements.repAccuracy.textContent = `${payload.accuracy_rate}%`;
  elements.reputationDimensions.innerHTML = "";
  Object.entries(payload.dimensions || {}).forEach(([key, value]) => {
    const label = key.replaceAll("_", " ");
    elements.reputationDimensions.appendChild(renderMetricCard(label, `${value}`));
  });
}

async function saveReflection() {
  if (!lastSavedQueryId || !lastPrediction) {
    return;
  }
  const response = await fetch(`/api/queries/${encodeURIComponent(lastSavedQueryId)}/reflect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action_taken: elements.actionTaken.value.trim(),
      outcome_summary: elements.outcomeSummary.value.trim(),
      forecast_accuracy: currentAccuracy,
    }),
  });
  if (!response.ok) {
    return;
  }
  const payload = await response.json();
  const reflection = payload.reflection;
  elements.reflectionOutput.innerHTML = `
    <p><strong>Reflective comparison:</strong> ${reflection.reflective_comparison}</p>
    <p><strong>Trust recap:</strong> ${reflection.trust_building_recap}</p>
    <p><strong>Learning insight:</strong> ${reflection.learning_insight}</p>
  `;
  elements.reflectionOutput.classList.remove("hidden");
  await loadHistory();
  await loadReputation();
}

featureTabs.forEach((button) => {
  button.addEventListener("click", () => setFeature(button.dataset.feature));
});

workspaceModeButtons.forEach((button) => {
  button.addEventListener("click", () => setWorkspaceMode(button.dataset.workspaceMode));
});

exampleChips.forEach((button) => {
  button.addEventListener("click", () => {
    elements.situation.value = button.dataset.example || "";
  });
});

accuracyButtons.forEach((button) => {
  button.addEventListener("click", () => {
    currentAccuracy = button.dataset.accuracy;
    accuracyButtons.forEach((candidate) => candidate.classList.toggle("active", candidate === button));
  });
});

elements.run.addEventListener("click", runForecast);
elements.saveReflection.addEventListener("click", saveReflection);
elements.queryMenuButton.addEventListener("click", async () => {
  await loadHistory();
  openDrawer("history");
});
elements.reputationButton.addEventListener("click", async () => {
  await loadReputation();
  openDrawer("reputation");
});
elements.queryClose.addEventListener("click", closeDrawers);
elements.reputationClose.addEventListener("click", closeDrawers);
elements.scrim.addEventListener("click", closeDrawers);
elements.querySearch.addEventListener("input", loadHistory);
elements.generalQueryMode.addEventListener("change", updateGeneralHint);
elements.generalRun.addEventListener("click", runGeneralPrediction);
elements.generalTrackSituation.addEventListener("click", trackGeneralSituation);
elements.generalRunCompare.addEventListener("click", runGeneralCompare);
elements.generalRunTimeline.addEventListener("click", runGeneralTimeline);
elements.generalTimelineAdd.addEventListener("click", () => {
  timelineState.push({ label: `T${timelineState.length + 1}`, situation: "" });
  renderTimelineRows();
});
elements.generalCompareToggle.addEventListener("click", () => {
  elements.generalComparePanel.classList.toggle("hidden");
});
elements.generalTimelineToggle.addEventListener("click", () => {
  elements.generalTimelinePanel.classList.toggle("hidden");
  renderTimelineRows();
});
elements.generalSemanticsToggle.addEventListener("click", async () => {
  const willOpen = elements.generalSemanticsPanel.classList.contains("hidden");
  if (willOpen) {
    await loadGeneralSemantics();
  } else {
    elements.generalSemanticsPanel.classList.add("hidden");
  }
});

setFeature(currentFeature);
setWorkspaceMode(workspaceMode);
updateGeneralHint();
renderTimelineRows();
loadHistory();
loadReputation();
