// Shape of scores.json, written by the bot (bot/src/beach_bot/export.py) on every run.

export type SpotKind = "swim" | "surf";

export interface Spot {
  id: string;
  name: string;
  kind: SpotKind;
  snorkel?: boolean;
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
  lead: { name: string | null; score: number; rating: number; window: [string, string] | null };
  conditions: {
    wind_kmh: number;
    wind_dir: string;
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
  scores: SpotScore[];
}

export interface Scores {
  generated_at: string;
  thresholds: { post: number; fire: number };
  spots: Spot[];
  sessions: Session[];
}
