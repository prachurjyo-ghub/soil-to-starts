#!/usr/bin/env python3
"""Rebuild the versioned administrative map asset from checked-in source bytes. No network."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/admin'
OUTPUT = ROOT / 'prototype/public/reference/data'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fixture_samples(data, source_sha):
    """Independent Python ring parity, used only to produce labelled geometric test fixtures."""
    def inside(point, ring):
        x, y = point
        crossed = False
        for a, b in zip(ring, ring[1:]):
            if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
                crossed = not crossed
        return crossed
    samples = []
    for feature in data['features']:
        geometry = feature['geometry']
        polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
        found = None
        for polygon in polygons:
            xs, ys = [p[0] for p in polygon[0]], [p[1] for p in polygon[0]]
            for j in range(1, 16):
                for i in range(1, 16):
                    point = [min(xs)+(max(xs)-min(xs))*i/16, min(ys)+(max(ys)-min(ys))*j/16]
                    if inside(point, polygon[0]) and not any(inside(point, hole) for hole in polygon[1:]):
                        found = point
                        break
                if found:
                    break
            if found:
                break
        assert found, feature['id']
        samples.append({'district_id':feature['id'], 'source_shape_id':feature['properties']['source_shape_id'], 'point':found})
    return {'kind':'geometry-derived test interiors, not observed farms/city centroids', 'boundary_version':data['boundary_version'],
            'source_sha256':source_sha, 'method':'Independent Python odd-even ring test, first interior 1/16 bounding-grid sample in a source polygon excluding holes; expected district from explicit source shape mapping.', 'samples':samples}


def main():
    raw = gzip.decompress((SOURCE / 'bgd-adm2-source.geojson.gz').read_bytes())
    retrieval = json.loads((SOURCE / 'bgd-adm2-retrieval.json').read_text())
    assert sha(raw) == retrieval['source_sha256'] == '7dbdb186f3b8af10417147a99859196fcd89c619fb5c6ac3804251fb6b449b6a'
    metadata = json.loads((SOURCE / 'bgd-adm2-metadata.json').read_text())
    mapping = json.loads((SOURCE / 'bgd-adm2-mapping.json').read_text())
    by_shape = {row['source_shape_id']: row for row in mapping}
    assert len(by_shape) == len({row['district_id'] for row in mapping}) == 64
    collection = json.loads(raw)
    features = []
    vertices = 0
    for feature in collection['features']:
        props, geometry = feature['properties'], feature['geometry']
        row = by_shape[props['shapeID']]
        assert row['source_name'] == props['shapeName']
        assert geometry['type'] in ('Polygon', 'MultiPolygon')
        polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
        positions = []
        for polygon in polygons:
            for ring in polygon:
                assert len(ring) >= 4 and ring[0] == ring[-1]
                positions.extend(ring)
        vertices += len(positions)
        bbox = [min(p[0] for p in positions), min(p[1] for p in positions), max(p[0] for p in positions), max(p[1] for p in positions)]
        features.append({'type':'Feature', 'id':row['district_id'], 'bbox':bbox,
                         'properties':{'district_id':row['district_id'], 'source_shape_id':props['shapeID'], 'source_name':props['shapeName']},
                         'geometry':geometry})
    assert len(features) == 64
    version = 'BGD-ADM2-16705992@9469f09-local1'
    data = {'type':'FeatureCollection', 'boundary_version':version, 'features':sorted(features,key=lambda f:f['id'])}
    processed = (json.dumps(data,separators=(',',':'),ensure_ascii=False)+'\n').encode()
    manifest = {
        'id':'geoboundaries-bgd-adm2', 'version':version, 'boundary_id':metadata['boundaryID'],
        'represented_year':metadata['boundaryYearRepresented'], 'upstream_revision':'9469f09',
        'metadata_url':'https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM2/',
        'download_url':metadata['simplifiedGeometryGeoJSON'],
        'lfs_download_url':metadata['simplifiedGeometryGeoJSON'].replace('https://github.com/wmgeolab/geoBoundaries/raw/','https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/'),
        'source_providers':metadata['boundarySource'], 'upstream_source_url':'https://'+metadata['boundarySourceURL'],
        'source_build_date':metadata['buildDate'], **retrieval,
        'license':metadata['boundaryLicense'], 'license_url':'https://creativecommons.org/licenses/by/3.0/igo/',
        'attribution':'geoBoundaries gbOpen Bangladesh ADM2; Bangladesh Bureau of Statistics (BBS), OCHA ROAP; CC BY 3.0 IGO',
        'processed_sha256':sha(processed), 'processed_bytes':len(processed), 'gzip_bytes':len(gzip.compress(processed,mtime=0)),
        'feature_count':64, 'vertex_count':vertices, 'coordinate_order':'longitude, latitude (GeoJSON)',
        'processing':['Use pinned upstream simplified geometry; verify its Git LFS SHA-256.',
                      'Map every source shape ID/name through the explicit 64-row alias ledger; no fuzzy matching.',
                      'Preserve all coordinate values, polygons, multipolygons and holes; no further simplification/rounding.',
                      'Replace properties with source identity/application ID, add per-feature bbox, sort by ID, minify JSON.',
                      'Use the SAME local geometry for display and containment; no separate coarse country mask.'],
        'limitations':['Administrative reference, not a field survey or scientific coverage.',
                       'Upstream metadata says represented year 2020; its source URL refers to boundaries as of 2015. Current legal alignment is not established.',
                       'Upstream simplification tolerance/positional accuracy is unspecified here; coastal gaps/islands and border uncertainty can remain.',
                       'Border/overlap/unresolved points require correction or district search; never snap to the nearest district.']
    }
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/'district-boundaries.v1.geojson').write_bytes(processed)
    (OUTPUT/'district-boundaries.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'tests/fixtures/district-interior-points.json').write_text(json.dumps(fixture_samples(data,sha(raw)),indent=2)+'\n')
    print(f"64 districts; {vertices} vertices; {len(processed)} bytes; {manifest['gzip_bytes']} gzip bytes; SHA-256 {sha(processed)}")


if __name__ == '__main__':
    main()
