const runButton = document.getElementById("run");
const situationInput = document.getElementById("situation");
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

const stub = {
  mode: "B",
  horizon: "days",
  confidence: 0.68,
  outcome:
    "The employee quietly searches for another job while maintaining performance.",
  explanation:
    "This outcome is most likely given the constraints and priors in the situation.",
  factors: [
    "performance review process",
    "job market mobility",
    "career preservation",
    "status sensitivity",
  ],
  alternatives: [
    "The employee confronts management directly, escalating tension.",
    "The employee accepts the decision and increases effort to earn future promotion.",
  ],
  trace:
    "ESS constraints and MCM priors push toward a low-conflict response that preserves future options.",
};

function openSidebar() {
  sidebar.classList.add("open");
  sidebar.setAttribute("aria-hidden", "false");
  scrim.hidden = false;
}

function closeSidebar() {
  sidebar.classList.remove("open");
  sidebar.setAttribute("aria-hidden", "true");
  scrim.hidden = true;
}

function renderList(target, items) {
  target.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
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

function runStub() {
  const value = situationInput.value.trim();
  if (!value) {
    outcomeEl.textContent = "Add a situation to generate a PredictionResult.";
    explanationEl.textContent = "";
    output.classList.remove("hidden");
    return;
  }

  const mode = inferMode(value);
  const modeLabel = `Mode ${mode}`;
  const horizon = mode === "C" ? "weeks" : mode === "B" ? "days" : "hours";
  const outcome = stub.outcome;
  const explanation = `${outcome} ${stub.explanation}`;

  modeEl.textContent = modeLabel;
  horizonEl.textContent = `Horizon: ${horizon}`;
  confidenceEl.textContent = `Confidence: ${stub.confidence}`;
  outcomeEl.textContent = outcome;
  explanationEl.textContent = explanation;

  renderList(factorsEl, stub.factors);
  renderList(alternativesEl, stub.alternatives);
  traceEl.textContent = stub.trace;

  output.classList.remove("hidden");
}

runButton.addEventListener("click", runStub);

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
