# Handoff — Phase 2 (open) — conversion pass — 2026-09-17

## What was completed
- **Owner's design mandate recorded in the rules.** His words: he does not
  dictate look or function; the only goal is a person tapping through to a
  retailer, in as few taps as possible. Pictures were the reason he hesitated
  to tap. Written into SASQUATCH_OS.md section 2a as an owner amendment; the
  text-only mockup of 7 September is superseded on the point of images.
- **Pictures on every listing.** The build fetches each style's picture from
  the merchant, resizes it, and serves it from the site itself, so the
  visitor's browser never contacts a third party and the privacy page stays
  true. Fetched originals are kept between builds so a redeploy is fast and a
  short merchant outage does not blank the site. A picture that cannot be
  fetched becomes a blank tile and a build warning, never a failed publish.
- **Every card is one tap.** Picture, name, type, width, features, colour
  count, price and "at NORTIV 8" are all inside a single link to the retailer.
  Two cards across on a phone, three on a desktop.
- **Price on every card**, from the feed, shown as a single figure or a range
  across the style's rows, with "prices and stock as of" the run date on each
  page. Currency is spelled out for anything other than US dollars.
- **Every picture address now resolves.** The feed's image addresses carried
  raw spaces and, for nine styles, Chinese filenames mangled by a double
  encoding at the merchant's end. Both are corrected at import. Tested
  against a real copy of the feed before shipping: all 84 resolve.
- **Names tidied.** The feed loses apostrophes ("Men s"); restored at import.
- **Disclosure page corrected.** It still said no affiliate links were live.
  They have been live since the first feed. It now says so plainly.
- **Filter chips scroll in one row on a phone** so pictures stay near the top.
- **Verified live** after a real feed run: 84 pictures processed, every card
  has a picture and a price, every sitemap page loads.

| Item | Before | After |
|---|---|---|
| Pictures on listings | none | every card |
| Price on listings | none | every card |
| Taps from a listing to the retailer | 1, on a small link | 1, anywhere on the card |
| Picture addresses that resolve | 61 of 84 | 84 of 84 |
| Typical picture size served | — | about 20 to 40 KB |

## What was NOT completed and why
- **Conversion rate is not yet in the daily report.** The measure is Awin
  clicks divided by analytics visits; both live in dashboards the owner can
  read. Folding it into the report waits on the project mailbox.
- **Rakuten** — owner's registration still pending.
- **Project mailbox** — not confirmed.
- **Social auto-post channel** — still held until a second merchant lands.
- **Zeba and FitVille** — still in the network's queue.

## Current state of the system
- Site: live at https://sasquatchindex.com, HTTPS enforced.
- Hosting: GitHub Pages. DNS: Namecheap. Unchanged.
- Catalogue: NORTIV 8 via Awin, 84 styles, sizes 13 to 15, now with price,
  colour count and a working picture for each.
- Scheduled rebuild: daily 09:00 UTC, unattended, unchanged. The deploy now
  also fetches and resizes pictures; the first run took under a minute.
- Link verification: every run, 84 checked, 0 broken this run.
- Analytics: live, cookieless. Search Console and Bing: verified, sitemap
  submitted 2026-09-17.
- Pending advertisers: Zeba, FitVille. Second feed source: Rakuten, not registered.

## Decisions made this session
- **Pictures are served from the site, not linked from the merchant.** Keeps
  the privacy page true and the pages fast; costs nothing but build time.
- **The whole card is the link.** A bigger target and one fewer decision.
- **No sort control, no image gallery, no scripts.** Each would add a tap or
  a delay for no gain against the mandate.
- **Prices carry a date, never "live".** The feed runs once a day.
- **A failed picture never fails the publish.** Blank tile plus warning.

## Open questions for the owner
- Open https://sasquatchindex.com/shoes/size-14/ on your phone. Does the card
  make you want to tap?
- Is the Namecheap mailbox set up yet?
- Do you want to do the Rakuten registration this week?

## Recommended next session
- Phase 2 close-out: wire Rakuten or an approved advertiser as the second
  feed source, whichever arrives first. The grid and the cards grow on
  their own as merchants are added.
- Gate that must be met first: a second feed available.
- Risk: Low.
