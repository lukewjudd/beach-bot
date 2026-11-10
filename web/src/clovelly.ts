// Clovelly underwater: the inlet's seabed at 1 m (NSW Marine LiDAR 2018, bot/scripts/build_clovelly_depth.py), and
// how deep the water is over it at each hour of the day as the tide comes and goes. Drag through the day; hover or
// tap for the depth at a spot. Depth = sea level - seabed height. The tide is the forecast's sea level, on mean sea
// level, which sits within about 10 cm of the survey's AHD heights at Sydney. Under it, NSW's aerial photo of the same
// box (Spatial Services' imagery, exported in the grid's own map projection so the two line up), so the concrete and
// rocks are the photo and only the water is coloured.

import { height } from "./units";
import type { SwellHours } from "./types";

interface Grid {
  box: [number, number, number, number]; // west, south, east, north in MGA zone 56 (EPSG:7856), metres
  w: number;
  h: number;
  cell: number;
  z: string; // base64 int16 cm above AHD, -32768 = no reading
  kind: string; // base64 uint8: 0 none, 1 sand, 2 reef or rock
  source: string;
}

const NONE = -32768;
// Depth bands (m) and their colours, shallow to deep
const BANDS: [number, [number, number, number], string][] = [
  [1, [200, 235, 225], "under 1m"],
  [2, [120, 205, 215], "1–2m"],
  [3, [60, 160, 205], "2–3m"],
  [4, [35, 110, 180], "3–4m"],
  [Infinity, [20, 60, 130], "4m+"],
];
const WATER_ALPHA = 150; // of 255: enough to read the depth, and still see the reef in the photo

// The aerial photo for the grid's box, three pixels a metre, straight from Spatial Services (no key)
const photo = (box: Grid["box"], w: number, h: number) =>
  "https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer/export?" +
  new URLSearchParams({
    bbox: box.join(","),
    bboxSR: "7856",
    imageSR: "7856",
    size: `${w * 3},${h * 3}`,
    format: "jpg",
    f: "image",
  });

const decode = (b64: string) => Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));

let grid: {
  w: number;
  h: number;
  cell: number;
  box: Grid["box"];
  z: Int16Array;
  kind: Uint8Array;
  shade: Float32Array;
  source: string;
} | null = null;

async function loadGrid() {
  if (grid) return grid;
  const g: Grid = (await import("./clovelly-depth.json")).default as unknown as Grid;
  const zb = decode(g.z);
  const z = new Int16Array(zb.buffer, zb.byteOffset, zb.byteLength / 2);
  const kind = decode(g.kind);
  // Hillshade from the north-west, so the reef's bumps and ledges show through the depth colours
  const shade = new Float32Array(g.w * g.h).fill(1);
  for (let r = 1; r < g.h - 1; r++)
    for (let c = 1; c < g.w - 1; c++) {
      const i = r * g.w + c;
      const nb = [z[i - 1], z[i + 1], z[i - g.w], z[i + g.w]];
      if (z[i] === NONE || nb.includes(NONE)) continue;
      const dx = (nb[1] - nb[0]) / 200; // cm over 2 m -> m/m
      const dy = (nb[3] - nb[2]) / 200;
      shade[i] = Math.max(0.75, Math.min(1.15, 1 + 0.5 * (dx * -0.7 + dy * -0.7))); // gentle: the photo has the texture
    }
  grid = { w: g.w, h: g.h, cell: g.cell, box: g.box, z, kind, shade, source: g.source };
  return grid;
}

function bandOf(depth: number) {
  return BANDS.find(([top]) => depth < top)!;
}

// The day's hours with a tide reading, for the slider
function dayTides(data: SwellHours, date: string) {
  const t0 = Date.parse(`${data.start}:00Z`);
  const out: { hour: number; tide: number; next: number | null }[] = [];
  data.tide.forEach((v, i) => {
    const t = new Date(t0 + i * 3600_000).toISOString();
    if (v == null || t.slice(0, 10) !== date) return;
    const hour = Number(t.slice(11, 13));
    if (hour >= 5 && hour <= 20) out.push({ hour, tide: v, next: data.tide[i + 1] ?? null });
  });
  return out;
}

const clock = (h: number) => `${((h + 11) % 12) + 1}${h < 12 ? "am" : "pm"}`;

export async function openClovelly(dlg: HTMLDialogElement, data: SwellHours | null | undefined, date: string, startHour: number) {
  const g = await loadGrid();
  const hours = data ? dayTides(data, date) : [];
  const day = new Date(`${date}T00:00:00Z`).toLocaleDateString("en-AU", { weekday: "long", day: "numeric", month: "short", timeZone: "UTC" });
  dlg.innerHTML = `
    <div class="about-head"><h2>Under the water at Clovelly</h2><button type="button" class="link" data-close>Done</button></div>
    <p class="fine">The inlet's seabed at 1m from the 2018 NSW marine LiDAR, with the water over it as the tide comes and goes.
      Drag through ${day}; hover or tap for the depth at a spot.</p>
    <div class="depth-wrap"><img class="depth-photo" alt="" src="${photo(g.box, g.w, g.h)}"><canvas width="${g.w}" height="${g.h}" aria-label="Depth map of Clovelly inlet"></canvas>
      <span class="depth-north" aria-hidden="true">N ↑</span><span class="depth-scale" aria-hidden="true" style="width:${(50 / (g.w * g.cell)) * 100}%">50m</span></div>
    <p class="depth-readout" aria-live="polite"></p>
    ${hours.length ? `<label class="depth-slider"><span class="depth-when"></span><input type="range" min="0" max="${hours.length - 1}" step="1"></label>` : `<p class="fine">No tide forecast for this day: shown at mean sea level.</p>`}
    <div class="depth-legend">${BANDS.map(([, rgb, label]) => `<span><i style="background:rgb(${rgb})"></i>${label}</span>`).join("")}</div>
    <p class="fine">Sand shifts and the survey is from 2018, so the sandy end may have moved; the reef and rock won't have.
      Gaps are where the laser couldn't see the bottom (white water). ${g.source}. Aerial photo © Spatial Services NSW.</p>`;
  const canvas = dlg.querySelector("canvas")!;
  const ctx = canvas.getContext("2d")!;
  const img = ctx.createImageData(g.w, g.h);
  const readout = dlg.querySelector<HTMLElement>(".depth-readout")!;
  const when = dlg.querySelector<HTMLElement>(".depth-when");
  const slider = dlg.querySelector<HTMLInputElement>("input[type=range]");
  let tide = 0;

  const draw = () => {
    for (let i = 0; i < g.w * g.h; i++) {
      const p = i * 4;
      if (g.z[i] === NONE) {
        img.data[p + 3] = 0;
        continue;
      }
      const depth = tide - g.z[i] / 100;
      if (depth <= 0) {
        img.data[p + 3] = 0; // out of the water: the photo
        continue;
      }
      const rgb = bandOf(depth)[1];
      const s = g.shade[i];
      img.data[p] = Math.min(255, rgb[0] * s);
      img.data[p + 1] = Math.min(255, rgb[1] * s);
      img.data[p + 2] = Math.min(255, rgb[2] * s);
      img.data[p + 3] = WATER_ALPHA;
    }
    ctx.putImageData(img, 0, 0);
  };

  const setHour = (k: number) => {
    const hr = hours[k];
    tide = hr ? hr.tide : 0;
    draw();
    if (when && hr) {
      const dir = hr.next == null ? "" : hr.next > hr.tide ? ", rising" : ", falling";
      when.innerHTML = `<b>${clock(hr.hour)}</b> · tide ${height(Math.abs(hr.tide))} ${hr.tide >= 0 ? "above" : "below"} mean sea level${dir}`;
    }
  };

  const at = (e: PointerEvent) => {
    const r = canvas.getBoundingClientRect();
    const c = Math.floor(((e.clientX - r.left) / r.width) * g.w);
    const row = Math.floor(((e.clientY - r.top) / r.height) * g.h);
    if (c < 0 || row < 0 || c >= g.w || row >= g.h) return;
    const i = row * g.w + c;
    if (g.z[i] === NONE) {
      readout.textContent = "No reading here";
      return;
    }
    const depth = tide - g.z[i] / 100;
    const bottom = g.kind[i] === 2 ? "reef or rock" : "sand";
    readout.textContent = depth <= 0 ? `Out of the water (${bottom})` : `${height(depth)} deep, ${bottom}`;
  };
  canvas.addEventListener("pointermove", at);
  canvas.addEventListener("pointerdown", at);

  if (slider) {
    const start = Math.max(0, hours.findIndex((h) => h.hour >= startHour));
    slider.value = String(start);
    slider.addEventListener("input", () => setHour(Number(slider.value)));
    setHour(start);
  } else setHour(0);
  readout.textContent = "Hover or tap the map for the depth there";
  dlg.querySelector("[data-close]")?.addEventListener("click", () => dlg.close());
  dlg.onclick = (e) => {
    if (e.target === dlg) dlg.close(); // a tap on the backdrop
  };
  dlg.showModal();
}
