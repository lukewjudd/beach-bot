// Self-hosted map: a Protomaps PMTiles extract of the eastern suburbs (map/ in the repo, uploaded to the bucket
// by deploy.sh), drawn by Leaflet + protomaps-leaflet (~80KB compressed, vs ~440KB for MapLibre). Tiles are
// read straight out of the one file with byte-range requests.

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { leafletLayer } from "protomaps-leaflet";
import { ICONS } from "./icons";
import type { Region } from "./regions";
import type { Spot } from "./types";

export { windLayer } from "./wind";

// In the public bucket next to the scores (see deploy.sh for why not GitHub Pages), one extract per region
const TILES_BASE = import.meta.env.VITE_TILES_BASE;

export function createMap(container: HTMLElement, region: Region): L.Map {
  // The region's first view covers every spot, so the map can start loading before the scores arrive
  const spotBounds = L.latLngBounds(region.fit);
  const map = L.map(container, {
    zoomControl: false,
    scrollWheelZoom: true, // the page fits the screen, so the wheel has nothing else to scroll
    maxBounds: L.latLngBounds(region.bounds), // inside the extract's bbox
    maxBoundsViscosity: 1,
    minZoom: 10, // the northern beaches run 25km: a short map needs ~10.5 to show them all
    maxZoom: 17,
    zoomSnap: 0.25, // fit the coastline snugly rather than rounding down a whole zoom level
  });
  L.control.zoom({ position: "bottomleft" }).addTo(map);
  const flavor = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  const tiles = leafletLayer({
    url: `${TILES_BASE}${region.tiles}.pmtiles`,
    flavor,
    lang: "en",
    maxDataZoom: 14, // the extract stops at z14; deeper zooms reuse those tiles
    attribution:
      '<a href="https://protomaps.com">Protomaps</a> &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
  });
  tiles.addTo(map);
  // Spinner until the first screenful of tiles is drawn
  tiles.once("load", () => container.classList.add("ready"));

  // Zoomed out, the pins sit close together: drop their kind icons so they're just the score
  const compact = () => container.classList.toggle("compact-pins", map.getZoom() < 14);
  map.on("zoomend", compact);

  const fit = () => map.fitBounds(spotBounds, { padding: [24, 24], animate: false });
  fit();
  compact();
  // The container can settle after first paint (fonts, grid); refit once it has its final size
  new ResizeObserver(() => {
    map.invalidateSize();
    fit();
  }).observe(container);
  return map;
}

export function addPin(map: L.Map, spot: Spot, pinClass: string, label: string, popupHtml: string, onClick: () => void) {
  // An icon for the kind of spot and its score, in a pill coloured by the score. Leaflet positions the
  // outer element; styling lives on the inner pin so our CSS can't shift it
  const icon = L.divIcon({
    className: "pin-wrap", // centres the pill, whose width depends on the score, on the anchor
    html: `<div class="${pinClass}">${ICONS[spot.kind]}<span class="n">${label}</span></div>`,
    iconSize: [48, 30],
    iconAnchor: [24, 15],
    popupAnchor: [0, -14],
  });
  return L.marker([spot.lat, spot.lon], { icon, title: spot.name, keyboard: true })
    .bindPopup(popupHtml, { closeButton: false })
    .on("click", onClick)
    .addTo(map);
}

// The wind trails' on/off switch, with the zoom buttons in the bottom-left corner
export function windButton(map: L.Map, on: boolean, toggle: () => boolean) {
  const Control = L.Control.extend({
    onAdd() {
      const b = L.DomUtil.create("button", "wind-switch");
      b.type = "button";
      b.setAttribute("role", "switch");
      b.setAttribute("aria-checked", String(on));
      b.innerHTML = `<span class="track" aria-hidden="true"><span class="knob"></span></span> Wind`;
      L.DomEvent.disableClickPropagation(b); // a tap on the switch isn't a tap on the map
      L.DomEvent.on(b, "click", () => b.setAttribute("aria-checked", String(toggle())));
      return b;
    },
  });
  new Control({ position: "bottomleft" }).addTo(map);
}
