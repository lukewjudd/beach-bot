// Windy-style wind trails drawn over the map: particles drift with the session's wind, leaving fading trails.
// Light wind = few, slow, faint, short trails; strong wind = faster, longer ones. Everything scales with how wind
// feels (its force grows with the square of its speed), so 8 km/h is a lazy drift and 35 km/h races. The forecast
// has one wind for the whole coast, so every particle shares a direction, with a little wobble.

import type L from "leaflet";
import { viewportCanvas } from "./pane";

interface Particle {
  x: number;
  y: number;
  age: number;
  life: number;
  wobble: number; // per-particle direction offset, radians
}

export interface Wind {
  set(kmh: number, gustKmh: number, fromDeg: number): void;
  show(on: boolean): void;
}

export function windLayer(map: L.Map): Wind {
  const container = map.getContainer();
  const canvas = viewportCanvas(map, "wind", 460); // under the score pins
  const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  let particles: Particle[] = [];
  let speed = 0; // km/h
  let gust = 0;
  let heading = 0; // radians, the direction the air is moving TO (screen: 0 = up)
  let on = false;
  let frame = 0;
  let w = 0;
  let h = 0;

  const colour = () =>
    getComputedStyle(document.documentElement).getPropertyValue("--wind").trim() || "rgba(30, 60, 80, .55)";

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    w = container.clientWidth;
    h = container.clientHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    seed();
  }

  function spawn(p?: Particle): Particle {
    const q = p ?? ({} as Particle);
    q.x = Math.random() * w;
    q.y = Math.random() * h;
    q.age = 0;
    q.life = 40 + Math.random() * 80;
    q.wobble = (Math.random() - 0.5) * 0.35;
    return q;
  }

  // 0 when still, 1 at 40 km/h and up, curving so light winds stay small
  const strength = (kmh: number) => Math.min(kmh, 40) ** 2 / 1600;
  const pxPerFrame = (kmh: number) => 0.12 + 0.01 * kmh + 0.0018 * Math.min(kmh, 45) ** 2; // 8: 0.3, 20: 1, 40: 3.4

  function seed() {
    // Fewer particles when it's calm, more when it's blowing; scaled to the map's area
    const density = 0.3 + strength(speed); // 0.3-1.3
    const n = Math.round(((w * h) / 3400) * density);
    particles = Array.from({ length: n }, () => {
      const p = spawn();
      p.age = Math.random() * p.life; // stagger so they don't all respawn together
      return p;
    });
    ctx.clearRect(0, 0, w, h);
  }

  function tick(t: number) {
    if (!on || reduceMotion) return;
    // Longer trails in stronger wind: fade less of the previous frame
    const fade = 0.17 - (Math.min(speed, 40) / 40) * 0.11; // 0.17 calm -> 0.06 at 40 km/h (light winds are short anyway: they're slow)
    ctx.globalAlpha = 1; // the trails' faintness mustn't slow the fade
    ctx.globalCompositeOperation = "destination-out";
    ctx.fillStyle = `rgba(0, 0, 0, ${fade})`;
    ctx.fillRect(0, 0, w, h);
    ctx.globalCompositeOperation = "source-over";

    // Gusts: a brief puff every several seconds, a quarter of the way to the gust value (forecast gusts are the
    // strongest few seconds in the hour, not what it feels like most of the time)
    const puff = Math.max(0, Math.sin(t / 1400)) ** 4;
    const px = pxPerFrame(speed + (gust > speed ? (gust - speed) * 0.25 * puff : 0));

    ctx.strokeStyle = colour();
    ctx.globalAlpha = 0.45 + 0.55 * Math.min(1, strength(speed) * 2); // faint when it's light
    ctx.lineWidth = 1.2;
    ctx.lineCap = "round";
    ctx.beginPath();
    for (const p of particles) {
      const a = heading + p.wobble;
      const nx = p.x + Math.sin(a) * px;
      const ny = p.y - Math.cos(a) * px;
      ctx.moveTo(p.x, p.y);
      ctx.lineTo(nx, ny);
      p.x = nx;
      p.y = ny;
      if (++p.age > p.life || nx < -5 || ny < -5 || nx > w + 5 || ny > h + 5) spawn(p);
    }
    ctx.stroke();
    frame = requestAnimationFrame(tick);
  }

  // Reduced motion: one still frame of short strokes instead of an animation
  function still() {
    ctx.clearRect(0, 0, w, h);
    const len = 4 + strength(speed) * 20;
    ctx.strokeStyle = colour();
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    for (const p of particles.filter((_, i) => i % 3 === 0)) {
      const a = heading + p.wobble;
      ctx.moveTo(p.x, p.y);
      ctx.lineTo(p.x + Math.sin(a) * len, p.y - Math.cos(a) * len);
    }
    ctx.stroke();
  }

  function start() {
    cancelAnimationFrame(frame);
    if (on && reduceMotion) still();
    else if (on) frame = requestAnimationFrame(tick);
  }

  new ResizeObserver(resize).observe(container);
  // Trails are drawn in screen space; wipe them when the map moves so they don't smear
  map.on("movestart zoomstart", () => ctx.clearRect(0, 0, w, h));

  return {
    set(kmh, gustKmh, fromDeg) {
      speed = kmh;
      gust = gustKmh;
      heading = ((fromDeg + 180) % 360) * (Math.PI / 180); // blows FROM fromDeg, so particles move the other way
      seed();
      start();
    },
    show(visible) {
      on = visible;
      canvas.hidden = !on;
      if (!on) ctx.clearRect(0, 0, w, h);
      start();
    },
  };
}
