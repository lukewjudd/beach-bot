// Beach calls: renders scores.json as a week of days, a summary of the chosen session, a map and a list of spots.

import type { Map as LeafletMap, Marker } from "leaflet";
import { ICONS } from "./icons";
import { renderSwellChart } from "./swellchart";
import { height, localise, setUnit, speed, speedNum, temp, units } from "./units";
import type { Units } from "./units";
import { pickRegion, REGIONS } from "./regions";
import "./style.css";
import type { Scores, Session, SpearCall, Spot, SpotKind, SpotScore, SurfCall } from "./types";

// the About dialog's figures, drawn by bot/scripts/draw_about_figures.py
const figures = import.meta.glob<string>("./about/*.svg", { query: "?raw", import: "default", eager: true });

// Which stretch of coast: from the link, else the browser's last choice, else the eastern suburbs
const params = new URLSearchParams(location.search);
const region = pickRegion(params);
const linkedSpot = params.get("spot"); // a shared spot link: see openLinked
// Set in .env.production / .env.development; ?data= overrides it
const DATA_URL = params.get("data") ?? `${import.meta.env.VITE_DATA_BASE}scores-${region.id}.json`;
const REFRESH_MS = 5 * 60_000; // the bot runs hourly; checking every 5 minutes keeps an open tab current
const STALE_MINS = 60;

const $ = (id: string) => document.getElementById(id) as HTMLElement;
// Traffic lights: green is worth going (the calendar's bar), amber is so-so, red is don't bother
const ratingClass = (r: number) => (r >= 8 ? "r-green" : r >= 5 ? "r-amber" : "r-red");
const pill = (r: number) => `<span class="pill ${ratingClass(r)}" aria-label="${r} out of 10">${r}</span>`;
// A spot's score with an icon for its kind: the same badge as its pin on the map. Surf is on its own scale
// (waves, not a swim), so its badge is outlined rather than filled and says "surf" to screen readers
const badge = (kind: SpotKind, r: number, label = `${r} out of 10`) =>
  `<span class="score ${kind} ${ratingClass(r)}" aria-label="${kind === "surf" ? `surf ${label}` : label}">${ICONS[kind]}<span>${r}</span></span>`;
const esc = (s: unknown) =>
  String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c] as string);
// GoatCounter events (index.html counts visits under the page alone, so links don't split it): link/<spot>,
// share/<spot>, mode/<mode> and clovelly-depth. It skips localhost, and does nothing if it's blocked
const track = (path: string, title?: string) => {
  try {
    (window as unknown as { goatcounter?: { count?: (o: object) => void } }).goatcounter?.count?.({ path, title, event: true });
  } catch {
    // blocked or not loaded: not counted
  }
};
const save = (k: string, v: string) => {
  try {
    localStorage.setItem(k, v);
  } catch {
    // storage blocked: not remembered, still works for this visit
  }
};
const load = (k: string) => {
  try {
    return localStorage.getItem(k);
  } catch {
    return null;
  }
};

let data: Scores;
let spotsById: Record<string, Spot>;
// The map code loads on the side: the forecast renders as soon as the scores arrive, and pins follow
const mapModule = import("./map");
let mapApi: typeof import("./map") | undefined;
let map: LeafletMap | undefined;
let wind: import("./wind").Wind | undefined;
let swell: import("./swell").Swell | undefined;
let markers: Record<string, Marker> = {};

let current = 0; // index into data.sessions
let week = 0; // 0 = this week, 1 = next
let openSpot: string | null = null; // the card that's expanded
type Activity = "swim" | "harbour" | "snorkel" | "pool";
const ACTIVITIES: Activity[] = ["swim", "harbour", "snorkel", "pool"];
// Which activities to show spots for (remembered per browser). The harbour beaches are opt-in: they're
// extras for a big-swell day, not what the site's about, so the map opens on the ocean coast
let activities = new Set<Activity>(ACTIVITIES.filter((a) => a !== "harbour"));
try {
  const saved = JSON.parse(load("activities") ?? "null");
  if (Array.isArray(saved)) activities = new Set(saved.filter((a) => ACTIVITIES.includes(a)));
} catch {
  // nothing saved, or garbled: show everything
}
// A linked swim spot shows whatever its activity filter: a harbour link ticks Harbour for this visit (not saved)
if (linkedSpot) {
  const kind = linkedSpot.split("-")[0];
  if (kind === "harbour" || kind === "swim" || kind === "pool") activities.add(kind as Activity);
}
let sort = load("sort") ?? "best";
let windOn = load("wind") === "on";
let swellOn = load("swell") === "on"; // off unless this browser turned it on
let basemap: "map" | "aerial" = load("basemap") === "aerial" ? "aerial" : "map";
// Swim, surf or spear: separate models with their own scores, so the whole page follows one. Swim unless the link
// says otherwise or this browser last picked another
type Mode = "swim" | "surf" | "spear";
const MODES: Mode[] = ["swim", "surf", "spear"];
const asMode = (v: string | null): Mode => (MODES.includes(v as Mode) ? (v as Mode) : "swim");
// A shared spot link (?spot=surf-maroubra) opens in that spot's own mode: its id starts with its kind
const linkedMode = linkedSpot?.startsWith("surf-") ? "surf" : linkedSpot?.startsWith("spear-") ? "spear" : linkedSpot ? "swim" : null;
let mode: Mode = linkedMode ?? asMode(params.get("mode") ?? load("mode"));
const MODE_NAME: Record<Mode, string> = { swim: "Swim", surf: "Surf", spear: "Spear" };

const TAG: Record<SpotKind, string> = { swim: "Beach", harbour: "Harbour", pool: "Pool", surf: "Surf", spear: "Spear" };
const tags = (spot: Spot) =>
  `<span class="tag">${TAG[spot.kind]}</span>` +
  (spot.snorkel ? `<span class="tag">Snorkel</span>` : "") +
  (spot.women_only ? `<span class="tag">Women only</span>` : "") +
  (spot.kind === "spear" && spot.level === "advanced"
    ? `<span class="tag tag-level" title="A long swim, a jump entry or an exposed point">Experienced</span>`
    : spot.level === "advanced" || spot.level === "expert" || spot.level === "pro"
    ? `<span class="tag tag-level" title="${spot.level === "pro" ? "Big-wave spot for pros: scored so you know when it's worth watching" : "Heavy reef or bombie: experienced surfers only"}">${spot.level === "pro" ? "Pros only" : spot.level === "expert" ? "Expert" : "Advanced"}</span>`
    : spot.level === "intermediate"
      ? `<span class="tag">Intermediate</span>`
      : "") +
  (spot.checked === false
    ? `<span class="tag" title="Set up from the guides; not yet checked against real days">Not checked yet</span>`
    : "");
// Surf mode shows the surf breaks. Swim mode shows a spot if it suits any ticked activity (Clovelly is a swim and a
// snorkel spot)
const shows = (spot: Spot) =>
  mode !== "swim"
    ? spot.kind === mode
    : spot.kind === "harbour"
      ? activities.has("harbour") // only ever with Harbour ticked, even the snorkel spots
      : (activities.has("swim") && spot.kind === "swim") ||
        (activities.has("snorkel") && !!spot.snorkel) ||
        (activities.has("pool") && spot.kind === "pool");

// Notes that should change your mind stand out from the nice-to-knows ("wave pool fun")
const WARN = /pollution|bluebottle|rain|murky|closed|shut|washy|rough|storm|southerly|upwelling|waves|swell|at the beach|current|shark|chop|drift/i;
const notesHtml = (notes: string[]) =>
  notes
    .map(localise)
    .map((n) => (WARN.test(n) ? `<span class="warn"><span aria-hidden="true">⚠</span> ${esc(n)}</span>` : esc(n)))
    .join(" · ");

// The session's call in this mode: swimming's lead spot, the best surf break on the surf scale, or the best
// spearfishing spot
const NO_SURF: SurfCall = { id: "", name: "", score: 0, rating: 0, window: null, posted: false, in_event: false };
const NO_SPEAR: SpearCall = { id: "", name: "", score: 0, rating: 0, window: null };
const call = (s: Session) => (mode === "surf" ? (s.surf ?? NO_SURF) : mode === "spear" ? (s.spear ?? NO_SPEAR) : s.lead);
// The session has a call in this mode (sessions called before a mode existed have none)
const hasCall = (s: Session) => mode === "swim" || !!(mode === "surf" ? s.surf : s.spear);
// Worth it: a swim at 8/10 or better (the calendar holds out for 9; further out than it posts, it's an early guess),
// surf that's pumping (8/10 or better on the surf scale), or a spearfishing spot at 8/10
const worth = (s: Session) =>
  mode === "surf"
    ? !!s.surf?.posted
    : mode === "spear"
      ? (s.spear?.rating ?? 0) >= 8
      : s.posted || (s.confidence === "low" && s.lead.score >= data.thresholds.post);
// Ranking: score, with the favourite winning close calls like the headline does
const rankScore = (x: SpotScore | undefined) =>
  x ? x.score + (data.favourite && x.id === data.favourite.id ? data.favourite.tolerance + 0.5 : 0) : -1;
const isPast = (s: Session) => s.started && new Date(s.end) < new Date();

// ---------------------------------------------------------------- dates (calendar days, from the session dates)
const DAY = 86_400_000;
const ymd = (d: Date) => d.toISOString().slice(0, 10);
const parse = (iso: string) => new Date(`${iso}T00:00:00Z`); // kept in UTC so day maths is exact
const today = () => parse(data.generated_at.slice(0, 10)); // generated_at is Sydney local time
const monday = (d: Date) => new Date(d.getTime() - ((d.getUTCDay() + 6) % 7) * DAY);
const dayName = (d: Date, style: "short" | "long" = "short") =>
  d.toLocaleDateString("en-AU", { weekday: style, timeZone: "UTC" });
// Every day has three sessions: sunrise-11am, 11am-2pm and 2pm-sunset. The key ends with the slot code
type SlotCode = "am" | "md" | "pm";
const SLOTS: Record<SlotCode, { short: string; name: string }> = {
  am: { short: "AM", name: "Morning" },
  md: { short: "MID", name: "Midday" },
  pm: { short: "PM", name: "Evening" },
};
const slotOf = (s: Session) => s.key.slice(-2) as SlotCode;
const slotName = (s: Session) => SLOTS[slotOf(s)].name;
const weekOf = (s: Session) => Math.floor((parse(s.date).getTime() - monday(today()).getTime()) / (7 * DAY));

// ---------------------------------------------------------------- loading and refreshing
// Eastern / Northern. Switching reloads the page on the other region, so the map starts fresh on its coast
function renderRegionPick() {
  $("region-pick").innerHTML = REGIONS.map(
    (r) =>
      `<button type="button" data-r="${r.id}" aria-pressed="${r.id === region.id}">${esc(r.name)}</button>`,
  ).join("");
  $("region-pick")
    .querySelectorAll<HTMLButtonElement>("button")
    .forEach((b) =>
      b.addEventListener("click", () => {
        if (b.dataset.r === region.id) return;
        save("region", b.dataset.r as string);
        location.href = location.pathname + (mode !== "swim" ? `?mode=${mode}` : ""); // drop ?s=, which belongs to the other region
      }),
    );
}

// Settings, behind the cog: swim or surf, the coast, and units. All remembered per browser
function wireSettings() {
  const dlg = $("settings") as HTMLDialogElement;
  $("cog-icon").innerHTML = ICONS.cog;
  $("settings-open").addEventListener("click", () => dlg.showModal());
  $("settings-close").addEventListener("click", () => dlg.close());
  dlg.addEventListener("click", (e) => {
    if (e.target === dlg) dlg.close(); // a tap on the backdrop
  });
  for (const group of dlg.querySelectorAll<HTMLElement>(".seg[data-unit]")) {
    const k = group.dataset.unit as keyof Units;
    const buttons = [...group.querySelectorAll<HTMLButtonElement>("button")];
    const show = () => buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.v === units[k])));
    buttons.forEach((b) =>
      b.addEventListener("click", () => {
        setUnit(k, b.dataset.v as never);
        show();
        if (data) render();
      }),
    );
    show();
  }
  wireModePick();
}

// Swim / Surf / Spear. Remembered per browser and kept in the link, so a surf or spear view can be shared
function wireModePick() {
  const buttons = [...$("mode-pick").querySelectorAll<HTMLButtonElement>("button")];
  const apply = () => {
    document.body.classList.toggle("mode-surf", mode === "surf");
    document.body.classList.toggle("mode-spear", mode === "spear");
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.mode === mode)));
    $("activity").hidden = mode !== "swim"; // nothing to filter: it's all surf breaks, or all spear spots
    if (data) renderUpdated();
  };
  buttons.forEach((b) =>
    b.addEventListener("click", () => {
      if (b.dataset.mode === mode) return;
      mode = b.dataset.mode as Mode;
      save("mode", mode);
      track(`mode/${mode}`);
      apply();
      openSpot = null;
      if (data) {
        if (!hasCall(data.sessions[current])) current = firstUpcoming();
        render();
        fitToShown();
      }
    }),
  );
  apply();
}

async function start() {
  renderRegionPick();
  wireSettings();
  mapModule.then((m) => {
    map = m.createMap($("map"), region);
    mapApi = m;
    wind = m.windLayer(map);
    wind.show(windOn);
    swell = m.swellLayer(map, region.id);
    swell.show(swellOn);
    m.basemapPicker(map, basemap, (b) => {
      basemap = b;
      save("basemap", b);
    });
    m.layerSwitches(map, [
      { label: "Wind", icon: "wind", on: windOn, toggle: toggleWind },
      { label: "Swell", icon: "swell", on: swellOn, toggle: toggleSwell },
    ]);
    // Phones, map view: "Details" in a popup goes to that spot's card in the list. Bound on the popup itself,
    // since Leaflet stops clicks inside popups from reaching the page
    map.on("popupopen", (e) => {
      const link = e.popup.getElement()?.querySelector<HTMLElement>("[data-details]");
      link?.addEventListener("click", () => {
        setView("list");
        openCard(link.dataset.details as string, false);
      });
    });
    if (data) render(); // scores got here first: add the pins now
  });
  try {
    // Plain fetch so it picks up the <link rel="preload"> in index.html
    const res = await fetch(DATA_URL);
    if (!res.ok) throw new Error(String(res.status));
    adopt(await res.json(), params.get("s"));
  } catch (e) {
    $("hero").innerHTML = `<p class="error">Couldn't load the latest scores (${esc((e as Error).message)}). Try again shortly.</p>`;
    return;
  }
  wireControls();
  render();
  openLinked();
  setInterval(renderUpdated, 60_000);
  setInterval(refresh, REFRESH_MS);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") refresh();
  });
}

// A shared spot link: open its card (the list on a phone), fly the map to it, and for ?depth Clovelly's underwater map
function openLinked() {
  if (!linkedSpot || !spotsById[linkedSpot]) return;
  track(`link/${linkedSpot}`, spotsById[linkedSpot].name);
  if (innerWidth < 860) setView("list");
  openCard(linkedSpot, true);
  if (params.has("depth") && linkedSpot === "swim-clovelly") openDepth();
}

// Take on a scores.json, keeping the chosen session (or the one in the link) if it's there
function adopt(next: Scores, wantKey: string | null) {
  data = next;
  spotsById = Object.fromEntries(data.spots.map((s) => [s.id, s]));
  const wanted = wantKey ? data.sessions.findIndex((s) => s.key === wantKey) : -1;
  current = wanted >= 0 ? wanted : firstUpcoming();
  renderUpdated();
}

// The next session that has a call in this mode (one frozen before the mode existed has none), else the next one
function firstUpcoming() {
  const withCall = data.sessions.findIndex((s) => !isPast(s) && hasCall(s));
  const upcoming = data.sessions.findIndex((s) => !isPast(s));
  return withCall >= 0 ? withCall : upcoming >= 0 ? upcoming : 0;
}

// New scores land hourly; pick them up without a reload so an open tab never goes quietly stale
async function refresh() {
  if (document.visibilityState !== "visible") return;
  try {
    const res = await fetch(DATA_URL, { cache: "no-cache" }); // revalidate rather than trust the 5-minute cache
    const next: Scores = await res.json();
    if (next.generated_at !== data.generated_at) {
      adopt(next, data.sessions[current]?.key ?? null);
      render();
    }
  } catch {
    // offline or the bucket hiccuped: keep what's on screen; the stale warning covers it
  }
  renderUpdated();
}

// "updated 25 min ago"; past an hour, a warning that conditions may have moved on
function renderUpdated() {
  const at = new Date(data.generated_at);
  const mins = Math.max(0, Math.round((Date.now() - at.getTime()) / 60_000));
  const age = mins < 1 ? "" : mins < 60 ? `${mins} min` : mins < 48 * 60 ? `${Math.round(mins / 60)}h` : "days";
  const exact = at.toLocaleString("en-AU", {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
    timeZone: "Australia/Sydney",
  });
  $("updated").innerHTML =
    `${esc(region.name)} · ${MODE_NAME[mode]} · <span title="${esc(exact)}">updated ${age ? `${age} ago` : "just now"}</span>`;
  const stale = $("stale");
  stale.hidden = mins <= STALE_MINS;
  stale.textContent = `These scores are ${age} old, so conditions may have changed. The page updates itself when new ones arrive.`;
}

// ---------------------------------------------------------------- controls
function toggleSwell() {
  swellOn = !swellOn;
  save("swell", swellOn ? "on" : "off");
  swell?.show(swellOn);
  return swellOn;
}

function toggleWind() {
  windOn = !windOn;
  save("wind", windOn ? "on" : "off");
  wind?.show(windOn);
  return windOn;
}

function wireControls() {
  const about = $("about") as HTMLDialogElement;
  for (const el of about.querySelectorAll<HTMLElement>("[data-how]")) el.innerHTML = figures[`./about/${el.dataset.how}.svg`] ?? "";
  $("about-open").addEventListener("click", () => about.showModal());
  $("about-close").addEventListener("click", () => about.close());
  about.addEventListener("click", (e) => {
    if (e.target === about) about.close(); // a tap on the backdrop
  });
  const act = $("activity") as HTMLDetailsElement;
  const boxes = [...act.querySelectorAll<HTMLInputElement>("input[type=checkbox]")];
  const summarise = () => {
    const names = boxes.filter((b) => b.checked).map((b) => b.parentElement?.textContent?.trim());
    const harbour = activities.has("harbour");
    $("activity-value").textContent =
      names.length === ACTIVITIES.length
        ? "All"
        : names.length === ACTIVITIES.length - 1 && !harbour
          ? "All ocean"
          : names.length
            ? names.join(", ")
            : "None";
  };
  boxes.forEach((b) => {
    b.checked = activities.has(b.value as Activity);
    b.addEventListener("change", () => {
      activities = new Set(boxes.filter((x) => x.checked).map((x) => x.value as Activity));
      save("activities", JSON.stringify([...activities]));
      summarise();
      render();
      if (b.value === "harbour") fitToShown(); // take the map out to the harbour, or back to the coast
    });
  });
  summarise();
  // Close the dropdown when you tap away from it
  document.addEventListener("click", (e) => {
    if (act.open && !act.contains(e.target as Node)) act.open = false;
  });
  const srt = $("sort") as HTMLSelectElement;
  srt.value = sort;
  srt.addEventListener("change", () => {
    sort = srt.value;
    save("sort", sort);
    renderSpots(data.sessions[current]);
  });
  // Phones: the list or the map, one at a time
  $("view-toggle")
    .querySelectorAll<HTMLButtonElement>("button")
    .forEach((b) => b.addEventListener("click", () => setView(b.dataset.view as "list" | "map")));
}

function setView(view: "list" | "map") {
  $("layout").dataset.view = view;
  $("view-toggle")
    .querySelectorAll<HTMLButtonElement>("button")
    .forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === view)));
  if (view === "map") map?.invalidateSize();
}

function selectSession(i: number) {
  current = i;
  openSpot = null;
  const url = new URL(location.href);
  url.searchParams.set("s", data.sessions[i].key); // shareable, and the same link the calendar uses
  history.replaceState(null, "", url);
  render();
}

// ---------------------------------------------------------------- week and day picker
function renderWeek() {
  const hasNext = data.sessions.some((s) => weekOf(s) === 1);
  $("week-pick").innerHTML = ["This week", "Next week"]
    .map(
      (label, w) =>
        `<button type="button" data-w="${w}" aria-pressed="${w === week}" ${w === 1 && !hasNext ? "disabled" : ""}>${label}</button>`,
    )
    .join("");
  $("week-pick")
    .querySelectorAll<HTMLButtonElement>("button:not([disabled])")
    .forEach((b) =>
      b.addEventListener("click", () => {
        const w = Number(b.dataset.w);
        const first = data.sessions.findIndex((s) => weekOf(s) === w && !isPast(s));
        if (first >= 0) selectSession(first);
      }),
    );

  // Always Monday to Sunday, so a day sits in the same place every time you look
  const start = new Date(monday(today()).getTime() + week * 7 * DAY);
  const selectedDate = data.sessions[current].date;
  // Each day shows its morning, midday and evening scores stacked under its date; tapping one opens that session
  $("days").innerHTML = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start.getTime() + i * DAY);
    const date = ymd(d);
    const daySessions = data.sessions.map((s, idx) => ({ s, idx })).filter(({ s }) => s.date === date);
    const low = daySessions.length > 0 && daySessions.every(({ s }) => s.confidence === "low");
    const slot = (code: SlotCode) => {
      // A session called before surf had its own call has none to show in surf mode
      const found = daySessions.find(({ s }) => slotOf(s) === code && hasCall(s));
      const live = found && !isPast(found.s);
      const name = `${dayName(d, "long")} ${SLOTS[code].name.toLowerCase()}`;
      // Finished sessions stay for the week, greyed out but still tappable, with the call made before they started
      const r = found ? call(found.s).rating : 0;
      const said = found && !live ? `, finished, was ${r} out of 10` : ", no forecast";
      const score = found
        ? `<span class="pill${live ? ` ${ratingClass(r)}` : " none"}">${r}</span>`
        : `<span class="pill none">–</span>`;
      return `<button type="button" class="slot${found && !live ? " past" : ""}" ${found ? `data-i="${found.idx}"` : "disabled"}
          aria-pressed="${found?.idx === current}" aria-label="${name}${live ? `, ${mode !== "swim" ? `${mode} ` : ""}${r} out of 10` : said}">
        <span class="lbl">${SLOTS[code].short}</span>${score}
      </button>`;
    };
    return `<div class="day${low ? " low" : ""}${date === selectedDate ? " selected" : ""}">
      <span class="dh"><span class="dn">${date === ymd(today()) ? "Today" : dayName(d)}</span><span class="dd">${d.getUTCDate()}</span></span>
      ${slot("am")}${slot("md")}${slot("pm")}
    </div>`;
  }).join("");
  $("days")
    .querySelectorAll<HTMLButtonElement>(".slot[data-i]")
    .forEach((b) => b.addEventListener("click", () => selectSession(Number(b.dataset.i))));
}

// ---------------------------------------------------------------- summary of the chosen session
function bars(rep: Record<string, number>) {
  return Object.entries(rep)
    .map(
      ([k, v]) => `<div class="bar"><span>${esc(k)}</span>
      <div class="track"><div class="fill ${ratingClass(v)}" style="width:${v * 10}%"></div></div>
      <span class="num ${ratingClass(v)}-text">${v}/10</span></div>`,
    )
    .join("");
}

// Frame the map on the spots on show (ticking Harbour takes it in to Camp Cove and Murray Rose Pool)
function fitToShown() {
  const pins = data.spots.filter(shows).map((p) => [p.lat, p.lon] as [number, number]);
  if (map && pins.length) map.flyToBounds(pins, { padding: [24, 24], duration: 0.6 });
}

// One line on why it's worth it: the lead spot's best conditions, in words
function whyWorth(s: Session) {
  const c = s.conditions;
  const rep = (call(s).id && s.reports?.[call(s).id as string]) || s.report;
  const say: Record<string, string> = {
    Wind: c.wind_kmh < 8 ? "barely any wind" : `light ${c.wind_dir} wind`,
    "Calm water": "calm water",
    "Calm in the pool": "calm in the pool",
    Tide: "a good tide",
    "Wave size": `${height(c.swell_m)} of swell`,
    "Wave quality": `clean ${c.period_s}s swell`,
    Weather: `${temp(c.air_c)} and dry`,
    "Water quality": "clean water",
    // Spearfishing
    Visibility: (() => {
      const vis = s.scores.find((x) => x.id === call(s).id)?.here?.vis_m;
      return vis ? `about ${vis}m visibility` : "good visibility";
    })(),
    Surge: "little surge",
    Light: "good light",
  };
  const good = Object.entries(rep)
    .filter(([k, v]) => v >= 8 && say[k])
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([k]) => say[k]);
  if (c.water_c != null && c.water_c >= 22) good.push(`warm ${temp(c.water_c)} water`);
  return good.length ? good.join(" · ").replace(/^./, (x) => x.toUpperCase()) : "";
}

// One line on why it isn't worth it: the reason most spots are ruled out, or the weakest conditions.
// Says what's wrong without naming a spot.
function whyNotWorth(s: Session) {
  const top = `Nothing above ${call(s).rating}/10`;
  // Surf: the best break's weakest parts. Ruled-out beaches and pools are a swimming matter
  if (mode === "surf" && !s.surf) return "No surf call: this session was called before surf had its own";
  if (mode === "spear" && !s.spear) {
    // Every spot's a no-go, or the session was called before spearfishing had its own
    const reasons = Object.entries(s.ruled_out ?? {}).filter(([id]) => spotsById[id]?.kind === "spear");
    if (!reasons.length) return "No spearfishing call: this session was called before spearfishing had its own";
    const counts = new Map<string, number>();
    reasons.forEach(([, r]) => counts.set(r, (counts.get(r) ?? 0) + 1));
    const [reason] = [...counts.entries()].sort((a, b) => b[1] - a[1])[0];
    return `No spot worth it · ${localise(reason)}`;
  }
  if (mode !== "swim") {
    const id = call(s).id;
    const weak = Object.entries((id && s.reports?.[id]) || {})
      .filter(([, v]) => v <= 4)
      .sort((a, b) => a[1] - b[1])
      .slice(0, 2)
      .map(([k, v]) => `${k.toLowerCase()} ${v}/10`);
    return weak.length ? `${top} · ${weak.join(", ")}` : top;
  }
  // Ocean beaches and pools only: the harbour doesn't decide whether it's worth going
  const counts = new Map<string, number>();
  Object.entries(s.ruled_out ?? {})
    .filter(([id]) => spotsById[id]?.kind !== "harbour")
    .forEach(([, r]) => counts.set(r, (counts.get(r) ?? 0) + 1));
  const [reason, n] = [...counts.entries()].sort((a, b) => b[1] - a[1])[0] ?? ["", 0];
  const swimmable = data.spots.filter((p) => p.kind === "swim" || p.kind === "pool").length;
  if (n >= 3) return `${top} · ${localise(reason)} at ${n} of ${swimmable} beaches and pools`;
  const weak = Object.entries(s.coast ?? s.report)
    .filter(([, v]) => v <= 4)
    .sort((a, b) => a[1] - b[1])
    .slice(0, 2)
    .map(([k, v]) => `${k.toLowerCase()} ${v}/10`);
  return weak.length ? `${top} · ${weak.join(", ")}` : top;
}

// ---------------------------------------------------------------- hour by hour
// "2pm" -> 14
const hourOfLabel = (t: string) => (parseInt(t, 10) % 12) + (t.endsWith("pm") ? 12 : 0);

// "2pm", "4pm" -> "2–4pm"; "11am", "1pm" -> "11am–1pm"
const span = (a: string, b: string) => (a.slice(-2) === b.slice(-2) ? `${a.slice(0, -2)}–${b}` : `${a}–${b}`);

// A row of hours for one spot: each coloured by its own score, the best two hours (what the score is) ringed,
// storms and ruled-out hours marked, and hours already gone faded. The score stays the best stretch; this shows
// how the rest of the session goes, so a lovely 2pm doesn't hide a stormy 5pm.
function strip(s: Session, sc: SpotScore | undefined, name: string, named = false) {
  if (!sc?.hourly || !s.hours || sc.hourly.length !== s.hours.length) return "";
  const offset = s.start.slice(-6); // the session's UTC offset, e.g. +11:00
  const [w0, w1] = sc.window ? [hourOfLabel(sc.window[0]), hourOfLabel(sc.window[1])] : [-1, -1];
  const live = !isPast(s);
  const words: string[] = [];
  const cells = s.hours
    .map((t, i) => {
      const score = sc.hourly![i];
      const why = sc.why?.[String(i)] ?? "";
      const storm = why.includes("storms");
      const r = score == null ? 0 : Math.max(1, Math.min(10, Math.floor(score / 10)));
      const hr = hourOfLabel(t);
      const best = hr >= w0 && hr < w1;
      const gone = live && new Date(`${s.date}T${String(hr + 1).padStart(2, "0")}:00:00${offset}`) <= new Date();
      const said = storm ? "storms" : score == null ? localise(why) || "ruled out" : `${r} out of 10`;
      words.push(`${t} ${said}${best ? " (best)" : ""}`);
      const cls = storm ? "storm" : score == null ? "none" : ratingClass(r);
      const inner = storm ? "⚡" : score == null ? "–" : String(r);
      return `<li class="hr${best ? " best" : ""}${gone ? " gone" : ""}" title="${esc(`${t}: ${said}`)}">
        <span class="cell ${cls}">${inner}</span><span class="t">${t}</span></li>`;
    })
    .join("");
  // Under the strip, in words: when the best two hours are, and what ends the session early if anything does
  // The top card leaves the best hours to the highlighted cells; only an early end (storms) gets a line there
  const best = sc.window && !named ? `Best ${span(sc.window[0], sc.window[1])}` : "";
  const note = [best && `<span>${esc(best)}</span>`, sc.later && `<span class="later">${esc(sc.later)}</span>`]
    .filter(Boolean)
    .join(`<span aria-hidden="true"> · </span>`);
  return `<div class="strip-wrap">
    <ol class="strip" aria-label="${esc(`Hour by hour at ${name}: ${words.join(", ")}`)}">${cells}</ol>
    ${note ? `<p class="strip-note">${note}</p>` : ""}
  </div>`;
}

function renderHero(s: Session) {
  const c = s.conditions;
  const lead = call(s);
  const d = parse(s.date);
  const ok = worth(s);
  const leadSpot = lead.id ? spotsById[lead.id] : undefined;
  const verdict = ok
    ? `<span class="verdict"><span class="where"><button type="button" class="link top-name" data-open="${esc(lead.id ?? "")}">${esc(lead.name)}</button>${leadSpot && leadSpot.kind !== "swim" && leadSpot.kind !== "surf" ? ` <span class="tag">${TAG[leadSpot.kind]}</span>` : ""} · ${lead.rating}/10</span>
       ${whyWorth(s) ? `<span class="why worth">${esc(whyWorth(s))}</span>` : ""}</span>`
    : `<span class="why">${esc(whyNotWorth(s))}</span>`;
  // Only what matters for this session: sunrise for a morning, sunset for an evening, and that part of the day's
  // tides (a midday shows the ones from 9am to 4pm, and no sun times)
  const slot = slotOf(s);
  const morning = slot === "am";
  const tides = (s.tides ?? [])
    .filter((t) => (slot === "md" ? hourOfLabel(t.time) >= 9 && hourOfLabel(t.time) <= 16 : t.time.endsWith(morning ? "am" : "pm")))
    .map((t) => `${t.kind === "high" ? "High" : "Low"} <b>${t.time}</b>`)
    .join(" · ");
  // A chip's border is a traffic light when the stat is good or bad for a swim, using the bot's own rules;
  // tides, sun and UV are just information and stay plain
  const chip = (icon: string, label: string, value: string, rating?: number, lead = false) =>
    `<span class="chip${lead ? " lead" : ""}${rating != null ? ` edge-${ratingClass(rating).slice(2)}` : ""}">${icon}<span class="sr-only">${label}</span> ${value}</span>`;
  // Chip colours. Swim: the typical beach, the median of each bar across the ocean beaches. Surf: the best break.
  // The bars themselves are in each spot's card, so they always match that spot's score
  const surfRep = mode === "surf" && s.surf ? s.reports?.[s.surf.id] : undefined;
  const spearRep = mode === "spear" && s.spear ? s.reports?.[s.spear.id] : undefined;
  const coast = surfRep ?? spearRep ?? s.coast ?? s.report;
  const spearHere = mode === "spear" && s.spear ? s.scores.find((x) => x.id === s.spear!.id)?.here : undefined;
  const air = c.air_c >= 26 ? 10 : c.air_c >= 23 ? 8 : c.air_c >= 21 ? 6 : c.air_c >= 19 ? 4 : 2; // the scoring bands
  const rain = c.rain_pct >= 60 ? 2 : c.rain_pct >= 40 ? 5 : 10;
  // Water: how it feels going in (20°+ green, 17-19° amber, colder red). Only a colour: cool water is never
  // a minus in the scores
  const w = c.water_c;
  const water = w == null ? undefined : w >= 20 ? 8 : w >= 17 ? 6 : 3;
  // Stats on three lines by what they describe, the one that swings a session most leading each line
  const line = (label: string, chips: string) =>
    `<div class="stat-line"><span class="stat-label">${label}</span><div class="chips">${chips}</div></div>`;
  const month = d.toLocaleDateString("en-AU", { month: "short", timeZone: "UTC" });
  $("hero").classList.toggle("finished", isPast(s));
  $("hero").innerHTML = `
    <div class="hero-top">
    <h2 class="hero-title">${dayName(d, "long")} ${d.getUTCDate()} ${month} · ${slotName(s).toLowerCase()}</h2>
    <div class="headline">
      <span class="flag ${ok ? "yes" : "no"}">${ok ? (s.fire && mode === "swim" ? `<span aria-hidden="true">🔥</span> Worth it` : "Worth it") : "Not worth it"}</span>
      ${verdict}
    </div>
    </div>
    ${lead.id ? strip(s, s.scores.find((x) => x.id === lead.id), lead.name ?? "", true) : ""}
    ${isPast(s) ? `<p class="done">Finished. This is the call the bot made before it started.</p>` : ""}
    ${s.confidence === "low" ? `<p class="early">Early forecast: more than two days out, so treat it as a guide. The calendar only posts once it's two days away.</p>` : ""}
    <div class="stats-wrap">
    <div class="stats">
      ${line(
        "Weather",
        chip(ICONS.wind, "Wind", `<b>${esc(c.wind_dir)} ${speed(c.wind_kmh)}</b>, gusting up to ${speedNum(c.gust_kmh)}`, coast.Wind, true) +
          chip(ICONS.air, "Air", `Air <b>${temp(c.air_c)}</b>`, air) +
          chip(ICONS.rain, "Rain", `Rain <b>${c.rain_pct}%</b>`, rain),
      )}
      ${line(
        "Ocean",
        (mode === "surf" && c.trains?.length
          ? c.trains
              .map((t, i) =>
                chip(
                  ICONS.swell,
                  t.kind === "chop" ? "Wind chop" : t.kind === "swell2" ? "Second swell" : "Main swell",
                  `${t.kind === "chop" ? "Chop " : ""}<b>${height(t.m)} ${esc(t.dir)}</b> @ ${t.s}s`,
                  i === 0 ? coast["Wave size"] : undefined,
                  i === 0,
                ),
              )
              .join("")
          : (spearHere?.vis_m != null ? chip(ICONS.spear, "Visibility", `Vis <b>about ${spearHere.vis_m}m</b>`, coast.Visibility, true) : "") +
            chip(ICONS.swell, "Swell", `<b>${height(c.swell_m)} ${esc(c.swell_dir)}</b> @ ${c.period_s}s`, coast[surfRep ? "Wave size" : spearRep ? "Surge" : "Calm water"], !spearHere)) +
          (c.water_c != null ? chip(ICONS.water, "Water", `Water <b>${temp(c.water_c)}</b>`, water) : "") +
          (tides ? chip(ICONS.tide, "Tides", tides) : ""),
      )}
      ${line(
        "Sun",
        (s.sun && slot !== "md" ? chip(ICONS.sun, morning ? "Sunrise" : "Sunset", morning ? `Sunrise <b>${s.sun.rise}</b>` : `Sunset <b>${s.sun.set}</b>`) : "") +
          chip(ICONS.uv, "UV", `UV <b>${c.uv}</b>`),
      )}
    </div>
    </div>`;
}

// ---------------------------------------------------------------- spots: list and map
function popup(spot: Spot, sc: SpotScore | undefined) {
  // Just enough to say which spot it is; its details and warnings live in its card, not twice
  return `<div class="popup"><span class="t">${esc(spot.name)}</span> · ${spot.kind === "surf" || spot.kind === "spear" ? `${spot.kind} ` : ""}${sc ? sc.rating : 0}/10
    <span class="tag">${TAG[spot.kind]}</span> <button type="button" class="link" data-details="${spot.id}">Details</button></div>`;
}

function renderPins(s: Session) {
  if (!map || !mapApi) return; // map still loading; render() runs again when it's ready
  const byId = Object.fromEntries(s.scores.map((x) => [x.id, x]));
  Object.values(markers).forEach((m) => m.remove());
  markers = {};
  const leadId = worth(s) ? call(s).id : null; // no "top pick" ring when nothing's worth it
  // Lowest scores first so the best spots are drawn on top where pins overlap
  const order = [...data.spots].sort((a, b) => rankScore(byId[a.id]) - rankScore(byId[b.id]));
  for (const spot of order) {
    if (!shows(spot)) continue;
    const sc = byId[spot.id];
    const r = sc ? sc.rating : 0;
    const cls = ["marker", spot.kind, ratingClass(r), spot.id === leadId ? "lead" : "", spot.id === openSpot ? "open" : ""];
    markers[spot.id] = mapApi.addPin(map, spot, cls.join(" "), String(r), popup(spot, sc), () => openCard(spot.id, true));
  }
}

function card(s: Session, spot: Spot, sc: SpotScore | undefined) {
  const open = spot.id === openSpot;
  const notes = notesHtml(sc ? sc.notes : [whyNot(s, spot)]);
  const rep = s.reports?.[spot.id];
  return `<li class="spot${open ? " open" : ""}" data-id="${spot.id}">
    <button type="button" class="spot-head" aria-expanded="${open}">
      ${sc ? badge(spot.kind, sc.rating) : badge(spot.kind, 0, "ruled out, 0 out of 10")}
      <span class="body"><span class="name">${esc(spot.name)}</span>${notes ? `<span class="meta">${notes}</span>` : ""}</span>
      <span class="side">${tags(spot)}</span>
    </button>
    ${open && rep ? `<div class="details"><button type="button" class="link share" data-share="${spot.id}">Share</button>${strip(s, sc, spot.name)}${here(spot, sc)}${spot.watch_from ? `<p class="watch">Watch from ${esc(spot.watch_from)}</p>` : ""}${spot.id === "swim-clovelly" ? `<button type="button" class="link depth-open" data-depth>Under the water at Clovelly</button>` : ""}${seabed(spot)}${spot.entry ? `<p class="watch">${esc(spot.entry)}</p>` : ""}<h3>Conditions at ${esc(spot.name)}</h3><div class="report">${bars(rep)}</div>${lifeguards(s, spot)}</div>` : ""}
  </li>`;
}

// The session at this spot rather than out at sea: the swell chip up top is the offshore swell, the same for the
// whole coast, while a sheltered beach like Clovelly might only see a fraction of it at the sand
const WIND_KIND: Record<string, string> = { offshore: "offshore", cross: "cross-shore", onshore: "onshore" };
function here(spot: Spot, sc: SpotScore | undefined) {
  const h = sc?.here;
  if (!h) return "";
  const feet = (m: number) => (units.height === "ft" && m * 3.281 < 1 ? "under 1ft" : height(m));
  const [kind0, shelter0] = h.wind_kind.split(", ");
  const windWords = kind0 === "light" ? "" : `${WIND_KIND[kind0] ?? esc(kind0)}${shelter0 ? `, ${esc(shelter0)}` : ""}`;
  if (spot.kind === "spear") {
    // On the reef: what you'll see, the swell there, and how far it pushes you about on the bottom
    const parts = [
      h.vis_m != null ? `About ${h.vis_m}m visibility` : "",
      h.waves_m != null ? (h.waves_m < 0.15 ? "flat on the reef" : `${feet(h.waves_m)} of swell on the reef`) : "",
      h.surge_m != null ? (h.surge_m < 0.15 ? "next to no surge" : `surge ${feet(h.surge_m)} either way`) : "",
      windWords,
    ].filter(Boolean);
    return parts.length ? `<p class="here">${parts.join(" · ")}</p>` : "";
  }
  const trains = h.trains?.length
    ? `${h.trains.map((t) => `${feet(t.m)} ${esc(t.dir)} @ ${t.s}s`).join(", ")} at the break`
    : "";
  const waves = trains
    ? trains
    : h.waves_m === undefined
      ? ""
      : h.waves_m < 0.15
        ? "Flat"
        : `${units.height === "ft" && h.waves_m * 3.281 < 1 ? "Under 1ft" : height(h.waves_m)} ${spot.kind === "surf" ? "at the break" : "at the sand"}`;
  const [kind, shelter] = h.wind_kind.split(", ");
  const wind = kind === "light" ? "" : `${WIND_KIND[kind] ?? esc(kind)}${shelter ? `, ${esc(shelter)}` : ""}`;
  const line = [waves, wind].filter(Boolean).join(" · ");
  return line ? `<p class="here">${line.charAt(0).toUpperCase()}${line.slice(1)}</p>` : "";
}

// Spearfishing: the bottom round the pin, from the NSW seabed survey. "Reef, 4–12m deep" or "Reef and sand"
function seabed(spot: Spot) {
  const b = spot.seabed;
  if (!b) return "";
  const kind = b.reef == null ? "" : b.reef >= 0.6 ? "Reef" : b.reef >= 0.25 ? "Reef and sand" : "Mostly sand";
  const [lo, hi] = b.range_m;
  const depth = units.height === "ft" ? `${Math.round(lo * 3.281)}–${Math.round(hi * 3.281)}ft` : `${lo}–${hi}m`;
  const steep = b.steep != null && b.steep >= 0.3 ? ", with drop-offs" : "";
  const words = kind ? `${kind}${steep}, ${depth} deep` : `${depth} deep${steep}`;
  return `<p class="here">${words}</p>`;
}

// This morning's lifeguard report, on today's sessions only: it's what they saw first thing, not a forecast
function lifeguards(s: Session, spot: Spot) {
  const r = data.lifeguards?.[spot.id];
  if (!r || s.date !== data.generated_at.slice(0, 10)) return "";
  const when = new Date(r.time)
    .toLocaleTimeString("en-AU", { hour: "numeric", minute: "2-digit", timeZone: "Australia/Sydney" })
    .replace(/\s/g, "")
    .toLowerCase();
  const rows = [
    ["Beach", r.status],
    ["Waves", r.waves && localise(r.waves)],
    ["Rips", r.rips],
    ["Bluebottles", r.bluebottles],
    ["Water", r.water_c != null ? temp(r.water_c) : null],
  ].filter(([, v]) => v);
  return `<h3>Lifeguards, ${esc(when)}${r.summary ? `: ${esc(r.summary.toLowerCase())}` : ""}</h3>
    <dl class="lifeguards${r.closed ? " closed" : ""}">${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
    ${r.description ? `<p class="lifeguard-says">“${esc(r.description)}”</p>` : ""}`;
}

// The address says which card is open, so it can be copied or shared as it is
function syncSpotParam() {
  const url = new URL(location.href);
  if (openSpot) url.searchParams.set("spot", openSpot);
  else url.searchParams.delete("spot");
  url.searchParams.delete("mode"); // a spot link carries its mode in its id; otherwise the page remembers it
  if (mode !== "swim" && !openSpot) url.searchParams.set("mode", mode);
  if (!openSpot) url.searchParams.delete("depth");
  history.replaceState(null, "", url);
}

// The link for a spot in a session: the session (which says the region) and the spot (which says the mode)
function spotLink(id: string, s: Session) {
  const url = new URL(location.pathname, location.origin);
  url.searchParams.set("s", s.key);
  url.searchParams.set("spot", id);
  return url.toString();
}

async function share(id: string, btn: HTMLElement) {
  const s = data.sessions[current];
  const spot = spotsById[id];
  const url = spotLink(id, s);
  const title = `${spot.name} · ${s.label}`;
  track(`share/${id}`, spot.name);
  try {
    if (navigator.share) {
      await navigator.share({ title, url });
      return;
    }
    await navigator.clipboard.writeText(url);
    btn.textContent = "Link copied";
  } catch {
    btn.textContent = "Couldn't share"; // cancelled the share sheet, or no clipboard access
  }
  setTimeout(() => (btn.textContent = "Share"), 2000);
}

function renderSpots(s: Session) {
  const byId = Object.fromEntries(s.scores.map((x) => [x.id, x]));
  const spots = data.spots.filter(shows);
  // Swims and pools first: surf is on its own scale, so a surf 8 never sits above a swim 7
  const best = (a: Spot, b: Spot) =>
    Number(a.kind === "surf") - Number(b.kind === "surf") || rankScore(byId[b.id]) - rankScore(byId[a.id]);
  const north = (a: Spot, b: Spot) => b.lat - a.lat;
  let html: string;
  if (sort === "area") {
    // One group per place (Coogee: the beach, its surf break and its pools), north to south
    const areas = new Map<string, Spot[]>();
    for (const p of [...spots].sort(north)) areas.set(p.area ?? p.name, [...(areas.get(p.area ?? p.name) ?? []), p]);
    html = [...areas.entries()]
      .map(
        ([name, group]) =>
          `<li class="group"><h3>${esc(name)}</h3><ol>${group
            .sort(best)
            .map((p) => card(s, p, byId[p.id]))
            .join("")}</ol></li>`,
      )
      .join("");
  } else {
    html = [...spots]
      .sort(sort === "north" ? north : best)
      .map((p) => card(s, p, byId[p.id]))
      .join("");
  }
  $("spots").innerHTML = html || `<li class="empty">No spots: tick an activity to see some.</li>`;
  syncSpotParam();
  $("spots")
    .querySelectorAll<HTMLElement>(".spot")
    .forEach((li) =>
      li.querySelector(".spot-head")?.addEventListener("click", () => {
        const id = li.dataset.id as string;
        if (openSpot === id) {
          openSpot = null; // tap an open card to close it
          renderSpots(s);
          renderChart(s);
          markOpenPin();
        } else openCard(id, true);
      }),
    );
}

// A card's Share button: the phone's share sheet, else the link copied
document.addEventListener("click", (e) => {
  const btn = (e.target as HTMLElement).closest<HTMLElement>("[data-share]");
  if (btn?.dataset.share) share(btn.dataset.share, btn);
});

// Clovelly's underwater map, from its card: the seabed at 1m and the water over it through the session's day.
// While it's open the address carries &depth, so a shared link opens it too
document.addEventListener("click", (e) => {
  if ((e.target as HTMLElement).closest("[data-depth]")) openDepth();
});
async function openDepth() {
  const s = data.sessions[current];
  const { openClovelly } = await import("./clovelly");
  // Start on Clovelly's best hours this session, else the session's first hour
  const w = s.scores.find((x) => x.id === "swim-clovelly")?.window;
  const start = w ? hourOfLabel(w[0]) : Number(s.start.slice(11, 13));
  track("clovelly-depth", "Under the water at Clovelly");
  const dlg = $("depth") as HTMLDialogElement;
  await openClovelly(dlg, data.swell_hours, s.date, start);
  const url = new URL(location.href);
  url.searchParams.set("depth", "1");
  history.replaceState(null, "", url);
  dlg.onclose = () => {
    const u = new URL(location.href);
    u.searchParams.delete("depth");
    history.replaceState(null, "", u);
  };
}

// Expand a spot's card (closing any other), bring it into view, and show it on the map
// The top pick's name in the top card opens its card in the list (and flies the map to it)
document.addEventListener("click", (e) => {
  const el = (e.target as HTMLElement).closest<HTMLElement>("[data-open]");
  if (el?.dataset.open) openCard(el.dataset.open, true);
});

function openCard(id: string, fly: boolean) {
  openSpot = id;
  renderSpots(data.sessions[current]);
  renderChart(data.sessions[current]);
  markOpenPin();
  document.querySelector(`.spot[data-id="${id}"]`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  if (fly) focusPin(id);
}

// Ring the open spot's pin. Only the classes change: rebuilding the pins would close the popup just opened
function markOpenPin() {
  for (const [id, m] of Object.entries(markers)) {
    m.getElement()?.querySelector(".marker")?.classList.toggle("open", id === openSpot);
  }
}

// Fly in to a spot (never zooming back out if you're already closer) and open its popup
function focusPin(id: string) {
  const m = markers[id];
  const mapHidden = innerWidth < 860 && $("layout").dataset.view === "list"; // phone list view
  if (!m || !map || mapHidden) return;
  map.flyTo(m.getLatLng(), Math.max(map.getZoom(), 15), { duration: 0.6 });
  m.openPopup();
}

// The bot's own reason when it has one (e.g. "waves over the walls", "closed until 7am")
function whyNot(s: Session, spot: Spot) {
  const why = s.ruled_out?.[spot.id];
  return why ?? "not scored"; // lower case, like the notes on spots that are scored
}

const COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];

// Surf mode only: the week's swell, hour by hour. Redrawn when the session or the window width changes
function renderChart(s: Session) {
  const el = $("swell-chart");
  el.hidden = mode === "swim" || !data.swell_hours; // surf and spearfishing both read the swell
  if (el.hidden || !data.swell_hours) return;
  renderSwellChart(el, {
    data: data.swell_hours,
    sessions: data.sessions.filter((x) => weekOf(x) === weekOf(s)),
    selected: s,
    weekStart: monday(parse(s.date)),
    onPick: (x) => selectSession(data.sessions.indexOf(x)),
    spot: openSpot && spotsById[openSpot]?.kind === "surf" ? { id: openSpot, name: spotsById[openSpot].name } : undefined,
  });
}
let chartWidth = 0;
new ResizeObserver(() => {
  const w = $("swell-chart").clientWidth;
  if (data && w && Math.abs(w - chartWidth) > 4) {
    chartWidth = w;
    renderChart(data.sessions[current]);
  }
}).observe($("swell-chart"));

function render() {
  const s = data.sessions[current];
  week = weekOf(s);
  renderWeek();
  renderHero(s);
  renderChart(s);
  const c = s.conditions;
  if (c.wind_deg !== undefined) wind?.set(c.wind_kmh, c.gust_kmh, c.wind_deg);
  const swellDeg = c.swell_deg ?? COMPASS.indexOf(c.swell_dir) * 22.5; // older scores only have the compass point
  if (swellDeg >= 0) swell?.set(c.swell_m, swellDeg, c.period_s);
  renderPins(s);
  renderSpots(s);
}

start();
