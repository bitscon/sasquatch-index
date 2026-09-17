# Handoff — Phase 2 (open) — the freshness rule — 2026-09-17

## What was completed
- **The daily run now asks Awin itself how fresh the feed is.** Awin's feed
  list reports when it last imported each feed. The run reads it with the
  product-feed key already in the feed address, so no new secret was needed,
  and records the answer in the run marker, the run report and a committed
  status file.
- **The answer was bad.** Awin last imported the NORTIV 8 feed on 15 May
  2026. Every feed the account has joined (NORTIV 8, TideWe, Piscifun,
  Giftlab) stopped on that same day; all four come through the old
  ShareASale path. Merchants the account has not joined update daily. The
  site's in-stock promise had been resting on four-month-old stock flags,
  which is why nothing ever changed between runs.
- **The freshness rule, decided by the owner.** The site lists only feeds
  the network has imported within the last 30 days. Older feeds are dropped
  automatically and return on their own when they move. No tickets, no
  chasing; the site is not going to maintain a merchant's feed for them.
  Recorded in the rules, section 2b, and in the Phase 2 gate.
- **The site now says its real state.** Every promise line shows the date
  the network last imported the feed, not the time the site pulled it. With
  the feed stale, the home and browse pages say the connected retailer's
  feed has not been updated since 15 May 2026, that the index is still being
  built, and lead with the guides. Listing pages and cards are gone until a
  fresh feed exists.
- **When the network cannot answer**, the site keeps what the last run
  published and the run marker says "unknown". It does not change on an
  answer it did not get.
- **Ready for the Awin Publisher API.** With a read-only token in the
  repository secrets, the same run records every advertiser relationship,
  shouts when one changes (Zeba, FitVille), and reports click-through and
  transaction counts. Counts only, never money, never in a committed file:
  the repository and its run logs are public.
- **Verified:** stale, fresh and unknown paths each built locally with the
  deploy's Hugo version; the live run after landing is the final check and
  is recorded in the run's job summary.

## What was NOT completed and why
- **The Awin API token is not in the repository yet.** The owner has it;
  adding it is a browser step in the repo's secrets. Awin's docs say the
  token's user needs Admin on the publisher account; a viewer-only token may
  be refused, and the run report will say so if it is.
- **No fresh feed exists.** The site is empty of products until one does.
  Zeba and FitVille are still pending on Awin; if they come through the
  same ShareASale path they may be frozen too. Rakuten is not registered.
- Project mailbox, social channel: unchanged.

## Current state of the system
- Site: live at https://sasquatchindex.com, HTTPS enforced. Products: none
  published (feed stale). Guides, disclosure, privacy: live.
- Hosting: GitHub Pages. DNS: Namecheap. Unchanged.
- Scheduled rebuild: daily 09:00 UTC, unattended. Order: download feed,
  ask Awin about freshness and account, build with the freshness rule,
  verify links, commit, deploy, report.
- Analytics: live, cookieless. Search Console and Bing: verified. The 55
  listing pages previously indexed now return not-found until a fresh feed
  brings them back; accepted, the site is not ready for visitors.
- Pending advertisers: Zeba, FitVille. Second feed source: Rakuten, not registered.

## Decisions made this session
- **Drop by rule, not by hand.** A 30-day freshness limit, automatic both
  ways. Reason: the owner will not maintain or steer a network's data.
- **Date the promise by the feed's import time, never the pull time.** The
  pull time implied freshness the data did not have.
- **Keep the previous catalogue when the network does not answer.** An
  outage at Awin is not evidence the feed is stale.
- **Counts, not money, in anything public.** Repo and run logs are public.
- **The site is not ready for visitors** and says so; feeds are pursued in
  parallel.

## Open questions for the owner
- Has the Awin API token been added to the repository secrets?
- Do you want to register with Rakuten this week, now that Awin's joined
  feeds are all frozen?
- Is the project mailbox at Namecheap set up yet?

## Recommended next session
- Phase 2 close-out: wire the first feed whose import date is current, from
  whichever network delivers one. The run report now shows every feed's
  import date before it is wired.
- Gate that must be met first: a feed the network has imported within 30
  days.
- Risk: Low.
