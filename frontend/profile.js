function attributesToText(attrs) {
  return Object.entries(attrs || {})
    .map(([k, v]) => `${k}:${v}`)
    .join("\n");
}

function parseAttributes(text) {
  const attrs = {};
  text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line)
    .forEach((line) => {
      const idx = line.indexOf(":");
      if (idx <= 0) {
        return;
      }
      const k = line.slice(0, idx).trim();
      const v = line.slice(idx + 1).trim();
      if (k && v) {
        attrs[k] = v;
      }
    });
  return attrs;
}

function getTagFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return params.get("tag") || "";
}

async function loadProfile(tag) {
  const res = await fetch(`/api/profiles/${encodeURIComponent(tag)}`);
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.error || `HTTP ${res.status}`);
  }
  return data;
}

async function updateProfile(tag, payload) {
  const res = await fetch(`/api/profiles/${encodeURIComponent(tag)}/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.error || `HTTP ${res.status}`);
  }
  return data;
}

async function init() {
  const status = document.getElementById("status");
  const form = document.getElementById("update-form");
  const tag = getTagFromQuery();
  if (!tag) {
    status.textContent = "Missing profile tag in URL.";
    return;
  }

  try {
    const profile = await loadProfile(tag);
    document.getElementById("name").value = profile.name || "";
    document.getElementById("tag").value = profile.tag || "";
    document.getElementById("profile-type").value = profile.profile_type || "individual";
    document.getElementById("description").value = profile.description || "";
    document.getElementById("attributes").value = attributesToText(profile.attributes || {});
  } catch (error) {
    status.textContent = `Failed to load profile (${error.message}).`;
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = {
      name: document.getElementById("name").value.trim(),
      profile_type: document.getElementById("profile-type").value,
      description: document.getElementById("description").value.trim(),
      attributes: parseAttributes(document.getElementById("attributes").value),
    };

    try {
      const updated = await updateProfile(tag, payload);
      status.textContent = `Profile updated: @${updated.tag}`;
    } catch (error) {
      status.textContent = `Update failed (${error.message}).`;
    }
  });
}

init();
