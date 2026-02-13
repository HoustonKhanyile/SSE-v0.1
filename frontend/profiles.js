const form = document.getElementById("profile-form");
const statusEl = document.getElementById("status");
const profilesEl = document.getElementById("profiles");

function parseAttributes(text) {
  const attrs = {};
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  lines.forEach((line) => {
    const idx = line.indexOf(":");
    if (idx <= 0) {
      return;
    }
    const key = line.slice(0, idx).trim();
    const value = line.slice(idx + 1).trim();
    if (key && value) {
      attrs[key] = value;
    }
  });
  return attrs;
}

function renderProfiles(items) {
  profilesEl.innerHTML = "";
  if (!items.length) {
    profilesEl.innerHTML = '<p class="hint">No profiles yet.</p>';
    return;
  }

  items.forEach((item) => {
    const block = document.createElement("article");
    block.className = "profile";
    const attrs = Object.entries(item.attributes || {})
      .map(([k, v]) => `${k}: ${v}`)
      .join("; ");
    const profileUrl = `/static/profile.html?tag=${encodeURIComponent(item.tag)}`;

    block.innerHTML = `
      <strong><a class="profile-link" href="${profileUrl}">${item.name}</a></strong>
      <p><code>@${item.tag}</code> (${item.profile_type})</p>
      <p>${item.description || "No description"}</p>
      <p>${attrs || "No attributes"}</p>
      <p><a class="profile-link" href="${profileUrl}">Open profile</a></p>
    `;
    profilesEl.appendChild(block);
  });
}

async function loadProfiles() {
  let items = [];
  try {
    const response = await fetch("/api/profiles");
    if (response.ok) {
      items = await response.json();
    }
  } catch (error) {
    items = [];
  }
  renderProfiles(items);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    name: document.getElementById("name").value.trim(),
    tag: document.getElementById("tag").value.trim() || null,
    profile_type: document.getElementById("profile-type").value,
    description: document.getElementById("description").value.trim(),
    attributes: parseAttributes(document.getElementById("attributes").value),
  };

  try {
    const response = await fetch("/api/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok || data.error) {
      statusEl.textContent = `Failed to create profile (${data.error || response.status}).`;
      return;
    }

    statusEl.textContent = `Saved profile @${data.tag}`;
    form.reset();
    await loadProfiles();
  } catch (error) {
    statusEl.textContent = "Failed to create profile (network error).";
  }
});

loadProfiles();
