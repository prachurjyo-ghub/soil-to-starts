# AI use and human contributions

This disclosure covers how the Soil to Stars team used AI to develop the app and prepare its presentation.

| Tool | Why we used it | How we used it | Human involvement |
| --- | --- | --- | --- |
| OpenAI Codex | Speed up implementation and verification | Assisted with the Next.js workspace, local SQLite integration, source matching, reproducible data transformations, tests, debugging and release documentation. | Fardin defined the workflow and required real, source-linked evidence. Saim collected and prepared NASA weather data, Maruf assembled regional crop evidence, and Prachurjo built and refined the workspace UI. Fardin led final integration and release decisions. |
| ChatGPT | Draft and refine educational and presentation material | Helped develop the project explanation, demo storyboard, voice-over script and prompts for illustrative footage. | The team chose which product features to demonstrate, supplied project facts and team imagery, and directed the pacing and edit. |
| Google Flow | Create illustrative farm footage for the demo | Generated scenes of an adult farmer examining crops under changing skies and looking at a phone beside a field. | The team specified the shots and timing, selected the usable takes, and paired them with screen recordings of the app. |
| Built-in image generation tool | Prepare a custom cursor asset | Produced a transparent twig-shaped cursor from a supplied reference. | The maintainer supplied the reference and requested the shape and styling. See the [asset credit](../prototype/public/reference/assets/credits.txt). |

## Representative implementation and media prompts

- **Codex.** Connect farmer inputs to archived NASA POWER weather and matched regional crop calendars. Preserve units, source IDs and unknown values, and test the results against local files.
- **Codex.** Put the farmer’s answers first on the rotation screen and place the published Bogura trial in Data & methodology.
- **ChatGPT / Google Flow.** Show an adult farmer studying a field beneath changing skies, then cut to the app’s real climate visualization. Use a separate narration track.
- **Image generation.** Isolate a realistic brown twig with a small green offshoot on a transparent background for use as a cursor.

## Evidence and media

Published datasets and research are credited in the [README](../README.md) and bundled source records. Weather calculations, source joins and supported warning checks run as deterministic code. The running app uses no generative model to create crop values or recommendations.

Screen recordings show the app. Generated farm scenes are illustrative. CapCut was the planned editor. The final voice-over tool and media watermarking and metadata could not be confirmed from the repository records. Credit the exact voice tool in the video description and metadata if generated narration is present, and verify visible AI labels on generated shots before submission.

## Decisions and contributions by the team

| Contribution | What the team supplied or decided | How to inspect the work |
| --- | --- | --- |
| Product and integration | Fardin set the Bangladesh-wide district scope, chose to combine farmer inputs with NASA weather and local crop evidence, and made the final integration and submission decisions. | [README and workflow](../README.md), [assessment source](../src/compute/assessment.py) |
| Climate acquisition | Saim collected and prepared NASA POWER data and supplied the archive and handoff records. | [Packaged climate manifest](../data/climate/packages/v1.0.0/PACKAGE_MANIFEST.json), [daily index and parity checks](../src/api/daily_index.py) |
| Regional crop research | Maruf collected regional crop records, preserving distinctions between regions, seasons and source tables. | [Evidence package](../data/catalog/EVIDENCE_PACKAGE.md), [evidence dictionary](../data/catalog/EVIDENCE_DICTIONARY.md) |
| Workspace | Prachurjo contributed the farmer-facing interface, navigation and result layouts that the team iterated on. | [Workspace route](../prototype/app/workspace/page.js), [result rendering](../prototype/public/reference/result-ui.js) |
| Presentation | The team directed the project narrative, selected demonstration scenes and used footage of the running app to show the product. Nadim and Hla were assigned presentation work covering motion and narration respectively. | [Short demonstration](https://www.youtube.com/watch?v=2CR_mM3GDlw), [long presentation](https://www.youtube.com/watch?v=LOkSu0I2Ack) |

## How the AI-assisted work was checked

1. **Source handling.** Codex helped implement stable district and crop IDs, date aggregation, and source tracking. Original documents and publisher observations remain the evidence. The implementation preserves missing values and gives each reported window a source and spatial context.
2. **Calculation and scope.** For date windows extending beyond cached observations, the code uses the same calendar dates from past archive years and reports the median across complete windows. It handles leap days and cross-year windows explicitly. The user can inspect every contributing annual result. No model estimates future weather or invents planting and harvest dates.
3. **Crop comparison.** The team wanted decisions to stay tied to the farmer's area. The interface matches the region first and shows the source's seasons, lifespans and page references. Only a source-backed, applicable warning enters an exposure count. The tool shows why uncertainty remains when the reference is missing.
4. **Technical checks.** Verification includes automated tests and a production build. The nationwide audit generated 1,984 reports from the real archive, recomputed source statistics and compared every crop match in that audit with its SQLite source rows. Browser checks submitted the Barishal example, switched from banana to rice in the comparison, and verified the Bangla view. The calculation and results are inspectable in [weather computation](../src/compute/weather.py), [weather tests](../tests/test_weather_windows.py), [workspace tests](../tests/workspace-pages.test.cjs) and exported reports. These checks cover software and data handling. Independent agronomic validation remains separate.
5. **Media disclosure.** Google Flow was used for illustrative farming scenes. The screen-recorded app and NASA-derived charts are identified separately in the project. The final narration tool, visible marks and uploaded audio metadata are still unverified in this repository.

## Final implementation instruction

> Fix the missing field answers across Bangladesh, verify the calculations and screens on the bundled evidence, and expand the submission documents to explain the project's creativity, impact, AI tools and human contributions.

Codex added the date-matched historical summaries and interactive two-crop calendar comparison, then checked the generated reports against the source data. The maintainer set the nationwide scope and supplied the demonstrated Barishal case.

**Release follow-up.** Fardin supplied the failing GitHub check and the Chattogram chilli report. Codex inspected the runner logs, made climate aggregation reproducible across Python versions, and matched the English BAMIS source PDF to the archive checksum. The report now shows the count of days in the published daily rainfall range, with the crop-stage limits beside it. Heat risk and prospective rotations still require additional evidence.

**Rotation display follow-up.** Fardin reported that a crop entered by season was missing from the results and asked to put rotation first. Codex moved the saved sequence to the top of the report, translated its season labels, fixed server validation that rejected numeric season years, made the date validation easier to find, and checked that the API rejects a past season and saves a valid season-based Brinjal row.

**Farmer-facing crop options follow-up.** Fardin asked for three next-crop choices, clearer seasons, a reason on each card and visible current-crop weather checks. Codex added a shortlist from the published BAMIS month spans, preserved each record's lifespan and source, and tested that the cards and weather comparisons render from the saved answers. Selection prioritizes a different crop from the current one, then the earliest calendar start. Its order is an exploration aid. Verified field suitability and exact planting or harvest dates require local agronomy.

The team supplied video frames showing the baseline, two three-crop alternatives and an operations table. Codex adapted the comparison layout to two evidence-based calendar sequences within a common horizon. It used month spans from the actual sources and kept test operation dates out of field results.

Codex investigated the reported chart-table overlap, removed the height constraint from the expandable table, preferred different crop mixes for the three calendar alternatives, and added a field-ready date to What-if Studio. The user supplied the screenshot and requested more meaningful alternatives and scenario verification.

Codex changed the regional crop calendar list so the season, published lifespan and source are visible without opening each crop. The user supplied the screenshot showing the repeated clicks.
