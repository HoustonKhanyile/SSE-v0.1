const listEl = document.getElementById("list");

async function loadTracking() {
  let items = [];
  try {
    const response = await fetch("/api/tracking");
    if (response.ok) {
      items = await response.json();
    }
  } catch (error) {
    items = [];
  }

  if (!items.length) {
    listEl.innerHTML = '<div class="item"><p>No tracked situations yet.</p></div>';
    return;
  }

  listEl.innerHTML = "";
  items.forEach((item) => {
    const block = document.createElement("article");
    block.className = "item";

    const link = document.createElement("a");
    link.href = `/static/tracking-detail.html?id=${encodeURIComponent(item.id)}`;

    const title = document.createElement("strong");
    title.textContent = item.situation;

    const line = document.createElement("p");
    line.textContent = `Started: ${item.started_at} | Status: ${item.status}`;

    link.appendChild(title);
    link.appendChild(line);
    block.appendChild(link);
    listEl.appendChild(block);
  });
}

loadTracking();
