// Beach calls: renders scores.json as session tabs, a map and a ranked list.

import type { Map as LeafletMap, Marker } from "leaflet";
import "./style.css";
import type { Scores, Session, Spot, SpotKind, SpotScore } from "./types";

// Set in .env.production / .env.development; ?data= overrides it
const DATA_URL = new URLSearchParams(location.search).get("data") ?? import.meta.env.VITE_SCORES_URL;

const $ = (id: string) => document.getElementById(id) as HTMLElement;
const ratingClass = (r: number) => (r >= 9 ? "r-great" : r >= 8 ? "r-good" : r >= 6 ? "r-mid" : "r-low");
const pill = (r: number) => `<span class="pill ${ratingClass(r)}">${r}</span>`;
const esc = (s: unknown) =>
  String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c] as string);

let data: Scores;
let spotsById: Record<string, Spot>;
// The map code loads on the side: the forecast renders as soon as the scores arrive,
// and pins are added once the map is ready
const mapModule = import("./map");
let mapApi: typeof import("./map") | undefined;
let map: LeafletMap | undefined;
let wind: import("./wind").Wind | undefined;
let markers: Record<string, Marker> = {};
let current = 0;
let activeSpot: string | null = null;

const ICON: Record<SpotKind, string> = { swim: "🏖️", pool: "🏊", surf: "🏄" };
const KIND_LABEL: Record<SpotKind, string> = { swim: "Beaches", pool: "Pools", surf: "Surf" };

// Which kinds of spot to show on the map and in the list; remembered per browser
let shown = new Set<SpotKind>(["swim", "pool", "surf"]);
try {
  const saved = JSON.parse(localStorage.getItem("shown") ?? "null");
  if (Array.isArray(saved)) shown = new Set(saved);
} catch {
  // private mode or blocked storage: just show everything
}
// Wind trails on the map, off until turned on (remembered per browser)
let windOn = false;
try {
  windOn = localStorage.getItem("wind") === "on";
} catch {
  // storage blocked: default off
}

const spotMeta = (spot: Spot) => (spot.kind === "swim" ? (spot.snorkel ? "swim / snorkel" : "swim") : spot.kind);
const prefix = (spot: Spot) => (spot.kind === "swim" ? "" : `${ICON[spot.kind]} `);

// Worth it uses the calendar's own bar, and a best window only means something for spots that clear it
const worth = (score: number) => score >= data.thresholds.post;
const windowText = (x: SpotScore) => (worth(x.score) && x.window ? `${x.window[0]}–${x.window[1]}` : "");
// Ranking used everywhere on the page: score, with the favourite winning close calls like the headline does
const rankScore = (x: SpotScore) =>
  x.score + (data.favourite && x.id === data.favourite.id ? data.favourite.tolerance + 0.5 : 0);
const byRank = (a: SpotScore, b: SpotScore) => rankScore(b) - rankScore(a);
const isPast = (s: Session) => s.started && new Date(s.end) < new Date();

async function load() {
  mapModule.then((m) => {
    map = m.createMap($("map"));
    mapApi = m;
    wind = m.windLayer(map);
    wind.show(windOn);
    if (data) render(); // scores got here first: add the pins now
  });
  try {
    // Plain fetch so it picks up the <link rel="preload"> in index.html; the bucket's max-age keeps it fresh
    const res = await fetch(DATA_URL);
    if (!res.ok) throw new Error(String(res.status));
    data = await res.json();
  } catch (e) {
    $("hero").innerHTML = `<p class="error">Couldn't load the latest scores (${esc((e as Error).message)}). Try again shortly.</p>`;
    return;
  }
  spotsById = Object.fromEntries(data.spots.map((s) => [s.id, s]));
  const updated = new Date(data.generated_at).toLocaleString("en-AU", {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
    timeZone: "Australia/Sydney",
  });
  $("updated").textContent = `Eastern suburbs, Sydney · updated ${updated}`;

  const upcoming = data.sessions.findIndex((s) => !isPast(s));
  current = upcoming === -1 ? 0 : upcoming;
  renderTabs();
  renderFilters();
  render();
}

function renderFilters() {
  const el = $("filters");
  el.innerHTML =
    (Object.keys(KIND_LABEL) as SpotKind[])
      .map(
        (k) =>
          `<button class="filter" aria-pressed="${shown.has(k)}" data-kind="${k}">${ICON[k]} ${KIND_LABEL[k]}</button>`,
      )
      .join("") + `<button class="filter wind-toggle" aria-pressed="${windOn}" id="wind-toggle">💨 Wind</button>`;
  $("wind-toggle").addEventListener("click", (e) => {
    windOn = !windOn;
    (e.currentTarget as HTMLElement).setAttribute("aria-pressed", String(windOn));
    try {
      localStorage.setItem("wind", windOn ? "on" : "off");
    } catch {
      // not remembered, still works for this visit
    }
    wind?.show(windOn);
  });
  el.querySelectorAll<HTMLButtonElement>(".filter[data-kind]").forEach((b) =>
    b.addEventListener("click", () => {
      const k = b.dataset.kind as SpotKind;
      if (shown.has(k)) shown.delete(k);
      else shown.add(k);
      b.setAttribute("aria-pressed", String(shown.has(k)));
      try {
        localStorage.setItem("shown", JSON.stringify([...shown]));
      } catch {
        // not remembered, still works for this visit
      }
      render();
    }),
  );
}

function renderTabs() {
  const tabs = $("tabs");
  tabs.setAttribute("role", "tablist");
  tabs.innerHTML = data.sessions
    .map(
      (s, i) => `
    <button class="tab ${isPast(s) ? "past" : ""}" role="tab" aria-selected="${i === current}" data-i="${i}">
      ${esc(s.label)} ${pill(s.lead.rating)}${s.fire ? " 🔥" : ""}
    </button>`,
    )
    .join("");
  tabs.querySelectorAll<HTMLButtonElement>(".tab").forEach((b) =>
    b.addEventListener("click", () => {
      current = Number(b.dataset.i);
      tabs.querySelectorAll(".tab").forEach((t) => t.setAttribute("aria-selected", String(t === b)));
      render();
    }),
  );
  tabs.querySelector('[aria-selected="true"]')?.scrollIntoView({ inline: "center", block: "nearest" });
}

function renderHero(s: Session, leadSpot: Spot | undefined) {
  const c = s.conditions;
  const lead = s.lead;
  const icon = ICON[leadSpot?.kind ?? "swim"];
  // Only name a spot when it's worth going: "best option at 3/10" reads like a recommendation
  const verdict = s.posted
    ? `<span class="where">${icon} ${esc(lead.name)} · ${lead.rating}/10</span>
       ${lead.window ? `<span class="when">best ${esc(lead.window[0])}–${esc(lead.window[1])}</span>` : ""}`
    : "";
  $("hero").innerHTML = `
    <div class="headline">
      <span class="flag ${s.posted ? "yes" : "no"}">${s.posted ? (s.fire ? "🔥 Worth it" : "Worth it") : "Not worth it"}</span>
      ${verdict}
    </div>
    <div class="chips">
      <span class="chip">💨 <b>${esc(c.wind_dir)} ${c.wind_kmh} km/h</b>, gusting up to ${c.gust_kmh}</span>
      <span class="chip">Swell <b>${c.swell_m}m ${esc(c.swell_dir)}</b> @ ${c.period_s}s</span>
      <span class="chip">Air <b>${c.air_c}°</b></span>
      ${c.water_c != null ? `<span class="chip">Water <b>${c.water_c}°</b></span>` : ""}
      <span class="chip">Rain <b>${c.rain_pct}%</b></span>
      <span class="chip">UV <b>${c.uv}</b></span>
    </div>`;
}

function renderPins(s: Session, byId: Record<string, SpotScore>, leadId: string | undefined) {
  if (!map || !mapApi) return; // map still loading; render() runs again when it's ready
  Object.values(markers).forEach((m) => m.remove());
  markers = {};
  // Lowest scores first so the best spots are drawn on top where pins overlap
  const order = [...data.spots].sort((a, b) => (byId[a.id]?.score ?? -1) - (byId[b.id]?.score ?? -1));
  for (const spot of order) {
    const sc = byId[spot.id];
    if (!shown.has(spot.kind)) continue;
    const cls = ["marker", spot.kind, sc ? ratingClass(sc.rating) : "none", spot.id === leadId ? "lead" : ""].join(" ");
    markers[spot.id] = mapApi.addPin(map, spot, cls, sc ? String(sc.rating) : "–", popup(s, spot, sc), () =>
      highlight(spot.id, false),
    );
  }
}

function renderSpots(s: Session, byId: Record<string, SpotScore>) {
  const ranked = [...s.scores].filter((x) => shown.has(spotsById[x.id].kind)).sort(byRank);
  const scored = ranked.map((x) => {
    const spot = spotsById[x.id];
    const meta = [spotMeta(spot), ...x.notes].join(" · ");
    return `<li class="spot" data-id="${x.id}">
      ${pill(x.rating)}
      <div><div class="name">${prefix(spot)}${esc(spot.name)}</div><div class="meta">${esc(meta)}</div></div>
      <div class="win">${esc(windowText(x))}</div>
    </li>`;
  });
  const unsafe = data.spots
    .filter((p) => !byId[p.id] && p.kind !== "surf" && shown.has(p.kind))
    .map(
      (p) => `<li class="spot" data-id="${p.id}"><span class="pill r-low">–</span>
        <div><div class="name">${prefix(p)}${esc(p.name)}</div><div class="meta">${esc(whyNot(s, p))}</div></div><div></div></li>`,
    );
  $("spots").innerHTML = [...scored, ...unsafe].join("");
  document
    .querySelectorAll<HTMLElement>(".spot")
    .forEach((li) => li.addEventListener("click", () => highlight(li.dataset.id as string, true)));

  renderConditions(s);
}

// The session's top pick among the kinds you're showing: the overall pick if it's visible,
// otherwise the best-scoring visible spot
function topPick(s: Session): string | null {
  if (s.lead.id && shown.has(spotsById[s.lead.id]?.kind)) return s.lead.id;
  const best = s.scores.filter((x) => shown.has(spotsById[x.id].kind)).sort(byRank)[0];
  return best?.id ?? null;
}

// Conditions at the spot you've picked, or the top pick
function renderConditions(s: Session) {
  if (activeSpot && !shown.has(spotsById[activeSpot]?.kind)) activeSpot = null; // its kind was filtered out
  const id = activeSpot ?? topPick(s);
  const spot = id ? spotsById[id] : undefined;
  const picked = activeSpot !== null && spot !== undefined;
  $("conditions-title").innerHTML =
    `Conditions at ${esc(spot?.name ?? "the coast")}` +
    (picked ? ` <button class="link" id="conditions-reset">show top pick</button>` : "");
  document.getElementById("conditions-reset")?.addEventListener("click", () => {
    activeSpot = null;
    const top = topPick(s);
    document.querySelectorAll<HTMLElement>(".spot").forEach((li) => li.classList.toggle("active", li.dataset.id === top));
    renderConditions(s);
    if (top) focusPin(top); // take the map to it too
  });
  const rep = (id && s.reports?.[id]) || s.report;
  $("report").innerHTML = Object.entries(rep)
    .map(
      ([k, v]) => `
    <div class="bar"><span>${esc(k)}</span>
      <div class="track"><div class="fill ${ratingClass(v)}" style="width:${v * 10}%"></div></div>
      <span class="num">${v}/10</span></div>`,
    )
    .join("");
}

function render() {
  const s = data.sessions[current];
  const leadSpot = s.lead.id ? spotsById[s.lead.id] : undefined;
  const byId = Object.fromEntries(s.scores.map((x) => [x.id, x]));
  renderHero(s, leadSpot);
  const c = s.conditions;
  if (c.wind_deg !== undefined) wind?.set(c.wind_kmh, c.gust_kmh, c.wind_deg);
  renderPins(s, byId, leadSpot?.id);
  renderSpots(s, byId);
  // Keep the chosen spot highlighted in the list across tabs, without flying the map around again
  if (activeSpot) document.querySelector(`.spot[data-id="${activeSpot}"]`)?.classList.add("active");
}

// The bot's own reason when it has one (e.g. "waves over the walls", "closed until 7am")
function whyNot(s: Session, spot: Spot) {
  const why = s.ruled_out?.[spot.id];
  return why ? why.charAt(0).toUpperCase() + why.slice(1) : spot.kind === "pool" ? "Closed or too rough" : "Too rough";
}

function popup(s: Session, spot: Spot, sc: SpotScore | undefined) {
  if (!sc) {
    return `<div class="popup"><div class="t">${esc(spot.name)}</div><div class="m">${esc(whyNot(s, spot))}</div></div>`;
  }
  return `<div class="popup">
    <div class="t">${prefix(spot)}${esc(spot.name)} · ${sc.rating}/10</div>
    ${windowText(sc) ? `<div class="m">Best ${esc(windowText(sc))}</div>` : ""}
    ${sc.notes.length ? `<div class="m">${esc(sc.notes.join(" · "))}</div>` : ""}
  </div>`;
}

function highlight(id: string, fromList: boolean) {
  activeSpot = id;
  document.querySelectorAll<HTMLElement>(".spot").forEach((li) => li.classList.toggle("active", li.dataset.id === id));
  renderConditions(data.sessions[current]);
  focusPin(id);
  if (fromList) $("map").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Fly in to a spot (never zooming back out if you're already closer) and open its popup
function focusPin(id: string) {
  const m = markers[id];
  if (!m || !map) return;
  map.flyTo(m.getLatLng(), Math.max(map.getZoom(), 15), { duration: 0.6 });
  m.openPopup(); // Leaflet closes any other open popup
}

load();
