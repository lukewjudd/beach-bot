// Self-hosted map: a Protomaps PMTiles extract of the eastern suburbs, with fonts and sprites, all in public/map/.
// GitHub Pages serves byte ranges, so MapLibre reads tiles straight out of the one file.

import { layers, namedFlavor } from "@protomaps/basemaps";
import { addProtocol, LngLatBounds, Map as MapLibreMap, Marker, NavigationControl, Popup, setWorkerUrl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import { Protocol } from "pmtiles";
import type { Spot } from "./types";

const MAP_BASE = new URL(`${import.meta.env.BASE_URL}map/`, location.href).href;
const MAP_BOUNDS: [[number, number], [number, number]] = [
  [151.17, -34.01],
  [151.32, -33.83],
]; // must sit inside the extract's bbox

// MapLibre 6 is ESM-only and loads its worker from a separate file; point it at the copy Vite emits
setWorkerUrl(workerUrl);

export function createMap(container: HTMLElement, spots: Spot[]): MapLibreMap {
  addProtocol("pmtiles", new Protocol().tile);
  const flavor = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  const map = new MapLibreMap({
    container,
    style: {
      version: 8,
      // Not built with URL(): it would percent-encode the {fontstack}/{range} placeholders
      glyphs: `${MAP_BASE}fonts/{fontstack}/{range}.pbf`,
      sprite: `${MAP_BASE}sprites/${flavor}`,
      sources: {
        protomaps: {
          type: "vector",
          url: `pmtiles://${MAP_BASE}eastern-suburbs.pmtiles`,
          attribution:
            '<a href="https://protomaps.com">Protomaps</a> &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
        },
      },
      layers: layers("protomaps", namedFlavor(flavor), { lang: "en" }),
    },
    maxBounds: MAP_BOUNDS,
    minZoom: 10,
    maxZoom: 17,
    cooperativeGestures: true, // one-finger scroll moves the page on phones, not the map
    attributionControl: { compact: true },
  });
  map.addControl(new NavigationControl({ showCompass: false }), "bottom-right");

  const bounds = spots.reduce((b, s) => b.extend([s.lon, s.lat]), new LngLatBounds());
  const fit = () => map.fitBounds(bounds, { padding: 32, duration: 0 });
  fit();
  // The container can settle after first paint (fonts, grid); refit once it has its final size
  new ResizeObserver(() => {
    map.resize();
    fit();
  }).observe(container);
  return map;
}

export function addPin(map: MapLibreMap, spot: Spot, pinClass: string, label: string, popupHtml: string, onClick: () => void) {
  // MapLibre positions this outer element with a transform. Styling lives on the inner pin so our CSS
  // (position, borders) can't fight that and make pins drift while zooming.
  const el = document.createElement("div");
  el.title = spot.name;
  el.innerHTML = `<div class="${pinClass}">${label}${spot.kind === "surf" ? '<span class="badge">🏄</span>' : ""}</div>`;
  el.addEventListener("click", onClick);
  return new Marker({ element: el })
    .setLngLat([spot.lon, spot.lat])
    .setPopup(new Popup({ offset: 18, closeButton: false }).setHTML(popupHtml))
    .addTo(map);
}
