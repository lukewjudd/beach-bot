// Display units, remembered per browser. The bot works in km/h, metres and °C; this only changes what's shown,
// including numbers inside the bot's notes ("~1.4m at the beach").

export type Units = { wind: "kmh" | "kn" | "mph"; height: "m" | "ft"; temp: "c" | "f" };
const DEFAULTS: Units = { wind: "kmh", height: "m", temp: "c" };
const CHOICES = { wind: ["kmh", "kn", "mph"], height: ["m", "ft"], temp: ["c", "f"] } as const;

export let units: Units = { ...DEFAULTS };
try {
  const saved = JSON.parse(localStorage.getItem("units") ?? "null");
  for (const k of Object.keys(CHOICES) as (keyof Units)[]) {
    if ((CHOICES[k] as readonly string[]).includes(saved?.[k])) (units as Record<string, string>)[k] = saved[k];
  }
} catch {
  // nothing saved, private window or garbled: metric
}

export function setUnit<K extends keyof Units>(k: K, v: Units[K]) {
  units = { ...units, [k]: v };
  try {
    localStorage.setItem("units", JSON.stringify(units));
  } catch {
    // can't save: it still applies until the page reloads
  }
}

/** A wind speed's number alone ("gusting up to 19"), in the chosen unit */
export const speedNum = (kmh: number) =>
  Math.round(units.wind === "kn" ? kmh / 1.852 : units.wind === "mph" ? kmh / 1.609 : kmh);
export const speed = (kmh: number) => `${speedNum(kmh)} ${units.wind === "kmh" ? "km/h" : units.wind}`;
/** Wave height: metres to one decimal, or whole feet (as surfers say it) */
export const height = (m: number) => (units.height === "ft" ? `${Math.max(1, Math.round(m * 3.281))}ft` : `${m}m`);
export const temp = (c: number) => (units.temp === "f" ? `${Math.round((c * 9) / 5 + 32)}°F` : `${c}°`);

/** The same conversions on text: "~1.4m at the beach", "2m", "20°", "25 km/h". Rain in mm is left alone */
export const localise = (text: string) =>
  text
    .replace(/(\d+(?:\.\d+)?)m\b/g, (_, n) => height(Number(n)))
    .replace(/(\d+(?:\.\d+)?) ?km\/h/g, (_, n) => speed(Number(n)))
    .replace(/(\d+(?:\.\d+)?)°(?!F)/g, (_, n) => temp(Number(n)));
