# Affiliate Applications — the owner's keyboard packet

Everything needed to apply, in order. The applications want real account and tax
details, so this is keyboard work. Facts below were checked against the
networks' own pages on 2026-09-02.

## Apply in this order

| # | Network | Why this one | Cost to join | Status |
|---|---|---|---|---|
| 1 | Awin — https://www.awin.com | Largest feed-driven network; absorbed ShareASale. Product feeds come with approval via its Create-a-Feed tool | Small refundable card deposit (currently $5), a verification step | **Submitted 2026-09-02** — awaiting approval |
| 2 | Rakuten Advertising — https://rakutenadvertising.com | Carries Zappos, the single most on-theme merchant for big and wide sizes. Open network; no screening at signup, merchants screen individually | Free | **Owner applying — directed 2026-09-03.** Step-by-step below |
| 3 | CJ — https://www.cj.com | Broad merchant base, a solid second feed source. Note: accounts with no results in the first 6 months can be deactivated, so join it when ready to use it | Free | Not yet applied |

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
