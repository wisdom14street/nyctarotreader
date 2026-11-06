"""Local Chromium checks; all external requests are intercepted and never sent.
Requires Python playwright and Chromium (or CHROMIUM_PATH). Build dist first.
Run: python3 tests/browser_checks.py
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from threading import Thread
from urllib.parse import parse_qs, urlsplit
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT / 'dist')))
    Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        subprocess.run([sys.executable, 'scripts/release.py', 'manifest', '--sha', 'local-check'], cwd=ROOT, check=True)
        subprocess.run([sys.executable, 'scripts/release.py', 'verify', '--url', base, '--sha', 'local-check'], cwd=ROOT, check=True)
        with sync_playwright() as p:
            executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
            browser = p.chromium.launch(executable_path=executable, headless=True, args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 1280, 'height': 900})
            external = []

            def route(request):
                url = request.request.url
                if url.startswith(base + '/'):
                    request.continue_()
                else:
                    external.append(url)
                    request.abort()

            context.route('**/*', route)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.add_init_script("""
                document.addEventListener('click', e => {
                    const a = e.target.closest('a[href]');
                    if (a && !a.href.startsWith(location.origin + '/')) e.preventDefault();
                });
                document.addEventListener('auxclick', e => e.preventDefault());
            """)

            def events():
                return page.evaluate("Array.from(window.dataLayer || []).map(a => Array.from(a)).filter(a => a[0] === 'event')")

            page.goto(base + '/readers/tyler-t-mann-tarot/')
            book = page.locator('a[data-reader-id][href^="https://book.squareup.com"]')
            book.click()
            event = events()[-1]
            assert event[1] == 'booking_click', event
            assert event[2]['reader_id'] == 'tyler-t-mann-tarot'
            assert len(events()) == 1
            book.click(button='middle')
            assert len(events()) == 2
            page.locator('.btns a[href^="tel:"]').click()
            assert events()[-1][1:2] == ['contact_click']
            page.locator('a[data-link-type="readers"]').click()
            assert events()[-1][1] == 'namaste_referral_click'
            assert '?' not in events()[-1][2]['link_url']
            print('PASS: booking, middle-click, contact and referral intent events; no external navigation')

            readers = json.loads((ROOT / 'site/readers.json').read_text())
            for key, reader in readers.items():
                page.goto(base + '/readers/' + key + '/')
                booking = page.locator('a[data-reader-id][href^="https://book.squareup.com"]')
                assert booking.get_attribute('href') == reader['book'], key
                booking.click()
                recorded = events()
                assert len(recorded) == 1 and recorded[0][1] == 'booking_click', (key, recorded)
                assert recorded[0][2]['reader_id'] == key
                assert page.url == base + '/readers/' + key + '/'
            # Query strings containing a booking URL must not turn unrelated links
            # into bookings. Internal navigation must not become a lead either.
            page.evaluate("""() => {
                for (const href of ['/book-today/', 'https://example.com/?next=https://book.squareup.com/appointments/test']) {
                    const a = document.createElement('a'); a.href = href; a.textContent = 'Book now';
                    a.addEventListener('click', e => e.preventDefault()); document.body.append(a); a.click(); a.remove();
                }
            }""")
            assert len(events()) == 1
            print('PASS: all 18 booking routes emit one correctly identified click; unrelated links emit no booking or lead')

            page.goto(base + '/book-today/')
            cards = page.locator('[data-reader-card]:visible')
            expect(cards).to_have_count(len(readers))
            page.locator('#reader-format').select_option('remote')
            expect(cards).to_have_count(1)
            expect(cards).to_contain_text('Mychal')
            page.locator('#reader-budget').select_option('40')
            expect(cards).to_have_count(0)
            expect(page.locator('[data-reader-empty]')).to_be_visible()
            page.locator('[data-reader-reset]').click()
            expect(cards).to_have_count(len(readers))
            page.locator('#reader-format').select_option('phone')
            expect(cards).to_have_count(sum(bool(r['phone']) for r in readers.values()))
            page.locator('[data-reader-reset]').click()
            for key, reader in readers.items():
                link = page.locator('[data-reader-card] a[data-reader-id="' + key + '"]')
                assert link.get_attribute('href') == reader['book']
                link.click()
                assert events()[-1][1] == 'booking_click'
                assert events()[-1][2]['placement'] == 'reader_directory'
            page.goto(base + '/')
            page.locator('[data-placement="home_hero"]').click()
            expect(page).to_have_url(base + '/book-today/')
            print('PASS: directory filters, empty/reset states, all direct bookings and homepage journey')

            page.goto(base + '/find-the-shop/')
            page.locator('a.go[href^="https://www.google.com/maps/"]').click()
            assert events()[-1][1] == 'directions_click'
            assert '?' not in events()[-1][2]['link_url']
            print('PASS: directions event excludes URL query parameters')

            catalog = json.loads((ROOT / 'dist/data/catalog.json').read_text())
            products = [x for x in catalog if not x['x']][:2]
            assert len(products) == 2
            for product in products:
                page.goto(base + '/products/' + product['h'] + '/')
                assert events()[0][1] == 'view_item'
                page.locator('#buy').click()
                expect(page.locator('#cart')).to_be_visible()
                assert any(e[1] == 'add_to_cart' for e in events())
                page.keyboard.press('Escape')
                expect(page.locator('#cart')).to_be_hidden()

            page.goto(base + '/cart/')
            page.locator('[data-cart-page] [data-inc]').first.click()
            page.reload()
            expect(page.locator('[data-cart-page] [data-qty]').first).to_have_value('2')
            checkout = page.locator('[data-cart-page] [data-checkout]')
            url = urlsplit(checkout.get_attribute('href'))
            query = parse_qs(url.query)
            assert url.hostname == 'namastebookshop.com'
            assert url.path == f'/cart/{products[0]["v"]}:2,{products[1]["v"]}:1'
            assert query['attributes[Storefront]'] == ['nyctarotreader.com']
            assert query['attributes[Site]'] == ['nyctarotreader.com']
            assert query['ref'] == ['nyctarotreader']
            assert query['note'] == ['Ordered on NYC Tarot Reader (nyctarotreader.com)']
            checkout.click()
            assert page.url == base + '/cart/'
            assert events()[-1][1] == 'begin_checkout'
            assert sum(i['quantity'] for i in events()[-1][2]['items']) == 3
            assert not any(e[1] in ('purchase', 'generate_lead', 'booking_complete') for e in events())
            page.evaluate('window.gtag = undefined')
            page.locator('[data-cart-page] [data-rm]').first.click()
            expect(page.locator('[data-cart-page] .ci')).to_have_count(1)
            checkout.click()
            assert page.url == base + '/cart/'
            print('PASS: multi-item cart, quantity, persistence, Shopify attribution, checkout intent and blocked analytics')

            page.goto(base + '/search/?q=tarot')
            expect(page.locator('[data-sgrid] .pc').first).to_be_visible()
            page.goto(base + '/your-own-deck/decks/')
            page.locator('[data-f="q"]').fill('zzzz-no-such-deck')
            expect(page.locator('[data-count]')).to_contain_text('0 items match')
            print('PASS: product search and shelf filtering')

            # The direct booking/product links must remain usable without scripts.
            plain = browser.new_context(java_script_enabled=False)
            plain.route('**/*', route)
            plain_page = plain.new_page()
            for key, reader in readers.items():
                plain_page.goto(base + '/readers/' + key + '/')
                booking = plain_page.locator('a[data-reader-id][href^="https://book.squareup.com"]')
                expect(booking).to_be_visible()
                assert booking.get_attribute('href') == reader['book'], key
            plain_page.goto(base + '/book-today/')
            expect(plain_page.locator('[data-reader-card]')).to_have_count(len(readers))
            expect(plain_page.locator('[data-reader-filters]')).to_be_hidden()
            expect(plain_page.locator('[data-reader-card] a[data-reader-id]').first).to_be_visible()
            plain_page.goto(base + '/products/' + products[0]['h'] + '/')
            direct = plain_page.locator('a[data-link-type="product"]')
            expect(direct).to_be_visible()
            assert urlsplit(direct.get_attribute('href')).path == '/products/' + products[0]['h']
            plain_page.goto(base + '/cart/')
            expect(plain_page.locator('noscript a')).to_be_visible()
            assert urlsplit(plain_page.locator('noscript a').get_attribute('href')).hostname == 'namastebookshop.com'
            plain.close()
            print('PASS: all booking links, product details and cart fallback remain visible without JavaScript')

            # Storage restrictions should not prevent adding an item and handing
            # off the current in-memory cart. Persistence cannot work in this mode.
            restricted = browser.new_context()
            restricted.route('**/*', route)
            restricted.add_init_script("""
                Object.defineProperty(window, 'localStorage', {get() {
                    throw new DOMException('Storage disabled for regression check', 'SecurityError');
                }});
            """)
            restricted_page = restricted.new_page()
            restricted_page.on('pageerror', lambda error: errors.append(str(error)))
            restricted_page.goto(base + '/products/' + products[0]['h'] + '/')
            restricted_page.locator('#buy').click()
            expect(restricted_page.locator('#cart')).to_be_visible()
            local_checkout = restricted_page.locator('#cart [data-checkout]').get_attribute('href')
            assert urlsplit(local_checkout).path == f'/cart/{products[0]["v"]}:1'
            assert parse_qs(urlsplit(local_checkout).query)['attributes[Storefront]'] == ['nyctarotreader.com']
            restricted.close()
            print('PASS: storage denial preserves in-page cart and attributed checkout link')

            page.set_viewport_size({'width': 390, 'height': 844})
            for path in ('/', '/book-today/', '/readers/jennifer-shanteau/', '/products/' + products[0]['h'] + '/', '/cart/'):
                page.goto(base + path)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), path
            screenshots = ROOT / 'artifacts'
            screenshots.mkdir(exist_ok=True)
            page.goto(base + '/')
            page.screenshot(path=str(screenshots / 'home-mobile.png'), full_page=True)
            page.goto(base + '/book-today/')
            page.screenshot(path=str(screenshots / 'readers-mobile.png'), full_page=True)
            assert not errors, errors
            assert not any('/cart/' in u or 'book.squareup.com' in u for u in external), external
            print('PASS: mobile overflow checks, screenshots, no JavaScript errors; zero checkout/booking requests')
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    run()
