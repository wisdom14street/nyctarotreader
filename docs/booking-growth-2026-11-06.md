# Booking path improvement

Visitors can now reach each saved Square booking destination directly from the
reader directory and seven homepage cards. The homepage places reader choices
before the long first-visit guide. Format and starting-guide-price filters help
visitors compare options; all cards and links remain available without JavaScript.
Five information pages now end with a reader-selection call to action.

The Namaste public reader page was read on November 6, 2026:
https://namastebookshop.com/pages/book-a-reading
It supports the guide-price caveat, Square confirmation flow and conditional
same-day availability. Existing reader data, prices and destinations are unchanged.
This site is a selection of readers; the directory also links to Namaste's full list.

## Measurement

GA4 booking_click includes reader_id and placement (home_readers,
reader_directory, reader_profile). reader_directory_click identifies home_hero
and guide_end entry points. reader_filter carries only fixed format/budget options
and a result count. No free-text answers or contact details are collected.

Compare visitor sessions, directory engagement and booking-click sessions by
landing page and source/medium. The primary business outcome is confirmed paid
bookings, which must come from the scheduling/payment system. Do not mark these
click events as paid conversions or infer revenue from them. GA4 reporting access
and confirmed-booking attribution are still unresolved; no uplift is claimed.
No ads, outreach, purchases or bookings were initiated.

## Validation

Offline tests cover canonical URLs, sitemap, assets, product offers, unchanged
reader prices/destinations, direct booking cards and guide entry points.
Chromium covers every booking link, filter/reset/empty state, mobile overflow,
script-free fallback, analytics events, cart and attributed checkout handoff.
External booking and checkout requests are intercepted during local tests.
Publication verifies exact hashes of 30 production pages/assets, now including
reader-filter JavaScript and the stylesheet.

## Organic traffic addition

Added /phone-tarot-readings/ with five supported phone readers, practical booking
and preparation instructions, visible FAQs with matching structured data, unique
metadata and links from the main navigation. Automatic sitemap and llms.txt
include the new page. Official source checked November 6, 2026:
https://namastebookshop.com/pages/phone-tarot-readings
Phone booking clicks carry placement=phone_landing. The release manifest now
checks 31 files. Twelve unit tests and the expanded browser suite cover this page.

Search Console connection was checked again: only sc-domain:namastebookshop.com
is available. nyctarotreader.com is not available in the connected property list,
so its query baseline, URL indexing status and sitemap submission cannot be
verified through this connection. Do not substitute Namaste's traffic totals for
this domain's results. No property access or verification settings were changed.

## Returning visitor booking follow-up

Moved the existing profile booking button above the service table so visitors who
already chose a reader can check times earlier. The homepage now explicitly
separates in-person reader selection from phone sessions. Directory format and
budget selections are restored from whitelisted URL parameters; reset removes
only those parameters and preserves campaign attribution. Existing booking URLs,
prices and the number of profile booking links remain unchanged.

Rechecked GA4 reporting: list_ga4_properties returned connected=false and no
properties because the connected Google account lacks Analytics scope. Analytics
reporting remains blocked pending Google Analytics connection in GSC Wizard.
No reconnection or permissions changes were made. No supported Square connector
was available for confirmed-booking reporting. No booking growth is claimed.
