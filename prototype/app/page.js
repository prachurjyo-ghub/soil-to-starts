import Script from "next/script";
import { getReferenceBody } from "@/lib/reference";

export default function Page() {
  const html = getReferenceBody("index.html");

  return (
    <>
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet" />
      <link rel="preload" href="/assets/field-landscape.webp" as="image" />
      <link rel="stylesheet" href="/reference/styles.css" />
      <link rel="stylesheet" href="/reference/polish.css" />
      <link rel="stylesheet" href="/reference/bengali-fonts.css" />
      <link rel="stylesheet" href="/reference/i18n.css" />
      <div className="reference-root" dangerouslySetInnerHTML={{ __html: html }} />
      <Script src="/reference/script.js" strategy="afterInteractive" />
      <Script src="/reference/polish.js" strategy="afterInteractive" />
      <Script src="/reference/i18n.js" strategy="afterInteractive" />
    </>
  );
}
