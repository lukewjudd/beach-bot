// Clovelly underwater: the inlet's seabed at 1 m (NSW Marine LiDAR 2018, bot/scripts/build_clovelly_depth.py), and
// how deep the water is over it as the tide comes and goes. Scroll the tide chart through the week; hover or tap the
// map for the depth at a spot. Depth = sea level - seabed height. The tide is the forecast's sea level, on mean sea
// level, which sits within about 10 cm of the survey's AHD heights at Sydney. Under it, NSW's aerial photo of the same
// box (Spatial Services' imagery, exported in the grid's own map projection so the two line up), so the concrete and
// rocks are the photo and only the water is coloured. Depths are always in metres: it's a chart, not a surf report.

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
const metres = (m: number) => `${(Math.round(m * 10) / 10).toFixed(1)}m`;

// The aerial photo for the grid's box, four pixels a metre (the main map's sharpness at its closest zoom), straight
// from Spatial Services (no key)
const PHOTO_PX_PER_M = 4;
const photo = (box: Grid["box"], w: number, h: number) =>
  "https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer/export?" +
  new URLSearchParams({
    bbox: box.join(","),
    bboxSR: "7856",
    imageSR: "7856",
    size: `${w * PHOTO_PX_PER_M},${h * PHOTO_PX_PER_M}`,
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
  shade: Float32Array;
} | null = null;

async function loadGrid() {
  if (grid) return grid;
  const g: Grid = (await import("./clovelly-depth.json")).default as unknown as Grid;
  const zb = decode(g.z);
  const z = new Int16Array(zb.buffer, zb.byteOffset, zb.byteLength / 2);
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
  grid = { w: g.w, h: g.h, cell: g.cell, box: g.box, z, shade };
  return grid;
}

function bandOf(depth: number) {
  return BANDS.find(([top]) => depth < top)!;
}

// ---------------------------------------------------------------- the tide through the week
const PX_PER_HOUR = 22;
const CHART_H = 112;
const DAY_FROM = 5; // the unshaded part of each day: 5am to 8pm
const DAY_TO = 20;

// The forecast's hourly sea level from its start (local time, written as if UTC), up to its last reading
function tideSeries(data: SwellHours) {
  let n = data.tide.length;
  while (n > 0 && data.tide[n - 1] == null) n--;
  const v = data.tide.slice(0, n).map((x, i, a) => x ?? a.slice(0, i).reverse().find((y) => y != null) ?? 0);
  return { t0: Date.parse(`${data.start}:00Z`), v: v as number[] };
}

// Sea level at a fractional hour, smoothed between the hourly readings (Catmull-Rom)
function tideAt(v: number[], h: number) {
  const i = Math.max(0, Math.min(v.length - 1, Math.floor(h)));
  const f = Math.max(0, Math.min(1, h - i));
  const p0 = v[Math.max(0, i - 1)];
  const p1 = v[i];
  const p2 = v[Math.min(v.length - 1, i + 1)];
  const p3 = v[Math.min(v.length - 1, i + 2)];
  return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f);
}

const at = (t0: number, h: number) => new Date(t0 + h * 3600_000);
const clock = (d: Date) => {
  const hh = d.getUTCHours();
  const mm = d.getUTCMinutes();
  return `${((hh + 11) % 12) + 1}${mm ? `:${String(mm).padStart(2, "0")}` : ""}${hh < 12 ? "am" : "pm"}`;
};
const dayName = (d: Date) =>
  d.toLocaleDateString("en-AU", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" }).replace(",", "");

// The chart: the tide curve, night shaded, each high and low marked, a label at noon each day
function tideSvg(t0: number, v: number[]) {
  const hours = v.length - 1;
  const w = hours * PX_PER_HOUR;
  const lo = Math.min(...v) - 0.15;
  const hi = Math.max(...v) + 0.35; // room for the high-tide labels
  const y = (m: number) => CHART_H - 32 - ((m - lo) / (hi - lo)) * (CHART_H - 50); // room below for low-tide and hour labels
  const pts: string[] = [];
  for (let h = 0; h <= hours; h += 0.25) pts.push(`${(h * PX_PER_HOUR).toFixed(1)},${y(tideAt(v, h)).toFixed(1)}`);
  const parts: string[] = [];
  const first = at(t0, 0);
  const startOfDay = -first.getUTCHours();
  for (let d = startOfDay; d < hours; d += 24) {
    // Night: midnight to 5am, and 8pm to midnight
    for (const [a, b] of [
      [d, d + DAY_FROM],
      [d + DAY_TO, d + 24],
    ]) {
      const x0 = Math.max(0, a) * PX_PER_HOUR;
      const x1 = Math.min(hours, b) * PX_PER_HOUR;
      if (x1 > x0) parts.push(`<rect class="tide-night" x="${x0}" y="0" width="${x1 - x0}" height="${CHART_H}"/>`);
    }
    if (d > 0) parts.push(`<line class="tide-midnight" x1="${d * PX_PER_HOUR}" x2="${d * PX_PER_HOUR}" y1="0" y2="${CHART_H}"/>`);
    for (const hr of [6, 12, 18]) {
      const x = (d + hr) * PX_PER_HOUR;
      if (x < 0 || x > w) continue;
      parts.push(`<text class="tide-hour" x="${x}" y="${CHART_H - 3}">${hr === 12 ? "12pm" : hr === 6 ? "6am" : "6pm"}</text>`);
    }
    // The day's name just after its midnight, in the night shading, clear of the tide labels
    const x0 = Math.max(0, d) * PX_PER_HOUR + 4;
    if (x0 < w - 60) parts.push(`<text class="tide-day" x="${x0}" y="13">${dayName(at(t0, Math.max(0, d) + 12))}</text>`);
  }
  // Highs and lows, to the quarter hour
  for (let h = 0.25; h < hours; h += 0.25) {
    const [a, b, c] = [tideAt(v, h - 0.25), tideAt(v, h), tideAt(v, h + 0.25)];
    const high = b > a && b >= c;
    if (!high && !(b < a && b <= c)) continue;
    const x = h * PX_PER_HOUR;
    parts.push(`<circle class="tide-turn" cx="${x}" cy="${y(b)}" r="2.5"/>`);
    parts.push(
      `<text class="tide-turn-label" x="${x}" y="${high ? y(b) - 6 : y(b) + 13}">${high ? "High" : "Low"} ${clock(at(t0, h))}</text>`,
    );
  }
  return `<svg class="tide-chart" width="${w}" height="${CHART_H}" viewBox="0 0 ${w} ${CHART_H}" aria-hidden="true">
    ${parts.join("")}<polyline class="tide-line" points="${pts.join(" ")}"/></svg>`;
}

export async function openClovelly(dlg: HTMLDialogElement, data: SwellHours | null | undefined, date: string, startHour: number) {
  const g = await loadGrid();
  const series = data ? tideSeries(data) : null;
  const hasTide = !!series && series.v.length > 1;
  dlg.innerHTML = `
    <div class="about-head"><h2>Under the water at Clovelly</h2>
      <div class="depth-mode" role="group" aria-label="View"><button type="button" data-v="map" aria-pressed="true">Map</button><button type="button" data-v="3d" aria-pressed="false">3D</button></div>
      <button type="button" class="link" data-close>Done</button></div>
    <div class="depth-wrap"><img class="depth-photo" alt="" crossorigin="anonymous" src="${photo(g.box, g.w, g.h)}"><canvas width="${g.w}" height="${g.h}" aria-label="Depth map of Clovelly inlet"></canvas>
      <span class="depth-north" aria-hidden="true">N ↑</span><span class="depth-scale" aria-hidden="true" style="width:${(50 / (g.w * g.cell)) * 100}%">50m</span></div>
    <div class="depth-3d" hidden></div>
    <p class="fine depth-3d-hint" hidden>Drag to turn, pinch or scroll to zoom, two fingers or right-drag to move. Heights under the water are stretched 2.5×.</p>
    <p class="depth-readout" aria-live="polite"></p>
    ${
      hasTide
        ? `<p class="depth-when"></p>
           <div class="tide-wrap"><div class="tide-scroll" tabindex="0" role="slider" aria-label="Time, on the tide chart"><div class="tide-pad"></div>${tideSvg(series.t0, series.v)}<div class="tide-pad"></div></div><span class="tide-cursor" aria-hidden="true"></span></div>`
        : `<p class="fine">No tide forecast: shown at mean sea level.</p>`
    }
    <div class="depth-legend">${BANDS.map(([, rgb, label]) => `<span><i style="background:rgb(${rgb})"></i>${label}</span>`).join("")}</div>
    <p class="fine">Seabed: NSW Marine LiDAR 2018 (DCCEEW, CC BY 4.0). Photo © Spatial Services NSW.</p>`;
  const canvas = dlg.querySelector("canvas")!;
  const ctx = canvas.getContext("2d")!;
  const img = ctx.createImageData(g.w, g.h);
  const readout = dlg.querySelector<HTMLElement>(".depth-readout")!;
  const when = dlg.querySelector<HTMLElement>(".depth-when");
  const scroller = dlg.querySelector<HTMLElement>(".tide-scroll");
  let tide = 0;
  let lastCell: number | null = null;
  let view3d: { setTide(m: number): void; dispose(): void } | null = null;

  // Map or 3D: the 3D view (and three.js) loads the first time it's picked, and goes when the dialog closes
  const wrap = dlg.querySelector<HTMLElement>(".depth-wrap")!;
  const box3d = dlg.querySelector<HTMLElement>(".depth-3d")!;
  const legend = dlg.querySelector<HTMLElement>(".depth-legend");
  dlg.querySelectorAll<HTMLButtonElement>(".depth-mode button").forEach((b) =>
    b.addEventListener("click", async () => {
      const three = b.dataset.v === "3d";
      dlg.querySelectorAll(".depth-mode button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      wrap.hidden = three;
      box3d.hidden = !three;
      readout.hidden = three;
      dlg.querySelector<HTMLElement>(".depth-3d-hint")!.hidden = !three;
      if (legend) legend.hidden = three;
      if (three && !view3d) {
        const { seabed3d } = await import("./clovelly3d");
        view3d = seabed3d(box3d, g, photo(g.box, g.w, g.h)); // the same photo the map's already loaded
        view3d.setTide(tide);
      }
    }),
  );
  dlg.addEventListener(
    "close",
    () => {
      view3d?.dispose();
      view3d = null;
    },
    { once: true },
  );

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
    view3d?.setTide(tide);
  };

  const describe = (i: number) => {
    if (g.z[i] === NONE) return "No reading here";
    const depth = tide - g.z[i] / 100;
    return depth <= 0 ? "Out of the water" : `${metres(depth)} deep`;
  };
  const pointAt = (e: PointerEvent) => {
    const r = canvas.getBoundingClientRect();
    const c = Math.floor(((e.clientX - r.left) / r.width) * g.w);
    const row = Math.floor(((e.clientY - r.top) / r.height) * g.h);
    if (c < 0 || row < 0 || c >= g.w || row >= g.h) return;
    lastCell = row * g.w + c;
    readout.textContent = describe(lastCell);
  };
  canvas.addEventListener("pointermove", pointAt);
  canvas.addEventListener("pointerdown", pointAt);

  dlg.querySelector("[data-close]")?.addEventListener("click", () => dlg.close());
  dlg.onclick = (e) => {
    if (e.target === dlg) dlg.close(); // a tap on the backdrop
  };
  dlg.showModal();
  readout.textContent = "Hover or tap the map for the depth there";

  if (!hasTide || !scroller || !when) {
    draw();
    return;
  }
  // The time is whatever sits under the centre line: pads half the box wide either side let the chart's ends reach it
  const { t0, v } = series;
  const pads = scroller.querySelectorAll<HTMLElement>(".tide-pad");
  const sizePads = () => pads.forEach((p) => (p.style.width = `${scroller.clientWidth / 2}px`));
  sizePads();
  let frame = 0;
  const update = () => {
    frame = 0;
    const h = Math.max(0, Math.min(v.length - 1, scroller.scrollLeft / PX_PER_HOUR));
    const shown = Math.round(h * 12) / 12; // to 5 minutes
    tide = tideAt(v, shown);
    draw();
    const rising = tideAt(v, shown + 0.1) > tide;
    when.innerHTML = `<b>${dayName(at(t0, shown))} ${clock(at(t0, shown))}</b> · tide ${metres(Math.abs(tide))} ${tide >= 0 ? "above" : "below"} mean sea level, ${rising ? "rising" : "falling"}`;
    scroller.setAttribute("aria-valuetext", when.textContent ?? "");
    if (lastCell != null) readout.textContent = describe(lastCell);
  };
  scroller.addEventListener("scroll", () => (frame ||= requestAnimationFrame(update)));
  // A mouse wheel scrolls the chart sideways; arrow keys step an hour
  scroller.addEventListener(
    "wheel",
    (e) => {
      if (Math.abs(e.deltaY) <= Math.abs(e.deltaX)) return;
      scroller.scrollLeft += e.deltaY;
      e.preventDefault();
    },
    { passive: false },
  );
  // A mouse drags the chart, as a finger does (touch scrolls natively)
  let dragX: number | null = null;
  scroller.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse") return;
    dragX = e.clientX;
    scroller.setPointerCapture(e.pointerId);
    scroller.classList.add("dragging");
  });
  scroller.addEventListener("pointermove", (e) => {
    if (dragX == null) return;
    scroller.scrollLeft -= e.clientX - dragX;
    dragX = e.clientX;
  });
  const endDrag = () => {
    dragX = null;
    scroller.classList.remove("dragging");
  };
  scroller.addEventListener("pointerup", endDrag);
  scroller.addEventListener("pointercancel", endDrag);
  scroller.addEventListener("keydown", (e) => {
    const step = { ArrowLeft: -1, ArrowRight: 1 }[e.key];
    if (!step) return;
    scroller.scrollLeft += step * PX_PER_HOUR;
    e.preventDefault();
  });
  addEventListener("resize", sizePads);
  dlg.addEventListener("close", () => removeEventListener("resize", sizePads), { once: true });
  // Start on the session's hour
  const start = (Date.parse(`${date}T00:00:00Z`) - t0) / 3600_000 + startHour;
  scroller.scrollLeft = Math.max(0, Math.min(v.length - 1, start)) * PX_PER_HOUR;
  update();
}
