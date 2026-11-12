import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";

export default defineConfig([
  ...nextVitals,
  // Supplied static reference bundles are preserved assets, not maintained app source.
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts", "public/**", "reference/**"]),
]);
