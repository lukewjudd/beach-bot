// Self-hosted map: a Protomaps PMTiles extract of the eastern suburbs (map/ in the repo, uploaded to the bucket
// by deploy.sh), drawn by Leaflet + protomaps-leaflet (~80KB compressed, vs ~440KB for MapLibre). Tiles are
// read straight out of the one file with byte-range requests.

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { leafletLayer } from "protomaps-leaflet";
import { ICONS } from "./icons";
import type { Region } from "./regions";
import type { Spot } from "./types";

export { swellLayer } from "./swell";
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
    maxZoom: 19,
    zoomSnap: 0.25, // fit the coastline snugly rather than rounding down a whole zoom level
  });
  L.control.zoom({ position: "bottomright" }).addTo(map);
  map.attributionControl.setPrefix(false); // short enough to stay in its corner on a phone (see .leaflet-control-attribution)
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

// The base map: the plain map, or NSW's aerial photos over it (Spatial Services' public imagery service, no key),
// where spearos read the reef off the dark patches against the sand. Its tiles are {z}/{y}/{x}. Picked from a
// layers button in the top-right corner
export type Basemap = "map" | "aerial";
export function basemapPicker(map: L.Map, initial: Basemap, onPick: (b: Basemap) => void) {
  const aerial = L.tileLayer("https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer/tile/{z}/{y}/{x}", {
    maxNativeZoom: 19,
    maxZoom: 19,
    zIndex: 2, // over the base map, under the wind, swell and pins
    attribution: "&copy; Spatial Services NSW",
  });
  let current = initial;
  const apply = () => {
    if (current === "aerial") aerial.addTo(map);
    else aerial.remove();
    map.getContainer().classList.toggle("aerial", current === "aerial"); // brighter swell and wind lines (style.css)
  };
  const OPTIONS: [Basemap, string][] = [
    ["map", "Map"],
    ["aerial", "Aerial"],
  ];
  const Control = L.Control.extend({
    onAdd() {
      const box = L.DomUtil.create("div", "basemap");
      const btn = L.DomUtil.create("button", "basemap-btn", box);
      btn.type = "button";
      btn.setAttribute("aria-label", "Map style");
      btn.setAttribute("aria-expanded", "false");
      btn.innerHTML = ICONS.layers;
      const menu = L.DomUtil.create("div", "basemap-menu", box);
      menu.setAttribute("role", "radiogroup");
      menu.setAttribute("aria-label", "Map style");
      menu.hidden = true;
      const draw = () => {
        menu.innerHTML = OPTIONS.map(
          ([v, label]) =>
            `<button type="button" role="radio" data-v="${v}" aria-checked="${v === current}">${label}</button>`,
        ).join("");
      };
      const open = (on: boolean) => {
        menu.hidden = !on;
        btn.setAttribute("aria-expanded", String(on));
      };
      draw();
      L.DomEvent.on(btn, "click", () => open(menu.hidden !== false));
      L.DomEvent.on(menu, "click", (e) => {
        const v = (e.target as HTMLElement).closest<HTMLElement>("[data-v]")?.dataset.v as Basemap | undefined;
        if (!v) return;
        current = v;
        apply();
        draw();
        open(false);
        onPick(v);
      });
      map.on("click", () => open(false)); // a tap on the map closes it
      L.DomEvent.disableClickPropagation(box);
      return box;
    },
  });
  new Control({ position: "topright" }).addTo(map);
  apply();
}

// The wind trails' on/off switch, with the zoom buttons in the bottom-left corner
// The map's layer switches: a small pill of icon chips (Wind, Swell) that fill in when on
export function layerSwitches(
  map: L.Map,
  switches: { label: string; icon: keyof typeof ICONS; on: boolean; toggle: () => boolean }[],
) {
  const Control = L.Control.extend({
    onAdd() {
      const row = L.DomUtil.create("div", "layer-switches");
      row.setAttribute("role", "group");
      row.setAttribute("aria-label", "Map layers");
      for (const sw of switches) {
        const b = L.DomUtil.create("button", "layer-chip", row);
        b.type = "button";
        b.setAttribute("aria-pressed", String(sw.on));
        b.innerHTML = `${ICONS[sw.icon]}<span>${sw.label}</span>`;
        L.DomEvent.on(b, "click", () => b.setAttribute("aria-pressed", String(sw.toggle())));
      }
      L.DomEvent.disableClickPropagation(row); // a tap on a chip isn't a tap on the map
      return row;
    },
  });
  new Control({ position: "bottomleft" }).addTo(map);
}
