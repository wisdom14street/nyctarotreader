"""Record and verify public release files without contacting booking or checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def manifest(sha):
    paths = ['index.html', 'cart/index.html', 'book-today/index.html',
             'privacy/index.html', 'sitemap.xml', 'robots.txt',
             'assets/ga.js', 'assets/cart.js', 'assets/shop.js']
    paths += ['readers/' + key + '/index.html' for key in json.loads((ROOT / 'site/readers.json').read_text())]
    paths += [str(next((ROOT / 'dist/products').glob('*/index.html')).relative_to(ROOT / 'dist'))]
    result = {'commit': sha, 'files': {p: digest((ROOT / 'dist' / p).read_bytes()) for p in paths}}
    (ROOT / 'dist/release.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'Recorded {len(paths)} release files for {sha}')


def read(url):
    request = Request(url, headers={'User-Agent': 'NYC-Tarot-Release-Check/1.0', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=30) as response:
        if urlsplit(response.url).netloc != urlsplit(url).netloc:
            raise ValueError('Unexpected cross-host redirect: ' + response.url)
        return response.read()


def verify(base, sha):
    base = base.rstrip('/')
    target = urlsplit(base)
    domain = json.loads((ROOT / 'site/config.json').read_text())['domain']
    if not ((target.scheme == 'https' and target.netloc == domain) or
            (target.scheme == 'http' and target.hostname == '127.0.0.1')):
        raise ValueError('Verification is restricted to this site or the local test server')
    if target.path or target.query or target.fragment:
        raise ValueError('Use the site origin without a path or query')
    for attempt in range(6):
        try:
            release = json.loads(read(base + '/release.json'))
            if release.get('commit') == sha:
                break
        except HTTPError as error:
            # Allow propagation of a newly published manifest, never retry 429.
            if error.code != 404:
                raise
        if attempt == 5:
            raise ValueError('The expected release is not live')
        time.sleep(10)
    expected = json.loads((ROOT / 'dist/release.json').read_text()) if (ROOT / 'dist/release.json').exists() else None
    if expected and expected != release:
        raise ValueError('Published manifest differs from the locally built manifest')
    files = release.get('files', {})
    if not files or 'cart/index.html' not in files or 'assets/ga.js' not in files:
        raise ValueError('Release manifest is missing required files')
    for path, checksum in files.items():
        if path.startswith('/') or '..' in path.split('/') or urlsplit(path).scheme or '?' in path or '#' in path:
            raise ValueError('Invalid release path')
        route = path[:-10] if path.endswith('index.html') else path
        data = read(base + '/' + route)
        if digest(data) != checksum:
            raise ValueError('Published file differs from the release: ' + path)
        print('PASS live: /' + route)
    print(f'LIVE VERIFIED: {sha}, {len(files)} matching pages/assets; no booking or checkout requests')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['manifest', 'verify'])
    parser.add_argument('--sha', required=True)
    parser.add_argument('--url', default='https://nyctarotreader.com')
    args = parser.parse_args()
    manifest(args.sha) if args.action == 'manifest' else verify(args.url, args.sha)
