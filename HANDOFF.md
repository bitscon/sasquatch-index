# Handoff — Phase 4 — 2026-09-09

## What was completed
- **The publishing job is now scheduled.** `build-catalogue.yml` fires daily
  at 09:00 UTC on its own, with no one watching it. The manual trigger stays
  available for an on-demand run.
- **Affiliate links are now verified every run.** A new step
  (`scripts/verify_links.py`) checks that every link in the catalogue
  actually resolves, following the merchant's redirect through to a real
  page. A broken link is reported, not treated as a failure — a dead link on
  the merchant's end shouldn't block an otherwise-good catalogue rebuild.
- **Every run now writes a short report** — feed totals, styles written,
  anything skipped and why, and the link-check result — to that run's job
  summary in Actions, so the state of the catalogue is visible without
  reading logs.
- **A stale status line was corrected.** `PROJECT_STATUS.md` still showed
  phase 3 as not started when it had already closed; that's fixed, and
  phase 4 now shows in progress.
- **A manual run of the updated job was watched end to end** to catch any
  problem in the new steps before the schedule ever fires unattended. It
  passed clean: catalogue rebuilt, all 87 affiliate links checked, zero
  broken, report written correctly.

## What was NOT completed and why
- **The phase gate itself is not yet met.** The gate is two consecutive
  *unattended* runs succeeding — today's clean run was a supervised manual
  trigger to prove the new code, not one of the two scheduled firings the
  gate requires. Nothing more to build; this is a matter of the schedule
  firing on its own over the next two days and someone confirming both
  runs came back clean.

## Current state of the system
- Site live at https://bitscon.github.io/sasquatch-index/, 156 styles across
  sizes 13–15, same as last session.
- The catalogue job now runs daily at 09:00 UTC, unattended, and reports to
  its own job summary each time. Deploy still triggers automatically off the
  catalogue job when it makes a real change.
- Analytics live and cookieless; the privacy page states it.
- Zeba and FitVille still pending advertiser approval. Rakuten remains
  available as a second source; CJ deferred.
- Feed address stored as a repository secret, never committed, never printed.

## Decisions made this session
- **Daily cadence, 09:00 UTC.** The feed changes slowly enough that daily is
  frequent enough to catch stock and price drift without generating noise,
  and it costs nothing extra — Actions minutes are free on a public repo.
- **The report lives in the Actions job summary, not an email.** No new
  secret, no new mail infrastructure, and it's one click from the Actions
  tab. If the owner wants it pushed to an inbox instead, that's a small
  follow-up, not a redesign.
- **A broken link is reported, never fatal.** Failing the whole job over one
  dead merchant link would stop good catalogue data from publishing over
  something outside this site's control.

## Open questions for the owner
- None blocking. If you'd rather the report land in your inbox instead of
  the Actions summary, say which address and that gets wired in as a small
  addition.

## Recommended next session
- Phase 4 close-out: confirm the schedule has fired twice on its own with
  both runs clean (check the Actions tab for `Build catalogue from feed` —
  two green scheduled runs after today), then mark phase 4 complete.
- Gate that must be met first: two consecutive unattended runs succeed —
  the mechanism is built and proven; this is just watching it happen.
- Risk: Low.
