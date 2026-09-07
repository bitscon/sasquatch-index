# FEED_HAZARDS.md — read before wiring any product feed

These are failures found while reviewing how the site will behave once a real
product feed is connected. They lived only in git history until now. Read this
file alongside `SASQUATCH_OS.md` before the first feed goes in, and treat each
item as a build-time check the feed importer must satisfy — not a suggestion.

A feed that fails a check is not wired around. The rule from the applications
packet stands: a merchant whose feed cannot power the pages honestly is dropped,
not patched over.

---

## The five hazards

### 1. Mixed size formats hide products while the page still counts them
Some feeds write a size as a number on one product and as text on another. When
that happens, only half the matching products land on a size page — yet the page
still prints a confident count of what it claims to be showing. It publishes
without any error. The visitor is told a falsehood, quietly.

**Required:** normalise every size to one format before matching, and count only
what actually matched. A page's stated count and its shown products must be the
same set.

### 2. A product with no width list stops the whole site publishing
The site filters by size and width together, so a product that arrives with no
width information halts the build. This one is loud, not silent — the publish
simply fails — and it is very likely in a real feed.

**Required:** the importer skips a product missing its widths rather than letting
it break the build, and records that it was skipped so the gap is visible.

### 3. A fractional size mangles the page address
A size written like `15 1/2` produces a broken page address if used directly in a
URL. The page publishes, but at a mangled and unreachable path — silent again.

**Required:** convert sizes to a safe URL form before they become page addresses,
and confirm the resulting path is valid.

### 4. A zero page-threshold silently becomes three
The rule that a page needs enough products before it is worth generating has a
floor. Setting that threshold to zero does not mean "generate everything" — it
silently falls back to three. Anyone tuning it should know the floor is there and
will not honour a zero.

**Required:** if the threshold is ever exposed as a setting, make the floor
explicit so no one believes they turned it off when they did not.

### 5. "No feed yet" and "feed ran, found nothing" must not look identical
Today the site reads "no feed is connected" from the product file simply being
empty. That is correct now, before any feed exists. But once a feed is wired, a
run that legitimately returns nothing writes the same empty file — and the site
would then state "no feed connected," which is untrue.

**Required:** the importer records that it ran — a timestamp or run marker — so
the pages can tell the two situations apart. An empty result after a real run
must read differently from never having run at all.

---

## Why these are written down here

Every one of the silent failures above publishes a confident, wrong page without
raising an error. That is the exact failure mode this site cannot afford: it
trades on coverage and accuracy, and a page that states a false count or sits at
a broken address undoes that trust while looking fine. The loud failure (2) is
merely inconvenient by comparison. Wire the feed so the silent ones cannot
happen.
