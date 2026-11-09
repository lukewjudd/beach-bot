// Swell lines drawn over the open ocean: broken wave crests drifting the way the swell is travelling, in the
// spirit of Windy's and Surfline's swell maps. Long-period groundswell has wide, even lines moving faster; short
// wind swell has tight ones. Bigger swell draws brighter. Clipped to the open ocean (sea.json, from the
// OpenStreetMap coastline), so it never runs over land, the harbour or the bays. The forecast has one swell for the
// whole coast, so it doesn't bend round headlands here; the About dialog explains that bit.

import type L from "leaflet";
import { viewportCanvas } from "./pane";
import sea from "./sea.json";

export interface Swell {
  set(metres: number, fromDeg: number, periodS: number): void;
  show(on: boolean): void;
}

// A steady pseudo-random number for crest k and segment i, so the gaps in a crest stay put as it moves
const hash = (k: number, i: number) => {
  const x = Math.sin(k * 127.1 + i * 311.7) * 43758.5453;
  return x - Math.floor(x);
};

const FADE_STEPS = 16; // brightness steps for the fade; plenty for lines this faint
// The wake behind each arc: how far back each copy sits (px) and how bright it is next to the arc
const TRAIL: [number, number][] = [
  [0, 1],
  [2.5, 0.4],
  [5, 0.18],
  [7.5, 0.07],
];
const EASE_MS = 450; // how long the layer takes to fade in, out, or across to a new swell
const LIFE_CRESTS = 7; // an arc lives for about seven crest spacings of travel

export function swellLayer(map: L.Map, regionId: string): Swell {
  const container = map.getContainer();
  const canvas = viewportCanvas(map, "swell", 450); // under the score pins
  canvas.hidden = true;
  const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const outline = (sea as unknown as Record<string, [number, number][]>)[regionId] ?? [];

  let on = false;
  let height = 0; // m
  let heading = 0; // radians, the way the swell travels (screen: 0 = up)
  let period = 10; // s
  let frame = 0;
  let w = 0;
  let h = 0;
  let clip: Path2D | null = null;
  let last = 0;
  let travel = 0; // px the swell has moved since the layer was switched on; only ever grows

  const colour = () =>
    getComputedStyle(document.documentElement).getPropertyValue("--swell").trim() || "rgba(255, 255, 255, .6)";

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    w = container.clientWidth;
    h = container.clientHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    clip = null;
    if (on) draw();
  }

  // The open ocean in screen space; rebuilt whenever the map moves
  function seaPath() {
    if (clip) return clip;
    clip = new Path2D();
    outline.forEach(([lat, lon], i) => {
      const p = map.latLngToContainerPoint([lat, lon]);
      if (i) clip!.lineTo(p.x, p.y);
      else clip!.moveTo(p.x, p.y);
    });
    clip.closePath();
    return clip;
  }

  // Wider apart and quicker for longer periods (real crests are 1.56 T² m apart and move at 1.56 T m/s; this keeps
  // the feel without the scale, which would be too fine zoomed out)
  const spacing = () => 16 + 2.4 * Math.min(Math.max(period, 4), 18); // 6 s: 30px, 14 s: 50px
  const pxPerSec = () => 6 + 1.3 * Math.min(Math.max(period, 4), 18); // 6 s: 14, 14 s: 24
  const alpha = () => 0.2 + 0.6 * Math.min(1, height / 2.5); // 0.5m faint, 2.5m+ full

  function draw() {
    ctx.clearRect(0, 0, w, h);
    if (height <= 0.05 || !outline.length) return;
    ctx.save();
    ctx.clip(seaPath());
    const dx = Math.sin(heading);
    const dy = -Math.cos(heading); // the way it travels
    const px = -dy; // along the crest
    const py = dx;
    const s = spacing();
    const reach = Math.hypot(w, h) / 2 + s;
    const cx = w / 2;
    const cy = h / 2;
    ctx.strokeStyle = colour();
    ctx.lineWidth = 1.4;
    ctx.lineCap = "round";
    // Arcs are sorted into a few brightness steps and each step stroked once, so fading costs no extra draws
    const paths = Array.from({ length: FADE_STEPS }, () => new Path2D());
    const life = s * LIFE_CRESTS; // how far an arc travels from fading in to fading out
    // Crest k keeps its number, and so its pattern of arcs, the whole way across: travel only grows, it never
    // wraps back a crest, which is what used to make the whole field jump once per crest
    const first = Math.ceil((-reach - travel) / s);
    for (let k = first; k * s + travel < reach; k++) {
      const t = k * s + travel; // how far along the travel direction this crest is
      // Each crest is broken into short arcs that bow forward in the middle, the way a swell line looks from
      // above, staggered from one crest to the next so it reads as sea rather than a grid
      let u = -reach - hash(k, 0) * 60;
      for (let i = 1; u < reach; i++) {
        const len = 26 + hash(k, i) * 48;
        const gap = 14 + hash(k, i + 50) * 34;
        // Each arc fades in, holds, and fades out as it travels, then comes round again, out of step with its
        // neighbours. Smooth at both ends, so nothing pops in or out
        const age = (((k * s + travel) / life + hash(k, i + 200)) % 1 + 1) % 1;
        const fade = Math.sin(Math.PI * age) ** 2;
        if (Math.round(fade * (FADE_STEPS - 1)) > 0) {
          const bow = len * (0.1 + 0.06 * hash(k, i + 100)); // how far the middle leads the ends
          const steps = Math.max(4, Math.round(len / 6));
          const pts: [number, number][] = [];
          for (let j = 0; j <= steps; j++) {
            const v = u + (len * j) / steps;
            const bend = bow * Math.sin((Math.PI * j) / steps) + 2 * Math.sin(v / 70 + k * 1.7);
            pts.push([cx + dx * (t + bend) + px * v, cy + dy * (t + bend) + py * v]);
          }
          // The arc itself, then a few fainter copies just behind it: the slightest wake
          for (const [back, weight] of TRAIL) {
            const step = Math.round(fade * weight * (FADE_STEPS - 1));
            if (!step) continue;
            const path = paths[step];
            pts.forEach(([x, y], j) => {
              if (j) path.lineTo(x - dx * back, y - dy * back);
              else path.moveTo(x - dx * back, y - dy * back);
            });
          }
        }
        u += len + gap;
      }
    }
    const a = alpha();
    paths.forEach((path, step) => {
      if (!step) return;
      ctx.globalAlpha = (a * step) / (FADE_STEPS - 1);
      ctx.stroke(path);
    });
    ctx.restore();
  }

  function tick(time: number) {
    if (!on) return;
    const dt = last ? Math.min(0.1, (time - last) / 1000) : 0;
    last = time;
    travel += pxPerSec() * dt;
    draw();
    frame = requestAnimationFrame(tick);
  }

  function start() {
    cancelAnimationFrame(frame);
    last = 0;
    if (!on) return;
    if (reduceMotion) draw(); // one still frame
    else frame = requestAnimationFrame(tick);
  }

  new ResizeObserver(resize).observe(container);
  map.on("move zoom", () => {
    clip = null;
    if (on && reduceMotion) draw();
  });

  // Fades are CSS opacity on the canvas, so the lines keep moving underneath while it eases
  canvas.style.transition = `opacity ${EASE_MS}ms ease-in-out`;
  canvas.style.opacity = "0";
  let swap = 0; // pending swap to a new swell
  let hiding = 0; // pending hide after fading out
  const fadeTo = (o: number) => {
    canvas.style.opacity = String(o);
  };

  function apply(metres: number, fromDeg: number, periodS: number) {
    height = metres;
    period = periodS || 10;
    heading = ((fromDeg + 180) % 360) * (Math.PI / 180); // comes FROM fromDeg, so the crests move the other way
    if (on && reduceMotion) draw();
  }

  return {
    set(metres, fromDeg, periodS) {
      const next = ((fromDeg + 180) % 360) * (Math.PI / 180);
      const turn = Math.abs(((next - heading + 3 * Math.PI) % (2 * Math.PI)) - Math.PI); // radians, shortest way
      // Only a new direction or period moves the lines; a bit more or less height just brightens them in place
      const moved = turn > 0.15 || Math.abs((periodS || 10) - period) >= 1.5;
      clearTimeout(swap);
      if (!moved || !on || hiding || reduceMotion) {
        apply(metres, fromDeg, periodS);
        if (on && !hiding) fadeTo(1); // in case this cut short a swap that had faded the lines out
        return;
      }
      // A new swell: ease the old lines out, swap, ease the new ones in, rather than snapping across
      fadeTo(0);
      swap = window.setTimeout(() => {
        apply(metres, fromDeg, periodS);
        if (on && !hiding) fadeTo(1);
      }, EASE_MS);
    },
    show(visible) {
      clearTimeout(hiding);
      hiding = 0;
      if (visible) {
        const was = on;
        on = true;
        canvas.hidden = false;
        if (!was) start();
        requestAnimationFrame(() => fadeTo(1)); // after a frame, so the transition runs from 0
      } else if (on) {
        // Keep the lines moving while they fade, then stop
        fadeTo(0);
        hiding = window.setTimeout(() => {
          hiding = 0;
          on = false;
          canvas.hidden = true;
          ctx.clearRect(0, 0, w, h);
          start(); // stops the loop
        }, EASE_MS);
      }
    },
  };
}
