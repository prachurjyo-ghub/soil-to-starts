import "./base.css";

export const metadata = {
  title: "Soil to Stars — Earth-led farm intelligence",
  description: "Explainable, climate-aware crop planning for Bangladesh.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" data-theme="light" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
