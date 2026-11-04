// Shape of scores.json, written by the bot (bot/src/beach_bot/export.py) on every run.

export type SpotKind = "swim" | "harbour" | "pool" | "surf";

export interface Spot {
  id: string;
  name: string;
  kind: SpotKind;
  snorkel?: boolean;
  women_only?: boolean;
  /** The place it belongs to, e.g. Coogee for the beach, its surf break and its pools */
  area?: string;
  lat: number;
  lon: number;
}

export interface SpotScore {
  id: string;
  score: number;
  rating: number;
  window: [string, string] | null;
  notes: string[];
}

export interface Session {
  key: string;
  date: string;
  label: string;
  start: string;
  end: string;
  started: boolean;
  /** Worth it: the same rule the calendar uses, so the site and calendar always agree */
  posted: boolean;
  fire: boolean;
  /** "low" past a couple of days out: a guide, not something the calendar posts */
  confidence?: "high" | "low";
  tides?: { kind: "high" | "low"; time: string }[];
  sun?: { rise: string; set: string } | null;
  lead: { id: string | null; kind: SpotKind; name: string | null; score: number; rating: number; window: [string, string] | null };
  conditions: {
    wind_kmh: number;
    wind_dir: string;
    wind_deg?: number;
    gust_kmh: number;
    wind_desc: string;
    swell_m: number;
    swell_dir: string;
    period_s: number;
    air_c: number;
    water_c: number | null;
    rain_pct: number;
    uv: number;
  };
  report: Record<string, number>;
  /** The typical beach: the median of each row across every beach */
  coast?: Record<string, number>;
  /** Conditions at each spot, by spot id */
  reports?: Record<string, Record<string, number>>;
  /** Spots that are a no-go all session, and why (e.g. "waves over the walls") */
  ruled_out?: Record<string, string>;
  scores: SpotScore[];
}

export interface Scores {
  region?: { id: string; name: string; key: string };
  generated_at: string;
  thresholds: { post: number; fire: number };
  favourite?: { id: string; tolerance: number };
  spots: Spot[];
  sessions: Session[];
}
