/* eslint-disable @next/next/no-css-tags -- Supplied reference styles/fonts retain their loading order; migration requires visual and font-rights review. */
import Script from "next/script";
import { getReferenceBody } from "@/lib/reference";
import IntakeMapRuntime from "@/components/IntakeMapRuntime";

export const metadata = { title: "Field Studio — Soil to Stars" };

export default function WorkspacePage() {
  const html = getReferenceBody("workspace-preview.html");

  return (
    <>
      <link rel="stylesheet" href="/reference/workspace.css" />
      <link rel="stylesheet" href="/reference/polish.css" />
      <link rel="stylesheet" href="/reference/bengali-fonts.css" />
      <link rel="stylesheet" href="/reference/i18n.css" />
      <link rel="stylesheet" href="/reference/workspace-fixes.css" />
      <IntakeMapRuntime />
      <div className="reference-root" dangerouslySetInnerHTML={{ __html: html }} />
      <Script src="/reference/workspace.js" strategy="afterInteractive" />
      <Script src="/reference/polish.js" strategy="afterInteractive" />
      <Script src="/reference/i18n.js" strategy="afterInteractive" />
    </>
  );
}
