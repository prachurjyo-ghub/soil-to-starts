# Acquisition boundary

Planned first source: NASA POWER daily rainfall and temperature for an agreed pilot location and date range. Save raw responses, cleaned tabular data, and a provenance manifest. Validate units, missing-value codes, time standard, coordinates, and expected day count. Only then add IMERG, SMAP, or vegetation indices where they answer a defined decision question.

NASA POWER acquisition is configured and smoke-tested; the full collection and
scientific integration are not implemented. See
[`docs/data/NASA_POWER_ACQUISITION.md`](../../docs/data/NASA_POWER_ACQUISITION.md).
The Step 3 reuse review is documented in
[`docs/data/NASA_POWER_REDUNDANCY_REVIEW.md`](../../docs/data/NASA_POWER_REDUNDANCY_REVIEW.md).

The nationwide district sampling registry is generated offline from the pinned
administrative geometry:

```bash
python3 src/acquire/build_district_sampling_registry.py --check
```

Use `--write --check` only when intentionally regenerating
`data/climate/district_sampling_registry.csv` and its manifest. The script uses
the Python standard library, makes no network request, downloads no weather
observations and never reads earlier sampling-coordinate fixtures.

POWER configuration and network-free request preview:

```bash
python3 src/acquire/download_nasa_power.py --check-config --scope smoke
```

Live execution requires `--execute`; full scope additionally requires
`--confirm-full-collection` and a verified parameter-complete reuse decision.
The current decision intentionally blocks full execution because POWER exposes
no authoritative equivalence key for the four-parameter point requests.
Generate the machine-readable dry-run plan with:

```bash
python3 src/acquire/download_nasa_power.py --check-config --scope full --write-reuse-decision --write-full-plan
```

`OFFLINE=1` blocks all live acquisition.

The separate Daily Regional Step 3B client does not alter the blocked Point
execution gate:

```bash
python3 src/acquire/download_nasa_power_regional.py --check-config --plan smoke --probe-multi-parameter
```

Its bounded live smoke, returned-coordinate extraction proposal and limitations
are documented in
[`docs/data/NASA_POWER_REGIONAL_PROPOSAL.md`](../../docs/data/NASA_POWER_REGIONAL_PROPOSAL.md).
The module has no full-execution flag.
