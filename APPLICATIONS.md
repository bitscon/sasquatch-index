# Affiliate Applications — the owner's keyboard packet

Everything needed to apply, in order. The applications want real account and tax
details, so this is keyboard work. Facts below were checked against the
networks' own pages on 2026-09-02.

## Apply in this order

| # | Network | Why this one | Cost to join | Status |
|---|---|---|---|---|
| 1 | Awin — https://www.awin.com | Largest feed-driven network; absorbed ShareASale. Product feeds come with approval via its Create-a-Feed tool | Small refundable card deposit (currently $5), a verification step | **Approved 2026-09-03.** NORTIV 8 approved 2026-09-08, feed accepted — see the bottom of this file |
| 2 | Rakuten Advertising — https://rakutenadvertising.com | Carries Zappos, the single most on-theme merchant for big and wide sizes. Open network; no screening at signup, merchants screen individually | Free | **Owner applying — directed 2026-09-03.** Step-by-step below |
| 3 | CJ — https://www.cj.com | Broad merchant base, a solid second feed source. Note: accounts with no results in the first 6 months can be deactivated, so join it when ready to use it | Free | Not yet applied |

## Screening a merchant invite (read this before joining or building anything)

This is what a Claude session working inside the Awin dashboard should apply
on its own, without asking each time — join freely, but never conclude a feed
is usable from the dashboard alone.

**Skip outright — do not join.** The merchant sells nothing footwear-related
at all (fishing tackle, unrelated gear categories, etc.). Joining costs
nothing so an occasional accidental accept is harmless, but don't spend time
on these.

**Join, then test — never judge by eye.** Any merchant carrying men's
footwear, even mixed into a broader catalogue (boots alongside backpacks and
apparel, work boots, hunting/outdoor boots, athletic shoes, etc.) is worth
joining. Joining is free and reversible. What is NOT reversible-by-eyeballing
is whether the feed is usable — that is decided by one thing only:

1. Get the feed's exact download URL from Awin's own Feed List (Toolbox →
   Datafeeds, or the feed-list API) — never hand-build one, and never trust a
   URL assembled by copying a column list from a different merchant's feed.
   A hand-built URL missing columns will silently read as no size data even
   when the merchant's real feed has it — this already produced one false
   negative here.
2. Hand the exact URL to the next Claude session working the repo (or run
   the repo's Check a product feed Action). That is the only source of
   truth for pass/fail — not the dashboard's product count, not a category
   name that sounds promising, not a claimed feed the Feed List doesn't
   actually contain.
3. Treat any product count, feed name, or column list you didn't get
   directly from Awin's own Feed List as unverified. If a feed you expected
   to exist 400s or isn't in the list, it doesn't exist — don't guess a
   substitute URL for it.

Every merchant that has been through this gate — accepted or dropped, and
why — is recorded below and at the end of this file. Check there first; don't
re-run a merchant that's already been dropped without a materially different
feed offer.

Application answers used for Awin: publisher type content/editorial website,
sector Retail & Shopping (footwear/fashion sub-sectors only), the 252-character
site description below.

## Paste-ready answers

**Site URL**

```
https://bitscon.github.io/sasquatch-index/
```

**Site description, short** (for boxes capped at 255 characters — this is 252)

```
Sasquatch Index is a free reference site for men's shoes in size 13 and up: plain guides to sizing and widths, built to index styles across retailers by size and width, linking buyers straight to whoever stocks them. Nothing is sold on the site itself.
```

**Site description, full** (fits the usual "describe your site" box)

```
Sasquatch Index is a free reference site for men's shoes in size 13 and up.
It carries plain-language guides to sizing past 13 and to what the width
letters mean, and it is built to index styles across many retailers by size
and width, sending visitors straight to the retailer that carries them.
Nothing is sold on the site itself. Listing pages will be generated from
retailer product feeds, so availability stays current without manual
editing. The audience is people with hard-to-fit feet who arrive ready to
buy.
```

**Common form answers**

| Question | Answer |
|---|---|
| Publisher / promotion type | Content or comparison site (pick whichever the form offers) |
| How do you promote | Editorial content and search. No paid ads, no email list, no social buying |
| Traffic | New site, launched August 2026. Be honest: small and growing |
| Audience region | United States |
| Incentives / cashback / toolbar | No to all |

## Rakuten — the sitting, step by step

Checked against Rakuten's own publisher help centre on 2026-09-03. Free, no
deposit, and no screening to join: the network lets you in, and then each
merchant decides about you separately.

| Step | What happens |
|---|---|
| 1 | Register at https://rakutenadvertising.com — email, first name, last name, password |
| 2 | Describe the site: its address, a short description, and **how many monthly visitors and page views it gets** |
| 3 | Tax information and a valid mailing address |
| 4 | Once in, apply to individual merchants. **Zappos first** — the most on-theme merchant on the list |

**The one question that has no good answer yet: monthly visitors and page views.**
No analytics has ever run on this site, so there are no figures to give. Say so
plainly — a new site with no measured traffic. Do not estimate or round up:
joining the network does not depend on the number, and a figure invented here is
one that a merchant can later hold against the account. This is also the reason
to grab the Cloudflare token in the same sitting (below); it will not
manufacture history, but it starts the clock.

**Expect merchant approvals to be the slow part, not the signup.** Getting into
the network is close to automatic. Zappos deciding about a site with no traffic
is the real gate, and it may say no on this attempt.

## After a network approves

1. **Request the merchant programs.** On Rakuten: Zappos first. On Awin and CJ:
   search for shoe retailers that stock size 13 and up (running, work boot, and
   comfort brands are the likely fits).
2. **Check the feed before committing to any merchant — this is the gate.**
   The whole site turns on filtering by size AND width together. Download one
   product feed sample and confirm it carries structured size values and a
   separate width field. A feed with one loose size string and no width cannot
   power these pages, whatever its commission rate. If the feed fails this
   check, drop the merchant and move on.
3. Hand feed access (API key or feed URL) to the next working session. It goes
   in as a repository secret, never into a committed file.

## Standing warnings

- **Amazon must never be the feed.** Its product API requires ongoing qualifying
  sales to keep access; a quiet month silently kills the data source, which
  breaks the site-runs-unattended constraint. Opportunistic Amazon links are
  fine. Amazon as the pipeline is not.
- Nothing goes live that claims first-hand product experience. Application
  answers stay factual for the same reason.

## While you're at the keyboard: the analytics token

1. Sign in (or sign up, free) at https://dash.cloudflare.com
2. Left menu: **Analytics & Logs → Web Analytics** (works for any site; the
   domain does not need to be on Cloudflare).
3. Add the site with hostname `bitscon.github.io`, choose the JS snippet /
   manual install option.
4. From the snippet Cloudflare shows, copy just the token value (the string
   after `"token":`) and send it to the next session by voice or paste.

The site is already wired: setting that one token in the site configuration
turns on cookieless measurement and rewrites the privacy page to match in the
same build. Until then, nothing runs and the privacy page keeps saying so.

---

## The first feed — NORTIV 8, via Awin (checked and accepted 2026-09-08)

Approved 2026-09-08. The feed was pulled and read by the hand-run check in the
repository (Actions → "Check a product feed"), which reads the feed address from
repository secrets and never prints it.

**It passes the gate, with one limit.** Sizes are structured. Width is not its
own field: it is a letter on the end of the size value, which is deterministic
to read and so is normalisation, not guesswork. It carries only two states.

| What the site needs | Where it is in this feed |
|---|---|
| Size | `custom_2` — the label sits in `custom_1` ("US Size") |
| Width | the letter ending a size value: `W` is wide, nothing is standard |
| Style name | `product_name` |
| Colour | `custom_3` |
| Category | `merchant_category` — coarse: Activity, Shoes, Boots |
| Price | `search_price` |
| Availability | `in_stock`, `is_for_sale` |
| Link out | `aw_deep_link` |
| Image | `merchant_image_url`, `aw_image_url` |

**Rules for whoever wires the importer**

- **Brand is NORTIV 8.** The feed's `brand_name` holds model codes (QUEST-1,
  TROOPER, 170390-M), not brands. Never print it as a brand.
- **Width vocabulary for this merchant is standard and wide only.** Never write
  extra-wide, 2E or 4E against these products — the data does not say it.
- **Skip the dual-sized rows and count the skips.** Values like
  `13.5WOMEN / 12MEN` do not parse; there are about three hundred of them.
- **Coverage stops at size 15.** Nothing above it exists in this feed.

**What it yields at size 13 and up:** 420 rows — 89 styles at 13, 49 at 14, 32
at 15, all flagged in stock. That clears the page threshold for three size pages.

---

## Merchants checked and dropped

**TideWe, via Awin (checked 2026-09-09) — FAILS the gate.** Only one real feed
exists for this merchant in Awin's own feed list (id `103245`, 633 products,
general outdoor gear — backpacks, waders, vests, boots all mixed together, not
footwear-only). Pulled with the full 36-column set and read by the same check
NORTIV 8 passed: `custom_1` through `custom_5` are empty on every row, no other
column is structured as size or width, and size only appears inside free-text
product titles (e.g. "400Gram & Standard"). That is exactly what the gate
exists to catch — width would have to be guessed. Dropped per this file's own
rule; do not re-apply without a materially different feed offer from TideWe.

Note: a second feed (labelled "Google New", id `F1386`, claimed ~2,590
products) was reported during this merchant's review but does not exist in
Awin's feed list for this account — the download 400s. Whatever surfaced that
number was not reading Awin's actual feed data; treat it as unverified if it
comes up again.

**Piscifun, via Awin — accepted 2026-09-09, out of scope, no feed to build.**
Fishing tackle, not footwear. Accepting the invite cost nothing, but this
merchant will never power a page here; noted so it isn't re-evaluated.
