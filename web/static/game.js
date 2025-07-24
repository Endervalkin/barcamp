async function createPlayer() {
    const name = document.getElementById("playerName").value;
    const res = await fetch("/create_player", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });
    const data = await res.json();
    document.getElementById("output").textContent = JSON.stringify(data.player, null, 2);
}

async function endMonth() {
    const res = await fetch("/end_month", { method: "POST" });
    const data = await res.json();
    document.getElementById("output").textContent = "Resources:\n" + JSON.stringify(data.resources, null, 2);
}

document.addEventListener("DOMContentLoaded", () => {
  registerHexClicks();
});

function registerHexClicks() {
  const hexes = document.querySelectorAll("[data-hex-id]");

  hexes.forEach(hex => {
    hex.addEventListener("click", async (e) => {
      const hexId = hex.dataset.hexId;
      console.log("Hex clicked:", hexId);

      try {
        const response = await fetch("/select_hex", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ hex: hexId })
        });

        const result = await response.json();
        console.log("Server confirmed:", result);
        updateStatus(`Hex ${hexId} selected successfully.`);
      } catch (err) {
        console.error("Hex selection failed:", err);
        updateStatus(`Error selecting hex ${hexId}.`);
      }
    });
  });
}

function updateStatus(message) {
  const statusEl = document.getElementById("status");
  if (statusEl) statusEl.innerText = message;
}

async function handleHexClick(hexId) {
  const response = await fetch("/check_hex", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hex: hexId })
  });

  const result = await response.json();

  if (result.has_settlement) {
    updateStatus(`Hex ${hexId} already has a settlement.`);
    // Later: show settlement details
  } else {
    showBuildMenu(hexId);
  }
}

function showBuildMenu(hexId) {
  const menu = document.createElement("div");
  menu.id = "build-menu";
  menu.style.position = "fixed";
  menu.style.top = "100px";
  menu.style.left = "100px";
  menu.style.background = "#fff";
  menu.style.border = "1px solid #333";
  menu.style.padding = "10px";
  menu.innerHTML = `<h4>Build Settlement</h4>
    <button onclick="chooseSettlement('${hexId}', 'Village Inn')">Village Inn</button>
    <button onclick="chooseSettlement('${hexId}', 'Outpost')">Outpost</button>
    <button onclick="chooseSettlement('${hexId}', 'City')">City</button>
    <button onclick="chooseSettlement('${hexId}', 'Fortress')">Fortress</button>`;

  document.body.appendChild(menu);
}

async function chooseSettlement(hexId, type) {
  const response = await fetch("/build_settlement", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hex: hexId, type })
  });

  const result = await response.json();
  updateStatus(`Built ${type} at ${hexId}`);
  drawSettlement(hexId);
  document.getElementById("build-menu").remove();
}

function drawSettlement(hexId) {
  const hex = document.querySelector(`[data-hex-id="${hexId}"]`);
  if (!hex) return;

  const bbox = hex.getBBox();
  const cx = bbox.x + bbox.width / 2;
  const cy = bbox.y + bbox.height / 2;
  const r = Math.min(bbox.width, bbox.height) / 4;

  const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  circle.setAttribute("cx", cx);
  circle.setAttribute("cy", cy);
  circle.setAttribute("r", r);
  circle.setAttribute("fill", "red");
  circle.setAttribute("data-icon", hexId);

  document.getElementById("hex-overlay").appendChild(circle);
}