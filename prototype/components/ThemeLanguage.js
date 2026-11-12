"use client";

import { useEffect, useSyncExternalStore } from "react";
import { FiMoon, FiSun } from "react-icons/fi";

function subscribePreferences(callback) {
  window.addEventListener("storage", callback);
  window.addEventListener("sts-preferences", callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener("sts-preferences", callback);
  };
}

function storedPreference(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}

export default function ThemeLanguage({ compact = false }) {
  const dark = useSyncExternalStore(subscribePreferences, () => storedPreference("sts-theme") === "dark", () => false);
  const bangla = useSyncExternalStore(subscribePreferences, () => storedPreference("sts-lang") === "bn", () => false);

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    document.documentElement.lang = bangla ? "bn" : "en";
  }, [dark, bangla]);

  function toggleTheme() {
    localStorage.setItem("sts-theme", dark ? "light" : "dark");
    window.dispatchEvent(new Event("sts-preferences"));
  }

  function toggleLanguage() {
    const language = bangla ? "en" : "bn";
    localStorage.setItem("sts-lang", language);
    window.dispatchEvent(new Event("sts-preferences"));
    window.dispatchEvent(new CustomEvent("sts-language", { detail: language }));
  }

  return (
    <div className={`utility-controls ${compact ? "compact" : ""}`}>
      <button className="icon-button" onClick={toggleTheme} aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}>{dark ? <FiSun /> : <FiMoon />}</button>
      <button className="language-button" onClick={toggleLanguage} aria-label="Change language">{bangla ? "EN" : "বাংলা"}</button>
    </div>
  );
}
