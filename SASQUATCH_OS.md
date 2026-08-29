# SASQUATCH_OS.md — Sasquatch Index

**Read this file completely at the start of every session before taking any action.**

---

## 1. What this project is

A free, public, static website that lets people browse shoe styles filtered by
size, focused on sizes most retailers stop short of. It links out to whoever
actually stocks each style.

It is **not** a store. No cart, no checkout, no inventory, no customer accounts,
no support queue.

**Scope: shoes only, for now.** The name was chosen so the site can later cover
hard-to-find apparel — shirts and pants in sizes that big-and-tall retail handles
badly. Build the data model and URL structure so apparel can be added later
without a rebuild. **Do not build apparel now.** Shoes ship first, simply.

**Owner:** Chad McCormack
**GitHub org:** BitsCon
**Working repo name:** `sasquatch-index` (owner may rename)

---

## 2. The non-negotiable constraints

These come from the owner directly. Do not design around them, do not propose
alternatives that violate them, and stop and ask if a task appears to require
breaking one.

| # | Constraint | Why it matters |
|---|---|---|
| 1 | **Nothing is sold to visitors.** No subscriptions, no products, no gated content. | Owner does not want customers to serve |
| 2 | **No scraping of retailer websites.** Data comes from affiliate product feeds only. | Fragile, and a terms-of-service problem |
| 3 | **The site must run unattended.** Routine updates happen on a schedule, not by hand. | Owner wants hands-off operation |
| 4 | **Design for phone-and-voice first.** See section 4 — this is a strong preference, not an absolute. | Owner can use a laptop when a task genuinely needs one |
| 5 | **Low profit is acceptable.** Do not optimize for revenue at the cost of constraints 1-4. | Stated explicitly and repeatedly |

---

## 2a. The design principle — read before any design decision

The visitor arrives with money in hand and one question: **where do I get these,
in my size, right now.**

Everything on the site serves answering that question fast. Nothing on the site
may get in the way of it.

**This rules out, permanently:**

| Pattern | Why it's banned |
|---|---|
| Interstitials, popups, newsletter modals over content | Delays the answer |
| Long preamble above the listings | Nobody is here to read |
| Invented scores, rankings, or "our top pick" theater | Dishonest and unhelpful |
| Ads wedged between listings | Serves the advertiser, not the visitor |
| Hiding availability behind a click | The availability *is* the product |

**The measure of a good page:** a person lands on it, sees what fits them, and
leaves for a retailer in seconds. If a change makes the site stickier at the cost
of that speed, reject it and tell the owner why.

The owner is explicit that the common playbook — ship a thin site fast, pile on
ads, chase volume — is not what this is. Do not propose it.

---

## 2b. Where the durability actually comes from

Recent search changes hit aggregated affiliate content hard. Thin listing sites
without first-hand knowledge lost most of their traffic. What survived carried
genuine original experience.

This site's protection is not its size or its speed to market. It is that the
owner wears the size and knows what actually fits. **The fit notes are the moat,
not a formality.** A page without them is a page that fails.

Never generate fit notes. They come from the owner. Flag pages that lack them and
report the list.

**Risk on depending on search traffic alone: High.** Plan for at least one channel
that does not run through a search engine.

---

## 3. How the owner works — session protocol

**Confirm before acting.** State the plan first. Wait for approval. Then execute.
Do not begin making changes on the assumption that approval is coming.

**One phase per session.** Each session tackles exactly one phase from the phase
plan. Do not roll ahead into the next phase even if there is time left.

**Approve the plan, then run.** Once the owner approves the plan for the session,
proceed without asking permission for each step. Interrupt only on divergence —
meaning the plan turns out to be wrong, a step fails, or something is discovered
that changes the plan. Routine progress does not need check-ins.

**State risk as a rating.** Every plan and every proposed change carries a rating
of Low, Medium, or High. Do not write narrative descriptions of what might go
wrong instead of the rating. Risk matters more than speed here.

**Explain like a systems engineer, not a coder.** The owner administers systems
well and does not read code. Describe what a change does to the system's
behavior. Do not walk through code line by line unless asked.

**Keep numbers out of prose.** Figures, versions, and counts belong in tables and
lists, not buried inside sentences.

**Prefer tables and bullets.** Avoid long paragraphs.

---

## 4. Phone and voice — the preferred lane

The owner drives most sessions by speaking into a phone. This is the lane to stay
in by default, and design should assume it.

- **Never require the owner to type exact strings** — no long file paths, no
  identifiers, no precise syntax as a prerequisite to progress.
- **Ask one question at a time.** A list of five questions cannot be answered by
  voice in one breath.
- **Offer numbered choices** rather than open-ended prompts where possible.
- **Confirm what you heard** when a spoken instruction is ambiguous, before acting.
- **Status answers must be speakable.** When asked "how's the site doing," reply
  with a short spoken summary first, then detail if asked.

**The escape hatch.** This is a preference, not a hard limit. The owner has a
laptop and administers his own public VPS, and can step in directly for setup
work that is genuinely better done at a keyboard — server configuration, domain
and DNS, credentials, anything requiring careful typing.

When a task is one of those, **say so plainly and hand it to him** rather than
inventing an awkward voice-driven path around it. Name the task, say why the
keyboard is the better tool, and state what you need back.

Do not use the escape hatch as a default. Routine operation stays on the phone.

**Note on hosting:** default to a free static host with automatic deploy on push.
The site is only files, so there is nothing to administer. The owner also runs his
own public VPS and can host there if needed — treat that as a fallback, not the
first choice, since it trades hands-off operation for maintenance he does not
need to take on.

**Do not confuse hosting with distribution.** Hosting is where the files sit and
is easily changed. Distribution is how people find the site, and no hosting
choice solves it. See section 8.

---

## 5. Architecture guardrails

| Area | Decision | Rationale |
|---|---|---|
| Site type | Static site, generated from a data file | Nothing to keep running; nearly free to host |
| Data source | Affiliate product feeds only | Legitimate, stable, machine-readable |
| Scheduling | Scheduled job in the repo, running on a cron schedule | Unattended by design |
| Hosting | Static host with automatic deploy on push | No servers to administer |
| Secrets | Stored as repository secrets, never committed to files | Credentials must not enter version control |
| Analytics | Required from day one | Ad network eligibility is measured in verified sessions |

---

## 5a. URL schema — this is the SEO engine

An exact-match domain name carries almost no ranking weight. What ranks is page
titles and URL structure. So the site's value comes from generating many narrow
pages, each aimed at one phrase a person would actually speak into a phone.

Generate the full grid from the data file:

| Page type | URL shape | Target search |
|---|---|---|
| Size | `/shoes/size-15/` | size 15 mens shoes |
| Size + width | `/shoes/size-15/extra-wide/` | size 15 extra wide |
| Size + category | `/shoes/size-15/clogs/` | size 15 clogs |
| Size + width + category | `/shoes/size-15/wide/running-shoes/` | size 15 wide running shoes |
| Size + attribute | `/shoes/size-15/waterproof/` | size 15 waterproof boots |
| Brand + size | `/shoes/crocs/size-15/` | crocs size 15 |

**Note the `/shoes/` segment.** It exists so apparel can be added later at its
own path without disturbing any existing URL. Never generate pages at the root
that assume footwear.

Cover the full size range, not just fifteen — thirteen and up is a much larger
audience than fifteen alone.

Suppress pages with no matching products. Empty pages hurt more than they help.

---

## 5b. Data model — built to expand, used narrowly

One record per product. Fields required now:

| Field | Notes |
|---|---|
| Product type | Set to shoes for every record today. This field is what lets apparel join later |
| Brand | |
| Style name | |
| Category | Sneakers, clogs, boots, dress, sandals, and so on |
| Sizes available | |
| Widths available | |
| Attributes | Waterproof, slip-resistant, and similar |
| Retailer | |
| Link | |
| Image | |
| Owner's fit notes | Written by the owner, not generated |

Do not add apparel-specific fields yet. The product type field is sufficient to
keep the door open.

---

## 6. Content quality rule — do not skip this

Ad networks screen against thin and heavily aggregated content, and a pure
feed-generated listing page is precisely what those filters target. A site that
is only a filtered catalog will likely be rejected.

**Therefore:** every category page must carry original commentary that a product
feed cannot produce — notes on fit, which brands run narrow or short, what holds
up over time. That writing comes from the owner, who actually wears the size.

When building category pages, always leave a clearly marked place for that
commentary, and flag to the owner which pages are still missing it.

---

## 7. Legal and disclosure requirements

- An affiliate disclosure must be present and visible before any affiliate link
  goes live. This is a legal requirement, not a nicety.
- A privacy policy is required once analytics or ads are running.
- Affiliate program terms vary by network. Read them before relying on a feed.

---

## 8. Phase plan and gates

Work one phase per session. Do not advance until the gate is met.

| Phase | Deliverable | Gate to advance | Risk |
|---|---|---|---|
| 0 | Repo created in BitsCon, structure scaffolded, hosting connected, empty site deploys | A public URL loads | Low |
| 1 | Hand-seeded catalog of roughly fifty styles, browsable by size and category, with disclosure and privacy pages | Site is live and would read as legitimate to a human reviewer | Low |
| 2 | Analytics installed; apply to affiliate programs using the live site | Approvals received | **Medium** — thin sites get rejected |
| 3 | Replace hand-seeded data with affiliate product feeds; site builds from feed | A full build runs clean end to end | Medium |
| 4 | Scheduled job: pull feed, rebuild, verify links, send owner a short report | Two consecutive unattended runs succeed | Low |
| 5 | Apply for display advertising | Approved and serving | Medium |
| 6 | Wait and measure. Change nothing. | Baseline revenue known | Low |
| 7 | Reinvest the majority of revenue into one traffic lever | Traffic measurably up against baseline | Medium |

---

## 9. End every session with a handoff

Before the session ends, write `HANDOFF.md` at the repo root, overwriting the
previous one. Use exactly this structure:

```
# Handoff — Phase <N> — <date>

## What was completed
- <plain-language bullets, no code>

## What was NOT completed and why
- <bullets, or "nothing outstanding">

## Current state of the system
- <what is live, what is not, what is running on a schedule>

## Decisions made this session
- <decision and the reason for it>

## Open questions for the owner
- <one question per bullet, phrased to be answerable by voice>

## Recommended next session
- Phase <N+1>: <one-line description>
- Gate that must be met first: <gate>
- Risk: <Low | Medium | High>
```

Then commit it. The next session begins by reading this file and HANDOFF.md
together.

---

## 10. Session start checklist

1. Read this file end to end.
2. Read `HANDOFF.md` if it exists.
3. State which phase this session covers.
4. State the plan and its risk rating.
5. **Wait for the owner's approval.**
6. Execute; interrupt only on divergence.
7. Write `HANDOFF.md` and commit before finishing.
