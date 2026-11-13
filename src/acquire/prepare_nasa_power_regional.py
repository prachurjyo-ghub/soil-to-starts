#!/usr/bin/env python3
"""Deterministic offline regional observation and monthly payload preparation."""
import argparse
import calendar
import gzip
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path
import download_nasa_power_regional as r

VERSION = "regional-preparation-v1"


def observations(raw, spec, config, artifact):
    r.validate_response_bytes(raw, spec, config)
    payload = json.loads(raw)
    for feature in sorted(payload["features"], key=lambda f: f["geometry"]["coordinates"][:2]):
        lon, lat = feature["geometry"]["coordinates"][:2]
        for parameter, series in sorted(feature["properties"]["parameter"].items()):
            for date, value in series.items():
                missing = value == payload["header"]["fill_value"]
                yield dict(collection_id=config["collection_id"], request_id=spec["request_id"],
                           parameter=parameter, date=f"{date[:4]}-{date[4:6]}-{date[6:]}",
                           output_longitude=lon, output_latitude=lat, value=None if missing else value,
                           unit=payload["parameters"][parameter]["units"], time_standard="LST",
                           missing_reason="source_fill_value" if missing else None, raw_artifact=artifact)


def monthly(rows):
    groups = defaultdict(list)
    seen = set()
    for row in rows:
        key = (row["parameter"], row["date"], row["output_longitude"], row["output_latitude"])
        if key in seen:
            raise ValueError(f"Duplicate/conflicting observation key: {key}")
        seen.add(key)
        groups[(key[0], row["date"][:7], key[2], key[3])].append(row)
    for (parameter, month, lon, lat), items in sorted(groups.items()):
        expected = calendar.monthrange(int(month[:4]), int(month[5:]))[1]
        values = [i["value"] for i in items if i["value"] is not None]
        complete = len(values) == expected
        # A daily mm/day rate represents a one-day interval; sum(value * 1 day).
        statistic = (sum(values) if parameter == "PRECTOTCORR" else sum(values) / len(values)) if values else None
        yield dict(parameter=parameter, date=month, output_longitude=lon, output_latitude=lat,
                   value=statistic if complete else None, available_day_statistic=statistic,
                   statistic="daily_rate_times_one_day_sum" if parameter == "PRECTOTCORR" else "mean_of_daily_values",
                   unit="mm" if parameter == "PRECTOTCORR" else "C", valid_days=len(values),
                   expected_days=expected, coverage="complete" if complete else "partial",
                   source_artifacts=sorted({i["raw_artifact"] for i in items}), processing_version=VERSION)


def join_wide(parameter_rows):
    """Join only identical coordinate/date support; reject duplicates first."""
    indexed = {}
    for parameter, rows in parameter_rows.items():
        entries = {}
        for row in rows:
            key = (row["date"], row["output_longitude"], row["output_latitude"])
            if key in entries or row["parameter"] != parameter:
                raise ValueError("Duplicate/conflicting wide input")
            entries[key] = row
        indexed[parameter] = entries
    if set(indexed) != set(r.PARAMETERS) or len({frozenset(v) for v in indexed.values()}) != 1:
        return None
    return [dict(date=key[0], output_longitude=key[1], output_latitude=key[2],
                 values={p: indexed[p][key]["value"] for p in sorted(indexed)},
                 units={p: indexed[p][key]["unit"] for p in sorted(indexed)},
                 missing_reasons={p: indexed[p][key]["missing_reason"] for p in sorted(indexed)},
                 raw_artifacts={p: indexed[p][key]["raw_artifact"] for p in sorted(indexed)},
                 time_standard="LST", processing_version=VERSION)
            for key in sorted(next(iter(indexed.values())))]


def select_periods(monthly_rows, start_month=1, month_count=12):
    """Provisional descriptive extrema, complete months only; cross-year supported."""
    if not 1 <= start_month <= 12 or not 1 <= month_count <= 12:
        raise ValueError("Month start/count must be in 1..12")
    by_month = {row["date"]: row for row in monthly_rows}
    candidates = []
    for year in sorted({int(d[:4]) for d in by_month}):
        months = []
        for offset in range(month_count):
            absolute = year * 12 + start_month - 1 + offset
            months.append(f"{absolute // 12:04d}-{absolute % 12 + 1:02d}")
        selected = [by_month.get(month) for month in months]
        if any(row is None or row["coverage"] != "complete" for row in selected):
            continue
        parameter = selected[0]["parameter"]
        if parameter == "PRECTOTCORR":
            value = sum(row["value"] for row in selected)
        else:
            value = sum(row["value"] * row["expected_days"] for row in selected) / sum(row["expected_days"] for row in selected)
        candidates.append(dict(start=months[0], end=months[-1], value=value))
    return dict(status="provisional_descriptive_only", start_month=start_month, month_count=month_count,
                usable_periods=len(candidates), tie_break="earliest start",
                minimum=min(candidates, key=lambda x: (x["value"], x["start"])) if candidates else None,
                maximum=min(candidates, key=lambda x: (-x["value"], x["start"])) if candidates else None)


def write_jsonl_gzip(path, rows):
    # Atomic, deterministic gzip without a filename or retrieval timestamp.
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".prepare-")
    try:
        with os.fdopen(descriptor, "wb") as file:
            with gzip.GzipFile(fileobj=file, mode="wb", mtime=0, filename="") as compressed:
                for row in rows:
                    compressed.write((json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def prepare(config, cache, output, start_month=1, month_count=12):
    output.mkdir(parents=True, exist_ok=True)
    downloader = r.RegionalDownloader(config, cache, opener=lambda *a, **kw: (_ for _ in ()).throw(AssertionError("Network forbidden")))
    inventory = []
    support = defaultdict(dict)
    chart = defaultdict(list)
    year_rows = {}
    wide_status = {}
    wide_artifacts = []
    current_year = None
    for spec in r.build_full_requests(config):
        if current_year != spec["start"][:4]:
            year_rows = {}
            current_year = spec["start"][:4]
        raw_path, manifest_path = downloader.paths(spec)
        if not raw_path.exists() or not manifest_path.exists():
            continue
        manifest = downloader._cached(spec)
        if manifest is None:
            raise ValueError(f"Invalid local cache: {spec['request_id']}")
        artifact = manifest["response"]["sha256"]
        rows = list(observations(raw_path.read_bytes(), spec, config, artifact))
        stem = spec["request_id"]
        normalized_path = output / f"{stem}.jsonl.gz"
        write_jsonl_gzip(normalized_path, rows)
        year_rows[spec["parameter_label"]] = rows
        if spec["parameter_label"] == list(r.PARAMETERS)[-1]:
            wide = join_wide(year_rows)
            wide_status[spec["start"][:4]] = "exact_keys_compatible" if wide is not None else "mismatched_or_missing_support"
            if wide is not None:
                wide_path = output / f"{spec['start'][:4]}.wide-replay.jsonl.gz"
                write_jsonl_gzip(wide_path, wide)
                wide_artifacts.append(dict(path=r.recorded_path(wide_path), sha256=r.sha256(wide_path.read_bytes()), rows=len(wide)))
            year_rows = {}
        summaries = list(monthly(rows))
        for item in summaries:
            chart[(item["output_longitude"], item["output_latitude"], item["parameter"])].append(item)
        r.atomic_write(output / f"{stem}.monthly.json", r.canonical_json(summaries))
        support[spec["start"][:4]][spec["parameter_label"]] = manifest["validation"]["coordinate_set_sha256"]
        inventory.append(dict(request_id=stem, raw_artifact=manifest["response"], source_metadata=manifest["validation"],
                              observations=len(rows), missing=sum(row["value"] is None for row in rows),
                              normalized_sha256=r.sha256(normalized_path.read_bytes())))
    for (lon, lat, parameter), series in sorted(chart.items()):
        series.sort(key=lambda row: row["date"])
        payload = dict(collection_id=config["collection_id"], output_longitude=lon, output_latitude=lat,
                       parameter=parameter, period=[series[0]["date"], series[-1]["date"]], time_standard="LST",
                       processing_version=VERSION, source_urls=config["source"]["documentation_urls"],
                       series=series, provisional_selection=select_periods(series, start_month, month_count))
        r.atomic_write(output / f"chart-{lon}-{lat}-{parameter}.json", r.canonical_json(payload))
    report = dict(processing_version=VERSION, period=["2001-01-01", "2025-12-31"], requests=inventory,
                  coordinate_support_by_year=support, wide_view_status=wide_status, wide_artifacts=wide_artifacts,
                  replay_status="Daily regional series prepared; seasonal bounds and selection criteria pending; descriptive configurable extrema only",
                  district_series_produced=False)
    r.atomic_write(output / "inventory.json", r.canonical_json(report))
    print(f"Prepared {len(inventory)} request partitions offline in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=r.ROOT / "cache/nasa_power_regional/prepared-v1")
    parser.add_argument("--start-month", type=int, default=1)
    parser.add_argument("--month-count", type=int, default=12)
    args = parser.parse_args()
    prepare(r.load_config(), r.DEFAULT_CACHE, args.output, args.start_month, args.month_count)
