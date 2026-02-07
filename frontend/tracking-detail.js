const detailEl = document.getElementById("detail");
const voteAccurateBtn = document.getElementById("vote-accurate");
const voteInaccurateBtn = document.getElementById("vote-inaccurate");
const inaccuratePanel = document.getElementById("inaccurate-panel");
const submitInaccurateBtn = document.getElementById("submit-inaccurate");
const actualOutcomeEl = document.getElementById("actual-outcome");
const voteStatusEl = document.getElementById("vote-status");

function itemIdFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id") || "";
}

async function fetchItem(id) {
  try {
    const response = await fetch(`/api/tracking/${encodeURIComponent(id)}`);
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    return null;
  }
  return null;
}

function renderItem(item) {
  if (!item || item.error) {
    detailEl.innerHTML = "<p>Tracking item not found.</p>";
    return;
  }

  const predictionLabel =
    item.prediction && item.prediction.predicted_outcome
      ? item.prediction.predicted_outcome.label
      : "n/a";

  detailEl.innerHTML = `
    <h2>Tracked Situation</h2>
    <p><strong>Situation:</strong> ${item.situation}</p>
    <p><strong>Predicted Outcome:</strong> ${predictionLabel}</p>
    <p><strong>Start Time:</strong> ${item.started_at}</p>
    <p><strong>Expected Time:</strong> ${item.expected_at || "not set"}</p>
    <p><strong>Actual Time:</strong> ${item.actual_at || "not set"}</p>
    <p><strong>Vote:</strong> ${item.vote || "pending"}</p>
    <p><strong>Actual Outcome Notes:</strong> ${item.actual_outcome || "none"}</p>
  `;
}

async function submitVote(id, vote, actualOutcome) {
  let payload = null;
  try {
    const response = await fetch(`/api/tracking/${encodeURIComponent(id)}/vote`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vote, actual_outcome: actualOutcome }),
    });
    if (response.ok) {
      payload = await response.json();
    }
  } catch (error) {
    payload = null;
  }

  if (!payload || payload.error) {
    voteStatusEl.textContent = "Vote failed. Check input and try again.";
    return;
  }

  voteStatusEl.textContent = `Saved vote: ${payload.vote}`;
  renderItem(payload);
  inaccuratePanel.classList.add("hidden");
}

async function init() {
  const id = itemIdFromQuery();
  if (!id) {
    detailEl.innerHTML = "<p>Missing tracking id.</p>";
    return;
  }

  const item = await fetchItem(id);
  renderItem(item);

  voteAccurateBtn.addEventListener("click", () => {
    submitVote(id, "accurate", null);
  });

  voteInaccurateBtn.addEventListener("click", () => {
    inaccuratePanel.classList.remove("hidden");
  });

  submitInaccurateBtn.addEventListener("click", () => {
    submitVote(id, "inaccurate", actualOutcomeEl.value.trim());
  });
}

init();
