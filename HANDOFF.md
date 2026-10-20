# Handoff — Phase 2 (open) — Rakuten gone, Impact.com recommended — 2026-10-19

## What was completed
- **The red daily build is fixed.** On 19 October the run went red even though
  the catalogue built fine. An advertiser on the shared Awin account changed
  (another site's application was rejected), the run treated that as an
  exception, and the alert-email step failed because no sending mailbox has
  ever existed. On the owner's choice the custom email is removed. A real
  failure turns the run red and GitHub's own failed-run notice reaches the
  owner. Softer signals are listed at the top of the run report under
  "Worth a look" and never fail the run. A manual run afterwards was green.
- **The board is reconciled.** Three cards are closed: the Rakuten importer
  (Rakuten ended the account), the Awin pending-advertiser watch (the daily
  run still flags any change) and the alert email (dropped). The feed parent
  card is rewritten around the new route. The display-advertising card stays
  parked on its scale condition.
- **The replacement network is researched.** Impact.com is recommended. It is
  the only network found that carries both big-and-tall stores (DXL Big & Tall,
  KingSize) plus DSW, New Balance, Brooks and Skechers, and its partner API
  returns stock status, size, picture, price and the tracking link for each
  item. Impact reviews identity and site ownership, not traffic. The
  comparison is published for the owner as a review page.

## What was NOT completed and why
- **No fresh feed exists.** Awin's feeds are still frozen on 15 May 2026, now
  157 days old. Nothing from Impact can be built or tested until the owner
  signs up and a store approves.
- **eBay is held by the owner.** eBay's terms require listing data no more
  than 6 hours old, so it would need four builds a day.
- **Amazon cannot be used yet.** Its product API needs 10 sales in the last
  30 days on the account.

## Current state of the system
- Site: live at https://sasquatchindex.com, HTTPS enforced. Products: none
  published (feed stale). Guides, disclosure, privacy: live.
- Hosting: GitHub Pages. DNS: Namecheap, which also forwards mail for the
  site's address.
- Scheduled rebuild: daily, unattended, green again. It has no email step.
- Awin: 4 joined, all frozen 15 May 2026. Zeba and FitVille still pending.
  Rakuten: terminated, ruled out permanently.

## Decisions made this session
- **No custom alert email.** The owner's choice: there is no mailbox, password
  or cost to maintain, and GitHub already reports a failed run.
- **Changes on the shared Awin account never fail this site's run.** That
  account also serves another site, so its changes are not this site's
  problem.
- **Network sign-ups use the content / editorial type, never comparison.** The
  Awin account was locked at "comparison engine", and only Awin support can
  change that. It has since cost another site an approval.

## Open questions for the owner
- Do we go with Impact.com: you sign up, and I build the importer and an About
  page while the stores review us?

## Recommended next session
- Phase 2 (continued): Impact sign-up, apply to DXL and KingSize, build the
  Impact importer next to the Awin one.
- Gate that must be met first: the owner approves the Impact route and creates
  the account.
- Risk: Medium. It adds a new data source to the live site; the freshness and
  in-stock rules still gate everything.
