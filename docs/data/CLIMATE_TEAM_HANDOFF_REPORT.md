# Saim → Fardin: local climate delivery report

**Historical local-delivery stage.** Saim subsequently authorized committing and
pushing the unchanged archive on `main2`. The current workflow is clone/pull +
`python3 scripts/setup_climate_data.py`; see [GitHub setup](CLIMATE_GITHUB_SETUP.md).
The local-only/no-push statements below describe the earlier instruction, not
the current delivery authorization. Scientific/recipient approval remains separate.

The delivery gap is resolved **locally**: Git contains code/docs/receipts, while
the ignored climate data must be transferred separately. No recipient delivery,
independent recipient acceptance, scientific approval or application integration
has occurred. This task made no download, commit, push, upload or contact.

## Actual implementation and local availability

Current `main2` baseline: `db37c6d02c13a9e9231b2396780e5f26465eabf3`.
Climate implementation was committed in `159adfa`; all nine sealed source hashes
match the files committed at the current baseline. The archive retains its
original build baseline `5c8c858` plus exact source hashes. That older HEAD is not
mistakenly presented as identifying the working implementation by itself.
The new delivery assembler, tests and documentation are uncommitted changes.

The original archive, sidecar, manifest, bootstrap, 100 raw responses/manifests
and 2,387 prepared files actually exist on Saim's computer. All 2,610 local
non-document payload entries match the sealed manifest. The original producer
receipt is unchanged from Git. Older packaged documentation predates measured
result addenda; that intentional documentation snapshot is not a data mismatch.
All 82 previous audit evidence hashes remain unchanged. No local missing data
or corrupted component was found. A committed receipt does not supply these
files to Fardin, and this report does not inspect or certify his machine.

## Folder to transfer outside Git

Repository-relative folder:
`cache/climate_delivery/Saim_to_Fardin_climate_v1.0.0/`.
It contains 13 files: archive, checksum sidecar, unchanged trusted producer receipt,
matching bootstrap, original package manifest, START_HERE, consumer guide,
compatibility dictionary, original setup/terms guides, real loaded example,
producer test results and a delivery-file inventory. The inventory hashes all
other folder files; it is not an authentication signature.

Archive: `soil-to-stars-climate-bgd-v1.0.0.tar.gz`, version **1.0.0**, exactly
**88,023,118 bytes**, 2,618 payload files plus the package manifest.

- Archive SHA-256: `4a0ba04c9c8beaa0a908e0b4d61cc23c6b90f87ad927bbe229405860eda6117b`.
- Package manifest SHA-256: `230b58fdc12b0cc12742387ab542e944d99facf35e6b7e071fa3636423dca29b`.
- Bootstrap SHA-256: `6b33abf5dee24570e04d01ed12e52a74a989aa7da1ecd1946f477f7aaf26bcd8`.

The [delivery receipt](../../data/climate/climate_team_delivery_receipt.json)
records actual total folder bytes and the delivery inventory hash. The original
archive/version/receipt were reused, not silently replaced or rebuilt. Supplemental
delivery documents do not alter the sealed scientific payload.

Saim can copy the whole folder in Finder to an available USB/external drive,
eject it, and hand it to Fardin. Fardin copies the folder locally, verifies the
receipt against his trusted `main2` copy and follows `START_HERE.md`. No specific
USB device is assumed present. If that method is unavailable, agree on a private
transfer method separately; nothing was uploaded, emailed or sent by this task.
The source-controlled [START_HERE](CLIMATE_DELIVERY_START_HERE.md) contains exact
commands and a recipient checklist. NASA's researcher-transmission notification
request and the BAMIS mapping's unresolved public-redistribution rights remain
in the original terms guide; local preparation does not resolve public clearance.

## Actual new verification

A fresh extraction at
`/private/tmp/soil-climate-team-delivery.IBiDOj/extracted/soil-to-stars-climate-bgd-v1.0.0`
verified all **2,618 payload files**. Offline validation passed for 100 raw request
identities/checksums/structures, original registry and coordinate roles. A separate
`/private/tmp/soil-climate-team-delivery.IBiDOj/reproduced/` tree, with no derived
inputs copied, recreated all **2,387 outputs byte-for-byte**; all **222 raw/source/
input files** and the extracted package remained unchanged. The existing workflow
used isolated Python `-I -B`, `OFFLINE=1` and a socket audit hook blocking DNS/
connections. No hidden local project dependency was found. Python 3.9.6/zlib
1.2.12 were tested; other compression runtimes can cause byte differences and
need investigation rather than silent acceptance. All **110 repository tests**
passed, including five new component/inventory/example checks.

Actual commands from repository root:

```bash
python3 -B src/acquire/prepare_climate_team_delivery.py
python3 cache/climate_delivery/Saim_to_Fardin_climate_v1.0.0/package_climate_data.py extract cache/climate_delivery/Saim_to_Fardin_climate_v1.0.0/soil-to-stars-climate-bgd-v1.0.0.tar.gz --destination /private/tmp/soil-climate-team-delivery.IBiDOj/extracted --sha256 4a0ba04c9c8beaa0a908e0b4d61cc23c6b90f87ad927bbe229405860eda6117b
OFFLINE=1 python3 /private/tmp/soil-climate-team-delivery.IBiDOj/extracted/soil-to-stars-climate-bgd-v1.0.0/src/acquire/package_climate_data.py validate --root /private/tmp/soil-climate-team-delivery.IBiDOj/extracted/soil-to-stars-climate-bgd-v1.0.0 --report /private/tmp/soil-climate-team-delivery.IBiDOj/validation.json
OFFLINE=1 python3 /private/tmp/soil-climate-team-delivery.IBiDOj/extracted/soil-to-stars-climate-bgd-v1.0.0/src/acquire/package_climate_data.py reproduce --root /private/tmp/soil-climate-team-delivery.IBiDOj/extracted/soil-to-stars-climate-bgd-v1.0.0 --destination /private/tmp/soil-climate-team-delivery.IBiDOj/reproduced --report /private/tmp/soil-climate-team-delivery.IBiDOj/reproduction.json
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

The folder assembler and existing extractor refuse to overwrite an existing
destination. Do not rerun those paths unchanged; use a fresh test parent. Fardin's
portable commands are in START_HERE. The real example was reloaded from the fresh
extraction and matches its delivered copy: 2001-01-01 LST at output (88.125,24.5),
PRECTOTCORR 0.04 mm/day, T2M 17.48 C, T2M_MIN 12.05 C, T2M_MAX 24.65 C.
January PRECTOTCORR accumulation at that output is 0.2 mm in both monthly and chart
records. Chapainawabganj context reuses those regional daily observations and
retains its separate interior anchor (88.256694,24.688357).

## Consumer interface, scientific limits and remaining owners

The [consumer guide](CLIMATE_CONSUMPTION.md) identifies daily wide regional and
district JSONL, monthly aggregates, chart arrays, exact key selection, units/LST,
null policy, source hashes and a loader. The
[compatibility dictionary](CLIMATE_PARAMETER_COMPATIBILITY.json) defines all four
parameter statistics and the stage/date/period/location matching prerequisites;
it defines no crop thresholds or scoring weights. Humidity/wind/sunshine are
unsupported by this core package. BAMIS normals are not crop tolerance limits.

No processing error was proved in the selected extreme audit lineages. Unusual
values remain unchanged/traceable, not corrected from statistical rarity.
The 64 anchors use 42 output positions, shared observations are not independent
district samples, and 11 mappings use positions outside pinned polygons. Padded
extrema are not Bangladesh-only extrema. Monthly T2M_MIN/T2M_MAX are means of
daily extrema. This is historical representative-location context, not district
averages, field measurements, forecasts or independently validated meteorology.
Review source/applicability questions before scientific use; no data correction
or mapping change is justified merely to hide these limitations.

- Saim: manually/separately authorize actual transfer, support recipient
  reproducibility failures and source/applicability review. No new NASA acquisition
  is required for this handoff. Recipient receipt/independent validation remain open.
- Fardin: independently run the checklist, configure persistent local prepared
  data and implement backend/calculation integration under existing project gates.
  Request-serving code reads local verified data; NASA access belongs only to a
  deliberate refresh/acquisition operation, with explicit unavailable states.
- Maruf/Fardin: resolve source-backed stage/date/rainfall/water definitions and
  valid comparisons; keep inactive crop evidence inactive until appropriately reviewed.
- Prachurjo: integrate real API data/states and separately address application
  dependencies, assets/fonts/maps and browser offline behavior. This climate
  package does not make the entire website offline. No region receives priority.

Small Git candidates: new delivery assembler/tests, START_HERE, consumer guide,
compatibility dictionary, this report, new small delivery receipt, cache README,
climate handoff and workflow/contribution records. Large archives, sidecars,
bootstrap delivery copy, raw/prepared caches, loaded example and test workspaces
remain outside tracked source and must travel separately. No commit or push is
performed by this instruction. The original scientific source/package stays unchanged.
