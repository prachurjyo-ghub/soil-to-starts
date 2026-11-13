# START HERE — Saim to Fardin climate delivery v1.0.0

Current repository delivery supersedes the USB workflow below: clone/pull
`main2`, then run `python3 scripts/setup_climate_data.py`. See
[GitHub setup](CLIMATE_GITHUB_SETUP.md) in the repository. The folder instructions
below remain historical/manual fallback documentation; no manual transfer is
required by the current workflow.

Git contains the implementation and producer receipt, **not the ignored data**.
Receive this entire delivery folder separately. No upload, email or external
transfer has been performed by the assistant. The sealed archive remains v1.0.0.

## Transfer the folder

Saim: copy the entire `Saim_to_Fardin_climate_v1.0.0` folder to an available USB
storage device using Finder, eject it safely, and give it to Fardin. Fardin: copy
the whole folder from USB to a local directory, then verify before extracting.
Use an existing external drive if one is available; no particular device or
account availability has been assumed or configured. If USB is unavailable,
choose a mutually available private file-transfer method; no account, cloud
upload or message is authorized here. Do not commit the archive/cache to Git.
Preserve `CLIMATE_DATA_PACKAGE_TERMS.md`: NASA requests notification of research
redistribution, none was sent, and BAMIS mapping public-redistribution rights are
unverified. This local preparation is not public-sharing clearance.

## Verify before running the bootstrap

The trusted producer receipt is also committed on `main2` at revision `db37c6d`:
`data/climate/climate_data_package_v1_receipt.json`. Compare the received receipt
with that trusted repository copy. Hashes from the same untrusted transfer channel
prove consistency, not sender identity. Expected archive SHA-256:
`4a0ba04c9c8beaa0a908e0b4d61cc23c6b90f87ad927bbe229405860eda6117b`.
Expected bootstrap SHA-256:
`6b33abf5dee24570e04d01ed12e52a74a989aa7da1ecd1946f477f7aaf26bcd8`.

Use Python 3.9+ (standard library only) and at least 2 GiB free. Set the delivery
path once; `/path/to/...` is the only received-folder placeholder below:

```bash
export CLIMATE_DELIVERY=/path/to/Saim_to_Fardin_climate_v1.0.0
python3 - <<'PY'
import hashlib, json, os
from pathlib import Path
p = Path(os.environ['CLIMATE_DELIVERY'])
r = json.loads((p/'climate_data_package_v1_receipt.json').read_text())
for name, expected in [
    ('soil-to-stars-climate-bgd-v1.0.0.tar.gz', r['archive_sha256']),
    ('PACKAGE_MANIFEST.json', r['manifest_sha256']),
    ('package_climate_data.py', r['bootstrap_sha256'])]:
    h = hashlib.sha256()
    with (p/name).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    if h.hexdigest() != expected: raise SystemExit('Mismatch: '+name)
assert (p/'soil-to-stars-climate-bgd-v1.0.0.tar.gz').stat().st_size == r['archive_bytes']
assert (p/'soil-to-stars-climate-bgd-v1.0.0.tar.gz.sha256').read_text().split()[0] == r['archive_sha256']
print('PASS archive, manifest, bootstrap and sidecar against producer receipt')
PY
```

The package manifest lists 2,618 payload files; one additional manifest makes
2,619 archive members. Do not run a mismatched bootstrap or silently replace
artifacts. The package's older HEAD identifies its build baseline, while its nine
source-file hashes identify the working implementation. These source bytes were
subsequently committed in `159adfa` and are present at `db37c6d`. No archive rebuild
or package-version change is necessary to transfer the same verified bytes.

## Extract and test in fresh directories

Use paths that do not already exist. On Windows use equivalent fresh paths and
`python`/PowerShell environment syntax if required; these exact shell commands
are the tested POSIX/macOS/Linux form. Python/zlib differences may cause compressed
byte mismatches: record the mismatch and environment, do not waive it silently.

```bash
mkdir /tmp/soil-climate-fardin
python3 "$CLIMATE_DELIVERY/package_climate_data.py" extract "$CLIMATE_DELIVERY/soil-to-stars-climate-bgd-v1.0.0.tar.gz" --destination /tmp/soil-climate-fardin/extracted --sha256 4a0ba04c9c8beaa0a908e0b4d61cc23c6b90f87ad927bbe229405860eda6117b
export CLIMATE_ROOT=/tmp/soil-climate-fardin/extracted/soil-to-stars-climate-bgd-v1.0.0
python3 "$CLIMATE_ROOT/src/acquire/package_climate_data.py" verify --root "$CLIMATE_ROOT"
OFFLINE=1 python3 "$CLIMATE_ROOT/src/acquire/package_climate_data.py" validate --root "$CLIMATE_ROOT" --report /tmp/soil-climate-fardin/validation.json
OFFLINE=1 python3 "$CLIMATE_ROOT/src/acquire/package_climate_data.py" reproduce --root "$CLIMATE_ROOT" --destination /tmp/soil-climate-fardin/reproduced --report /tmp/soil-climate-fardin/reproduction.json
python3 "$CLIMATE_ROOT/src/acquire/package_climate_data.py" examples --root "$CLIMATE_ROOT"
```

The first command creates the fresh parent; if it already exists, select a new
parent path throughout the commands. Extraction and reproduction destinations
themselves must not exist. A
failed attempt may leave a diagnostic tree; use a new empty parent on retry.
The existing helper rejects traversal, links, duplicate/unlisted files, checksum
failures and overwrite attempts. Validation/reproduction run isolated Python
with OFFLINE=1 plus a socket audit hook. No raw data needs to be reacquired.

## Read the data and record recipient results

See `CLIMATE_CONSUMPTION.md`, `CLIMATE_PARAMETER_COMPATIBILITY.json` and the real
`CLIMATE_DELIVERY_EXAMPLE.json`. The original package setup/terms documents are
also included. Local backend requests must read prepared files; NASA calls belong
only to deliberate acquisition/refresh. This does not make the entire website
offline or supply backend deployment, frontend assets, fonts, maps or dependencies.

Recipient checklist — Fardin fills this after actually running the checks:

- [ ] Record OS, Python version and zlib runtime; producer tested Python 3.9.6/zlib 1.2.12.
- [ ] Confirm receipt via trusted Git/source and verify archive/manifest/bootstrap hashes.
- [ ] Verify all 2,618 payload files in a fresh extraction.
- [ ] Validate all 100 raw request identities and original registry/output roles offline.
- [ ] Reproduce all 2,387 derived files exactly in a separate root with no derived inputs copied.
- [ ] Load a regional and district record; inspect anchor/output coordinates, nulls, units and provenance.
- [ ] Acknowledge 42 shared positions, 11 outside-polygon mappings, historical-context limits and source anomalies.
- [ ] Record actual commands/results and issues; do not mark scientific approval or application integration from these checks.

Producer-side local verification is separate from independent recipient validation.
No recipient result or acceptance is claimed. Fardin owns backend/calculation
integration, Maruf crop evidence and applicable rules, Prachurjo frontend work.
Saim supplies the unchanged data and resolves actual reproducibility issues.
