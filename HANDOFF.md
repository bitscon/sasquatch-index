# Handoff — Phase 3 — 2026-09-09

## What was completed
- **Phase 3 is closed.** The gate was a full build running clean end to end
  from feed data. It does, and it is live.
- **A catalogue importer was built** (`scripts/build_catalogue.py`). It reads
  the downloaded feed the same way the Phase 2 check does, applies the NORTIV 8
  field mapping from `APPLICATIONS.md`, and applies the skip-and-count guards
  from `FEED_HAZARDS.md`. It never receives or prints the feed address.
- **A manual publishing job was built and run** (`Build catalogue from feed`
  in Actions). It pulls the feed, writes the catalogue, commits it, and
  triggers the site rebuild. Two real runs against the live feed both
  succeeded.
- **The catalogue is live.** Size 13, 14 and 15 each have a real page: 86, 43
  and 27 styles respectively, all in stock, all linking straight to NORTIV 8
  via the Awin affiliate link, widths correctly limited to standard and wide.
- **A run marker was added** (`data/feed_run.yaml`) so the site can now tell
  "no feed has ever run" apart from "a feed ran and matched nothing" — those
  used to read identically to a visitor (`FEED_HAZARDS.md` hazard 5). The
  homepage and the size-listing page both carry the three-way message now.
- **The zero-threshold note was added** to `hugo.toml` next to the setting
  itself, so nobody mistakes an explicit 0 for "generate everything" — it
  silently stays 3 either way (`FEED_HAZARDS.md` hazard 4).
- **A real deploy failure was hit and fixed**, twice, before anything wrong
  reached a visitor:
  - The publishing job's first commit did not reach production automatically.
    GitHub does not let the built-in Actions token trigger other workflows —
    a loop guard, not a bug in this repo — so the job now explicitly asks for
    the site rebuild once it has pushed a real change.
  - The first real deploy then failed outright: a handful of NORTIV 8 image
    filenames carry mangled bytes from a broken transcode at the source, which
    decode to literal control characters. YAML refuses those outright, even
    inside a quoted string, so the build stopped rather than publish anything
    wrong. The importer now strips control characters from every text field
    it pulls from a row before writing the catalogue.

## What was NOT completed and why
- Nothing planned for this phase was skipped.
- Cosmetic only, not fixed: a number of NORTIV 8 style names are missing an
  apostrophe ("Men s" instead of "Men's") in the feed itself. That is the
  merchant's own data, passed through honestly rather than guessed at — the
  same broken-transcode issue that produced the control characters likely
  dropped the character. Worth knowing, not worth inventing a fix for.

## Current state of the system
- Site live at https://bitscon.github.io/sasquatch-index/ showing real
  inventory: three size pages (13, 14, 15), 156 styles total, one retailer,
  one brand, all sourced from the NORTIV 8 feed.
- The publishing job is manual only (`workflow_dispatch`). Nothing is
  scheduled yet — running it again is a deliberate action, not automatic.
- Analytics live and cookieless; the privacy page states it.
- Zeba and FitVille still pending advertiser approval. Rakuten remains
  available as a second source; CJ deferred.
- Feed address stored as a repository secret, never committed, never printed.

## Decisions made this session
- **Grouped by style name, not by row.** The feed is one row per size; the
  catalogue groups all sizes and widths of the same style into one product
  record, matching the data model's "sizes available" / "widths available"
  fields and the "86 styles" language the count is meant to carry.
- **Filtered to size 13 and up at import time.** The feed carries the full
  size range down to roughly size 7; only rows at 13 and above are written,
  since sizes below that are outside this site's purpose by design, not by
  omission.
- **Retailer is NORTIV 8.** The feed has no separate retailer field — this
  program is NORTIV 8's own storefront, so brand and retailer are the same
  name, which is what the affiliate link actually points at.
- **No apparel-style categories invented.** Category is passed through
  exactly as the feed's coarse grouping (Activity, Boots, Shoes) rather than
  guessed into a finer vocabulary the data doesn't support.
- **Scheduling was deliberately left out.** Phase 4 owns turning this same job
  unattended and adding the owner's report; this phase only had to prove the
  pipeline works when run.

## Open questions for the owner
- None blocking. If Zeba or FitVille approves later, hand the next session
  that approval and its feed address the same way Awin's was handled.

## Recommended next session
- Phase 4: put the publishing job on a schedule, verify the affiliate links
  it writes actually resolve, and send a short report after each run.
- Gate that must be met first: two consecutive unattended runs succeed.
- Risk: Low — the pipeline itself is already proven this session; Phase 4 is
  wrapping it in a timer and a status message, not building it from scratch.
