// Beach calls: renders scores.json (written by beach_bot.py on every run) as tabs, a map and a ranked list.

const REMOTE_DATA = "https://storage.googleapis.com/beach-bot-513422-beach-scores/scores.json";
const params = new URLSearchParams(location.search);
const DATA_URL = params.get("data")
  || (["localhost", "127.0.0.1", ""].includes(location.hostname) ? "scores.json" : REMOTE_DATA);

const ratingClass = r => r >= 9 ? "r-great" : r >= 8 ? "r-good" : r >= 6 ? "r-mid" : "r-low";
const pill = r => `<span class="pill ${ratingClass(r)}">${r}</span>`;
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let data, spotsById, map, markers = {}, current = 0, activeSpot = null;

async function load() {
  try {
    const res = await fetch(DATA_URL, { cache: "no-cache" });
    if (!res.ok) throw new Error(res.status);
    data = await res.json();
  } catch (e) {
    document.getElementById("hero").innerHTML = `<p class="error">Couldn't load the latest scores (${esc(e.message)}). Try again shortly.</p>`;
    return;
  }
  spotsById = Object.fromEntries(data.spots.map(s => [s.id, s]));
  const updated = new Date(data.generated_at);
  document.getElementById("updated").textContent =
    `Eastern suburbs, Sydney · updated ${updated.toLocaleString("en-AU", { weekday: "short", hour: "numeric", minute: "2-digit", timeZone: "Australia/Sydney" })}`;

  const upcoming = data.sessions.findIndex(s => !s.started || new Date(s.end) > new Date());
  current = upcoming === -1 ? 0 : upcoming;
  initMap();
  renderTabs();
  render();
}

// Self-hosted map: a Protomaps PMTiles extract of the eastern suburbs, plus fonts and sprites, all in docs/map/.
// GitHub Pages serves byte ranges, so MapLibre reads tiles straight out of the one file.
const MAP_BASE = location.origin + location.pathname.replace(/[^/]*$/, "") + "map/";
const MAP_BOUNDS = [[151.17, -34.01], [151.32, -33.83]];   // must sit inside the extract's bbox

function initMap() {
  const protocol = new pmtiles.Protocol();
  maplibregl.addProtocol("pmtiles", protocol.tile);
  const flavor = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  map = new maplibregl.Map({
    container: "map",
    style: {
      version: 8,
      glyphs: MAP_BASE + "fonts/{fontstack}/{range}.pbf",
      sprite: MAP_BASE + "sprites/" + flavor,
      sources: {
        protomaps: {
          type: "vector",
          url: "pmtiles://" + MAP_BASE + "eastern-suburbs.pmtiles",
          attribution: '<a href="https://protomaps.com">Protomaps</a> &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
        },
      },
      layers: basemaps.layers("protomaps", basemaps.namedFlavor(flavor), { lang: "en" }),
    },
    maxBounds: MAP_BOUNDS,
    minZoom: 10,
    maxZoom: 17,
    cooperativeGestures: true,   // one-finger scroll moves the page on phones, not the map
    attributionControl: { compact: true },
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
  const bounds = data.spots.reduce((b, s) => b.extend([s.lon, s.lat]), new maplibregl.LngLatBounds());
  const fit = () => map.fitBounds(bounds, { padding: 32, duration: 0 });
  fit();
  // The container can settle after first paint (fonts, grid); refit once it has its final size
  new ResizeObserver(() => { map.resize(); fit(); }).observe(document.getElementById("map"));
}

function renderTabs() {
  const tabs = document.getElementById("tabs");
  tabs.setAttribute("role", "tablist");
  tabs.innerHTML = data.sessions.map((s, i) => `
    <button class="tab ${s.started && new Date(s.end) < new Date() ? "past" : ""}" role="tab"
            aria-selected="${i === current}" data-i="${i}">
      ${esc(s.label)} ${pill(s.lead.rating)}${s.fire ? " 🔥" : ""}
    </button>`).join("");
  tabs.querySelectorAll(".tab").forEach(b => b.addEventListener("click", () => {
    current = +b.dataset.i;
    activeSpot = null;
    tabs.querySelectorAll(".tab").forEach(t => t.setAttribute("aria-selected", t === b));
    render();
  }));
  tabs.querySelector('[aria-selected="true"]')?.scrollIntoView({ inline: "center", block: "nearest" });
}

// A best window only means something when the spot is worth going to
const worth = score => score >= data.thresholds.post;
const windowText = x => worth(x.score) && x.window ? `${x.window[0]}–${x.window[1]}` : "";

function render() {
  const s = data.sessions[current];
  const c = s.conditions;
  const lead = s.lead;
  const leadSpot = data.spots.find(p => p.name === lead.name && s.scores.some(x => x.id === p.id && x.score === lead.score));

  const icon = leadSpot?.kind === "surf" ? "🏄" : "🏖️";
  document.getElementById("hero").innerHTML = `
    <div class="wind">💨 ${esc(c.wind_dir)} ${c.wind_kmh} km/h, gusting up to ${c.gust_kmh} km/h</div>
    <div class="headline">
      <span class="flag ${s.posted ? "yes" : "no"}">${s.posted ? (s.fire ? "🔥 Worth it" : "Worth it") : "Not worth it"}</span>
      ${s.posted
        ? `<span class="where">${icon} ${esc(lead.name)} · ${lead.rating}/10</span>
           ${lead.window ? `<span class="when">best ${esc(lead.window[0])}–${esc(lead.window[1])}</span>` : ""}`
        : `<span class="when">best option ${esc(lead.name || "–")} at ${lead.rating}/10</span>`}
    </div>
    <div class="chips">
      <span class="chip">Swell <b>${c.swell_m}m ${esc(c.swell_dir)}</b> @ ${c.period_s}s</span>
      <span class="chip">Air <b>${c.air_c}°</b></span>
      ${c.water_c != null ? `<span class="chip">Water <b>${c.water_c}°</b></span>` : ""}
      <span class="chip">Rain <b>${c.rain_pct}%</b></span>
      <span class="chip">UV <b>${c.uv}</b></span>
    </div>`;

  const ranked = [...s.scores].sort((a, b) => b.score - a.score);
  const leadId = leadSpot?.id;

  // Markers: every spot, coloured by this session's rating; spots with no score (unsafe/unsurfable) are hollow
  Object.values(markers).forEach(m => m.remove());
  markers = {};
  const byId = Object.fromEntries(s.scores.map(x => [x.id, x]));
  // Lowest scores first so the best spots are drawn on top where markers overlap
  const order = [...data.spots].sort((a, b) => (byId[a.id]?.score ?? -1) - (byId[b.id]?.score ?? -1));
  for (const spot of order) {
    const sc = byId[spot.id];
    if (spot.kind === "surf" && !sc) continue;   // surf not working: no marker, so it can't be mistaken for the beach
    // MapLibre positions this outer element with a transform; styling lives on the inner pin so our CSS
    // (position, borders) can't fight that and make pins drift while zooming
    const el = document.createElement("div");
    el.title = spot.name;
    const cls = ["marker", spot.kind, sc ? ratingClass(sc.rating) : "none", spot.id === leadId ? "lead" : ""].join(" ");
    el.innerHTML = `<div class="${cls}">${sc ? sc.rating : "–"}${spot.kind === "surf" ? '<span class="badge">🏄</span>' : ""}</div>`;
    el.addEventListener("click", () => highlight(spot.id, false));
    markers[spot.id] = new maplibregl.Marker({ element: el })
      .setLngLat([spot.lon, spot.lat])
      .setPopup(new maplibregl.Popup({ offset: 18, closeButton: false }).setHTML(popup(spot, sc)))
      .addTo(map);
  }

  document.getElementById("spots").innerHTML = ranked.map(x => {
    const spot = spotsById[x.id];
    const meta = [spot.kind === "surf" ? "surf" : spot.snorkel ? "swim / snorkel" : "swim", ...x.notes].join(" · ");
    return `<li class="spot" data-id="${x.id}">
      ${pill(x.rating)}
      <div><div class="name">${spot.kind === "surf" ? "🏄 " : ""}${esc(spot.name)}</div><div class="meta">${esc(meta)}</div></div>
      <div class="win">${esc(windowText(x))}</div>
    </li>`;
  }).join("") + data.spots.filter(p => !byId[p.id] && p.kind === "swim").map(p =>
    `<li class="spot" data-id="${p.id}"><span class="pill r-low">–</span><div><div class="name">${esc(p.name)}</div><div class="meta">too rough or unsafe this session</div></div><div></div></li>`
  ).join("");
  document.querySelectorAll(".spot").forEach(li => li.addEventListener("click", () => highlight(li.dataset.id, true)));

  document.getElementById("report").innerHTML = Object.entries(s.report).map(([k, v]) => `
    <div class="bar"><span>${esc(k)}</span>
      <div class="track"><div class="fill ${ratingClass(v)}" style="width:${v * 10}%"></div></div>
      <span class="num">${v}/10</span></div>`).join("");

  if (activeSpot) highlight(activeSpot, false);
}

function popup(spot, sc) {
  if (!sc) return `<div class="popup"><div class="t">${esc(spot.name)}</div><div class="m">${spot.kind === "surf" ? "Not working this session" : "Too rough or unsafe this session"}</div></div>`;
  return `<div class="popup">
    <div class="t">${spot.kind === "surf" ? "🏄 " : ""}${esc(spot.name)} · ${sc.rating}/10</div>
    ${windowText(sc) ? `<div class="m">Best ${esc(windowText(sc))}</div>` : ""}
    ${sc.notes.length ? `<div class="m">${esc(sc.notes.join(" · "))}</div>` : ""}
  </div>`;
}

function highlight(id, fromList) {
  activeSpot = id;
  document.querySelectorAll(".spot").forEach(li => li.classList.toggle("active", li.dataset.id === id));
  const m = markers[id];
  if (m && fromList) {
    Object.values(markers).forEach(o => o !== m && o.getPopup().isOpen() && o.togglePopup());
    map.easeTo({ center: m.getLngLat() });
    if (!m.getPopup().isOpen()) m.togglePopup();
    document.getElementById("map").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

load();
