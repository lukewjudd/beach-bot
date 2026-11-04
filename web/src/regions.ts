// The stretches of coast the bot scores (bot/src/beach_bot/beaches.py, REGIONS). The site picks one from the
// link (a session key's prefix says which region it's from), then the browser's last choice, then Eastern.

export interface Region {
  id: string;
  name: string;
  key: string; // session key prefix, e.g. beach20261107am
  tiles: string; // map/<tiles>.pmtiles in the bucket
  bounds: [[number, number], [number, number]]; // where the map can pan, inside the tiles' bbox
  fit: [[number, number], [number, number]]; // the first view: every spot, before the scores arrive
}

export const REGIONS: Region[] = [
  {
    id: "eastern",
    name: "Eastern suburbs",
    key: "beach",
    tiles: "eastern-suburbs",
    bounds: [
      [-34.05, 151.05],
      [-33.8, 151.4],
    ],
    fit: [
      [-33.982, 151.2505],
      [-33.889, 151.284], // the ocean coast, Bondi to Little Bay; ticking Harbour widens it
    ],
  },
  {
    id: "northern",
    name: "Northern beaches",
    key: "north",
    tiles: "northern-beaches",
    bounds: [
      [-33.87, 151.05],
      [-33.53, 151.45],
    ],
    fit: [
      [-33.805, 151.27],
      [-33.578, 151.335],
    ],
  },
];

export function pickRegion(params: URLSearchParams): Region {
  const s = params.get("s") ?? "";
  const fromLink = REGIONS.find((r) => s.startsWith(r.key));
  if (fromLink) return fromLink;
  let saved: string | null = null;
  try {
    saved = localStorage.getItem("region");
  } catch {
    // storage blocked: default
  }
  return REGIONS.find((r) => r.id === saved) ?? REGIONS[0];
}
