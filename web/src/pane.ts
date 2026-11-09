// A canvas fixed to the map's viewport but living in one of the map's panes, so it draws under the score pins
// (Leaflet's marker pane is z-index 600) instead of over them. The pane moves as the map pans, so the canvas is
// shifted back each move to stay put on screen; it hides while a zoom animates and shows again when it lands.

import type L from "leaflet";

export function viewportCanvas(map: L.Map, name: string, zIndex: number) {
  const pane = map.getPane(name) ?? map.createPane(name);
  pane.style.zIndex = String(zIndex);
  pane.style.pointerEvents = "none";
  const canvas = document.createElement("canvas");
  canvas.className = `${name}-layer`;
  pane.appendChild(canvas);
  const pin = () => {
    const p = map.containerPointToLayerPoint([0, 0]);
    canvas.style.transform = `translate(${p.x}px, ${p.y}px)`;
  };
  map.on("move", pin);
  map.on("zoomstart", () => (canvas.style.visibility = "hidden"));
  map.on("zoomend", () => {
    pin();
    canvas.style.visibility = "";
  });
  pin();
  return canvas;
}
