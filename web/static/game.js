console.log("✅ game.js loaded");

document.addEventListener('DOMContentLoaded', () => {

  const zoomLayer = document.getElementById('zoomLayer');
  const svgContainer = document.getElementById('svg-container');
  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let isMiddleMouseDown = false;

  // Track mouse position for panning
  let lastMouseX = 0;
  let lastMouseY = 0;

  // Wait for SVG injection


  const observer = new MutationObserver(() => {
    const svg = svgContainer.querySelector('svg');
    const zoomLayer = svg?.querySelector('#zoomLayer');

    if (!zoomLayer) {
      console.warn('🚫 No zoomLayer found in injected SVG.');
      return;
    }

    console.log('🔍 zoomLayer ready');

    // Apply transform
    const updateTransform = () => {
      zoomLayer.setAttribute(
        'transform',
        `translate(${panX}, ${panY}) scale(${zoom})`
      );
    };

    // Mouse wheel zoom
    svg.addEventListener('wheel', e => {
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      zoom = Math.max(0.5, Math.min(zoom + delta, 5)); // clamp zoom
      updateTransform();
      e.preventDefault();
    });

    // Middle mouse drag to pan
    svg.addEventListener('mousedown', e => {
      if (e.button === 1) {
        isMiddleMouseDown = true;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        e.preventDefault();
      }
    });

    svg.addEventListener('mouseup', e => {
      if (e.button === 1) {
        isMiddleMouseDown = false;
        e.preventDefault();
      }
    });

    svg.addEventListener('mousemove', e => {
      if (isMiddleMouseDown) {
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        panX += dx;
        panY += dy;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;
        updateTransform();
        e.preventDefault();
      }
    });

    // Optional: hex click feedback
    const hexes = svg.querySelectorAll('#hexes polygon');
    hexes.forEach(hex => {
      hex.addEventListener('click', () => {
        console.log(`🟨 Clicked hex: ${hex.id}`);
        hex.setAttribute('stroke', 'red');
      });
    });

    console.log(`🔍 Found hex polygons: ${hexes.length}`);
    observer.disconnect(); // Done observing
  });

  observer.observe(svgContainer, { childList: true });
});