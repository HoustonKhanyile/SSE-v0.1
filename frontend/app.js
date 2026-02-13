const runButton = document.getElementById("run");
const compareToggleButton = document.getElementById("compare-toggle");
const runCompareButton = document.getElementById("run-compare");
const timelineToggleButton = document.getElementById("timeline-toggle");
const runTimelineButton = document.getElementById("run-timeline");
const timelineAddButton = document.getElementById("timeline-add");
const semanticsToggleButton = document.getElementById("semantics-toggle");
const semanticsRunButton = document.getElementById("semantics-run");
const semanticsAddButton = document.getElementById("semantics-add");
const situationInput = document.getElementById("situation");
const semanticsPanel = document.getElementById("semantics-panel");
const semanticsRowsEl = document.getElementById("semantics-rows");
const profileMentionsEl = document.getElementById("profile-mentions");
const output = document.getElementById("output");
const comparePanel = document.getElementById("compare-panel");
const timelinePanel = document.getElementById("timeline-panel");
const variantSituationInput = document.getElementById("variant-situation");
const timelineRowsEl = document.getElementById("timeline-rows");
const compareOutput = document.getElementById("compare-output");
const timelineOutput = document.getElementById("timeline-output");
const compareDeltaEl = document.getElementById("compare-delta");
const compareBaseOutcomeEl = document.getElementById("compare-base-outcome");
const compareBaseMetaEl = document.getElementById("compare-base-meta");
const compareVariantOutcomeEl = document.getElementById("compare-variant-outcome");
const compareVariantMetaEl = document.getElementById("compare-variant-meta");
const compareAddedEl = document.getElementById("compare-added");
const compareRemovedEl = document.getElementById("compare-removed");
const compareSharedEl = document.getElementById("compare-shared");
const timelineTrendEl = document.getElementById("timeline-trend");
const timelineStepsListEl = document.getElementById("timeline-steps-list");
const timelineInflectionsEl = document.getElementById("timeline-inflections");
const outcomeEl = document.getElementById("outcome");
const explanationEl = document.getElementById("explanation");
const trackSituationButton = document.getElementById("track-situation");
const modeEl = document.getElementById("mode");
const horizonEl = document.getElementById("horizon");
const confidenceEl = document.getElementById("confidence");
const toggle = document.getElementById("toggle");
const sidebar = document.getElementById("sidebar");
const closeButton = document.getElementById("close");
const scrim = document.getElementById("scrim");
const factorsEl = document.getElementById("factors");
const alternativesEl = document.getElementById("alternatives");
const traceEl = document.getElementById("trace");
const metaSourceEl = document.getElementById("meta-source");
const metaTimeEl = document.getElementById("meta-time");
let semanticsState = [];
let lastPredictionPayload = null;
let timelineState = [{ label: "T1", situation: "" }];
const MENTION_RE = /@([A-Za-z0-9_-]+)/g;

function renderTimelineRows() {
  timelineRowsEl.innerHTML = "";
  timelineState.forEach((row, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "timeline-row";

    const labelInput = document.createElement("input");
    labelInput.className = "timeline-label";
    labelInput.type = "text";
    labelInput.value = row.label;
    labelInput.readOnly = true;
    labelInput.setAttribute("aria-readonly", "true");
    labelInput.setAttribute("aria-label", `Checkpoint label ${index + 1}`);

    const situationInputEl = document.createElement("input");
    situationInputEl.className = "timeline-situation";
    situationInputEl.type = "text";
    situationInputEl.value = row.situation;
    situationInputEl.placeholder = "Describe checkpoint situation update...";
    situationInputEl.setAttribute("aria-label", `Checkpoint situation ${index + 1}`);
    situationInputEl.addEventListener("input", (event) => {
      timelineState[index].situation = event.target.value;
    });

    wrapper.appendChild(labelInput);
    wrapper.appendChild(situationInputEl);
    timelineRowsEl.appendChild(wrapper);
  });
}

function renderProfileMentionLinks() {
  const text = situationInput.value || "";
  const tags = Array.from(text.matchAll(MENTION_RE)).map((m) => m[1]);
  const uniqueTags = [...new Set(tags)];

  profileMentionsEl.innerHTML = "";
  if (!uniqueTags.length) {
    return;
  }

  uniqueTags.forEach((tag) => {
    const link = document.createElement("a");
    link.className = "mention-link";
    link.href = `/static/profile.html?tag=${encodeURIComponent(tag)}`;
    link.textContent = `@${tag}`;
    link.title = `Open profile @${tag}`;
    profileMentionsEl.appendChild(link);
  });
}

function renderSemanticsRows() {
  semanticsRowsEl.innerHTML = "";
  semanticsState.forEach((row, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "semantics-row";

    const keyInput = document.createElement("input");
    keyInput.className = "semantics-key";
    keyInput.type = "text";
    keyInput.value = row.key;
    keyInput.setAttribute("aria-label", `Semantic key ${index + 1}`);
    if (!row.removable) {
      keyInput.readOnly = true;
      keyInput.setAttribute("aria-readonly", "true");
      keyInput.setAttribute("title", "Built-in semantic names are read-only");
    }
    keyInput.addEventListener("input", (event) => {
      semanticsState[index].key = event.target.value;
    });

    const valueInput = document.createElement("input");
    valueInput.className = "semantics-value";
    valueInput.type = "text";
    valueInput.value = row.value;
    valueInput.setAttribute("aria-label", `Semantic value ${index + 1}`);
    valueInput.addEventListener("input", (event) => {
      semanticsState[index].value = event.target.value;
    });

    wrapper.appendChild(keyInput);
    wrapper.appendChild(valueInput);
    if (row.removable) {
      const deleteButton = document.createElement("button");
      deleteButton.type = "button";
      deleteButton.className = "semantics-delete";
      deleteButton.textContent = "x";
      deleteButton.setAttribute("aria-label", `Delete semantic row ${index + 1}`);
      deleteButton.addEventListener("click", () => {
        semanticsState.splice(index, 1);
        renderSemanticsRows();
      });
      wrapper.appendChild(deleteButton);
    }
    semanticsRowsEl.appendChild(wrapper);
  });
}

function openSidebar() {
  sidebar.classList.add("open");
  sidebar.setAttribute("aria-hidden", "false");
  sidebar.removeAttribute("inert");
  toggle.setAttribute("aria-expanded", "true");
  scrim.hidden = false;
  closeButton.focus();
}

function closeSidebar() {
  sidebar.classList.remove("open");
  sidebar.setAttribute("aria-hidden", "true");
  sidebar.setAttribute("inert", "");
  toggle.setAttribute("aria-expanded", "false");
  scrim.hidden = true;
  toggle.focus();
}

function renderList(target, items) {
  target.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    target.appendChild(li);
  });
}

function renderFactors(target, factors) {
  target.innerHTML = "";
  factors.forEach((factor, index) => {
    const li = document.createElement("li");
    li.className = "factor-item";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "factor-trigger";
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", `factor-panel-${index}`);

    const title = document.createElement("span");
    title.className = "factor-name";
    title.textContent = factor.name;

    const badge = document.createElement("span");
    badge.className = "factor-category";
    badge.textContent = factor.category;

    button.appendChild(title);
    button.appendChild(badge);

    const panel = document.createElement("div");
    panel.id = `factor-panel-${index}`;
    panel.className = "factor-panel";
    panel.hidden = true;
    panel.textContent = factor.role;

    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", expanded ? "false" : "true");
      panel.hidden = expanded;
    });

    li.appendChild(button);
    li.appendChild(panel);
    target.appendChild(li);
  });
}

function inferMode(text) {
  const lower = text.toLowerCase();
  if (/(government|policy|tax|platform|commuters|businesses)/.test(lower)) {
    return "C";
  }
  if (/(manager|employee|hr|promotion|team|coworker)/.test(lower)) {
    return "B";
  }
  return "A";
}

async function fetchSemantics() {
  const value = situationInput.value.trim();
  if (!value) {
    semanticsState = [];
    renderSemanticsRows();
    return;
  }

  let payload = null;
  try {
    const response = await fetch("/api/semantics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ situation: value }),
    });
    if (response.ok) {
      payload = await response.json();
    }
  } catch (error) {
    payload = null;
  }

  if (!payload) {
    semanticsState = [
      { key: "mode", value: inferMode(value), removable: false },
      { key: "domain", value: "unknown", removable: false },
      { key: "conflict", value: "unknown", removable: false },
      { key: "actors", value: "unknown", removable: false },
      { key: "institutions", value: "unknown", removable: false },
    ];
    renderSemanticsRows();
    return;
  }

  semanticsState = [
    { key: "mode", value: payload.mode || "-", removable: false },
    { key: "domain", value: payload.domain || "-", removable: false },
    { key: "conflict", value: String(payload.conflict), removable: false },
    {
      key: "actors",
      value: (payload.actors || []).length ? payload.actors.join(", ") : "none",
      removable: false,
    },
    {
      key: "institutions",
      value: (payload.institutions || []).length ? payload.institutions.join(", ") : "none",
      removable: false,
    },
  ];
  renderSemanticsRows();
}

async function runSse() {
  const value = situationInput.value.trim();
  if (!value) {
    outcomeEl.textContent = "Add a situation to generate a PredictionResult.";
    explanationEl.textContent = "";
    output.classList.remove("hidden");
    return;
  }

  let payload = null;
  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        situation: value,
        depth: "default",
        alternatives: true,
      }),
    });

    if (response.ok) {
      payload = await response.json();
    }
  } catch (error) {
    payload = null;
  }

  if (!payload) {
    const mode = inferMode(value);
    const modeLabel = `Mode ${mode}`;
    const horizon = mode === "C" ? "weeks" : mode === "B" ? "days" : "hours";
    modeEl.textContent = modeLabel;
    horizonEl.textContent = `Horizon: ${horizon}`;
    confidenceEl.textContent = "Confidence: n/a";
    outcomeEl.textContent = "API unavailable. Start the backend with `python -m sse.api`.";
    explanationEl.textContent = "";
    renderFactors(factorsEl, []);
    renderList(alternativesEl, []);
    traceEl.textContent = "";
    metaSourceEl.textContent = "";
    metaTimeEl.textContent = "";
    lastPredictionPayload = null;
    output.classList.remove("hidden");
    return;
  }

  const modeLabel = `Mode ${payload.mode}`;
  const outcome = payload.predicted_outcome.label;
  const explanation = payload.explanation;
  const confidence = payload.predicted_outcome.confidence;
  const alternatives = (payload.alternatives || []).map((alt) => alt.label);
  const factors = payload.factors || [];
  const trace = payload.trace || "";
  const source = payload.source || "unknown";
  const timestamp = payload.timestamp || "";

  modeEl.textContent = modeLabel;
  horizonEl.textContent = `Horizon: ${payload.horizon}`;
  confidenceEl.textContent = `Confidence: ${confidence}`;
  outcomeEl.textContent = outcome;
  explanationEl.textContent = explanation;

  renderFactors(factorsEl, factors);
  renderList(alternativesEl, alternatives);
  traceEl.textContent = trace;
  metaSourceEl.textContent = `Source: ${source}`;
  metaTimeEl.textContent = timestamp ? `Timestamp: ${timestamp}` : "";
  lastPredictionPayload = payload;
  output.classList.remove("hidden");
}

async function runCompare() {
  const baseSituation = situationInput.value.trim();
  const variantSituation = variantSituationInput.value.trim();

  if (!baseSituation || !variantSituation) {
    compareDeltaEl.textContent = "Delta n/a";
    compareBaseOutcomeEl.textContent = "Provide both base and variant situations.";
    compareBaseMetaEl.textContent = "";
    compareVariantOutcomeEl.textContent = "";
    compareVariantMetaEl.textContent = "";
    compareAddedEl.textContent = "";
    compareRemovedEl.textContent = "";
    compareSharedEl.textContent = "";
    compareOutput.classList.remove("hidden");
    return;
  }

  let payload = null;
  try {
    const response = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        base_situation: baseSituation,
        variant_situation: variantSituation,
        depth: "default",
        alternatives: true,
      }),
    });
    if (response.ok) {
      payload = await response.json();
    }
  } catch (error) {
    payload = null;
  }

  if (!payload || !payload.base || !payload.variant || !payload.comparison) {
    compareDeltaEl.textContent = "Delta n/a";
    compareBaseOutcomeEl.textContent = "Compare unavailable. Check API status.";
    compareBaseMetaEl.textContent = "";
    compareVariantOutcomeEl.textContent = "";
    compareVariantMetaEl.textContent = "";
    compareAddedEl.textContent = "";
    compareRemovedEl.textContent = "";
    compareSharedEl.textContent = "";
    compareOutput.classList.remove("hidden");
    return;
  }

  const base = payload.base;
  const variant = payload.variant;
  const cmp = payload.comparison;

  compareDeltaEl.textContent = `Delta ${cmp.confidence_delta}`;
  compareBaseOutcomeEl.textContent = base.predicted_outcome.label;
  compareBaseMetaEl.textContent = `Mode ${base.mode} | Horizon ${base.horizon} | Confidence ${base.predicted_outcome.confidence}`;
  compareVariantOutcomeEl.textContent = variant.predicted_outcome.label;
  compareVariantMetaEl.textContent = `Mode ${variant.mode} | Horizon ${variant.horizon} | Confidence ${variant.predicted_outcome.confidence}`;
  compareAddedEl.textContent = cmp.added_factors.length ? cmp.added_factors.join("; ") : "none";
  compareRemovedEl.textContent = cmp.removed_factors.length ? cmp.removed_factors.join("; ") : "none";
  compareSharedEl.textContent = cmp.shared_factors.length ? cmp.shared_factors.join("; ") : "none";
  compareOutput.classList.remove("hidden");
}

async function runTimeline() {
  const baseSituation = situationInput.value.trim();
  const checkpoints = timelineState
    .map((row) => ({ label: row.label, situation: (row.situation || "").trim() }))
    .filter((row) => row.situation.length > 0);

  if (!baseSituation || !checkpoints.length) {
    timelineTrendEl.textContent = "Trend n/a";
    timelineStepsListEl.innerHTML = "<p class='trace'>Provide base situation and at least one checkpoint.</p>";
    timelineInflectionsEl.textContent = "";
    timelineOutput.classList.remove("hidden");
    return;
  }

  let payload = null;
  try {
    const response = await fetch("/api/timeline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        base_situation: baseSituation,
        checkpoints,
        depth: "default",
        alternatives: true,
      }),
    });
    if (response.ok) {
      payload = await response.json();
    }
  } catch (error) {
    payload = null;
  }

  if (!payload || !payload.steps) {
    timelineTrendEl.textContent = "Trend n/a";
    timelineStepsListEl.innerHTML = "<p class='trace'>Timeline unavailable. Check API status.</p>";
    timelineInflectionsEl.textContent = "";
    timelineOutput.classList.remove("hidden");
    return;
  }

  timelineTrendEl.textContent = `Trend ${payload.confidence_trend.join(" -> ")}`;
  timelineStepsListEl.innerHTML = "";
  payload.steps.forEach((step) => {
    const card = document.createElement("article");
    card.className = "compare-card";
    const pred = step.prediction;
    const delta = step.delta;
    const deltaText = delta
      ? `Delta ${delta.confidence_delta}; outcome_changed=${delta.outcome_changed}; mode_changed=${delta.mode_changed}`
      : "Baseline step";

    card.innerHTML = `
      <h3>${step.label}</h3>
      <p class="trace">${step.situation}</p>
      <p class="explanation">${pred.predicted_outcome.label}</p>
      <p class="trace">Mode ${pred.mode} | Horizon ${pred.horizon} | Confidence ${pred.predicted_outcome.confidence}</p>
      <p class="trace">${deltaText}</p>
    `;
    timelineStepsListEl.appendChild(card);
  });

  if (payload.inflections && payload.inflections.length) {
    timelineInflectionsEl.textContent = payload.inflections
      .map((inf) => `${inf.at_step}: ${inf.reason} (${inf.from_outcome} -> ${inf.to_outcome})`)
      .join(" ; ");
  } else {
    timelineInflectionsEl.textContent = "No inflection points detected.";
  }

  timelineOutput.classList.remove("hidden");
}

runButton.addEventListener("click", runSse);
runCompareButton.addEventListener("click", runCompare);
runTimelineButton.addEventListener("click", runTimeline);
semanticsRunButton.addEventListener("click", runSse);
situationInput.addEventListener("input", renderProfileMentionLinks);
compareToggleButton.addEventListener("click", () => {
  const isHidden = comparePanel.classList.contains("hidden");
  if (isHidden) {
    comparePanel.classList.remove("hidden");
    compareToggleButton.setAttribute("aria-expanded", "true");
  } else {
    comparePanel.classList.add("hidden");
    compareToggleButton.setAttribute("aria-expanded", "false");
  }
});
timelineToggleButton.addEventListener("click", () => {
  const isHidden = timelinePanel.classList.contains("hidden");
  if (isHidden) {
    renderTimelineRows();
    timelinePanel.classList.remove("hidden");
    timelineToggleButton.setAttribute("aria-expanded", "true");
  } else {
    timelinePanel.classList.add("hidden");
    timelineToggleButton.setAttribute("aria-expanded", "false");
  }
});
timelineAddButton.addEventListener("click", () => {
  const nextLabel = `T${timelineState.length + 1}`;
  timelineState.push({ label: nextLabel, situation: "" });
  renderTimelineRows();
});

semanticsToggleButton.addEventListener("click", async () => {
  const isHidden = semanticsPanel.classList.contains("hidden");
  if (isHidden) {
    await fetchSemantics();
    semanticsPanel.classList.remove("hidden");
    semanticsToggleButton.setAttribute("aria-expanded", "true");
  } else {
    semanticsPanel.classList.add("hidden");
    semanticsToggleButton.setAttribute("aria-expanded", "false");
  }
});
semanticsAddButton.addEventListener("click", () => {
  semanticsState.push({ key: "user variable", value: "", removable: true });
  renderSemanticsRows();
});
trackSituationButton.addEventListener("click", async () => {
  if (!lastPredictionPayload) {
    outcomeEl.textContent = "Run SSE first before tracking this situation.";
    output.classList.remove("hidden");
    return;
  }

  const situation = situationInput.value.trim();
  if (!situation) {
    outcomeEl.textContent = "Enter a situation before creating tracking.";
    output.classList.remove("hidden");
    return;
  }

  let created = null;
  let statusText = "";
  try {
    const response = await fetch("/api/tracking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        situation,
        prediction: lastPredictionPayload,
      }),
    });
    if (response.ok) {
      created = await response.json();
    } else {
      statusText = `HTTP ${response.status}`;
    }
  } catch (error) {
    created = null;
    statusText = "network error";
  }

  if (!created || created.error) {
    metaSourceEl.textContent = `Tracking: failed to save (${statusText || "unknown error"})`;
    return;
  }
  metaSourceEl.textContent = `Tracking: saved (${created.id})`;
});

toggle.addEventListener("click", (event) => {
  event.preventDefault();
  if (sidebar.classList.contains("open")) {
    closeSidebar();
  } else {
    openSidebar();
  }
});

closeButton.addEventListener("click", closeSidebar);

scrim.addEventListener("click", closeSidebar);

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeSidebar();
  }
});

closeSidebar();
renderProfileMentionLinks();
renderTimelineRows();
