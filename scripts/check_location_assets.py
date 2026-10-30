#!/usr/bin/env python3
"""Read-only loopback production-asset smoke check. Does not exercise browser/WebGL behavior."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:3014')
    args = parser.parse_args()
    assert urlparse(args.base_url).hostname in ('localhost', '127.0.0.1', '::1'), 'Use a local preview'
    worker = next((ROOT / 'prototype/.next/static/media').glob('maplibre-gl-worker*.mjs'))
    public = ROOT / 'prototype/public'
    paths = ['/workspace', '/reference/location.js', '/reference/intake.js', '/reference/intake-map.js', '/reference/intake-ui.js',
             '/reference/data/district-boundaries.v1.geojson', '/reference/licenses/maplibre-gl.LICENSE.txt', '/_next/static/media/' + worker.name]
    for path in paths:
        started = time.perf_counter()
        request = Request(args.base_url.rstrip('/') + path, headers={'Accept-Encoding': 'gzip'})
        with urlopen(request, timeout=10) as response:
            body = response.read()
            encoding = response.headers.get('Content-Encoding', 'identity')
            content = gzip.decompress(body) if encoding == 'gzip' else body
            assert response.status == 200
            if path.startswith('/reference/'):
                assert content == (public / path.lstrip('/')).read_bytes(), 'Stale/missing local asset: ' + path
            elif 'worker' in path:
                assert content == worker.read_bytes()
                assert 'javascript' in response.headers.get('Content-Type', '')
            else:
                assert b'/reference/workspace.js' in content
            print(json.dumps({'asset': path, 'status': response.status, 'encoding': encoding, 'transfer_bytes': len(body),
                              'decoded_bytes': len(content), 'loopback_ms': round((time.perf_counter()-started)*1000,2)}))
    manifest = json.loads((public/'reference/data/district-boundaries.manifest.json').read_text())
    assert hashlib.sha256((public/'reference/data/district-boundaries.v1.geojson').read_bytes()).hexdigest() == manifest['processed_sha256']
    assert (public/'reference/licenses/maplibre-gl.LICENSE.txt').read_bytes() == (ROOT/'prototype/node_modules/maplibre-gl/LICENSE.txt').read_bytes()
    print('All 8 loopback assets match; boundary checksum and deployed license verified. Browser/WebGL/mobile not tested.')


if __name__ == '__main__':
    main()
