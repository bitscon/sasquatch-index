# Handoff — Phase 2 (open) — Awin cannot supply this site — 2026-09-17

## What was completed
- **The daily run now scans the whole network for a merchant worth applying
  to.** The feed list it already downloads carries every feed Awin will show
  this key, not just the joined ones, with the date Awin last imported each.
  Those rows used to be discarded. The run now reads them and names, in the
  run report, the footwear merchants whose feed the network has imported
  within the same 30-day limit the site applies to its own feed.
- **Two tiers, because a shoe brand is not obliged to say so in its name.**
  NORTIV 8 itself is filed under Clothing & Accessories, so matching shoe
  words alone found one merchant in 562 and that was not credible. Tier one
  is the shoe-word match. Tier two appears only when tier one is empty and
  lists the apparel and sports merchants with current feeds, to be read by
  eye. One line per merchant from its largest feed; home region sorts first.
- **The answer is that Awin has nothing for this site.** Of 562 feeds the key
  can see, 220 merchants have a current feed, so the network is importing
  normally — the freshest was imported the same day. Exactly one footwear
  merchant appears on the entire visible network, CHIKO (US), and its feed is
  frozen on 15 May 2026 like every joined feed. The 18 apparel merchants with
  current feeds are jewellery, socks, watches and perfume, almost all European;
  the only recognisable shoe brand among them is Converse PL, Poland only.
- **So the open question is answered.** Waiting on Awin is not a strategy. A
  second network is the only path to a first feed, which makes the Rakuten
  registration the critical item rather than an optional one.
- **Report only, never committed.** The scan is a fact about the network, not
  about this site, and it changes daily. The committed status file is
  unchanged in shape. The feed key stays masked.
- **The scan says why it is empty, not just that it is.** It reports how many
  merchants were scanned, how many footwear merchants exist at any age, the
  freshest feed of any kind with a plain reading of what that implies, and the
  nearest footwear merchants with their import dates. An empty shortlist can
  now be told apart from a shortlist that could not be read.
- **Verified:** six report paths covered by an offline test against a
  synthetic feed list — a live footwear merchant, the apparel fallback, the
  sector breakdown, nothing current, no unjoined rows, and the deduplication
  and region ranking. Four live runs, each clean, the last at 17:44 UTC.

## What was NOT completed and why
- **No fresh feed exists, and none is coming from Awin.** This is now measured
  rather than assumed. Zeba and FitVille are still pending; both came through
  the ShareASale path, so approval may hand over a frozen feed.
- Rakuten: not registered. It is the only remaining route to a first feed.
- Project mailbox, social channel: unchanged.

## Current state of the system
- Site: live at https://sasquatchindex.com, HTTPS enforced. Products: none
  published (feed stale, 125 days). Guides, disclosure, privacy: live.
- Hosting: GitHub Pages. DNS: Namecheap. Unchanged.
- Scheduled rebuild: daily 09:00 UTC, unattended. Order: download feed, ask
  Awin about freshness, the account and the network, build with the freshness
  rule, verify links, commit, deploy, report.
- Analytics: live, cookieless. Search Console and Bing: verified.
- Awin: 4 joined (NORTIV 8, TideWe, Piscifun, Giftlab), all frozen 15 May 2026.
  2 pending (Zeba, FitVille). 0 clicks in the last seven days, consistent with
  an empty catalogue.

## Decisions made this session
- **Rank the home region, do not filter it.** A US site does not want a Swiss
  merchant at the top of its shortlist, but a genuinely on-theme brand abroad
  should still be visible further down.
- **One line per merchant, from its largest feed.** Awin lists a merchant once
  per feed; the raw list gave the same advertiser four lines.
- **The network scan stays out of the committed files.** It is a daily-changing
  scan of someone else's data, not a fact about this site.

## Open questions for the owner
- Rakuten registration is now the critical path, not an option. Is the project
  mailbox needed first, or register with a personal address and change it later?

## Recommended next session
- Nothing on the feed side can move until a network delivers a current feed,
  and Awin will not. Register with Rakuten and apply to Zappos; the run checks
  any new feed's import date before anything is published.
- Worth considering if Rakuten also stalls: the scan can be pointed at a
  second network's feed list the same way, so the same question gets answered
  before a signup rather than after.
- Risk: Low.
