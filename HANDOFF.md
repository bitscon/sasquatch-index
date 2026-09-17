# Handoff — Phase 2 (open) — search grid — 2026-09-17

## What was completed
- **The search grid is built and live.** The site's rules call the URL grid
  its search engine, and until today only the three size pages existed. The
  site now generates a page for every size, size + width, size + type,
  size + width + type, size + feature, brand, and brand + size combination
  that has enough products behind it. Each page carries its own computed
  facts, a "narrow it down" row of chips to the pages beneath it, and a
  breadcrumb back up. Nothing changed for the existing pages.
- **Types and features now come from the merchant's own product names.**
  The feed's category is too coarse to search on ("Activity"). The importer
  reads words the merchant wrote in the name — work boots, snow boots,
  sneakers, waterproof, steel toe — and records them. It repeats, it never
  adds. This means the daily rebuild now writes two new fields (family,
  attributes) and the category is more specific than before.
- **Children's shoes no longer appear on the size 13 page.** Three kids'
  water shoes were being listed as men's size 13 because the feed labels
  both scales "US Size". The importer now skips rows on the children's scale
  and counts them in the run report. Recorded as hazard 6 in FEED_HAZARDS.md.
- **Search-engine basics added:** a robots file pointing at the sitemap, a
  canonical address on every page, and link-preview tags. The default site
  address in config and the two project files that still named the old
  github.io address now say sasquatchindex.com.
- **Verified end to end on the live site** after a real feed run: every
  sitemap page loads, every page's stated count equals the rows it shows,
  all affiliate links resolved.

| Item | Before | After |
|---|---|---|
| Pages in the sitemap | 9 | 55 |
| Listing pages | 3 | 49 |
| Styles published | 87 | 84 (3 children's rows removed) |
| Types recognised | 3 (feed labels) | 13 (from product names) |
| Features recognised | 0 | 5 |

## What was NOT completed and why
- **Search engines have not been told about the new domain.** Google Search
  Console and Bing Webmaster Tools need the owner's own account to verify
  sasquatchindex.com and submit the sitemap. Keyboard task, his to do.
- **Rakuten** — decided yes last session, still needs the owner's tax and
  business details to register.
- **Project mailbox** — not confirmed; the daily report still goes to the
  Actions job summary.
- **The social auto-post channel** proposed last session — deliberately held.
  With one brand in the catalogue a daily "new in stock" feed would read as
  that brand's own advertising. Revisit once a second merchant lands.
- **Zeba and FitVille** — still in the network's queue.

## Current state of the system
- Site: live at https://sasquatchindex.com, HTTPS enforced.
- Hosting: GitHub Pages. DNS: Namecheap. Unchanged.
- Catalogue: NORTIV 8 via Awin, 84 styles, sizes 13 to 15, standard and wide.
- Scheduled rebuild: daily 09:00 UTC, unattended, unchanged. The first run
  with the new rules was dispatched by hand this session and came back green.
- Link verification: every run, 84 checked, 0 broken this run.
- Analytics: live, cookieless.
- Pending advertisers: Zeba, FitVille. Second feed source: Rakuten, not registered.

## Decisions made this session
- **Types come from product names, not the feed category.** The feed's own
  label is not something a person would ever search for; the merchant's
  product name is. Reading it is repetition, not invention.
- **No "shoes" type page.** The size page already is the "size N shoes"
  page; a second page with the same title would compete with it.
- **A feature page names the family only when every match shares one.**
  "Size 14 waterproof shoes and boots" when mixed, "size 14 insulated boots"
  when they are all boots. The title never claims more than the page holds.
- **Held the social auto-post.** Reason above.
- **Kids' rows are skipped, not relabelled.** The site has no children's
  scale and should not pretend to.

## Open questions for the owner
- Have you verified sasquatchindex.com in Google Search Console yet? If you
  pick the "HTML file" method and read me the file name, I can commit it and
  you just press verify.
- Is the Namecheap mailbox set up yet?
- Do you want to do the Rakuten registration this week?

## Recommended next session
- Phase 2 close-out: wire Rakuten or an approved advertiser as the second
  feed source, whichever arrives first. The grid grows on its own as
  merchants are added.
- Gate that must be met first: a second feed available, or Search Console
  verified so the new pages start getting indexed.
- Risk: Low.
