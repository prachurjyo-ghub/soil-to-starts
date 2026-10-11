# Soil to Stars — Next.js prototype

This is the working frontend for the [Field Shift project](../README.md). The root README describes the challenge scope, planned data architecture, source status, and validation work.

A Next.js port of the supplied Soil to Stars reference. The original markup, layered styling, motion system, video behavior, branch cursor, language controls, and workspace interactions remain the visual and behavioral source of truth.

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000` for the presentation site and `http://localhost:3000/workspace` for the field-planning studio.

## Production check

```bash
npm run build
npm run start
```

All supplied media and fonts are stored locally in `public/assets`. Field preferences, the selected theme, and saved plans use browser local storage. Crop scores and environmental series are illustrative prototype data, not agricultural advice or live NASA observations.
