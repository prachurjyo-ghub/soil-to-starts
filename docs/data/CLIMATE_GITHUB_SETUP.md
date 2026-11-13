# Clone-and-setup climate data through GitHub

**Publication blocked:** implementation is committed locally and local Git-clone
setup passed, but automatic approval review rejected the archive push before
execution. The archive is not yet available from origin/main2. Exact user approval
for this payload/destination and BAMIS redistribution permission are pending. The
commands below become available remotely only after a successful authorized push.

Saim has authorized Git-hosted delivery on `main2`, replacing manual folder
transfer as the current teammate workflow. This includes the unchanged v1.0.0
archive directly in Git; no cloud account, Git LFS, USB copy or NASA request is
needed. Git cloning/fetching requires internet; installation uses local files.

```bash
git clone --branch main2 https://github.com/prachurjyo-ghub/soil-to-starts.git
cd soil-to-starts
python3 scripts/setup_climate_data.py
```

Existing clones instead run `git pull --ff-only origin main2` (preserving any local
work first), then the same setup command. Use Python 3.9+, standard library only.
Keep at least 2 GiB free. Git contains one 88,023,118-byte archive in
`data/climate/packages/v1.0.0/`, plus its checksum and manifest. That archive is
below GitHub's 100 MiB ordinary-Git limit but above the 50 MiB warning threshold;
new data versions should consider repository growth instead of repeatedly
replacing this binary. No second raw/prepared copy is committed.

Setup verifies the archive, manifest and matching helper against the original
producer receipt, extracts safely, verifies every payload checksum and runs the
existing offline raw/registry/geometry checks with socket networking blocked.
It fails explicitly on missing/corrupt data and never reacquires NASA data.
Repeated setup verifies the same installed bytes; it does not overwrite modified
files. For an incomplete/modified installation, inspect it or choose a fresh
`--install-dir`; the script never deletes an old cache.

The default data root is:
`cache/climate_repository/v1.0.0/extracted/soil-to-stars-climate-bgd-v1.0.0/`.
Its `cache/nasa_power_regional/prepared-v1/` contains daily regional/district,
monthly, chart and replay files. Setup prints `CLIMATE_DATA_ROOT` and
`CLIMATE_PREPARED_ROOT`, and records them in
`cache/climate_repository/v1.0.0/installed.json`. These are integration inputs,
not claims that the current backend reads them. Fardin should use a configured
persistent local prepared root while serving requests; acquisition/refresh stays
separate. The entire website is not automatically offline or scientifically integrated.

```bash
python3 scripts/setup_climate_data.py --verify-only
python3 src/acquire/package_climate_data.py examples --root cache/climate_repository/v1.0.0/extracted/soil-to-stars-climate-bgd-v1.0.0
OFFLINE=1 python3 src/acquire/package_climate_data.py reproduce --root cache/climate_repository/v1.0.0/extracted/soil-to-stars-climate-bgd-v1.0.0 --destination /tmp/soil-climate-git-reproduction
```

The reproduction destination must not exist. Compressed-byte equality was tested
with Python 3.9.6/zlib 1.2.12; investigate differences on other compression runtimes.
See [consumption fields/examples](CLIMATE_CONSUMPTION.md) and
[parameter compatibility](CLIMATE_PARAMETER_COMPATIBILITY.json). The 64 anchors
use 42 output positions, 11 mappings use positions outside pinned country polygons,
shared series are not independent samples, and monthly minimum/maximum temperature
series are means of daily extrema. No clipping, crop thresholds or priority is added.

The archive and original producer receipt retain their historical build-time
local-only status as immutable provenance. Current delivery authorization is the
new Git distribution task/receipt; it does not retroactively rewrite those bytes
or establish third-party license grants, scientific approval or recipient acceptance.
Retain [original terms/attribution](CLIMATE_DATA_PACKAGE_TERMS.md). NASA requests
researcher-transmission notification; none has been sent. Public redistribution
rights for the supplied BAMIS mapping remain unverified. The owner's instruction
authorizes this Git distribution; it does not resolve that rights question.
