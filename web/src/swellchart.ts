// Surf mode's swell chart: the week hour by hour, each wave train offshore (the main swell as a filled area, a
// second swell and the wind chop as lines), arrows for the way the main swell comes from, and the tide underneath.
// Hover or drag along it for a readout; tap to jump to that session. The heights are offshore, the same for the
// whole coast; what reaches each break is on its card. Idea from open-swells (ideas only: it has no licence).

import { height } from "./units";
import type { Session, SwellHours } from "./types";

type Train = [number, number, number] | null; // [height m, from deg, period s]
const KINDS = [
  { key: "swell", name: "Main swell", cls: "t1" },
  { key: "swell2", name: "Second swell", cls: "t2" },
  { key: "chop", name: "Wind chop", cls: "t3" },
] as const;
const COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
const compass = (deg: number) => COMPASS[Math.round((((deg % 360) + 360) % 360) / 22.5) % 16];
const HOUR = 3600_000;

export interface ChartOpts {
  data: SwellHours;
  sessions: Session[]; // the week's sessions, for the selected band and tapping through to one
  selected: Session;
  weekStart: Date; // Monday 00:00 Sydney, as a UTC-midnight date like the rest of the site
  onPick: (s: Session) => void;
  spot?: { id: string; name: string }; // the open surf break: its height at the break goes over the offshore swell
}

// Hour keys are Sydney local time ("2026-11-10T05:00"); like the rest of the site we treat them as UTC dates, so a
// day is just its UTC date and nothing shifts with the viewer's own time zone
const toMs = (key: string) => Date.parse(`${key}:00Z`);
const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

export function renderSwellChart(el: HTMLElement, o: ChartOpts) {
  const t0 = toMs(o.data.start);
  const w0 = o.weekStart.getTime();
  const hours = 7 * 24;
  const at = (i: number) => (t0 - w0) / HOUR + i; // hour index in the week for data index i
  const W = Math.max(300, el.clientWidth);
  const top = 30; // day labels and arrows
  const plotH = 110;
  const tideH = 34;
  const bottom = 16;
  const H = top + plotH + 10 + tideH + bottom;
  const x = (h: number) => (h / hours) * W;

  const series = KINDS.map((k) => (o.data[k.key] as Train[]) ?? []);
  const atBreak = o.spot ? (o.data.breaks?.[o.spot.id] ?? null) : null;
  const inWeek = (i: number) => at(i) >= 0 && at(i) <= hours;
  const max = Math.max(1, ...series.flat().filter(Boolean).map((t) => (t as number[])[0]), ...(atBreak ?? [])) * 1.1;
  const y = (m: number) => top + plotH - (m / max) * plotH;

  // The selected session as a band, and night shaded, so it reads like the day picker above
  const band = (() => {
    const a = (Date.parse(o.selected.start.slice(0, 16) + ":00Z") - w0) / HOUR;
    const b = (Date.parse(o.selected.end.slice(0, 16) + ":00Z") - w0) / HOUR;
    return `<rect class="band" x="${x(a)}" y="${top}" width="${Math.max(2, x(b) - x(a))}" height="${plotH + 10 + tideH}"/>`;
  })();
  let grid = "";
  for (let d = 0; d < 7; d++) {
    const day = new Date(w0 + d * 24 * HOUR);
    const label = `${day.toLocaleDateString("en-AU", { weekday: "short", timeZone: "UTC" })} ${day.getUTCDate()}`;
    grid += `<rect class="night" x="${x(d * 24)}" y="${top}" width="${x(5.5)}" height="${plotH}"/>`;
    grid += `<rect class="night" x="${x(d * 24 + 19.5)}" y="${top}" width="${x(4.5)}" height="${plotH}"/>`;
    grid += `<line class="day" x1="${x(d * 24)}" x2="${x(d * 24)}" y1="${top - 4}" y2="${H - bottom}"/>`;
    grid += `<text class="day-label" x="${x(d * 24 + 12)}" y="11">${label}</text>`;
  }

  // Each train as a path, broken wherever it's missing
  const path = (s: Train[], close: boolean) => {
    let dpath = "";
    let run: [number, number][] = [];
    const flush = () => {
      if (run.length > 1) {
        dpath += `M${run.map(([a, b]) => `${a.toFixed(1)},${b.toFixed(1)}`).join("L")}`;
        if (close) dpath += `L${run[run.length - 1][0].toFixed(1)},${top + plotH}L${run[0][0].toFixed(1)},${top + plotH}Z`;
      }
      run = [];
    };
    s.forEach((t, i) => {
      if (!t || !inWeek(i)) return flush();
      run.push([x(at(i)), y(t[0])]);
    });
    flush();
    return dpath;
  };
  const lines =
    KINDS.map((k, n) => `<path class="train ${k.cls}${n === 0 ? " area" : ""}" d="${path(series[n], n === 0)}"/>`).join(
      "",
    ) + (atBreak ? `<path class="train at-break" d="${path(atBreak.map((m) => [m, 0, 0] as Train), false)}"/>` : "");

  // Arrows every 6 hours (6am, noon, 6pm) for the main swell, pointing the way it travels
  let arrows = "";
  series[0].forEach((t, i) => {
    const h = at(i);
    if (!t || !inWeek(i) || ![6, 12, 18].includes(Math.round(h) % 24)) return;
    arrows += `<g transform="translate(${x(h)},22) rotate(${t[1] + 180})"><path class="arrow" d="M0,-6L3.5,3L0,1L-3.5,3Z"/></g>`;
  });

  // Tide lane: the sea level, scaled to its own range
  const tides = o.data.tide ?? [];
  const tv = tides.filter((v, i) => v != null && inWeek(i)) as number[];
  const [lo, hi] = [Math.min(...tv), Math.max(...tv)];
  const ty = (v: number) => top + plotH + 10 + tideH - ((v - lo) / Math.max(0.1, hi - lo)) * tideH;
  let tidePath = "";
  let pen = false;
  tides.forEach((v, i) => {
    if (v == null || !inWeek(i)) return void (pen = false);
    tidePath += `${pen ? "L" : "M"}${x(at(i)).toFixed(1)},${ty(v).toFixed(1)}`;
    pen = true;
  });

  // Y axis: a couple of heights in the chosen unit
  const ticks = [max / 1.1 / 2, max / 1.1].map((m) => Math.round(m * 10) / 10);
  const yAxis = ticks
    .map((m) => `<line class="tick" x1="0" x2="${W}" y1="${y(m)}" y2="${y(m)}"/><text class="tick-label" x="4" y="${y(m) - 3}">${height(m)}</text>`)
    .join("");

  el.innerHTML = `
    <div class="swell-head">
      <h3>Swell this week</h3>
      <span class="legend">${atBreak && o.spot ? `<span class="key brk">At ${esc(o.spot.name)}</span>` : ""}${KINDS.map((k) => `<span class="key ${k.cls}">${k.name}</span>`).join("")}<span class="key tide-key">Tide</span></span>
    </div>
    <p class="swell-readout" aria-live="polite"></p>
    <svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Swell offshore, hour by hour this week: each wave train's height, and the tide">
      ${grid}${band}${yAxis}${lines}${arrows}
      <path class="tide" d="${tidePath}"/>
      <text class="lane-label" x="4" y="${top + plotH + 20}">Tide</text>
      <line class="cursor" x1="0" x2="0" y1="${top}" y2="${H - bottom}" visibility="hidden"/>
    </svg>
`;

  // Readout: the hour under the pointer, else the middle of the selected session
  const svg = el.querySelector("svg")!;
  const cursor = el.querySelector<SVGLineElement>(".cursor")!;
  const readout = el.querySelector<HTMLElement>(".swell-readout")!;
  const show = (h: number) => {
    const i = Math.round(h - (t0 - w0) / HOUR);
    if (i < 0 || i >= series[0].length) return;
    const when = new Date(w0 + Math.round(h) * HOUR);
    const hr = when.getUTCHours();
    const label = `${when.toLocaleDateString("en-AU", { weekday: "short", timeZone: "UTC" })} ${(hr + 11) % 12 + 1}${hr < 12 ? "am" : "pm"}`;
    const parts = KINDS.map((k, n) => {
      const t = series[n][i];
      return t ? `<span class="key ${k.cls}">${k.key === "chop" ? "chop " : ""}<b>${height(t[0])} ${compass(t[1])}</b> @ ${Math.round(t[2])}s</span>` : "";
    }).filter(Boolean);
    const tide = tides[i];
    const next = tides[i + 1];
    const tideWord = tide == null ? "" : next == null ? "" : next > tide ? "rising" : "falling";
    const here = atBreak?.[i] != null && o.spot ? `<span class="key brk">at the break <b>${height(atBreak[i])}</b></span>` : "";
    readout.innerHTML = `<b>${esc(label)}</b> ${here}${parts.join(" ")}${tide != null ? ` <span class="muted">tide ${tideWord}</span>` : ""}`;
    cursor.setAttribute("x1", String(x(h)));
    cursor.setAttribute("x2", String(x(h)));
    cursor.setAttribute("visibility", "visible");
  };
  const mid = (Date.parse(o.selected.start.slice(0, 16) + ":00Z") + Date.parse(o.selected.end.slice(0, 16) + ":00Z")) / 2;
  const rest = () => show(Math.round((mid - w0) / HOUR));
  const hourAt = (e: PointerEvent) => {
    const r = svg.getBoundingClientRect();
    return ((e.clientX - r.left) / r.width) * hours;
  };
  svg.addEventListener("pointermove", (e) => show(hourAt(e)));
  svg.addEventListener("pointerleave", rest);
  svg.addEventListener("click", (e) => {
    const t = w0 + hourAt(e) * HOUR;
    const s = o.sessions.find((x) => Date.parse(x.start.slice(0, 16) + ":00Z") <= t && t < Date.parse(x.end.slice(0, 16) + ":00Z"));
    if (s) o.onPick(s);
  });
  rest();
}
