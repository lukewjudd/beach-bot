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
  /** Every hour of the session, for the hour-by-hour strip: the score, or null when ruled out */
  hourly?: (number | null)[];
  /** Why an hour was ruled out or stormy, by its index in hourly */
  why?: Record<string, string>;
  /** What rules out the rest of the session after the best hours, e.g. "⚡ storms from 4pm" */
  later?: string;
}

export interface Session {
  key: string;
  /** The start of each hour in the session ("2pm"), matching each spot's hourly */
  hours?: string[];
  date: string;
  label: string;
  start: string;
  end: string;
  started: boolean;
  /** Worth it on the site: 8/10 or better */
  posted: boolean;
  /** In the shared calendar's event for the day: 9/10 or better (or still above 8 once in) */
  in_event?: boolean;
  fire: boolean;
  /** "low" past a couple of days out: a guide, not something the calendar posts */
  confidence?: "high" | "low";
  tides?: { kind: "high" | "low"; time: string }[];
  sun?: { rise: string; set: string } | null;
  /** Surf's own call: the best break on the surf scale, and whether it's in the day's surf event */
  surf?: SurfCall | null;
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

export interface SurfCall {
  id: string;
  name: string;
  score: number;
  rating: number;
  window: [string, string] | null;
  /** Pumping: 8/10 or better on the surf scale */
  posted: boolean;
  in_event: boolean;
}

/** A lifeguard's morning report for a beach (Randwick's patrolled beaches), as the feed has it */
export interface LifeguardReport {
  time: string;
  summary: string | null;
  status: string | null;
  closed: boolean;
  water_c: number | null;
  waves: string | null;
  rips: string | null;
  bluebottles: string | null;
  description: string | null;
}

export interface Scores {
  region?: { id: string; name: string; key: string };
  generated_at: string;
  thresholds: { post: number; fire: number; surf?: number };
  favourite?: { id: string; tolerance: number };
  spots: Spot[];
  sessions: Session[];
  /** This morning's lifeguard reports, by spot id */
  lifeguards?: Record<string, LifeguardReport>;
}
