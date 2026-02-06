const runButton = document.getElementById("run");
const semanticsToggleButton = document.getElementById("semantics-toggle");
const semanticsRunButton = document.getElementById("semantics-run");
const situationInput = document.getElementById("situation");
const semanticsPanel = document.getElementById("semantics-panel");
const semModeEl = document.getElementById("sem-mode");
const semDomainEl = document.getElementById("sem-domain");
const semConflictEl = document.getElementById("sem-conflict");
const semActorsEl = document.getElementById("sem-actors");
const semInstitutionsEl = document.getElementById("sem-institutions");
const output = document.getElementById("output");
const outcomeEl = document.getElementById("outcome");
const explanationEl = document.getElementById("explanation");
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
    semModeEl.textContent = "-";
    semDomainEl.textContent = "-";
    semConflictEl.textContent = "-";
    semActorsEl.textContent = "-";
    semInstitutionsEl.textContent = "-";
    return;
  }

  let payload = null;
  try {
    const response = await fetch("http://127.0.0.1:8000/api/semantics", {
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
    semModeEl.textContent = inferMode(value);
    semDomainEl.textContent = "unknown";
    semConflictEl.textContent = "unknown";
    semActorsEl.textContent = "unknown";
    semInstitutionsEl.textContent = "unknown";
    return;
  }

  semModeEl.textContent = payload.mode || "-";
  semDomainEl.textContent = payload.domain || "-";
  semConflictEl.textContent = String(payload.conflict);
  semActorsEl.textContent = (payload.actors || []).length ? payload.actors.join(", ") : "none";
  semInstitutionsEl.textContent = (payload.institutions || []).length
    ? payload.institutions.join(", ")
    : "none";
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
    const response = await fetch("http://127.0.0.1:8000/api/predict", {
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
  output.classList.remove("hidden");
}

runButton.addEventListener("click", runSse);
semanticsRunButton.addEventListener("click", runSse);

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
