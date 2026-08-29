# Phase 0 Brief — Stand up the repo and get an empty site live

Hand this to Claude Code together with `SASQUATCH_OS.md`. This is a single session.

**Risk: Low.** Nothing is public-facing yet that matters, nothing is monetized,
and everything in this phase is reversible by deleting the repo.

---

## Goal of this session

A public URL that loads a nearly empty page, built from a data file, deploying
automatically when the repo changes. Nothing more.

---

## Tasks

1. **Create the repository** in the BitsCon GitHub org.
   - Suggested name: `sasquatch-index`. Ask the owner to confirm or rename.
   - Public or private is the owner's call — ask.

2. **Place the operating docs** at the repo root.
   - `SASQUATCH_OS.md` — the standing preflight doc.
   - `PHASE_0_BRIEF.md` — this file, for the record.

3. **Scaffold the structure.** Pick a static site generator and justify the
   choice in one sentence against these criteria, in priority order:
   - Builds fine in an unattended scheduled job
   - Minimal dependencies to keep working over time
   - Straightforward to generate many pages from one data file

4. **Create the data file** that the site will be generated from, using the data
   model in SASQUATCH_OS.md section 5b. Include the product type field even
   though every record is a shoe today — it is what lets apparel join later
   without a rebuild.

   Seed it with two or three placeholder records only. Real curation is Phase 1.

5. **Set up the URL structure** from SASQUATCH_OS.md section 5a, including the
   `/shoes/` path segment. Generating the full page grid is Phase 1; this session
   only proves the structure builds.

6. **Connect hosting** with automatic deploy on push. Free tier. Report the live
   URL to the owner.

7. **Confirm the loop works** by making one trivial change and verifying it
   appears on the live site without manual intervention.

8. **Write `HANDOFF.md`** using the structure in SASQUATCH_OS.md, and commit it.

---

## Explicitly out of scope this session

- Any real shoe data or curation
- Anything apparel-related beyond the product type field
- Any affiliate links or program applications
- Any advertising
- Any scheduled job
- Any design work beyond making the page legible

---

## Questions to ask the owner — one at a time, by voice

1. Confirm or change the repo name.
2. Public repo or private?
3. Does he already own a domain for this, or should hosting supply a default
   address for now?
