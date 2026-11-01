"""NYC Tarot Reader: a first-timer's walk-through for getting one tarot reading today at Namaste Bookshop on 14th Street."""
import json, os
import engine as G
E = G.E
BUSINESS_TYPE = 'LocalBusiness'
THEME_COLOR = '#b4532a'
FONTS = 'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap'
ORG_DESC = 'NYC Tarot Reader helps first-timers get a tarot reading in New York today: walk in or book a reader at Namaste Bookshop on West 14th Street.'
LLMS_NOTE = ('NYC Tarot Reader is a Wealth Edge Ventures Inc. brand connected to Namaste Bookshop, 2 West 14th Street, New York. It is a first-timer guide, not a directory; '
             'every reader it mentions works at Namaste Bookshop and is booked through the shop.')
R = json.load(open(os.path.join(os.path.dirname(__file__), 'readers.json')))
FLOOR = [('tyler-t-mann-tarot', 'Upbeat and practical, a good fit if you want concrete next steps.'),
         ('andrea-dopewitchkira', 'Warm and talkative; reads cards and also offers longer "Witch Talk" conversations.'),
         ('priya', 'If you would like astrology in the mix, she reads both charts and cards.'),
         ('sophia-strange', 'Gentle sessions that end with a short poem she writes for you.'),
         ('alexander-d-santiago', 'Tarot, or tarot with a quick look at your chart.'),
         ('brinly-erin', 'Intuitive and encouraging, with a lot of focus on self-worth.'),
         ('lizanne', 'Likes to start from one clear question, which suits a short first session.')]
STEPS = [('pick', 'Pick fifteen or thirty minutes', 'For a first reading, short is fine. Fifteen minutes covers one question; thirty lets you ask a follow-up or two.'),
         ('choose', 'Choose walk-in or a booked time', 'Booking is the surest way to get a seat today. Walking in can work when a reader is free.'),
         ('ask', 'Think of one question', 'Something you actually care about. It does not need to be clever.'),
         ('sit', 'Sit down and listen', 'The reader shuffles, lays cards and talks you through them. Ask anything that is unclear.'),
         ('after', 'Take one thing with you', 'Write down the card or sentence that stuck. That is the part worth keeping.')]
NAV = [('/', 'Today'), ('/walk-in-or-book/', 'Walk in or book'), ('/what-to-ask/', 'What to ask'), ('/what-it-costs/', 'Cost'), ('/at-the-table/', 'At the table'), ('/find-the-shop/', 'Find the shop')]

def shell(pg):
    nav = ''.join(f'<a href="{h}"' + (' class="here"' if pg['path'] == h else '') + f'>{t}</a>' for h, t in NAV)
    return (f'<body><a class="skip" href="#main">Skip to content</a><div class="strip">First tarot reading in New York? Start here.</div>'
            f'<header class="hdr"><a class="nm" href="/">NYC<span>Tarot Reader</span></a><a class="today" href="{G.BOOK}">Book for today</a></header>'
            f'<nav class="tabs" aria-label="Guide">{nav}</nav><main id="main">{pg["body"]}</main>'
            f'<footer class="ftr"><p><b>NYC Tarot Reader</b> is a first-reading guide from Wealth Edge Ventures Inc. Every reading it points to happens at Namaste Bookshop, {G.ADDR}.</p>'
            f'<p><a href="tel:{G.TEL}">{G.PHONE}</a> &middot; <a href="mailto:{G.EMAIL}">{G.EMAIL}</a> &middot; <a href="/privacy/">Privacy</a></p></footer></body></html>')

def pages():
    home = (f'<section class="ticket"><p class="stub">Admit one &middot; Namaste Bookshop &middot; 2 W 14th St</p><h1>Get your first tarot reading today</h1>'
            f'<p class="sub">No experience needed and nothing to prepare except a question. This short guide walks you from "I have never done this" to sitting at the table on 14th Street, a few steps from Fifth Avenue.</p>'
            f'<p class="btns"><a class="go" href="{G.BOOK}">See who can read for me today</a><a class="alt" href="tel:{G.TEL}">Call {G.PHONE}</a></p></section>'
            f'<ol class="five">' + ''.join(f'<li id="{s}"><h2>{t}</h2><p>{d}</p></li>' for s, t, d in STEPS) + '</ol>'
            f'<section class="today-box"><h2>Is the shop open now?</h2><ul class="hrs">' + ''.join(f'<li><span>{d}</span><b>{h}</b></li>' for d, h in G.HOURS) + '</ul>'
            f'<p>Readers keep their own schedules within those hours. The <a href="{G.CALENDAR}">reader calendar</a> shows who is working each day.</p></section>'
            f'<section class="floor"><h2>Readers who work the 14th Street shop floor</h2><p>Any of them is a fine choice for a first reading. Tap a name for open times.</p><ul>'
            + ''.join(f'<li><a href="{E(R[k]["book"])}"><b>{E(R[k]["name"])}</b><span>{E(l)}</span><em>from ${R[k]["from"]}</em></a></li>' for k, l in FLOOR) + '</ul>'
            f'<p class="sm">Other Namaste readers see clients in the Healing Center upstairs; the <a href="{G.BOOK}">full booking page</a> lists everyone.</p></section>')
    G.add('/', 'NYC Tarot Reader | Your First Tarot Reading in New York, Today',
          'Never had a tarot reading? Get one today at Namaste Bookshop on West 14th Street, Manhattan. Five simple steps, real prices, and readers you can book now.', home,
          ld=[G.shop_ld('LocalBusiness')])
    wf = [('Can I just walk in?', 'You can walk in and ask. Whether someone can read for you right away depends on who is working and whether they have an open slot. Calling ahead on ' + G.PHONE + ' saves a wasted trip.'),
          ('How far ahead should I book?', 'Same-day booking often works. Weekends and evenings fill faster, so book earlier for those.'),
          ('Can I pay with cash?', 'Namaste Bookshop accepts cash at the shop if you have trouble booking online.')]
    wb = ('<section class="pg"><h1>Walk in, or book a time?</h1><div class="vs"><div><h2>Booking</h2><ul><li>Your seat is held</li><li>You pick the reader</li><li>You pay up front online</li></ul></div>'
          '<div><h2>Walking in</h2><ul><li>Good if you are already nearby</li><li>Depends on who is free</li><li>Check with staff when you arrive</li></ul></div></div>'
          '<p>If you have your heart set on a reading today, booking is the safer bet. Open the booking page, tap "Today" and choose any reader with an open time.</p>'
          '<dl class="qa">' + ''.join(f'<dt>{q}</dt><dd>{a}</dd>' for q, a in wf) + f'</dl><p><a class="go" href="{G.BOOK}">Check today\'s openings</a></p></section>')
    G.add('/walk-in-or-book/', 'Walk-In Tarot Reading in NYC or Book Ahead? | NYC Tarot Reader',
          'Should you walk in or book a tarot reading at Namaste Bookshop? What each option means for a first-timer, and how to grab a same-day slot.', wb,
          ld=[G.faq_ld(wf)], crumbs=[('Today', '/'), ('Walk in or book', '/walk-in-or-book/')])
    qs = [('Work', 'What would help me most at work over the next few months?'), ('Love', 'What am I not seeing about this relationship?'),
          ('A decision', 'What should I weigh before I decide on this?'), ('A rough patch', 'What can I lean on while this is hard?'), ('Just curious', 'What do I most need to hear right now?')]
    wa = ('<section class="pg"><h1>What to ask at your first reading</h1><p>You do not have to tell the reader your whole story. One honest question is enough to start.</p>'
          '<h2>Questions that read well</h2><ul class="qs">' + ''.join(f'<li><b>{a}</b>{b}</li>' for a, b in qs) + '</ul>'
          '<h2>Questions that read badly</h2><p>Very narrow yes-or-no questions, and questions about what someone else is secretly thinking, tend to give muddy answers. Try turning them around: instead of "Does he like me?", ask "How can I tell where I stand?"</p>'
          '<h2>Is it okay to say nothing?</h2><p>Yes. Some people like to stay quiet and see what the cards bring up. Tell the reader that is what you want.</p></section>')
    G.add('/what-to-ask/', 'Good Questions for Your First Tarot Reading | NYC Tarot Reader',
          'Simple questions that work well in a first tarot reading, a few that do not, and whether you need to share anything at all.', wa,
          crumbs=[('Today', '/'), ('What to ask', '/what-to-ask/')])
    wc = (f'<section class="pg"><h1>What a tarot reading costs at Namaste</h1><table class="cost"><thead><tr><th>Time</th><th>Usual price</th></tr></thead><tbody>'
          f'<tr><td>15 min</td><td>about $35 to $40</td></tr><tr><td>30 min</td><td>about $70 to $80</td></tr><tr><td>45 min</td><td>about $100 to $110</td></tr><tr><td>60 min</td><td>about $130 to $140</td></tr></tbody></table>'
          f'<p>These ranges come from the readers\' posted prices on namastebookshop.com. A few specialists, mostly astrologers, charge more. Online booking can add a small amount; the booking page always shows your final price before you pay.</p>'
          f'<h2>Tipping</h2><p>There is no tipping rule. If you would like to leave something extra, ask the staff.</p><p><a class="go" href="{G.BOOK}">See prices for each reader</a></p></section>')
    G.add('/what-it-costs/', 'How Much Is a Tarot Reading in NYC? Prices at Namaste | NYC Tarot Reader',
          'Typical tarot reading prices at Namaste Bookshop in Manhattan: about $35 for 15 minutes up to about $140 for an hour, with exact prices before you pay.', wc,
          crumbs=[('Today', '/'), ('Cost', '/what-it-costs/')])
    at = ('<section class="pg"><h1>What happens at the table</h1><ol class="tl"><li><b>Hello.</b> The reader asks your name and whether you have a question.</li>'
          '<li><b>Shuffle.</b> Some readers hand you the deck; some shuffle for you.</li><li><b>The spread.</b> Cards go down in a pattern. Each spot in it means something.</li>'
          '<li><b>The talk.</b> The reader explains the cards and how they connect. This is your time, so interrupt with questions.</li><li><b>Wrap-up.</b> Many readers sum it up in a sentence or two. If you would like a picture of the cards, ask before you snap one.</li></ol>'
          '<h2>A few things first-timers wonder</h2><p><b>Will it be scary?</b> Cards like Death or The Tower usually point to change, not disaster. A good reader explains them calmly.</p>'
          '<p><b>Will they tell me what to do?</b> A reading offers perspective. The decision stays yours, and health, legal or emotional crises need a professional, not a deck.</p></section>')
    G.add('/at-the-table/', 'What Happens During a Tarot Reading: A First-Timer\'s View | NYC Tarot Reader',
          'Step by step through a tarot reading at Namaste Bookshop, from shuffle to wrap-up, and answers to the worries first-timers usually have.', at,
          crumbs=[('Today', '/'), ('At the table', '/at-the-table/')])
    fs = (f'<section class="pg"><h1>Finding Namaste Bookshop</h1><p class="addr">{G.ADDR}</p><p>Look for it a few doors from the Fifth Avenue corner, on 14th, in the blocks linking Union Square to the Village.</p>'
          f'<h2>By subway</h2><ul><li>Coming on the L, or on the N, Q, R, W, or the 4, 5, 6? Get off at Union Square, then head west along 14th, crossing University Place and then Fifth.</li><li>On the F or M (or the L from the west side), or on PATH, use the Sixth Avenue stop and head east toward Fifth.</li></ul>'
          f'<h2>Upstairs readings</h2><p>Some readers see clients upstairs in Suite 1104, reached through the 80 Fifth Avenue door of the same building with its entrance around the corner. If your booking says Healing Center, go there.</p>'
          f'<p><a class="go" href="{G.DIRECTIONS}">Open directions</a> <a class="alt" href="tel:{G.TEL}">{G.PHONE}</a></p></section>')
    G.add('/find-the-shop/', 'Directions to Namaste Bookshop, 2 W 14th St | NYC Tarot Reader',
          'How to get to Namaste Bookshop for your tarot reading: subway lines, which corner to look for, and where upstairs Healing Center readings happen.', fs,
          crumbs=[('Today', '/'), ('Find the shop', '/find-the-shop/')])
    G.add('/privacy/', 'Privacy | NYC Tarot Reader', 'Analytics and booking privacy on nyctarotreader.com.',
          '<section class="pg">' + G.privacy('nyctarotreader.com is a short guide. It does not collect names, emails or payments itself.') + '</section>', crumbs=[('Today', '/'), ('Privacy', '/privacy/')])

NOTFOUND_DESC = 'Page not found on nyctarotreader.com.'
NOTFOUND = '<section class="pg"><h1>Wrong turn</h1><p>This page is not part of the guide. <a href="/">Start from step one</a>.</p></section>'

CSS = """:root{--clay:#b4532a;--cream:#fdf6ec;--char:#2b2522;--sand:#f1e2cc}
*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--char);font:17px/1.6 'Source Serif 4',Georgia,serif}a{color:#9a3f18}
h1,h2{font-family:'Bricolage Grotesque',system-ui,sans-serif;line-height:1.1;letter-spacing:-.01em}h1{font-size:clamp(2.1rem,8vw,3.4rem);font-weight:800;margin:.15em 0 .3em}
.skip{position:absolute;left:-999px}.skip:focus{left:6px;top:6px;background:#fff;padding:6px}
.strip{background:var(--char);color:#f6e7d3;text-align:center;font:600 .8rem 'Bricolage Grotesque',sans-serif;padding:6px}
.hdr{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;max-width:900px;margin:0 auto}
.nm{font:800 1.5rem 'Bricolage Grotesque',sans-serif;text-decoration:none;color:var(--clay);line-height:.95}.nm span{display:block;color:var(--char);font-size:.95rem;font-weight:600}
.today{background:var(--clay);color:#fff;text-decoration:none;padding:10px 14px;border-radius:6px;font:700 .9rem 'Bricolage Grotesque',sans-serif}
.tabs{display:flex;gap:6px;overflow-x:auto;padding:0 16px 10px;max-width:900px;margin:0 auto;scrollbar-width:none}.tabs a{white-space:nowrap;border:1.5px solid var(--char);border-radius:99px;padding:5px 12px;text-decoration:none;color:var(--char);font:600 .85rem 'Bricolage Grotesque',sans-serif}
.tabs a.here{background:var(--char);color:var(--cream)}
main{max-width:900px;margin:0 auto;padding:0 16px 30px}
.ticket{background:#fff;border:2px dashed var(--clay);border-radius:14px;padding:22px 18px;margin-top:8px}.stub{font:700 .75rem 'Bricolage Grotesque',sans-serif;text-transform:uppercase;letter-spacing:.12em;color:var(--clay);margin:0}
.sub{font-size:1.1rem}.btns{display:flex;flex-wrap:wrap;gap:10px}.go{display:inline-block;background:var(--clay);color:#fff;text-decoration:none;padding:13px 18px;border-radius:8px;font:700 1rem 'Bricolage Grotesque',sans-serif}
.alt{display:inline-block;padding:13px 18px;border:2px solid var(--char);border-radius:8px;text-decoration:none;color:var(--char);font:700 1rem 'Bricolage Grotesque',sans-serif}
.five{list-style:none;padding:0;counter-reset:s;margin:26px 0}.five li{counter-increment:s;position:relative;padding:4px 0 10px 62px;border-left:3px solid var(--sand);margin-left:22px}
.five li:before{content:counter(s);position:absolute;left:-24px;top:0;width:44px;height:44px;border-radius:50%;background:var(--clay);color:#fff;display:grid;place-items:center;font:800 1.2rem 'Bricolage Grotesque',sans-serif}
.five h2{margin:.25em 0 .2em;font-size:1.3rem}.five p{margin:0}
.today-box{background:var(--sand);border-radius:14px;padding:6px 18px 14px}.hrs{list-style:none;padding:0}.hrs li{display:flex;justify-content:space-between;border-bottom:1px solid #e3cfb2;padding:6px 0}
.floor ul{list-style:none;padding:0;display:grid;gap:8px}@media(min-width:700px){.floor ul{grid-template-columns:1fr 1fr}}
.floor a{display:flex;flex-direction:column;background:#fff;padding:12px 14px;border-radius:10px;text-decoration:none;color:var(--char);border-left:5px solid var(--clay)}.floor b{font-family:'Bricolage Grotesque',sans-serif}.floor em{color:var(--clay);font-style:normal;font-weight:600;font-size:.9rem}
.sm{font-size:.9rem}.pg{max-width:720px;padding-top:10px}.vs{display:grid;gap:12px}@media(min-width:640px){.vs{grid-template-columns:1fr 1fr}}.vs>div{background:#fff;border-radius:12px;padding:4px 16px}
.qa dt{font-weight:600;margin-top:.8em}.qa dd{margin:.2em 0 0}.qs{list-style:none;padding:0}.qs li{background:#fff;margin:8px 0;padding:10px 14px;border-radius:10px}.qs b{display:block;color:var(--clay);font-family:'Bricolage Grotesque',sans-serif}
.cost{width:100%;border-collapse:collapse;background:#fff}.cost td,.cost th{padding:10px;border-bottom:1px solid var(--sand);text-align:left}.tl li{margin:.5em 0}.addr{font:700 1.2rem 'Bricolage Grotesque',sans-serif}
.ftr{background:var(--char);color:#e9dccb;padding:22px 16px;font-size:.9rem}.ftr a{color:#f2b28f}
"""
