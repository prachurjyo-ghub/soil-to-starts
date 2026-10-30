# UI/UX specification

Status: target behavior, not implemented science. Current / and /workspace load supplied reference HTML/assets; inspect actual imports before editing unused components. Preserve the existing app. [MVP_SCOPE](MVP_SCOPE.md) defines mandatory capability; [FUTURE_ROADMAP](FUTURE_ROADMAP.md) holds expansion.

## Short farmer journey

Latest intake requirement, authorized by Fardin on 30 October 2026: nationwide selection and meaningful required core answers supersede the older pilot-only wizard and general unknown response for these questions. See [INTAKE-UI](tasks/INTAKE-UI.json) and [intake contract](API_CONTRACT.md).

Location comes first with two labelled independent controls: **Choose on map** and **Search district by name**. The local EN/BN district selector works without WebGL, tiles or boundary loading and never assigns coordinates. The MapLibre map starts with Bangladesh in view and no selection; clicks/taps place a draggable pin, an explicit action confirms it, and the locally resolved district is displayed. Keyboard users can pan the map, explicitly place a pin at its center, move the focused pin with arrows, and confirm. No field polygon or area tools.

Keep street-basemap and boundary attribution visible. Resolve pins against the versioned local district geometry, including islands/holes. Reject ambiguous borders, overlaps, invalid points and unresolved coverage with correction text and a district-search fallback. Do not snap to the nearest district. Map/style/WebGL/network failure preserves the six answers. Pending pins remain unsubmitted. Changing a pin invalidates confirmation; changing location method clears inactive values.

During form/language rerenders, detach/reinsert the same map host and resize its single instance. Keep camera/marker and genuine answers. Destroy the map on leaving the map/form view or runtime disposal; cancel stale asynchronous initialization and permit retry. Restore confirmed saved pins only after local boundary rechecking. A precise pin is farmer input, not field-resolution NASA evidence or validated scientific coverage. See [schema/migration](API_CONTRACT.md) and [location QA](LOCATION_QA.md).

Show one ordered form, with all six questions visible together:

1. What crop is growing now? Require a supported intake identity or explicit empty/fallow state.
2. When will the field be available after harvest? Require a real date or bounded window and explicit expected/estimated basis; for an empty field, collect available-from date.
3. What crops did you grow previously? Require chronological crop/period entries or explicit first cultivation/no prior history.
4. What would you normally grow next? Require a usual crop/season sequence (repeats/fallow allowed) or explicit no established rotation. Keep this separate from past history.
5. What water access do you have? Require Rainfed, Limited irrigation or Reliable irrigation; collect applicable seasonal limitations.
6. What matters most? Require Save water, Soil protection / rotation diversity or Balanced, with no preselected priority.

No blank, placeholder, unknown or “any” answer satisfies a core question. Do not force a guess: the named absence/fallow states have distinct meanings. Validate dependent controls, real calendar dates, ordering and known contradictions. Present specific adjacent errors with labels, `aria-describedby`/`aria-invalid`, an accessible linked error summary and focus on the first invalid control. Preserve entered answers and keyboard focus on conditional rerenders and language changes. Use browser required attributes plus the shared programmatic validator.

No fertilizer, pH, nutrient, organic-matter or demo-estimate question is part of this intake. Other scientific unknowns remain unknown. New-farmer answers do not come from demo fields, soil defaults, example coordinates or demo priorities. Versioned browser-local drafts stay distinct from revalidated submissions. Escape user text; provide EN/BN, native keyboard controls, visible focus, mobile wrapping and reduced motion.

Until a real scientific API is connected, save/show the validated field-input summary and a planning-unavailable state. Explicitly separate any legacy illustrative demo; never run its mock rankings on submitted intake answers. Input JSON export does not claim to be G3-REPORT's scientific receipt. The later integrated result journey still compares existing practice with two sourced alternatives.

## Workspace

- Comparison matrix first: common horizon, existing practice, water-focused and soil/rotation-focused options; dates, supported indicators, priority and unknowns. Keep a problematic baseline visible.
- Three future main-crop cards per complete alternative after current harvest, with a responsive timeline/gaps. Calendar gaps are potential exposed-soil periods unless actual cover/residue evidence establishes surface condition.
- One compact intended-crop card reuses planner rules; no live monitoring or diagnosis.
- Why/why-not uses fixed translated check labels and source/rule IDs: pass/fail/caution/unknown. Identify the missing fact that could resolve a check. No generated advice paragraphs or confidence gauges.
- Climate charts show authentic arrays, units, period, missingness, scale and method. One reviewed historical stress preset compares changed checks/rankings with field/history/priority fixed.
- Evidence drawer exposes source/catalogue/method versions, URLs, fingerprints and limits. JSON and print use the actual result, including incomplete status; no separate PDF service required.

## Compact homepage story after G3

Four scenes: place/record → verified heat/rain pattern → reviewed crop-calendar implication → Plan My Field. Consume Saim's versioned statistics; scrolling reveals science, it does not calculate it. Carry location into the workspace. Show no clear shift when supported. Soil/root illustrations remain conceptual, not measured nutrient changes.

Keep CTA, skip, sources and EN/BN reachable. Static reduced motion, readable axes/units and narrow-phone behavior are mandatory. Heavy 3D, richer motion and voice are future options. Preserve current routes; new pages require a bounded assigned need.

## States and claims

Check partial/invalid input, loading, source failure, absent coverage, incomplete bundle with useful checks, complete plan in incomplete bundle, offline scientific cache, map failure, print/export, phone, keyboard/focus/labels, EN/BN and reduced motion.

Display actual data mode/coverage. No illustrative success fallback for API failure. Numerical totals are optional, not probabilities. Contribution cards and media need genuine reviewed evidence and consent. No invented achievements or profiles.
