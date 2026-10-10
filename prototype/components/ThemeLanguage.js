"use client";

import { useEffect, useState } from "react";
import { FiMoon, FiSun } from "react-icons/fi";

export default function ThemeLanguage({ compact = false }) {
  const [dark, setDark] = useState(false);
  const [bangla, setBangla] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("sts-theme");
    const next = stored === "dark";
    setDark(next);
    document.documentElement.dataset.theme = next ? "dark" : "light";
    setBangla(localStorage.getItem("sts-lang") === "bn");
  }, []);

  function toggleTheme() {
    const next = !dark;
    setDark(next);
    document.documentElement.dataset.theme = next ? "dark" : "light";
    localStorage.setItem("sts-theme", next ? "dark" : "light");
  }

  function toggleLanguage() {
    const next = !bangla;
    setBangla(next);
    document.documentElement.lang = next ? "bn" : "en";
    localStorage.setItem("sts-lang", next ? "bn" : "en");
    window.dispatchEvent(new CustomEvent("sts-language", { detail: next ? "bn" : "en" }));
  }

  return (
    <div className={`utility-controls ${compact ? "compact" : ""}`}>
      <button className="icon-button" onClick={toggleTheme} aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}>{dark ? <FiSun /> : <FiMoon />}</button>
      <button className="language-button" onClick={toggleLanguage} aria-label="Change language">{bangla ? "EN" : "বাংলা"}</button>
    </div>
  );
}
