<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

## Frontend scope

Keep the existing app/routes and supplied reference design. Current routes load reference HTML and static scripts; inspect imports before editing unused React components. Read only the relevant product/UI/API sections and task record. Preserve the generated Next.js instruction block above.

Use configured dependencies and lockfile. Real scientific UI consumes the approved API; never query NASA directly or hide a failing API behind demo constants. Preserve EN/BN, mobile/keyboard/reduced-motion access and map fallback. Mark illustrative scores/soil/charts clearly. Static reference CSS/font loading has narrow lint exceptions until a visual/rights-reviewed migration; do not broaden them to hide app errors.

Follow MVP_SCOPE for the short intake, comparison/quick check, receipt and compact story; FUTURE_ROADMAP is deferred. No runtime-generated advice, fertilizer form or scientific success fallback.

Run `npm run lint` and `npm run build -- --webpack` after relevant changes. Record remaining warnings and actual results. Only action commands and actual work go in prompt logs; discussions are excluded. Update the task record and regenerate views via the root helper.
