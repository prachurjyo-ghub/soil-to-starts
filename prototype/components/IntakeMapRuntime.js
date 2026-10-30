"use client";

import { useEffect } from "react";
import "maplibre-gl/dist/maplibre-gl.css";

// The static reference intake requests this lazy bundle only when map mode is opened.
export default function IntakeMapRuntime() {
  useEffect(() => {
    let bundle;
    const load = () => {
      bundle ??= import("maplibre-gl").then((maplibre) => {
        maplibre.setWorkerUrl(new URL("maplibre-gl/dist/maplibre-gl-worker.mjs", import.meta.url).href);
        return maplibre;
      });
      return bundle;
    };
    window.STS_LOAD_MAPLIBRE = load;
    window.STS_MAP_CONFIG = {
      styleUrl: process.env.NEXT_PUBLIC_BASEMAP_STYLE_URL || "https://tiles.openfreemap.org/styles/liberty",
      label: process.env.NEXT_PUBLIC_BASEMAP_LABEL || (process.env.NEXT_PUBLIC_BASEMAP_STYLE_URL ? "Configured reference basemap" : "OpenFreeMap Liberty"),
      isOpenFreeMap: !process.env.NEXT_PUBLIC_BASEMAP_STYLE_URL || process.env.NEXT_PUBLIC_BASEMAP_STYLE_URL === "https://tiles.openfreemap.org/styles/liberty",
    };
    document.dispatchEvent(new Event("sts-map-runtime-ready"));
    return () => {
      if (window.STS_LOAD_MAPLIBRE === load) delete window.STS_LOAD_MAPLIBRE;
      document.dispatchEvent(new Event("sts-map-runtime-dispose"));
    };
  }, []);
  return null;
}
