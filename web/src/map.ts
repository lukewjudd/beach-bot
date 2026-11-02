// Self-hosted map: a Protomaps PMTiles extract of the eastern suburbs (map/ in the repo, uploaded to the bucket
// by deploy.sh), drawn by Leaflet + protomaps-leaflet (~80KB compressed, vs ~440KB for MapLibre). Tiles are
// read straight out of the one file with byte-range requests.

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { leafletLayer } from "protomaps-leaflet";
import type { Spot } from "./types";

// In the public bucket next to scores.json (see deploy.sh for why not GitHub Pages)
const TILES_URL = import.meta.env.VITE_TILES_URL;
const MAP_BOUNDS = L.latLngBounds([-34.01, 151.17], [-33.83, 151.32]); // must sit inside the extract's bbox
// Covers every spot, so the map can start loading before the scores arrive
const SPOT_BOUNDS = L.latLngBounds([-33.982, 151.2505], [-33.889, 151.284]);

export function createMap(container: HTMLElement): L.Map {
  const map = L.map(container, {
    zoomControl: false,
    scrollWheelZoom: false,
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
  const badge = { surf: "🏄", pool: "🏊", swim: "" }[spot.kind];
  const icon = L.divIcon({
    className: "",
    html: `<div class="${pinClass}">${label}${badge ? `<span class="badge">${badge}</span>` : ""}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -14],
  });
  return L.marker([spot.lat, spot.lon], { icon, title: spot.name, keyboard: true })
    .bindPopup(popupHtml, { closeButton: false })
    .on("click", onClick)
    .addTo(map);
}
