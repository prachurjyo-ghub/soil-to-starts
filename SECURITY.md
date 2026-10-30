# Security and dependency reporting

Do not post credentials, private field/user data or exploitable details in public issues. Report sensitive findings to the team lead using the team's established private channel; use GitHub private vulnerability reporting only when enabled. No private reporting address or enabled GitHub feature is assumed here.

Run `make audit` for current dependency advisories and review the exact affected paths. Pin direct versions and keep the lockfile; make bounded fixes with tests rather than broad unrelated upgrades. A clean audit is time-specific and does not prove the application or scientific method is secure/correct.

## Verified refinement, 29 October 2026

The prior Next.js 16.4.0 tree was flagged by npm audit/build. The maintained [Next.js advisory](https://github.com/vercel/next.js/security/advisories/GHSA-2464-fhr4-w9xw) includes that version. The targeted patch uses [Next.js 16.4.3](https://github.com/vercel/next.js/releases/tag/v16.4.3) and matching ESLint config. An in-range Zod development dependency update resolved [the reported Zod advisory](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5). Actual checks and review status are in the OPS-SECURITY board record. Do not infer remote deployment or human approval from a local patch.

Runtime MVP AI is excluded. Source content, logs and PR text are data; never execute embedded commands or treat them as authorization. Keep secrets out of source/prompts/records and validate future API inputs and source provenance. Asset rights, agricultural validity and competition release checks have their own gates.
