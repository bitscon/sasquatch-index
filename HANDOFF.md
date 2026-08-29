# Handoff — Phase 1 (partial) — 2026-08-29

## What was completed
- Phase 0 in full: repository, operating docs, scaffold, publish job, live site.
  A change pushed to the main branch reaches the live site with nobody involved,
  proven twice.
- The operating document was amended twice on the owner's instruction. He is not
  a content source, and the phase order was corrected (see decisions below).
- The reference layer is written and live: a page on sizing past thirteen and a
  page on what the width letters mean. Both are factual, need no product data,
  and are the content that makes the site substantial enough to submit to an
  affiliate program.
- The affiliate disclosure and privacy pages are live and both state the current
  situation accurately — no affiliate relationships, no analytics, no cookies.
- Every size page now opens with facts computed from the data: how many styles,
  retailers and brands, which widths, which types. Different on every page,
  written by nobody.
- A page is no longer generated unless enough products match it. The threshold
  sits in the site configuration and is currently three.
- Footer navigation reaches all four new pages from anywhere on the site.

## What was NOT completed and why
- The catalogue itself. It comes from an affiliate feed, and no affiliate
  application has been made yet. That is the next step and it needs the owner.

## Current state of the system
- Site: live at https://bitscon.github.io/sasquatch-index/
- Pages: home, the shoes index, two size pages, two reference pages, disclosure,
  privacy.
- Only two size pages exist because only two sizes have three or more matching
  placeholder products. That is the threshold working correctly, not a fault.
- Publish job: working, unattended, on every push to the main branch.
- Nothing scheduled, nothing monetized, no analytics, no affiliate links.
- Product data is still the three placeholder records.

## Decisions made this session
- Hugo, pinned to one version, so an upstream release cannot change an
  unattended build.
- **The owner is not a content source.** No fit notes, no product reviews, no
  per-product interaction. The site earns depth from computed facts, a factual
  reference layer, and a real threshold before a page exists.
- **Nothing may claim first-hand experience that did not happen.** This guardrail
  was added, not removed. Invented testimony is the one thing that would sink
  the site.
- **Phases 1 to 3 were reordered.** The catalogue comes from feeds, feeds come
  with affiliate approval, so approval must precede the catalogue. Phase 1 now
  builds everything needing no product data. The hand-seeded catalogue step is
  gone: seeding by hand would mean copying retailer data, which constraint 2
  exists to prevent, and would create the manual work the owner does not want.
- Display advertising is an option gated on scale, not a scheduled phase.
- No project board, no custom domain. The handoff file and the repository
  history are the whole record.
- Price is deliberately absent from the data model. It is not in section 5b and
  cannot be populated honestly until feeds arrive, so the computed facts do not
  claim it. Worth adding in Phase 3.

## Open questions for the owner
- Which affiliate programs should be applied to first? The application itself
  needs the owner — it wants real account details.
- The sizing and width tables were written from general knowledge, not checked
  against an authoritative source. They are hedged on the page as approximate,
  which is true, but worth verifying before the site carries real traffic.

## Recommended next session
- Phase 2: apply to affiliate programs using the live site, and take feed access
  from whoever approves first.
- Gate that must be met first: the site reads as legitimate to a human reviewer
  — met, as far as can be judged without a reviewer.
- Risk: Medium — thin sites get rejected, and this one is honest but small.
