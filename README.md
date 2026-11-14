# Soil to Stars

**Field Shift · NASA Space Apps Challenge · Bangladesh**

Soil to Stars helps farmers and agricultural advisers explore how seasonal weather has changed and see what local crop records say about the crops they grow. Choose a district or drop a pin, describe your field, and get a report that brings historical NASA weather and regional crop evidence together in English or Bangla.

[Watch the short project demo](https://www.youtube.com/watch?v=2CR_mM3GDlw) · [Watch the 240 Seconds of Glory presentation](https://www.youtube.com/watch?v=LOkSu0I2Ack) · [Read our AI disclosure](docs/AI_USE.md)

## The decision we are trying to improve

A farmer deciding what to grow next needs to connect three different things: what happened on the land, what the local weather has been like, and what Bangladesh's crop calendars say. Those records live at different scales and use different terms. Soil to Stars brings them into one bilingual workspace. A farmer can take a saved report to an agriculture officer and discuss a specific crop, date range and source rather than start the conversation from scratch.

**What the submission covers.** The archive serves all 64 district selections through 42 representative NASA weather grids. It contains 25 complete historical years (2001–2025), a separate 2026 observation snapshot, and 366 source-table calendars with 7,834 preserved entries. These figures describe the dataset and app coverage. Farmer adoption, yield gains and water savings have yet to be measured.

## What we built creatively

- **Start with a farmer's dates.** Pick when the field will be ready. The app finds those exact month-and-day windows in each usable archive year. It shows the median of each year's highest daily air temperature, lowest daily air temperature and total rainfall. Open the year-by-year table to trace the answer. This gives a usable historical reference when the requested dates are beyond the observation archive.
- **Let farmers compare the local sources.** Compare two crops side by side, starting with the reported crop where a matching BAMIS calendar exists. See the source's season, printed lifespan and page reference. The app keeps each source table distinct, including different rice systems, so they are visible during the conversation about what could follow.
- **Make uncertainty visible where it matters.** A warning-day count appears only for an applicable published reference and matching weather statistic. The app preserves absent records and distinguishes the latest observation date from historical analogues. A separate Bogura field study shows how researchers tested real crop sequences, with the study's place and dates attached.
- **Make it usable on a shared or offline machine.** District search, weather, crop records and report generation run against bundled local data after setup. The workspace supports English and Bangla, and the JSON receipt preserves the inputs, sources and result so the same analysis can be checked independently.

## Run the submission

Install Git, Make, Node.js 24 with npm, and Python 3.10 or newer with SQLite support. Run these commands in a terminal with access to the npm registry for the first install.

```bash
git clone --depth 1 --branch main https://github.com/prachurjyo-ghub/soil-to-starts.git
cd soil-to-starts
npm --prefix prototype ci
make backend
make build
npm --prefix prototype start -- --hostname 127.0.0.1 --port 3000
```

Open [http://localhost:3000](http://localhost:3000) and select **Open workspace**. The first backend setup verifies the bundled data and builds the local SQLite indexes, which can take several minutes. You can reuse those indexes on subsequent starts. The evidence pipeline needs no NASA key, account, separate server, or live NASA request. For a fully local field-selection flow use **District search**. The optional street basemap needs a connection.

If port 3000 is in use, stop the other server or pass a free port to the same start command. To check prerequisites run `make doctor`. To run the test suites and lint use `make check`.

## Try a field report

1. Open **Set up your field**. Choose a district, enter the current crop and when the land will be ready, and fill in the remaining questions. The app accepts all 64 districts. Available crop evidence varies by crop and region.
2. Submit the form. **Your results** shows what matches your answers, the historical weather window and which checks have evidence. Save the report to this browser or download the source-linked JSON.
3. Open **Climate insights** to compare archived rainfall and air temperature between 2001–2010 and 2016–2025. **Rotation plans** displays your reported crop order and the crop calendars available for your area. **Data & methodology** includes a separately labelled published trial from Bogura.

## A reproducible judging walkthrough

**Barishal · Banana.** Use district search, enter a planting date of **14 November 2026** and a field-ready window of **20–30 November 2026**. Choose first cultivation, no usual rotation, rainfed and balanced for this walkthrough.

1. **Your results** shows the historical weather for 20–30 November. Expand **See each year** to inspect the underlying windows. In the current-crop section, the report explains the observation cutoff and shows historical weather for the same crop dates.
2. **Rotation plans** shows the reported crop order, the date-window weather and crop calendars for Barishal. **Compare plans** lets you change either crop and check how the recorded seasons and lifespans differ. **Data & methodology** contains the optional Bogura research case.
3. Change the district, then change the date window. The app recomputes from the matching grid and dates. Districts mapped to the same grid can legitimately share a weather result. Changing the crop changes the crop-source lookup. Water access and priorities are retained for review. Save the report or export its JSON and inspect the source IDs, representative grid and year-by-year values.

## The evidence behind the report

| Source | How we use it |
| --- | --- |
| [NASA POWER Daily](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | Archived gridded 2 m air temperature and precipitation support the historical charts and date-window summaries. Each district maps to a representative grid point. Districts can share a grid point. |
| [Bangladesh Agro-Meteorological Information Service crop calendars](https://www.bamis.gov.bd/en/calendar) | The app matches documented regional calendars to crop and region. Printed weather normals describe source conditions. A warning comparison requires an explicitly applicable source and matching weather statistic. |
| [Hasan et al., Bogura field study](https://hnpublication.com/upload/ijacr/2022-11-3001.pdf#page=3) | An optional research example shows published crop sequences beside NASA POWER summaries for the documented dates. |
| [geoBoundaries Bangladesh ADM2](data/admin/README.md) | Local district boundaries support district selection and pin matching. |

Farmer-entered dates can change the historical weather window, and the crop and district determine which evidence matches. Water access, priorities, and history stay in the report for review. A district-grid summary represents historical regional weather. Field-specific suitability scores, calibrated crop vulnerability and personalized three-crop recommendations require additional verified agronomy and field validation.

## Verification

- The full test suites cover date and unit boundaries, UI behavior, the local API and reproducible data preparation. Run `make check` and `make build`.
- The final nationwide audit generated **1,984 reports** across 64 districts using all 30 crop choices and fallow for the demonstration date range. It checked each crop match against the region and crop IDs in SQLite, and independently recomputed the 25 annual weather samples for each district. It found **1,266 crop/district pairs with a matching calendar**. A successful report can include a clear evidence gap.
- The demonstration case reproduced **27.62 °C** for the median annual maximum, **15.46 °C** for the median annual minimum, and **0 mm** for median total rainfall over 20–30 November in the representative Barishal grid. A median of zero does not imply all years were dry. The year-by-year values are included in the report.

## What is ready for judging

| Demonstrable today | Validation still needed |
| --- | --- |
| District or pin intake, matching regional crop calendars, observed weather when cached, date-specific historical summaries, two-crop calendar comparison, source-linked report export and historical trial replay | Independent field validation, complete variety- and stage-specific limits, site and irrigation rules, verified planting and field-turnaround guidance, and a reviewed prospective rotation model |

A field trial replay demonstrates how published plans can be examined. Personalized three-crop schedules, yield forecasts and calibrated vulnerability estimates remain outside the validated release. A practical next impact test would measure whether farmers and local advisers can find, interpret and use the right records when discussing the next planting window.

## How it fits together

```text
Field setup → same-origin Next.js API → Python + local SQLite
                                         ├─ NASA POWER observations
                                         └─ Regional crop evidence
                         ← source-linked field report
```

The web app lives in `prototype/`. The ingestion, deterministic calculations and local API live in `src/`. Packaged inputs, dictionaries and source receipts live in `data/` and `docs/data/`. User submissions stay on the machine running the local server, and saved report snapshots stay in the browser.

**Team** · Fardin, Saim, Maruf, Prachurjo, Nadim and Hla.

[Apache-2.0 license](LICENSE) · [Third-party notices and asset credits](THIRD_PARTY_NOTICES.md) · [AI use and human contributions](docs/AI_USE.md)
