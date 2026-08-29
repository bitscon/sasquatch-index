# Handoff — Phase 0 — 2026-08-29

## What was completed
- The repository was created in BitsCon and both operating documents sit at its
  root, copied from Drive without alteration.
- The site scaffold is in place and builds cleanly. Nine pages come out of it.
- The data file carries every field the operating document asks for, including
  the product type field that lets apparel join later. It holds three
  placeholder records and nothing real.
- The size pages are generated from that one data file, not hand-written. Adding
  a record to the file adds pages; removing one removes them.
- The address structure is proven, including the shoes path segment. Sizes with
  no matching product never get a page.
- The site is published and a public address loads it.
- The unattended loop was proven, not assumed: a small wording change was pushed,
  and the publish job ran on its own and put that exact change on the live site
  with nobody touching anything.
- The build names every product still missing the owner's fit notes. All three
  placeholders are on that list, which is expected at this stage.
- The owner loaded the published address and confirmed the page works.

## What was NOT completed and why
- Nothing outstanding for this phase.

## Current state of the system
- Repository: public, holding the operating docs, the scaffold, the data file
  and the publish job.
- Site: **live** at https://bitscon.github.io/sasquatch-index/
- Publish job: working. Every change to the main branch rebuilds and republishes
  the site with no person involved.
- Nothing is running on a schedule. Nothing is monetized. No affiliate links, no
  advertising, no analytics.
- No real product data. The three records are placeholders.

## Decisions made this session
- Hugo was chosen as the site generator because it is a single self-contained
  program with no dependency tree to rot, so unattended builds keep working, and
  it turns one data file into many pages natively.
- The generator version is pinned rather than tracking the newest release, so an
  overnight upstream change cannot alter an unattended build.
- The data file is written in a format meant for hand-editing, with comments,
  because the owner seeds roughly fifty styles by hand in Phase 1.
- Fit notes were left deliberately empty and are flagged at build time, because
  they are the owner's words and are never generated.
- Publishing was switched on by hand by the owner. Letting the publish job switch
  it on was tried on both a private and a public repository and refused by GitHub
  both times, so that attempt was removed rather than left to produce a
  misleading error.
- No project board. The owner runs this by voice and text straight to GitHub, so
  this handoff file and the repository history are the whole record. A future
  session should not create one without being asked.
- No custom domain. The owner does not own one for this yet, so the address the
  host supplies stands. Nothing in the site is pinned to that address: the
  publish job supplies it at build time, so pointing a domain at the site later
  needs no rebuild of anything.

## Open questions for the owner
- Nothing outstanding.

## Recommended next session
- Phase 1: hand-seed roughly fifty real styles, browsable by size and category,
  with the disclosure and privacy pages.
- Gate that must be met first: a public address loads — **met**.
- Risk: Low
