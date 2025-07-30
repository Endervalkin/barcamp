console.log("✅ game.js loaded");



document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM ready, registering hex clicks…");
  registerHexClicks();


  
  
  const svgContainer = document.getElementById('svg-container');
  console.log('svg-container innerHTML:', svgContainer.innerHTML);
  const observer = new MutationObserver(() => {
    const svg = svgContainer.querySelector('svg');
    const zoomLayer = svg?.querySelector('#zoomLayer');

    if (zoomLayer) {
      zoomLayer.addEventListener('wheel', e => {
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        zoom = Math.max(0.5, Math.min(zoom + delta, 5));
        zoomLayer.setAttribute('transform', `scale(${zoom})`);
        e.preventDefault();
      });

      const hexes = svg.querySelectorAll('#hexes polygon');
      hexes.forEach(hex => {
        hex.addEventListener('click', () => {
          console.log(`Clicked hex: ${hex.id}`);
          hex.setAttribute('stroke', 'red');
        });
      });

      console.log(`🔍 Found hex polygons: ${hexes.length}`);
      observer.disconnect(); // Done observing
    } else {
      console.warn('No zoomLayer found in injected SVG.');
    }
  });

  observer.observe(svgContainer, { childList: true });
});


function registerHexClicks() {
  const hexes = document.querySelectorAll(".hex");
  console.log("🔍 Found hex polygons:", hexes.length);

  hexes.forEach(hex => {
    hex.addEventListener("click", () => {
      const hexId = hex.dataset.hexId;
      console.log("✏️ Hex clicked:", hexId);
      updateDebug(`Hex clicked: ${hexId}`);
    });
  });
}

function updateDebug(message) {
  const debugBox = document.getElementById("debug-box");
  if (!debugBox) return;
  debugBox.textContent = message;

  // add & remove a CSS class if you defined a pulse animation
  debugBox.classList.add("clicked");
  setTimeout(() => debugBox.classList.remove("clicked"), 300);
}

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

  async function handleHexClick(hexId) {
  updateDebug(`Hex clicked: ${hexId}`);
  // existing logic
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



function updateDebug(message) {
  const debugBox = document.getElementById("debug-box");
  if (debugBox) debugBox.textContent = `Debug: ${message}`;
}

function updateDebug(message) {
  // grab the element each time (or cache it at top of file)
  const debugBox = document.getElementById("debug-box");
  if (!debugBox) return;

  debugBox.textContent = message;

  // optional pulse animation:
  debugBox.classList.add("clicked");
  setTimeout(() => debugBox.classList.remove("clicked"), 300);
}

let zoom = 1, offsetX = 0, offsetY = 0;
const zoomLayer = document.getElementById('zoom-layer');

function updateTransform() {
  zoomLayer.style.transform =
    `translate(${offsetX}px, ${offsetY}px) scale(${zoom})`;
}

const injectedSVG = document.querySelector('#svg-container svg');

if (injectedSVG) {
  injectedSVG.addEventListener('wheel', e => {
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    zoom = Math.max(0.5, Math.min(zoom + delta, 5));
    injectedSVG.style.transform = `scale(${zoom})`;
    e.preventDefault();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const svgContainer = document.getElementById('svg-container');

  const observer = new MutationObserver(() => {
    const svg = svgContainer.querySelector('svg');
    const zoomLayer = svg?.querySelector('#zoomLayer');

    if (zoomLayer) {
      zoomLayer.addEventListener('wheel', e => {
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        zoom = Math.max(0.5, Math.min(zoom + delta, 5));
        zoomLayer.setAttribute('transform', `scale(${zoom})`);
        e.preventDefault();
      });

      const hexes = svg.querySelectorAll('#hexes polygon');
      hexes.forEach(hex => {
        hex.addEventListener('click', () => {
          console.log(`Clicked hex: ${hex.id}`);
          hex.setAttribute('stroke', 'red');
        });
      });

      console.log(`🔍 Found hex polygons: ${hexes.length}`);
      observer.disconnect(); // Done observing
    } else {
      console.warn('No zoomLayer found in injected SVG.');
    }
  });

  observer.observe(svgContainer, { childList: true });
});



// 🔍 Listen for scroll and adjust zoom
document.addEventListener('scroll', () => {
  const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
  offsetY = -scrollTop; // Adjust offset based on scroll position
  updateTransform();
});