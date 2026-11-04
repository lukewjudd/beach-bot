// Beach calls: renders scores.json as a week of days, a summary of the chosen session, a map and a list of spots.

import type { Map as LeafletMap, Marker } from "leaflet";
import { ICONS } from "./icons";
import "./style.css";
import type { Scores, Session, Spot, SpotKind, SpotScore } from "./types";

// Set in .env.production / .env.development; ?data= overrides it
const params = new URLSearchParams(location.search);
const DATA_URL = params.get("data") ?? import.meta.env.VITE_SCORES_URL;
const REFRESH_MS = 5 * 60_000; // the bot runs hourly; checking every 5 minutes keeps an open tab current
const STALE_MINS = 60;

const $ = (id: string) => document.getElementById(id) as HTMLElement;
// Traffic lights: green is worth going (the calendar's bar), amber is so-so, red is don't bother
const ratingClass = (r: number) => (r >= 8 ? "r-green" : r >= 5 ? "r-amber" : "r-red");
const pill = (r: number) => `<span class="pill ${ratingClass(r)}" aria-label="${r} out of 10">${r}</span>`;
// A spot's score with an icon for its kind: the same badge as its pin on the map
const badge = (kind: SpotKind, r: number, label = `${r} out of 10`) =>
  `<span class="score ${ratingClass(r)}" aria-label="${label}">${ICONS[kind]}<span>${r}</span></span>`;
const esc = (s: unknown) =>
  String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c] as string);
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
let markers: Record<string, Marker> = {};

let current = 0; // index into data.sessions
let week = 0; // 0 = this week, 1 = next
let openSpot: string | null = null; // the card that's expanded
type Activity = "all" | "swim" | "snorkel" | "pool" | "surf";
let activity = (load("activity") as Activity) ?? "all";
let sort = load("sort") ?? "best";
let windOn = load("wind") === "on";

const TAG: Record<SpotKind, string> = { swim: "Beach", pool: "Pool", surf: "Surf" };
const tags = (spot: Spot) =>
  `<span class="tag">${TAG[spot.kind]}</span>` + (spot.snorkel ? `<span class="tag">Snorkel</span>` : "");
const shows = (spot: Spot) =>
  activity === "all" || (activity === "snorkel" ? !!spot.snorkel : spot.kind === activity);

// Notes that should change your mind stand out from the nice-to-knows ("wave pool fun")
const WARN = /pollution|bluebottle|rain|murky|closed|shut|washy|rough|storm|southerly|upwelling|waves|swell|at the beach/i;
const notesHtml = (notes: string[]) =>
  notes
    .map((n) => (WARN.test(n) ? `<span class="warn"><span aria-hidden="true">⚠</span> ${esc(n)}</span>` : esc(n)))
    .join(" · ");

// Worth it: the calendar's own rule. Further out than the calendar posts, an 8/10 still counts, as an early guess
const worth = (s: Session) => s.posted || (s.confidence === "low" && s.lead.score >= data.thresholds.post);
const windowText = (x: SpotScore) =>
  x.score >= data.thresholds.post && x.window ? `${x.window[0]}–${x.window[1]}` : "";
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
const slotName = (s: Session) => (s.key.endsWith("am") ? "Morning" : "Evening");
const weekOf = (s: Session) => Math.floor((parse(s.date).getTime() - monday(today()).getTime()) / (7 * DAY));

// ---------------------------------------------------------------- loading and refreshing
async function start() {
  mapModule.then((m) => {
    map = m.createMap($("map"));
    mapApi = m;
    wind = m.windLayer(map);
    wind.show(windOn);
    m.windButton(map, windOn, toggleWind);
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
  setInterval(renderUpdated, 60_000);
  setInterval(refresh, REFRESH_MS);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") refresh();
  });
}

// Take on a scores.json, keeping the chosen session (or the one in the link) if it's there
function adopt(next: Scores, wantKey: string | null) {
  data = next;
  spotsById = Object.fromEntries(data.spots.map((s) => [s.id, s]));
  const wanted = wantKey ? data.sessions.findIndex((s) => s.key === wantKey) : -1;
  const upcoming = data.sessions.findIndex((s) => !isPast(s));
  current = wanted >= 0 ? wanted : upcoming >= 0 ? upcoming : 0;
  renderUpdated();
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
    `Eastern suburbs, Sydney · <span title="${esc(exact)}">updated ${age ? `${age} ago` : "just now"}</span>`;
  const stale = $("stale");
  stale.hidden = mins <= STALE_MINS;
  stale.textContent = `These scores are ${age} old, so conditions may have changed. The page updates itself when new ones arrive.`;
}

// ---------------------------------------------------------------- controls
function toggleWind() {
  windOn = !windOn;
  save("wind", windOn ? "on" : "off");
  wind?.show(windOn);
  return windOn;
}

function wireControls() {
  const about = $("about") as HTMLDialogElement;
  $("about-open").addEventListener("click", () => about.showModal());
  $("about-close").addEventListener("click", () => about.close());
  about.addEventListener("click", (e) => {
    if (e.target === about) about.close(); // a tap on the backdrop
  });
  const act = $("activity") as HTMLSelectElement;
  const srt = $("sort") as HTMLSelectElement;
  act.value = activity;
  srt.value = sort;
  act.addEventListener("change", () => {
    activity = act.value as Activity;
    save("activity", activity);
    render();
  });
  srt.addEventListener("change", () => {
    sort = srt.value;
    save("sort", sort);
    renderSpots(data.sessions[current]);
  });
  // Phones: the list or the map, one at a time
  $("view-toggle")
    .querySelectorAll<HTMLButtonElement>("button")
    .forEach((b) => b.addEventListener("click", () => setView(b.dataset.view as "list" | "map")));
  // "Details" in a map popup opens that spot's card
  document.addEventListener("click", (e) => {
    const id = (e.target as HTMLElement).closest<HTMLElement>("[data-details]")?.dataset.details;
    if (!id) return;
    setView("list");
    openCard(id, false);
  });
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
  // Each day shows its morning and evening score side by side; tapping one opens that session
  $("days").innerHTML = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start.getTime() + i * DAY);
    const date = ymd(d);
    const daySessions = data.sessions.map((s, idx) => ({ s, idx })).filter(({ s }) => s.date === date);
    const low = daySessions.length > 0 && daySessions.every(({ s }) => s.confidence === "low");
    const slot = (code: "am" | "pm", label: string) => {
      const found = daySessions.find(({ s }) => s.key.endsWith(code));
      const live = found && !isPast(found.s);
      const name = `${dayName(d, "long")} ${code === "am" ? "morning" : "evening"}`;
      return `<button type="button" class="slot" ${live ? `data-i="${found.idx}"` : "disabled"}
          aria-pressed="${found?.idx === current}" aria-label="${name}${live ? `, ${found.s.lead.rating} out of 10` : ", no forecast"}">
        <span class="lbl">${label}</span>${live ? pill(found.s.lead.rating) : `<span class="pill none">–</span>`}
      </button>`;
    };
    return `<div class="day${low ? " low" : ""}${date === selectedDate ? " selected" : ""}">
      <span class="dh"><span class="dn">${date === ymd(today()) ? "Today" : dayName(d)}</span><span class="dd">${d.getUTCDate()}</span></span>
      ${slot("am", "AM")}${slot("pm", "PM")}
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
      <span class="num">${v}/10</span></div>`,
    )
    .join("");
}

// One line on why it isn't worth it: the reason most spots are ruled out, or the weakest conditions.
// Says what's wrong without naming a spot.
function whyNotWorth(s: Session) {
  const top = `Nothing above ${s.lead.rating}/10`;
  const counts = new Map<string, number>();
  Object.values(s.ruled_out ?? {}).forEach((r) => counts.set(r, (counts.get(r) ?? 0) + 1));
  const [reason, n] = [...counts.entries()].sort((a, b) => b[1] - a[1])[0] ?? ["", 0];
  const swimmable = data.spots.filter((p) => p.kind !== "surf").length;
  if (n >= 3) return `${top} · ${reason} at ${n} of ${swimmable} beaches and pools`;
  const weak = Object.entries(s.coast ?? s.report)
    .filter(([, v]) => v <= 4)
    .sort((a, b) => a[1] - b[1])
    .slice(0, 2)
    .map(([k, v]) => `${k.toLowerCase()} ${v}/10`);
  return weak.length ? `${top} · ${weak.join(", ")}` : top;
}

function renderHero(s: Session) {
  const c = s.conditions;
  const lead = s.lead;
  const d = parse(s.date);
  const ok = worth(s);
  const leadSpot = lead.id ? spotsById[lead.id] : undefined;
  const verdict = ok
    ? `<span class="where">${esc(lead.name)}${leadSpot && leadSpot.kind !== "swim" ? ` <span class="tag">${TAG[leadSpot.kind]}</span>` : ""} · ${lead.rating}/10</span>
       ${lead.window ? `<span class="when">best ${esc(lead.window[0])}–${esc(lead.window[1])}</span>` : ""}`
    : `<span class="why">${esc(whyNotWorth(s))}</span>`;
  const tides = (s.tides ?? []).map((t) => `${t.kind === "high" ? "High" : "Low"} ${t.time}`).join(" · ");
  const chip = (icon: string, label: string, value: string) =>
    `<span class="chip">${icon}<span class="sr-only">${label}</span> ${value}</span>`;
  const month = d.toLocaleDateString("en-AU", { month: "short", timeZone: "UTC" });
  $("hero").innerHTML = `
    <h2 class="hero-title">${dayName(d, "long")} ${d.getUTCDate()} ${month} · ${slotName(s).toLowerCase()}</h2>
    <div class="headline">
      <span class="flag ${ok ? "yes" : "no"}">${ok ? (s.fire ? `<span aria-hidden="true">🔥</span> Worth it` : "Worth it") : "Not worth it"}</span>
      ${verdict}
    </div>
    ${s.confidence === "low" ? `<p class="early">Early forecast: more than two days out, so treat it as a guide. The calendar only posts once it's two days away.</p>` : ""}
    <div class="chips">
      ${chip(ICONS.wind, "Wind", `<b>${esc(c.wind_dir)} ${c.wind_kmh} km/h</b>, gusting up to ${c.gust_kmh}`)}
      ${chip(ICONS.swell, "Swell", `<b>${c.swell_m}m ${esc(c.swell_dir)}</b> @ ${c.period_s}s`)}
      ${chip(ICONS.air, "Air", `Air <b>${c.air_c}°</b>`)}
      ${c.water_c != null ? chip(ICONS.water, "Water", `Water <b>${c.water_c}°</b>`) : ""}
      ${chip(ICONS.rain, "Rain", `Rain <b>${c.rain_pct}%</b>`)}
      ${chip(ICONS.uv, "UV", `UV <b>${c.uv}</b>`)}
      ${s.sun ? chip(ICONS.sun, "Sun", `Sunrise <b>${s.sun.rise}</b> · sunset <b>${s.sun.set}</b>`) : ""}
      ${tides ? chip(ICONS.tide, "Tides", tides) : ""}
    </div>
    <h3 class="coast-title">Across the coast</h3>
    <div class="report coast">${bars(s.coast ?? s.report)}</div>`;
}

// ---------------------------------------------------------------- spots: list and map
function popup(spot: Spot, sc: SpotScore | undefined) {
  // Just enough to say which spot it is; its details and warnings live in its card, not twice
  return `<div class="popup"><span class="t">${esc(spot.name)}</span> · ${sc ? sc.rating : 0}/10
    <span class="tag">${TAG[spot.kind]}</span> <button type="button" class="link" data-details="${spot.id}">Details</button></div>`;
}

function renderPins(s: Session) {
  if (!map || !mapApi) return; // map still loading; render() runs again when it's ready
  const byId = Object.fromEntries(s.scores.map((x) => [x.id, x]));
  Object.values(markers).forEach((m) => m.remove());
  markers = {};
  const leadId = worth(s) ? s.lead.id : null; // no "top pick" ring when nothing's worth it
  // Lowest scores first so the best spots are drawn on top where pins overlap
  const order = [...data.spots].sort((a, b) => rankScore(byId[a.id]) - rankScore(byId[b.id]));
  for (const spot of order) {
    if (!shows(spot)) continue;
    const sc = byId[spot.id];
    const r = sc ? sc.rating : 0;
    const cls = ["marker", spot.kind, ratingClass(r), spot.id === leadId ? "lead" : "", spot.id === openSpot ? "open" : ""];
    markers[spot.id] = mapApi.addPin(map, spot, cls.join(" "), String(r), popup(spot, sc), () => openCard(spot.id, false));
  }
}

function card(s: Session, spot: Spot, sc: SpotScore | undefined) {
  const open = spot.id === openSpot;
  const notes = notesHtml(sc ? sc.notes : [whyNot(s, spot)]);
  const win = sc ? windowText(sc) : "";
  const rep = s.reports?.[spot.id];
  return `<li class="spot${open ? " open" : ""}" data-id="${spot.id}">
    <button type="button" class="spot-head" aria-expanded="${open}">
      ${sc ? badge(spot.kind, sc.rating) : badge(spot.kind, 0, "ruled out, 0 out of 10")}
      <span class="body"><span class="name">${esc(spot.name)}</span>${notes ? `<span class="meta">${notes}</span>` : ""}</span>
      <span class="side">${tags(spot)}${win ? `<span class="win">${esc(win)}</span>` : ""}</span>
    </button>
    ${open && rep ? `<div class="details"><h3>Conditions at ${esc(spot.name)}</h3><div class="report">${bars(rep)}</div></div>` : ""}
  </li>`;
}

function renderSpots(s: Session) {
  const byId = Object.fromEntries(s.scores.map((x) => [x.id, x]));
  const spots = data.spots.filter(shows);
  const best = (a: Spot, b: Spot) => rankScore(byId[b.id]) - rankScore(byId[a.id]);
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
  $("spots").innerHTML = html || `<li class="empty">No spots for this activity.</li>`;
  $("spots")
    .querySelectorAll<HTMLElement>(".spot")
    .forEach((li) =>
      li.querySelector(".spot-head")?.addEventListener("click", () => {
        const id = li.dataset.id as string;
        if (openSpot === id) {
          openSpot = null; // tap an open card to close it
          renderSpots(s);
          markOpenPin();
        } else openCard(id, true);
      }),
    );
}

// Expand a spot's card (closing any other), bring it into view, and show it on the map
function openCard(id: string, fromList: boolean) {
  openSpot = id;
  renderSpots(data.sessions[current]);
  markOpenPin();
  document.querySelector(`.spot[data-id="${id}"]`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  if (fromList) focusPin(id);
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

function render() {
  const s = data.sessions[current];
  week = weekOf(s);
  renderWeek();
  renderHero(s);
  const c = s.conditions;
  if (c.wind_deg !== undefined) wind?.set(c.wind_kmh, c.gust_kmh, c.wind_deg);
  renderPins(s);
  renderSpots(s);
}

start();
