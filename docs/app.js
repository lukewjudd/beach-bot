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

function initMap() {
  map = L.map("map", { zoomControl: false, attributionControl: true, scrollWheelZoom: false });
  // Stadia Maps: localhost works without a key; the live site is authorised by domain in the Stadia dashboard
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  L.tileLayer(`https://tiles.stadiamaps.com/tiles/${dark ? "alidade_smooth_dark" : "alidade_smooth"}/{z}/{x}/{y}{r}.png`, {
    attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 20,
  }).addTo(map);
  L.control.zoom({ position: "bottomright" }).addTo(map);
  const fit = () => map.fitBounds(L.latLngBounds(data.spots.map(s => [s.lat, s.lon])), { padding: [24, 24] });
  fit();
  // The container can settle after first paint (fonts, grid); refit once it has its final size
  new ResizeObserver(() => { map.invalidateSize(); fit(); }).observe(document.getElementById("map"));
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

function verdict(s) {
  if (s.posted) return s.fire ? "🔥 One of the best sessions. Posted to the calendar." : "Worth going. Posted to the calendar.";
  if (s.lead.rating >= 6) return "Decent, but not quite a beach call.";
  return "Not worth the trip.";
}

function render() {
  const s = data.sessions[current];
  const c = s.conditions;
  const lead = s.lead;
  const leadSpot = data.spots.find(p => p.name === lead.name && s.scores.some(x => x.id === p.id && x.score === lead.score));

  document.getElementById("hero").innerHTML = `
    <div class="wind">💨 ${esc(c.wind_dir)} ${c.wind_kmh} km/h, gusts ${c.gust_kmh} · ${esc(c.wind_desc)}</div>
    <div class="headline">
      <span class="big">${lead.rating}/10</span>
      <span class="where">${leadSpot?.kind === "surf" ? "🏄" : "🏖️"} ${esc(lead.name || "–")}</span>
      ${lead.window ? `<span class="when">best ${esc(lead.window[0])}–${esc(lead.window[1])}</span>` : ""}
    </div>
    <div class="verdict">${verdict(s)}</div>
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
  for (const spot of data.spots) {
    const sc = byId[spot.id];
    const cls = ["marker", spot.kind, sc ? ratingClass(sc.rating) : "none", spot.id === leadId ? "lead" : ""].join(" ");
    const icon = L.divIcon({ className: "", html: `<div class="${cls}">${sc ? sc.rating : "–"}</div>`, iconSize: [30, 30], iconAnchor: [15, 15] });
    const m = L.marker([spot.lat, spot.lon], { icon, title: spot.name, zIndexOffset: sc ? sc.score * 10 : 0 }).addTo(map);
    m.bindPopup(popup(spot, sc));
    m.on("click", () => highlight(spot.id, false));
    markers[spot.id] = m;
  }

  document.getElementById("spots").innerHTML = ranked.map(x => {
    const spot = spotsById[x.id];
    const meta = [spot.kind === "surf" ? "surf" : spot.snorkel ? "swim / snorkel" : "swim", ...x.notes].join(" · ");
    return `<li class="spot" data-id="${x.id}">
      ${pill(x.rating)}
      <div><div class="name">${spot.kind === "surf" ? "🏄 " : ""}${esc(spot.name)}</div><div class="meta">${esc(meta)}</div></div>
      <div class="win">${x.window ? esc(x.window.join("–")) : ""}</div>
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
    ${sc.window ? `<div class="m">Best ${esc(sc.window[0])}–${esc(sc.window[1])}</div>` : ""}
    ${sc.notes.length ? `<div class="m">${esc(sc.notes.join(" · "))}</div>` : ""}
  </div>`;
}

function highlight(id, fromList) {
  activeSpot = id;
  document.querySelectorAll(".spot").forEach(li => li.classList.toggle("active", li.dataset.id === id));
  const m = markers[id];
  if (m && fromList) {
    map.panTo(m.getLatLng());
    m.openPopup();
    document.getElementById("map").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

load();
