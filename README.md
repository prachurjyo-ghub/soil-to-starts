# Soil to Stars

**Field Shift · NASA Space Apps Challenge · Bangladesh**

Soil to Stars helps farmers and agricultural advisers explore how seasonal weather has changed and see what local crop records say about the crops they grow. Choose a district or drop a pin, describe your field, and get a report that brings historical NASA weather and regional crop evidence together in English or Bangla.

[Watch the short project demo](https://www.youtube.com/watch?v=2CR_mM3GDlw) · [Watch the second project video](https://www.youtube.com/watch?v=LOkSu0I2Ack) · [Read our AI disclosure](docs/AI_USE.md)

## Run the submission

Install Git, Make, Node.js 24 with npm, and Python 3.10 or newer with SQLite support. Run these commands in a terminal with access to the npm registry for the first install.

```bash
git clone --branch main https://github.com/prachurjyo-ghub/soil-to-starts.git
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

## The evidence behind the report

| Source | How we use it |
| --- | --- |
| [NASA POWER Daily](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | Archived gridded 2 m air temperature and precipitation support the historical charts and date-window summaries. Each district maps to a representative grid point. Districts can share a grid point. |
| [Bangladesh Agro-Meteorological Information Service crop calendars](https://www.bamis.gov.bd/en/calendar) | The app matches documented regional calendars to crop and region. Printed weather normals describe source conditions. A warning comparison requires an explicitly applicable source and matching weather statistic. |
| [Hasan et al., Bogura field study](https://hnpublication.com/upload/ijacr/2022-11-3001.pdf#page=3) | An optional research example shows published crop sequences beside NASA POWER summaries for the documented dates. |
| [geoBoundaries Bangladesh ADM2](data/admin/README.md) | Local district boundaries support district selection and pin matching. |

Farmer-entered dates can change the historical weather window, and the crop and district determine which evidence matches. Water access, priorities, and history stay in the report for review. A district-grid summary represents historical regional weather. Field-specific suitability scores, calibrated crop vulnerability and personalized three-crop recommendations require additional verified agronomy and field validation.

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
