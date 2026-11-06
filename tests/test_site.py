"""Offline publishing checks. Run: python3 -m unittest discover -s tests -v"""
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.parse import parse_qs, unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
DOMAIN = 'nyctarotreader.com'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.source = path.read_text()
        self.tags, self.schemas = [], []
        self.schema = None
        self.feed(self.source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.schema = ''

    def handle_data(self, value):
        if self.schema is not None:
            self.schema += value

    def handle_endtag(self, tag):
        if tag == 'script' and self.schema is not None:
            self.schemas.append(json.loads(self.schema))
            self.schema = None

    def elements(self, tag):
        return [attrs for name, attrs in self.tags if name == tag]


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, 'scripts/build.py', '--offline'], cwd=ROOT, check=True)
        cls.pages = {p.relative_to(DIST).as_posix(): Page(p) for p in DIST.rglob('*.html')}

    def test_internal_links_and_assets_resolve(self):
        for name, page in self.pages.items():
            for tag, attrs in page.tags:
                for key in ('href', 'src'):
                    link = attrs.get(key, '')
                    parsed = urlsplit(link)
                    if not link or parsed.scheme or parsed.netloc or not parsed.path.startswith('/'):
                        continue
                    target = DIST / unquote(parsed.path).lstrip('/')
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), (name, tag, link))

    def test_discoverable_pages_and_sitemap_agree(self):
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemap = ET.parse(DIST / 'sitemap.xml')
        urls = [x.text for x in sitemap.findall('s:url/s:loc', ns)]
        self.assertEqual(len(urls), len(set(urls)))
        for name, page in self.pages.items():
            robots = next((m.get('content', '') for m in page.elements('meta') if m.get('name') == 'robots'), '')
            canonical = [x['href'] for x in page.elements('link') if x.get('rel') == 'canonical']
            if 'noindex' in robots:
                self.assertFalse(canonical, name)
            else:
                self.assertEqual(len(canonical), 1, name)
                self.assertIn(canonical[0], urls, name)
                self.assertEqual(urlsplit(canonical[0]).hostname, DOMAIN)
            self.assertEqual(len(page.elements('h1')), 1, name)
            descriptions = [x.get('content') for x in page.elements('meta') if x.get('name') == 'description']
            self.assertTrue(descriptions and descriptions[0], name)
            self.assertTrue(page.schemas, name)
        for url in urls:
            self.assertNotIn(urlsplit(url).path, ['/search/', '/cart/', '/404.html'])
        self.assertIn('Sitemap: https://' + DOMAIN + '/sitemap.xml', (DIST / 'robots.txt').read_text())

    def test_reader_prices_and_booking_routes_preserved(self):
        readers = json.loads((ROOT / 'site/readers.json').read_text())
        for key, reader in readers.items():
            page = self.pages[f'readers/{key}/index.html']
            bookings = [a for a in page.elements('a') if a.get('href', '').startswith('https://book.squareup.com/')]
            self.assertEqual(len(bookings), 1, key)
            self.assertEqual(bookings[0]['href'], reader['book'], key)
            self.assertEqual(bookings[0]['data-reader-id'], key)
            self.assertIn('online/card totals may differ', page.source, key)
            self.assertIn('cancellation terms on Square', page.source, key)
            for _, price in reader['services']:
                self.assertIn(f'<td>{price}</td>', page.source, key)
        hypno = self.pages['readers/jennifer-shanteau/index.html'].source
        self.assertIn('Jennifer Shanteau: Hypnotherapy &amp; Energy Work', hypno)
        remote = self.pages['readers/mychal-a-bryan/index.html'].source
        self.assertIn('Remote sessions through Namaste Bookshop.', remote)
        directory = self.pages['book-today/index.html'].source
        upstairs, remote_section = directory.split('<h2>Upstairs, by appointment</h2>')[1].split('<h2>Remote sessions</h2>')
        self.assertNotIn('/readers/mychal-a-bryan/', upstairs)
        self.assertIn('/readers/mychal-a-bryan/', remote_section)

    def test_direct_booking_directory_and_guides(self):
        readers = json.loads((ROOT / 'site/readers.json').read_text())
        page = self.pages['book-today/index.html']
        links = [a for a in page.elements('a') if a.get('data-placement') == 'reader_directory']
        self.assertEqual(len(links), len(readers))
        self.assertEqual({a['data-reader-id'] for a in links}, set(readers))
        for a in links:
            self.assertEqual(a['href'], readers[a['data-reader-id']]['book'])
        cards = [a for a in page.elements('li') if 'data-reader-card' in a]
        self.assertEqual(len(cards), len(readers))
        self.assertTrue(any('hidden' in a for a in page.elements('div') if 'data-reader-filters' in a))
        home = self.pages['index.html'].source
        self.assertLess(home.index('data-placement="home_readers"'), home.index('class="five"'))
        for path in ('what-to-ask', 'at-the-table', 'find-the-shop', 'what-it-costs', 'walk-in-or-book'):
            self.assertIn('data-placement="guide_end"', self.pages[path + '/index.html'].source)

    def test_phone_search_landing_is_accurate_and_linked(self):
        readers = json.loads((ROOT / 'site/readers.json').read_text())
        page = self.pages['phone-tarot-readings/index.html']
        links = [a for a in page.elements('a') if a.get('data-placement') == 'phone_landing']
        self.assertEqual({a['data-reader-id'] for a in links}, {k for k, r in readers.items() if r['phone']})
        for a in links:
            self.assertEqual(a['href'], readers[a['data-reader-id']]['book'])
        self.assertTrue(any(s.get('@type') == 'FAQPage' for s in page.schemas))
        for name in ('index.html', 'book-today/index.html', 'what-to-ask/index.html'):
            self.assertTrue(any(a.get('href') == '/phone-tarot-readings/' for a in self.pages[name].elements('a')))

    def test_product_offer_matches_cached_variant(self):
        products = {p['handle']: p for p in json.loads((ROOT / 'data/products.json').read_text())}
        for name, page in self.pages.items():
            if not name.startswith('products/'):
                continue
            handle = name.split('/')[1]
            source = products[handle]
            variant = next((v for v in source['variants'] if v['available']), source['variants'][0])
            schema = next(s for s in page.schemas if s['@type'] == 'Product')
            offer = schema['offers']
            self.assertEqual(float(offer['price']), float(variant['price']), name)
            self.assertEqual(offer['seller']['url'], 'https://namastebookshop.com/')
            expected_stock = 'InStock' if any(v['available'] for v in source['variants']) else 'OutOfStock'
            self.assertEqual(offer['availability'], 'https://schema.org/' + expected_stock)
            official = [a for a in page.elements('a') if a.get('data-link-type') == 'product']
            self.assertEqual(len(official), 1, name)
            self.assertEqual(urlsplit(official[0]['href']).path, '/products/' + handle)

    def test_namaste_referral_links_are_static_and_attributed(self):
        count = 0
        for page in self.pages.values():
            for a in page.elements('a'):
                url = urlsplit(a.get('href', ''))
                if url.hostname != 'namastebookshop.com':
                    continue
                query = parse_qs(url.query)
                self.assertEqual(query.get('utm_source'), [DOMAIN])
                self.assertEqual(query.get('utm_medium'), ['referral'])
                self.assertEqual(query.get('utm_campaign'), ['namaste_network'])
                self.assertTrue(query.get('utm_content'))
                count += 1
        self.assertGreater(count, len(self.pages))

    def test_analytics_configuration_and_privacy(self):
        for name, page in self.pages.items():
            self.assertIn('"site_domain": "nyctarotreader.com"', page.source, name)
            self.assertIn('G-Y7R5K9NMW0', page.source, name)
        privacy = self.pages['privacy/index.html'].source
        self.assertIn('Your cart is kept in this browser', privacy)
        self.assertIn('Namaste Bookshop', privacy)


if __name__ == '__main__':
    unittest.main()
