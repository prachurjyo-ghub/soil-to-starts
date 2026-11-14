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
