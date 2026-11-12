# Team playbook

Start with [the task board](PROGRESS.md). Pick one available work package and the first unchecked checklist item assigned to you. Each item says how, where, how to verify and who receives it. Owners coordinate; they do not need the lead to repeat the instructions.

## Two scopes and active release

[MVP_SCOPE](MVP_SCOPE.md) is mandatory now; [FUTURE_ROADMAP](FUTURE_ROADMAP.md) is deferred. Active release targets one reviewed pilot, not validated national coverage. The stronger MVP includes baseline versus two alternatives, same-engine intended-crop checking, why-not ledger, one historical replay, print/JSON receipt and a compact data-backed story after the first integrated flow. Fertilizer/NPK/restoration modeling and runtime AI are excluded.

Future tasks depend on accepted G5 and retain separate activation blockers; never start them just because the MVP is merged. Early MEDIA-STORY/MEDIA-STORYBOARD packages cover preparation only. Approved final narration, scientific captures, edit and exports belong to G5 after G4.

## The six owners and their responsibilities

Names and role assignments were supplied by the team. GitHub usernames are not yet recorded; do not infer them or publish invented profiles. An owner is accountable for delivery and handoff, not the sole person allowed to contribute.

| Member / role | Concrete deliverables | Required review and completion evidence |
| --- | --- | --- |
| **Fardin — technical lead, backend, rotation engine, integration** | Agree stable IDs and contracts; implement API validation/errors, hard exclusions, chronological three-step search, baseline comparison/preset ranking, quick checks, replay and reproducible receipts; coordinate CI, integration and freeze. Planned modules include `rotation.py`, `suitability.py`, and `scenarios.py`. | Saim reviews climate/data handling; Maruf reviews rules/outputs; Prachurjo reviews API usability. Done when an actual frontend request returns a reproducible sourced complete or honest incomplete result. |
| **Saim — NASA data, climate, scientific indicators** | Reproducible POWER acquisition; raw/normalized sample and manifest/checksum; missingness/units/time QA; deterministic aggregation/indicators; chart payloads; regional data-quality checks. Evaluate optional datasets only after the core slice. | Fardin reviews schemas/reproducibility; Maruf reviews agronomic use. Done when another teammate can reproduce each displayed climate number. |
| **Maruf — Bangladesh agronomy, crops, soils, rotation rules** | Diverse crop catalog with IDs, names/families, seasons/windows/duration, annual/perennial flags, sourced soil/water/sequence constraints, rule status, citations and limitations. Explicitly separate unknown, candidate and validated rules. | Fardin reviews executable rule format; Saim reviews climate-unit alignment. Done when unsupported crop-region combinations cannot silently enter advice and evidence gaps are documented. Student review must not be described as professional agronomic certification. |
| **Prachurjo — frontend, UX, maps, charts, bilingual access** | Preserve current Next.js app; implement location fallback and wizard, real API client, future-crop timeline, three-strategy matrix, intended-crop card, receipt/print/JSON, check ledger, compact story and climate charts, EN/BN, responsive/keyboard/reduced-motion behavior. Add narrative motion after integration. | Fardin reviews contracts/errors; Saim and Maruf review scientific labels; Hla reviews copy. Done when a new user can obtain and understand a traceable result on a phone. |
| **Nadim — video editing and motion design** | Storyboard/shot list, edit plan, licensed asset ledger, title cards, subtitles, actual-app recordings, required exports and source/AI credits. Store large source footage in agreed permitted storage, not huge Git commits. | Hla reviews timing/story; Saim/Maruf approve scientific visuals; Prachurjo supplies UI captures. Done when approved exports meet verified requirements and every asset has rights/credits. |
| **Hla — narration, story, presentation and Q&A** | Problem/solution story, script/timings, homepage copy with Prachurjo, narration recording, clear English/subtitles with Nadim, claims/citations checklist, rehearsals and judge Q&A. | Nadim reviews edit fit; Saim/Maruf verify claims; Fardin verifies feature status. Done when the pitch matches the actual build and approved evidence. |

The four technical owners each deliver a critical slice, its checks, documentation, a cross-review and integration support. Nadim and Hla contribute real authored media/scripts and reviews. Equal contribution means meaningful responsibility, **not equal commit counts**. Never fabricate commits, coauthors, review evidence, or achievements.


## Work order: who starts, who waits, and why

**A push makes work available for review. A reviewed, passing, merged PR completes a dependency.** Downstream teammates update from `main` after that merge; they do not quietly depend on another person's unfinished branch.

| Gate / proposed issue key | Owner and start condition | Deliverable to push for review | Gate acceptance / who can start next |
| --- | --- | --- | --- |
| **G0 — CONTRACT** | Fardin coordinates; all four technical owners review. Nadim/Hla agree story and asset-record format in parallel. | A bounded contract issue/PR: field/crop/source IDs, previous vs current crop, units/dates, rule schema, request/response examples, statuses/data modes, ownership and test expectations. | Saim, Maruf and Prachurjo agree the inputs/outputs and an independent reviewer approves. Merge before implementing shared contracts. These README rules are not a signed-off detailed API schema. |
| **G1A — POWER** | Saim, after G0. May run alongside G1B/G1C/G1D. | One authentic NASA POWER sample, raw/normalized files, manifest, processing command, QA/indicator tests and evidence limits. | Fardin can reproduce outputs; Maruf reviews fitness for use. Merge unlocks real-data compute and chart work. |
| **G1B — AGRONOMY** | Maruf, after G0; parallel with G1A. | Minimum source-backed crop/rule catalog for an explicit first evidence region, calendars crossing years, duration, water/soil/family constraints and unsupported cases. | Fardin can parse rules; sources and regional applicability are reviewable. Merge unlocks scientific sequence generation. A small pilot does not reduce the long-term nationwide-selection target; validated initial release coverage remains explicit. |
| **G1C — API/TOOLING** | Fardin, after G0; independent of final data values. | Agreed schema/validation/error skeleton and owned test/tooling setup. Track missing ESLint config separately with Prachurjo. | Schema checks pass. Synthetic tests are clearly synthetic; no successful scientific plan is claimed yet. Merge before frontend depends on the new API contract. |
| **G1D — UI SHELL** | Prachurjo, after G0; parallel with evidence work. | Existing-app wizard, field state, geographic fallback, loading/error/incomplete states and API adapter against the agreed contract. | Fardin reviews contract handling; illustrative views remain labeled and isolated. Merge before integrated screen work. |
| **G2 — FIRST SCIENTIFIC SLICE** | Fardin starts evidence-dependent integration only after G1A + G1B + G1C are merged. | Deterministic feasibility, common-horizon baseline plus distinct alternatives, chronological three-step search, quick-check parity, source-linked checks and versioned receipts; tests for plan/bundle status and missing evidence. | Saim and Maruf reproduce/review scientific outputs. A complete plan has exactly three feasible future steps; complete bundle also requires assessed baseline and two distinct alternatives. Missing evidence remains incomplete/unavailable. Merge unlocks live frontend integration. |
| **G3 — END-TO-END UI** | Prachurjo after G2 + G1D merge. Saim provides chart arrays; Maruf checks explanations. | Real request → sourced plan/incomplete state in existing UI; comparison/timeline, quick assessment, check ledger, evidence drawer and real climate history. | Fardin reviews transport/errors; Saim/Maruf check every claim; phone/keyboard/EN/BN checks recorded. This is the mandatory integration gate before decorative expansion. |
| **G3-STORY / G3-REPORT** | Prachurjo after accepted G3; Saim/Hla/Nadim support story, Fardin supports fingerprints/receipt. | Compact four-scene story and actual-result JSON/print, with accessible source labels and stable identities. | Source values, selected-location handoff, export parity, incomplete states and accessibility are checked; both accepted packages precede G4. |
| **G4 — COMPARISON AND VALIDATION** | Fardin + Saim + Maruf + Prachurjo after G3, G3-STORY and G3-REPORT. | Historical stress replay with fixed field assumptions; reviewed pilot cases and explicit unsupported coverage; offline scientific fixtures/network block; uncertainty, sensitivity and accessibility evidence. | Document findings, limits and source coverage. Missing evidence is a valid documented outcome, not permission to invent success. Merge before release claims. |
| **G5 — MVP RELEASE AND SUBMISSION HANDOFF** | Hla/Nadim draft from G0 onward; final scripts/captures require approved G3/G4 evidence. Fardin coordinates freeze. | Fact-checked script → approved narration/UI capture → edited/subtitled exports → source/license/AI/contribution audit → authorized persistent-data deployment/public access check → submission handoff. | Saim/Maruf approve claims, Prachurjo checks captured behavior, Fardin checks release status. Record genuine MVP release acceptance and verify portal requirements. Actual submission remains separately authorized; future tracks do not auto-start. |

**Media handoff order:** Hla drafts story and marks unknown claims → Saim/Maruf fact-check → Fardin/Prachurjo confirm shipped behavior → Hla locks narration text → Hla records and Prachurjo supplies real app captures → Nadim edits/subtitles → Hla and technical reviewers approve → Nadim exports. Storyboards and licensed-asset collection can begin early; final narration must not promise unbuilt features.

Current handoff: a teammate reviews PLAN-SCOPE while Fardin may draft G0-CONTRACT/s01. Planning review does not imply implemented science or remove G0 review/merge gates before G1.

Recommended first technical issues are G0/CONTRACT (Fardin, with all technical owners), then G1A/POWER (Saim), G1B/AGRONOMY (Maruf), and G1D/UI SHELL (Prachurjo). Fardin takes G1C after the contract review. Gate tasks now exist as local records in [PROGRESS.md](PROGRESS.md); their IDs are **not GitHub issue numbers**. Remote issues/PRs and branch protections have not been created by this workflow installation.

### Exact branch and handoff routine

From the repository root, after checking your working tree and agreeing the issue:

```bash
git status --short --branch
git switch main
git pull --ff-only origin main
git switch -c feature/your-bounded-task
```

Replace the example with your own branch, such as `feature/power-ingestion`, `feature/agronomy-rules`, `feature/rotation-three-step`, `feature/workspace-api`, `media/demo-edit`, or `content/narration-script`. Do not switch branches over uncommitted teammate changes, discard them, or force a pull. Coordinate with the owner first; do not share the same working directory for simultaneous branch work.

Humans commit reviewed changes on their feature branch, push, and open a PR to `main`. Stage only intended paths; inspect the staged diff. Do not commit secrets or large cache files. Assistants need explicit authorization to commit or push; authorization to edit files or maintain logs does not authorize those actions.

Every issue states: owner/reviewer, bounded purpose, dependencies, input/output contracts, intended files, sources/rights, acceptance checks, unknowns, and handoff target. Every PR states: linked issue, changed behavior, files, sources/units/period, exact checks/results, screenshot/reproduction evidence, offline/accessibility behavior where applicable, limitations, and AI-use record. A different teammate reviews. Scientific changes also need the relevant domain owner's review; do not merge with unexplained failed checks.

Handoff message template:

```text
Issue / PR / merged revision:
Owner → next owner:
Files, IDs and contract version:
Input and produced output:
Sources, units, period and evidence status:
Checks run and actual results:
Known limits / unresolved decisions:
How to reproduce:
AI-use record and reviewer:
```

After the prerequisite PR is merged, the next owner checks a clean tree, updates `main` with `git pull --ff-only origin main`, and creates their own branch. If already on a feature branch, integrate updated `main` using the team's agreed merge approach; never force-push or rewrite shared history. Work against sample contracts before a dependency lands is allowed only as an explicitly labeled interface task, not as a claim of integrated functionality.

Daily implementation rhythm: read generated next actions → log the action command → update the owned task record → run and record actual checks → render/check progress → owner review and integration. Keep issue/source/contribution status aligned. Before freeze, stop new features, rehearse the sourced demo, repair blockers, then prepare submission materials. Use gates rather than invented calendar deadlines.


## Manual and other-AI contributions

Everyone uses the same small PR declaration: Task, Work, Method/tools. Human-written code declares no AI used; AI-assisted work names actual tools and their role. Browser ChatGPT/Bolt work is not automatically visible to Codex. Command logs cover actual implementation commands only; discussion is excluded. GitHub supplies observed PR account metadata; mapping an account to a real teammate remains explicitly unconfirmed until verified. Never infer tools or human authorship from code style, Git author strings or commit counts.

A later teammate reads the linked task, diff, source evidence and checks for the relevant revision; they preserve working code and rerun only relevant/missing/stale checks. Missing handoff data means verification pending, not permission to recreate or claim completion.

## Small work sessions

Choose one available checklist item, inspect its owner/how/files/verification, and keep the change bounded. The PR may identify the exact item, for example `Task: G1A/s01`. Group items only when they form one coherent change and preserve their separate evidence. Do not ask the lead to restate a written requirement; bring the exact missing source/decision/error and a proposed next action. Peer-review another owner’s slice and keep integration time visible.
