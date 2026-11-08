// Line icons (24px grid, stroked in currentColor) for spot kinds on the pins and for the conditions chips.
// Kept as strings so they can go straight into Leaflet's divIcon HTML.

const svg = (body: string) =>
  `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`;

export const ICONS = {
  // Swimmer over a wave
  swim: svg(
    '<circle cx="16" cy="5.5" r="2"/><path d="M4 12l5-3 3 2.5 3-2"/><path d="M2 17c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/>',
  ),
  // Swimmer in a netted harbour cove
  harbour: svg(
    '<circle cx="16" cy="6.5" r="2"/><path d="M5 13l4.5-3 3 2.5 3-2"/><path d="M2 18c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 21h20M2 21V9M22 21V9" stroke-dasharray="2 2"/>',
  ),
  // Pool ladder
  pool: svg(
    '<path d="M8 20V6a2 2 0 0 1 4 0"/><path d="M16 20V6a2 2 0 0 1 4 0"/><path d="M8 10h8M8 15h8"/><path d="M2 20c1.5 0 1.5-1 3-1s1.5 1 3 1"/>',
  ),
  // Surfboard
  surf: svg('<path d="M18 3c2.5 2.5-1 9-5 13s-8.5 6.5-10 5S4 13 8 9s7.5-8.5 10-6z"/><path d="M6 18l9-9"/>'),
  // Settings
  cog: svg(
    '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
  ),
  wind: svg('<path d="M3 8h11a3 3 0 1 0-3-3"/><path d="M3 12h15a3 3 0 1 1-3 3"/><path d="M3 16h7"/>'),
  swell: svg(
    '<path d="M2 9c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2"/><path d="M2 15c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2"/>',
  ),
  air: svg(
    '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  ),
  water: svg('<path d="M10 14V4a2 2 0 1 1 4 0v10a4 4 0 1 1-4 0z"/>'),
  rain: svg('<path d="M7 15a4 4 0 1 1 1-7.9A5 5 0 0 1 18 8a3.5 3.5 0 0 1 0 7z"/><path d="M8 19l-1 2M12 19l-1 2M16 19l-1 2"/>'),
  uv: svg('<circle cx="12" cy="12" r="5"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3"/>'),
  // Sun on the horizon
  sun: svg('<path d="M2 18h20"/><path d="M7 18a5 5 0 0 1 10 0"/><path d="M12 6v3M4.9 10.9l2.1 2.1M19.1 10.9 17 13"/>'),
  tide: svg('<path d="M2 12c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2 2-2 4-2"/><path d="M12 22v-6M9 19l3 3 3-3"/>'),
};
