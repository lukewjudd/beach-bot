// Self-hosted map: a Protomaps PMTiles extract of the eastern suburbs (map/ in the repo, uploaded to the bucket
// by deploy.sh), drawn by Leaflet + protomaps-leaflet (~80KB compressed, vs ~440KB for MapLibre). Tiles are
// read straight out of the one file with byte-range requests.

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { leafletLayer } from "protomaps-leaflet";
import type { Spot } from "./types";

export { windLayer } from "./wind";

// In the public bucket next to scores.json (see deploy.sh for why not GitHub Pages)
const TILES_URL = import.meta.env.VITE_TILES_URL;
const MAP_BOUNDS = L.latLngBounds([-34.01, 151.17], [-33.83, 151.32]); // must sit inside the extract's bbox
// Covers every spot, so the map can start loading before the scores arrive
const SPOT_BOUNDS = L.latLngBounds([-33.982, 151.2505], [-33.889, 151.284]);

export function createMap(container: HTMLElement): L.Map {
  const map = L.map(container, {
    zoomControl: false,
    scrollWheelZoom: true, // the page fits the screen, so the wheel has nothing else to scroll
    maxBounds: MAP_BOUNDS,
    maxBoundsViscosity: 1,
    minZoom: 11,
    maxZoom: 17,
    zoomSnap: 0.25, // fit the coastline snugly rather than rounding down a whole zoom level
  });
  L.control.zoom({ position: "bottomright" }).addTo(map);
  const flavor = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  const tiles = leafletLayer({
    url: TILES_URL,
    flavor,
    lang: "en",
    maxDataZoom: 14, // the extract stops at z14; deeper zooms reuse those tiles
    attribution:
      '<a href="https://protomaps.com">Protomaps</a> &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
  });
  tiles.addTo(map);
  // Spinner until the first screenful of tiles is drawn
  tiles.once("load", () => container.classList.add("ready"));

  const fit = () => map.fitBounds(SPOT_BOUNDS, { padding: [24, 24], animate: false });
  fit();
  // The container can settle after first paint (fonts, grid); refit once it has its final size
  new ResizeObserver(() => {
    map.invalidateSize();
    fit();
  }).observe(container);
  return map;
}

export function addPin(map: L.Map, spot: Spot, pinClass: string, label: string, popupHtml: string, onClick: () => void) {
  // Leaflet positions the outer icon element; styling lives on the inner pin so our CSS can't shift it
  // Kind is shown by the pin's shape (see .marker.pool / .marker.surf); the label sits in its own span so a
  // diamond can turn it back upright
  const icon = L.divIcon({
    className: "",
    html: `<div class="${pinClass}"><span class="n">${label}</span></div>`,
    iconSize: [34, 34], // big enough to tap
    iconAnchor: [17, 17],
    popupAnchor: [0, -16],
  });
  return L.marker([spot.lat, spot.lon], { icon, title: spot.name, keyboard: true })
    .bindPopup(popupHtml, { closeButton: false })
    .on("click", onClick)
    .addTo(map);
}

// The wind trails' on/off switch, in the map's top-right corner
export function windButton(map: L.Map, on: boolean, toggle: () => boolean) {
  const Control = L.Control.extend({
    onAdd() {
      const b = L.DomUtil.create("button", "filter wind-toggle");
      b.type = "button";
      b.textContent = "Wind";
      b.setAttribute("aria-pressed", String(on));
      L.DomEvent.disableClickPropagation(b); // a tap on the button isn't a tap on the map
      L.DomEvent.on(b, "click", () => b.setAttribute("aria-pressed", String(toggle())));
      return b;
    },
  });
  new Control({ position: "topright" }).addTo(map);
}
