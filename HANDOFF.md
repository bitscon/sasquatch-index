# Handoff — Phase 0 — 2026-08-29

## What was completed
- The repository was created in BitsCon and both operating documents sit at its
  root, copied from Drive without alteration.
- The site scaffold is in place and builds cleanly. Nine pages come out of it.
- The data file exists and carries every field the operating document asks for,
  including the product type field that lets apparel join later. It holds three
  placeholder records and nothing real.
- The size pages are generated from that one data file, not hand-written. Adding
  a record to the file adds pages; removing one removes them.
- The address structure is proven, including the shoes path segment. Sizes with
  no matching product never get a page.
- A publish job is committed. It rebuilds and republishes the site on every
  change to the main branch, with no person involved.
- The build prints a warning naming every product still missing the owner's fit
  notes. All three placeholders are on that list, which is expected at this stage.

## What was NOT completed and why
- The site is not live. Two switches in the repository's settings are needed and
  the automation is not permitted to touch settings — it is blocked at the
  network layer, not by a missing password. They are a keyboard job for the owner.
- The publish job has therefore never completed a run. Its first attempt failed
  at exactly the expected step and for exactly the expected reason.
- Because nothing is live, the change-appears-on-the-site check could not be run.

## Current state of the system
- Repository: created, **private**, holding the operating docs, the scaffold, the
  data file and the publish job.
- Site: builds correctly on demand; **not published, no public address yet**.
- Publish job: installed and correct, waiting on the two settings switches.
- Nothing is running on a schedule. Nothing is monetized. No affiliate links, no
  advertising, no analytics.

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
- The publish job no longer tries to switch Pages on by itself. It failed at that
  and the failure was confusing; it now assumes the switch is already on.

## Open questions for the owner
- Will you flip the repository to public and turn on Pages, or would you rather
  I move the site to a host that does not need a settings change?
- Do you already own a domain for this, or should the default address stand for now?
- Do you want a Kanboard board created for this project?

## Recommended next session
- Phase 1: hand-seed roughly fifty real styles, browsable by size and category,
  with the disclosure and privacy pages.
- Gate that must be met first: a public address loads — this is Phase 0's gate and
  it is **not met yet**. Phase 1 does not start until it is.
- Risk: Low
