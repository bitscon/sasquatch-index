# Handoff — Domain migration — 2026-09-17

## What was completed
- Registered `sasquatchindex.com` and pointed it at GitHub Pages — DNS managed
  directly at Namecheap, hosting unchanged. Chosen over self-hosting on the
  owner's VPS after comparing the two: a custom domain on GitHub Pages gives
  the same branding, legitimacy, and SEO benefit as self-hosting, with none of
  the added server maintenance.
- Caught and fixed a build bug: the first deploy after adding the domain still
  baked in the old `bitscon.github.io/sasquatch-index/` path into every link
  and the stylesheet, because that deploy ran before the domain was registered
  with GitHub's Pages settings. Registered it, redeployed, verified every
  link, the stylesheet, and subpages now resolve at the domain root.
- HTTPS is enforced and verified. Site is fully live at
  `https://sasquatchindex.com`.
- Recorded the hosting decision in `SASQUATCH_OS.md` directly so it isn't
  relitigated next session.

## What was NOT completed and why
- The site's missing non-search traffic channel (flagged as a standing High
  risk in section 2b of this project's rules) — a direction was recommended
  this session (auto-post new in-stock styles from the daily feed to a social
  channel) but not built. Needs owner approval to start.
- Rakuten (second feed source) — owner decided to pursue it, but registration
  needs the owner's own tax/business info and hasn't happened yet.
- Project mailbox (`reports@sasquatchindex.com`) — owner is adding it via
  Namecheap's mail hosting; not yet confirmed done. The daily report still
  goes to the Actions job summary until that mailbox exists.
- Zeba and FitVille affiliate approvals — still sitting in the network's
  queue, nothing to do until they respond.

## Current state of the system
- Site: live at `https://sasquatchindex.com`, HTTPS enforced, certificate
  verified.
- Hosting: GitHub Pages, unchanged. DNS: Namecheap.
- Catalogue: unchanged — NORTIV 8 via Awin, 87 styles, sizes 13–15.
- Scheduled rebuild: unchanged, daily 09:00 UTC, unattended.
- Analytics: unchanged, live.
- Pending advertisers: Zeba, FitVille.
- Second feed source: Rakuten — owner decided to pursue, not yet registered.
- Report delivery: still in the Actions job summary.

## Decisions made this session
- Custom domain over self-hosting on the VPS — same visible benefit, no new
  maintenance surface.
- Pursue Rakuten now rather than keep waiting on Zeba/FitVille alone.
- Project email lives on a standard mailbox, not Google and not the owner's
  personal addresses — exact address pending the Namecheap mailbox setup.

## Open questions for the owner
- Is the Namecheap mailbox set up yet? If so, send its host, port, and login
  so the daily report can start emailing instead of sitting in Actions.
- Ready to approve building the feed-driven auto-post as the site's first
  non-search traffic channel?

## Recommended next session
- Phase 2 close-out / first traffic lever: build the auto-post channel once
  approved, and wire in Rakuten once it's registered.
- Gate that must be met first: none blocking the auto-post build; Rakuten
  needs registration done first.
- Risk: Low.
