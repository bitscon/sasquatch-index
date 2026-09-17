# Handoff — Phase 2 (open) — the in-stock promise — 2026-09-17

## What was completed
- **The site now says what it has always done.** The owner named the reason
  the site exists: finding the shoe you like, in your size, and landing on
  the shop to find it sold out. The importer has never listed a size unless
  the retailer's feed carried it as in stock and for sale; a size absent from
  the feed is not listed. Until today no page said so. Now every listing page
  opens with "Every shoe below was listed in stock in size N by the
  retailer's feed at <time>", every card's tap line reads "in stock at
  NORTIV 8", and the home and browse pages carry the promise with the time
  of the last check.
- **The wording claims exactly what the site knows.** "Listed as in stock by
  the retailer's feed at <time>", with "feeds are checked once a day, so
  stock can change between checks". Never "guaranteed", never "live".
- **No show/hide toggle was built**, because nothing out of stock is on the
  page to hide. A toggle would be one more tap that does nothing.
- **The feed's movement is now visible.** Each run records how many
  style-and-size rows were added or removed since the last run, in the run
  marker and in the run report. This is how we will learn whether the feed
  really tracks the shelf.
- **Recorded in the rules** (section 2b, "The promise, and what it rests on").
- **Verified live** after a real feed run: promise on every listing page,
  "in stock at" on every card, all 55 pages load.

## What was NOT completed and why
- **Whether the feed truly moves with stock is not yet proven.** Every
  well-formed size row in the feed is flagged in stock, and the published
  list did not change between 9 and 16 September. That is either a merchant
  with deep stock or a flag that does not move. The merchant's own product
  page loads its per-size stock by script, so it could not be read within
  the rules (no scraping). The new per-run change counts are the evidence
  to watch. The owner can also read the feed's "last updated" time in the
  Awin dashboard; that is a keyboard item, his to do.
- **Rebuilding more than once a day** was not changed. There is no evidence
  yet that the feed refreshes more often than daily; if the change counts
  show it does, the schedule can be tightened then.
- Rakuten, the project mailbox, the social channel, Zeba and FitVille: all
  unchanged from the previous handoff.

## Current state of the system
- Site: live at https://sasquatchindex.com, HTTPS enforced.
- Hosting: GitHub Pages. DNS: Namecheap. Unchanged.
- Catalogue: NORTIV 8 via Awin, 84 styles, sizes 13 to 15, pictures, prices.
- Scheduled rebuild: daily 09:00 UTC, unattended, unchanged. Run report now
  includes "changed since last run" counts.
- Link verification: every run, 84 checked, 0 broken.
- Analytics: live, cookieless. Search Console and Bing: verified, sitemap
  submitted.
- Pending advertisers: Zeba, FitVille. Second feed source: Rakuten, not registered.

## Decisions made this session
- **State the promise; do not build a toggle.** The promise is the
  differentiator and was invisible. A toggle would add a tap for nothing.
- **Date it, never guarantee it.** The site checks a feed once a day and
  cannot see the shelf.
- **Measure the feed before changing the schedule.** Extra runs against a
  feed that refreshes daily gain nothing.

## Open questions for the owner
- In the Awin dashboard, what does the NORTIV 8 feed show as its last
  updated time? That tells us how fresh the stock promise really is.
- Is the Namecheap mailbox set up yet?
- Do you want to do the Rakuten registration this week?

## Recommended next session
- Phase 2 close-out: wire Rakuten or an approved advertiser as the second
  feed source, whichever arrives first.
- Gate that must be met first: a second feed available.
- Risk: Low.
