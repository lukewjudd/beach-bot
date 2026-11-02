import { defineConfig } from "vite";

// Served from https://lukewjudd.github.io/beach-bot/
export default defineConfig({
  base: "/beach-bot/",
  build: { chunkSizeWarningLimit: 1500 }, // MapLibre alone is ~1MB; one cached chunk is fine for this site
});
