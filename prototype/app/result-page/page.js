/* eslint-disable @next/next/no-css-tags -- Supplied reference styles/fonts retain their loading order; migration requires visual and font-rights review. */
import Script from "next/script";
import { getReferenceBody } from "@/lib/reference";

export const metadata = {
  title: "Result page (demo) — Soil to Stars",
  description: "Illustrative result workspace with labelled mock data for demonstration.",
  robots: { index: false, follow: false },
};

/**
 * Demo-only result page: real workspace chrome + mock fixture result content.
 * Not scientific advice. Genuine intake remains on /workspace.
 */
export default function ResultPageDemo() {
  const html = getReferenceBody("workspace-preview.html");

  return (
    <>
      <link rel="stylesheet" href="/reference/workspace.css" />
      <link rel="stylesheet" href="/reference/polish.css" />
      <link rel="stylesheet" href="/reference/bengali-fonts.css" />
      <link rel="stylesheet" href="/reference/i18n.css" />
      <link rel="stylesheet" href="/reference/workspace-fixes.css" />
      <link rel="stylesheet" href="/reference/results.css" />
      <div className="reference-root" dangerouslySetInnerHTML={{ __html: html }} />
      <Script src="/reference/result-page.js" strategy="afterInteractive" type="module" />
      <Script src="/reference/polish.js" strategy="afterInteractive" />
      <Script src="/reference/i18n.js" strategy="afterInteractive" />
    </>
  );
}
