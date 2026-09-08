# Handoff — Phase 2 — 2026-09-08

## What was completed
- **Phase 2 is closed.** The gate was a network approval and a usable feed.
  Both are now met.
- **NORTIV 8 approved the join request** on 2026-09-08, which unlocked Awin's
  feed builder for that merchant.
- **The feed address is held as a repository secret**, added by the owner at the
  keyboard. It never passed through a session, a chat or a committed file.
- **A hand-run feed check was built and used.** It pulls the feed inside the
  publishing system, reports what the feed actually contains, and states plainly
  whether size and width can both be read from it. It changes nothing and never
  prints the feed address.
- **The feed was read and accepted.** It carries structured sizes and readable
  widths, and yields real inventory in the sizes this site exists for.
- **The rules for using it are written down** at the bottom of `APPLICATIONS.md`
  — which field holds what, and the four things that would otherwise be got
  wrong when the catalogue is built.
- **The redesign published yesterday is still live and unchanged.**

## What was NOT completed and why
- **The catalogue is not built.** That is Phase 3 and a session of its own. The
  site still shows no listings today.
- **The check's first verdict was wrong and had to be corrected.** It looked for
  fields by name, and this merchant keeps the size in a generically named column,
  so it reported a false failure on a usable feed. It now identifies fields by
  what they contain. Worth knowing: a name-only check would have caused a good
  merchant to be dropped.

## Current state of the system
- Site live at https://bitscon.github.io/sasquatch-index/ carrying the new
  design, still with no listings.
- Analytics live and cookieless; the privacy page states it.
- Awin approved. NORTIV 8 approved and its feed accepted. Zeba and FitVille
  still pending advertiser approval. Rakuten remains available as a second
  source; CJ deferred.
- Feed address stored as a repository secret. Nothing scheduled yet — the feed
  is pulled only when the check is run by hand.
- No product data in the repository.

## Decisions made this session
- **Accepted NORTIV 8 as the first feed.** Width is not a separate field in it;
  it is a letter on the end of the size value, which is read from the data
  rather than guessed at. The standing rule against patching around a bad feed
  is about inventing what the data does not say, and this feed does say it.
- **The width vocabulary for this merchant is standard and wide only.** The
  pages must never claim extra-wide, 2E or 4E for these products.
- **Brand is NORTIV 8, not the feed's brand field**, which holds model codes.
- **Rows with dual women's/men's sizing are skipped and counted**, not guessed at.
- **The feed check finds fields by their contents, not their names**, after the
  name-only version reported a false failure.

## Open questions for the owner
- None blocking. If Zeba or FitVille approves later, hand the next session that
  approval and its feed address the same way; a second merchant widens coverage
  above size 15, which NORTIV 8 does not reach.

## Recommended next session
- Phase 3: build the catalogue from the NORTIV 8 feed — pull it in the
  publishing job, apply the rules at the bottom of `APPLICATIONS.md` and the
  five checks in `FEED_HAZARDS.md`, and let the size pages generate themselves.
- Gate that must be met first: a full build runs clean end to end from feed data.
- Risk: Medium — the first real data through the pages, and every hazard in
  `FEED_HAZARDS.md` publishes a confident wrong page rather than an error.
