# nyctarotreader.com

NYC Tarot Reader: static site built by `scripts/build.py` and deployed to GitHub Pages by Actions. A Wealth Edge Ventures Inc. brand connected to Namaste Bookshop, 2 W 14th St, New York.

- `site/content.py`: this site's pages, layout, copy and CSS (all wording is unique to this site).
- `site/config.json`: brand, domain, GA4 ID (G-Y7R5K9NMW0, sends `site_brand` and `site_domain`).
- `site/readers.json`: active Namaste readers (name, booking link, starting price) taken from namastebookshop.com.
- `scripts/engine.py`: page assembly, JSON-LD, sitemap.xml, robots.txt, llms.txt, 404.
- `static/`: og.jpg link preview, favicon and icons.
- Checkout (if the site sells): Shopify cart permalinks to namastebookshop.com tagged `attributes[Storefront]=nyctarotreader.com`; `data/` keeps the last good product fetch as a fallback.

Build and check locally:

```sh
python3 -m unittest discover -s tests -v
node --check scripts/ga.js
python3 tests/browser_checks.py
```

The unit checks build with `--offline` and use the committed catalog without changing it. Browser checks require Python Playwright and Chromium (`CHROMIUM_PATH` can select an existing executable). They serve the generated site locally and block every external request, including analytics, bookings and checkout. Screenshots go to the ignored `artifacts/` folder. For a manual local preview with analytics omitted, run `python3 scripts/build.py --offline --preview`.

Referral links to Namaste use `utm_source=nyctarotreader.com`, `utm_medium=referral`, `utm_campaign=namaste_network` and a static placement in `utm_content`. These identify traffic sent from this website; they do not identify a visitor or prove a sale. Existing Square booking URLs are unchanged.

GA4 event meanings:

| Event | What it measures |
| --- | --- |
| `booking_click` | Opening a Square booking link; includes `reader_id` |
| `contact_click` | Selecting a phone or email link; `link_type` distinguishes them |
| `directions_click` | Opening directions |
| `namaste_referral_click` | Opening a Namaste information or product link |
| `view_item`, `add_to_cart`, `begin_checkout` | Product interest and checkout intent, using the existing cart implementation |

This site never emits `purchase`, a confirmed booking event, or `generate_lead` for a link click. A completed appointment or payment must come from Square or Shopify. Count distinct confirmed orders, with their payment/refund status, rather than adding clicks to orders. The legacy checkout URL retains `attributes[Storefront]`, `attributes[Site]`, the order note and `ref=nyctarotreader`; verify these on a real, authorized completed order before calling order attribution proven. Do not create test purchases to verify this site.

For reporting, use GA4's hostname dimension to isolate this site if the measurement ID is shared. Register `site_brand`, `site_domain`, `reader_id` and `link_type` as event-scoped custom dimensions where needed; this repository does not configure GA4 Admin or key events. Historical `generate_lead` counts from earlier builds were clicks, not confirmed leads or revenue. See [the review evidence and limitations](docs/review-2026-11-04.md).

The Pages workflow deploys pushes to `main` and manual workflow runs. A review branch and draft PR do not deploy this site. The offline checks run on pull requests. Approve and merge only when publication is authorized; a successful build alone does not verify the custom domain or GA4 collection.
