# Handoff — Phase 2 (partial) — 2026-09-03

## What was completed
- **The placeholder listings are gone.** The three fake products that linked to
  example.com were removed at the owner's direction, so an affiliate reviewer
  now sees a clean reference site rather than an unfinished one. The records
  remain in git history if they are ever wanted back.
- **Both pages that showed listings now degrade honestly.** Removing the data on
  its own would have left the home page showing the heading "Pick your size"
  above an empty box, and the shoes page blank — worse for a reviewer than the
  placeholders were. Both pages now say plainly that listings come from retailer
  feeds and that none is connected yet, and lead with the finished guides.
- **The empty guide links are fixed.** On the shoes page the links to the sizing
  and widths guides rendered as empty boxes with no text. They were being drawn
  by the same loop that draws the size buttons, which prints a size — and a guide
  has no size. Guides now render as ordinary links carrying their own titles;
  sizes still render as buttons. This was registered in the previous handoff as
  a known defect; it is closed.
- **A wording defect was caught by review and fixed before anything shipped.**
  The new "nothing listed yet" sentence originally said the feed was not
  connected, but what actually triggered it was there being no size pages — two
  different things. A real feed whose products were too sparse to fill a page
  would have made the site state something untrue about itself, on the first page
  a reviewer lands on. The sentence is now worked out from the data, so it cannot
  say the wrong one.
- **The size-button path was re-tested with product data restored**, so the
  mechanism Phase 3 depends on is proven working, not merely left untouched.
- **The analytics switch was re-tested in both states.** With a token set, the
  cookieless beacon appears and the privacy page flips to the matching wording;
  with it empty, neither appears. This change did not disturb it.

### The review round
Two waves, by reviewers independent of the work, under the workspace rule that a
round continues until a wave comes back clean.

| Wave | Raised | Confirmed | Refuted |
|---|---|---|---|
| 1 — correctness across data states · honesty and contract conformance | 9 | 1 | 8 |
| 2 — remediation integrity · build and deploy conformance | 19 | 0 | 15 (plus 4 reclassified as pre-existing) |

Started at the light review class for a change this size and was promoted to the
default class when wave 1 confirmed a finding. Wave 2 was clean, so the round is
closed. Between them the reviewers ran the site build in roughly forty different
data and configuration states.

## What was NOT completed and why
- **Phase 2 did not close.** Its gate is an approval plus at least one product
  feed. No network has approved yet: Awin was submitted on 2026-09-02 and is
  still pending, and Rakuten and CJ have not been applied to.
- **Analytics is still not running.** It needs the Cloudflare token, which has
  not been fetched yet. The wiring is in place and proven; one value turns it on.
- **No Phase 3 kickoff prompt was written**, because Phase 3 is gated on a feed
  that does not exist yet. Writing it now would mean guessing at the feed's shape.

## Current state of the system
- Site: live at https://bitscon.github.io/sasquatch-index/ — now a reference site
  with no listings, and it says so on the pages where listings will go.
- Pages published: home, shoes index, the sizing guide, the widths guide, the
  affiliate disclosure, the privacy page.
- Publish job: working, unattended, on every push to main.
- No analytics running, no affiliate links, no cookies, and no outbound links to
  any retailer. The privacy and disclosure pages remain accurate.
- Product data: empty on purpose. The file documents the shape of a record for
  whoever wires up the first feed.

## Decisions made this session
- Placeholder listings were removed rather than hidden behind a switch. A switch
  would be machinery kept alive for a state the site will never return to, and
  git history already preserves the records.
- The no-listings wording says what the site does have rather than apologising
  for what it does not, and names the feed as the source — which is accurate and
  matches what was told to Awin.
- The site description already submitted to Awin was left unchanged. It describes
  a reference site "built to index styles", so removing the placeholders made it
  more accurate, not less.
- `PHASE_0_BRIEF.md` still mentions seeding placeholder records; left alone
  deliberately, because it is a record of what Phase 0 was asked to do, not a
  description of the site today.
- The problems the reviewers found in older parts of the site were registered
  below rather than fixed in this session, to keep the change to what was asked
  for. They are listed in the order they should be dealt with.
- Apply to Rakuten now rather than waiting on Awin, so two applications are in
  flight at once (owner's decision, 2026-09-03). `APPLICATIONS.md` now carries a
  Rakuten step-by-step, checked against Rakuten's own publisher help centre the
  same day. The application itself is the owner's to submit — it needs tax
  details, a mailing address and acceptance of terms in his name.

## Registered for Phase 3 — found by review, deliberately not fixed here
None of these can affect the site today. All of them can bite the moment a real
feed arrives, so deal with them before the first feed goes in.

| # | What happens | Why it matters |
|---|---|---|
| 1 | If a feed writes some sizes as numbers and others as text, half the matching products vanish from the page — and the page still states a confident count of what it is showing | Publishes silently, no error. States a falsehood. Text sizes are common in affiliate feeds |
| 2 | A product missing its width list stops the site publishing | Loud, not silent: the publish job fails and nothing broken goes live. Very likely in a real feed |
| 3 | A size written like "15 1/2" creates a broken page address | Publishes silently with a mangled URL |
| 4 | Setting the per-page product threshold to zero silently means three | A configuration trap, not a falsehood |

Also worth building in from the start: the site currently reads "no feed is
connected" from the product file simply being empty. Once a feed exists, a run
that legitimately returns nothing would write the same empty file, and the site
would state something untrue — the same class of defect that was caught and
fixed in this session. Have the feed importer record that it ran, so the pages
can tell "no feed yet" apart from "feed ran, found nothing".

## Open questions for the owner
- Nothing outstanding. The one question raised this session — whether to wait on
  Awin or apply to Rakuten now — was answered: apply to Rakuten now.

## Recommended next session
- Phase 2 (still open): enter the Cloudflare token once you have it, record which
  networks approved — Awin and now Rakuten are both expected to be in flight —
  and take feed access from the first one that does.
- Gate that must be met first: at least one network approved, with feed access.
  `APPLICATIONS.md` is the keyboard packet — apply order, paste-ready answers,
  the width-check gate to run on any feed before committing to it, and the steps
  to fetch the token.
- Risk: Medium — thin sites get rejected; the site is honest and now clean, but
  it is small and has no listings until a feed arrives.
