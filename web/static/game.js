console.log("✅ game.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("svg-container").appendChild(svg);
  const svgContainer = document.getElementById("svg-container");
  if (!svgContainer) {
    console.error("🚫 svg-container not found");
    return;
  }

  fetch("static/hex_grid-01.svg")
    .then(res => res.text())
    .then(svgText => {
      const parser = new DOMParser();
      const svgDoc = parser.parseFromString(svgText, "image/svg+xml");
      const svgElement = svgDoc.documentElement;
      svgElement.id = "hex-overlay";
      svgElement.style.position = "absolute";
      svgElement.style.top = "0";
      svgElement.style.left = "0";
      svgElement.style.zIndex = "2";
      document.getElementById("map-container").appendChild(svgElement);
    });

  fetch("/static/map_data.json")
    .then(res => res.json())
    .then(data => {
      renderHexes(data.hexes); // now this will work
    })
    .catch(err => console.error("🚫 Failed to load map_data.json", err));

function axialToPixel(q, r, size) {
  const x = size * Math.sqrt(3) * (q + r / 2);
  const y = size * 1.5 * size * r;
  return { x, y };
}

function createHexPath(cx, cy, size) {
  const svgNS = "http://www.w3.org/2000/svg";
  const path = document.createElementNS(svgNS, "polygon");
  const points = [];

  for (let i = 0; i < 6; i++) {
    const angle = Math.PI / 180 * (60 * i - 30);
    const x = cx + size * Math.cos(angle);
    const y = cy + size * Math.sin(angle);
    points.push(`${x},${y}`);
  }

  path.setAttribute("points", points.join(" "));
  return path;
}

function renderHexes(hexes) {
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", "100%");
  svg.setAttribute("id", "hex-overlay");
  svg.style.position = "absolute";
  svg.style.top = "0";
  svg.style.left = "0";
  svg.style.zIndex = "2";

  hexes.forEach(hex => {
    const { q, r } = hex;
    const { x, y } = axialToPixel(q, r, 30); // hex size = 30px

    const hexPath = createHexPath(x, y, 30);
    hexPath.setAttribute("data-q", q);
    hexPath.setAttribute("data-r", r);
    hexPath.setAttribute("fill", "#ccc");
    hexPath.setAttribute("stroke", "black");
    hexPath.setAttribute("stroke-width", "2");
    hexPath.style.cursor = "pointer";

    hexPath.addEventListener("click", () => {
      buildSettlement(q, r);
    });

    svg.appendChild(hexPath);
  });

  const container = document.getElementById("svg-container");
  container.appendChild(svg);
}

function buildSettlement(q, r) {
  console.log(`🏗️ Building settlement at (${q}, ${r})`);
  const selector = `[data-q="${q}"][data-r="${r}"]`;
  const hex = document.querySelector(selector);
  if (hex) {
    hex.setAttribute("fill", "#88c"); // visually mark settlement
  } else {
    console.warn("🚫 Hex not found for settlement");
  }
}
});
