#!/usr/bin/env python3
"""Records what Awin itself says about the feed and the account.

Two questions the daily run could not answer before (HANDOFF.md, 2026-09-17):

1. How fresh is the retailer feed the in-stock promise rests on? Awin's
   feed-list download reports a "last imported" time for every feed the
   account can pull. It uses the same product-feed key that is already
   embedded in the Create-a-Feed address in AWIN_FEED_URL, so this needs no
   new secret.
2. Has a pending advertiser (Zeba, FitVille) been approved, and is anyone
   clicking through? That needs the Awin Publisher API and a read-only
   token in AWIN_API_TOKEN. Without the token this part reports
   "not configured" and the run carries on.

Writes data/awin_status.yaml (feed freshness and programme relationships —
committed, so the next run can say what changed) and awin_status_report.md
(the human-readable section for the run report — never committed). Click
and transaction counts go only in the report, never in the committed file,
and money figures are not written anywhere: the repository and its run logs
are public.

Never fails the build. Anything that goes wrong is recorded as a line in the
report and the catalogue rebuild proceeds as before. The feed key and the
API token are never printed.
"""

import csv
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

TIMEOUT = 30
USER_AGENT = "sasquatch-index-status/1.0"
API = "https://api.awin.com"
FEED_LIST = "https://productdata.awin.com/datafeed/list/apikey/{key}/"
RELATIONSHIPS = ("joined", "pending", "suspended", "rejected")

# Same limit build_catalogue.py applies to the feed the site publishes from
# (MAX_FEED_AGE_DAYS there). A merchant worth applying to has to clear the
# same bar, or joining it would change nothing.
MAX_FEED_AGE_DAYS = 30
SHORTLIST_LIMIT = 25
# The site serves US buyers, so a merchant shipping from Switzerland is noise
# on the shortlist even when its feed is current. Region is ranked, not
# filtered: a genuinely on-theme brand should still be visible further down.
HOME_REGIONS = ("US", "CA")
MERCHANT_PROFILE = "https://ui.awin.com/merchant-profile/{advertiser_id}"
FOOTWEAR = re.compile(
    r"\b(shoe|shoes|footwear|boot|boots|bootie|booties|sneaker|sneakers|"
    r"trainer|trainers|sandal|sandals|slipper|slippers)\b", re.I)
# A shoe brand is not obliged to say so in its name: NORTIV 8 itself is filed
# under Clothing & Accessories. So anything in an apparel sector with a current
# feed is worth reading by eye, even when nothing in the row says "shoe".
APPAREL = re.compile(
    r"(clothing|apparel|fashion|footwear|shoe|accessor|sportswear|sports|"
    r"outdoor|workwear|lifestyle)", re.I)


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def yaml_str(s):
    return json.dumps(str(s))


def to_int(s):
    try:
        return int(str(s).replace(",", "").strip() or 0)
    except ValueError:
        return 0


def parse_imported(s):
    """Awin's feed list writes its import times without a zone; they are UTC."""
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def feed_age_days(last_imported):
    d = parse_imported(last_imported)
    return None if d is None else (datetime.now(timezone.utc) - d).days


def looks_like_footwear(row):
    haystack = " ".join((row.get("advertiser", ""), row.get("sector", ""), row.get("feed_name", "")))
    return bool(FOOTWEAR.search(haystack))


def rank(rows):
    """One line per merchant, the ones this site could actually sell for first.

    Awin lists a merchant once per feed, so the same advertiser arrives three
    or four times; only its largest feed is worth a line. Home-region
    merchants sort above the rest, then by catalogue size."""
    best = {}
    for r in rows:
        key = r["advertiser_id"] or r["advertiser"]
        if key not in best or to_int(r["products"]) > to_int(best[key]["products"]):
            best[key] = r
    return sorted(best.values(),
                  key=lambda f: (f["region"].upper() not in HOME_REGIONS,
                                 -to_int(f["products"]),
                                 f["advertiser"].lower()))


def looks_like_apparel(row):
    return bool(APPAREL.search(" ".join((row.get("advertiser", ""), row.get("sector", "")))))


# --- 1. Feed freshness, from the key already in the feed address -----------

def feed_freshness(feed_url):
    """Returns (our_feed, all_feeds, candidates, stats, error). our_feed is the
    row for the feed the site actually pulls; all_feeds is every feed from an
    advertiser the account has a relationship with, which is also the earliest
    sign a newly approved advertiser has a feed; candidates are footwear
    advertisers the account has NOT joined whose feed the network has imported
    recently — the shortlist worth applying to while every joined feed is
    frozen (HANDOFF.md, 2026-09-17)."""
    key = re.search(r"/apikey/([^/]+)", feed_url or "")
    fid = re.search(r"/fid/(\d+)", feed_url or "")
    if not key:
        return None, [], [], {}, "the feed address does not carry a product-feed key"
    key = key.group(1)
    print(f"::add-mask::{key}")  # belt and braces: the key must never reach a log
    try:
        body = get(FEED_LIST.format(key=key))
    except (urllib.error.URLError, OSError) as e:
        return None, [], [], {}, f"feed list could not be downloaded ({getattr(e, 'code', None) or e.__class__.__name__})"
    rows = list(csv.DictReader(io.StringIO(body)))
    if not rows:
        return None, [], [], {}, "feed list was empty"

    def col(row, *names):
        for k, v in row.items():
            if k and k.strip().lower() in names:
                return (v or "").strip()
        return ""

    feeds, candidates, footwear, dated, fresh, apparel = [], [], [], [], [], []
    not_joined_seen = sector_seen = 0
    for r in rows:
        row = {
            "advertiser": col(r, "advertiser name"),
            "advertiser_id": col(r, "advertiser id"),
            "membership": col(r, "membership status"),
            "feed_id": col(r, "feed id"),
            "feed_name": col(r, "feed name"),
            "last_imported": col(r, "last imported"),
            "last_checked": col(r, "last checked"),
            "products": col(r, "no of products", "number of products", "products"),
            "sector": col(r, "primary sector", "sector", "vertical", "primary category"),
            "region": col(r, "primary region", "region"),
        }
        if row["sector"]:
            sector_seen += 1
        # The list carries every feed on the network. Advertisers we have a
        # relationship with are recorded as before; the rest are scanned for a
        # footwear merchant whose feed the network is still importing, because
        # that is the only thing that lifts the site out of its empty state.
        if row["membership"].lower() in ("not joined", "notjoined"):
            not_joined_seen += 1
            row["age_days"] = feed_age_days(row["last_imported"])
            if row["age_days"] is not None:
                dated.append(row)
                if looks_like_footwear(row):
                    footwear.append(row)
                if row["age_days"] <= MAX_FEED_AGE_DAYS:
                    fresh.append(row)
                    if looks_like_footwear(row):
                        candidates.append(row)
                    elif looks_like_apparel(row):
                        apparel.append(row)
            continue
        feeds.append(row)
    candidates = rank(candidates)
    apparel = rank(apparel)
    footwear.sort(key=lambda f: f["age_days"])
    dated.sort(key=lambda f: f["age_days"])
    sectors = Counter((f["sector"] or "unstated") for f in fresh)
    stats = {
        "rows": len(rows),
        "not_joined_seen": not_joined_seen,
        "sector_seen": sector_seen,
        "candidates": len(candidates),
        "merchants_fresh": len(rank(fresh)),
        "footwear_any_age": len(footwear),
        # When the shortlist is empty these say why: whether the network is
        # moving at all, and how close the nearest footwear merchant is.
        "nearest_footwear": footwear[:5],
        "freshest_on_network": dated[0] if dated else None,
        "fresh_seen": len(fresh),
        "apparel": apparel,
        "fresh_sectors": sectors.most_common(8),
    }
    ours = None
    if fid:
        ours = next((f for f in feeds if f["feed_id"] == fid.group(1)), None)
    return ours, feeds, candidates, stats, None if ours else "the feed the site pulls was not in the list"


# --- 2. Programme relationships and clicks, from the Publisher API ----------

def publisher_id_from_catalogue(data_dir):
    """The publisher id is the a= parameter on every affiliate link."""
    path = Path(data_dir, "products.yaml")
    if not path.exists():
        return None
    m = re.search(r"[?&]a=(\d+)", path.read_text())
    return m.group(1) if m else None


def api(token, path, **params):
    url = f"{API}{path}?{urllib.parse.urlencode(params)}" if params else f"{API}{path}"
    return json.loads(get(url, {"Authorization": f"Bearer {token}", "Accept": "application/json"}))


def programmes(token, pub):
    out, errors = {}, []
    for rel in RELATIONSHIPS:
        try:
            for p in api(token, f"/publishers/{pub}/programmes", relationship=rel):
                out[str(p.get("id"))] = {"name": p.get("name", ""), "relationship": rel}
        except (urllib.error.URLError, OSError, ValueError) as e:
            errors.append(f"{rel}: {getattr(e, 'code', None) or e.__class__.__name__}")
    return out, errors


def performance(token, pub, region, days):
    end = datetime.now(timezone.utc).date() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    rows = api(token, f"/publishers/{pub}/reports/advertiser",
               startDate=start.isoformat(), endDate=end.isoformat(), region=region, timezone="UTC")
    per = []
    for r in rows:
        per.append({
            "advertiser": r.get("advertiserName", ""),
            "impressions": int(r.get("impressions") or 0),
            "clicks": int(r.get("clicks") or 0),
            "transactions": int(r.get("totalNo") or 0),
        })
    return {"from": start.isoformat(), "to": end.isoformat(), "advertisers": per}


# --- Previous state, so the report can say what moved ------------------------

def previous_programmes(data_dir):
    path = Path(data_dir, "awin_status.yaml")
    if not path.exists():
        return {}
    out, cur = {}, None
    for line in path.read_text().splitlines():
        m = re.match(r'  "?(\d+)"?:$', line)
        if m:
            cur = m.group(1)
            out[cur] = {}
        elif cur and line.startswith("    "):
            k, _, v = line.strip().partition(": ")
            out[cur][k] = json.loads(v) if v.startswith('"') else v
    return out


# --- Output -------------------------------------------------------------------

def profile_link(f):
    link = MERCHANT_PROFILE.format(advertiser_id=f["advertiser_id"]) if f["advertiser_id"] else ""
    return f"[{f['advertiser']}]({link})" if link else f["advertiser"]


def merchant_lines(rows):
    out = []
    for f in rows[:SHORTLIST_LIMIT]:
        bits = [f"imported {f['last_imported']} ({f['age_days']}d ago)"]
        if f["products"]:
            bits.append(f"{f['products']} products")
        if f["region"]:
            bits.append(f["region"])
        out.append("- " + profile_link(f) + " — " + ", ".join(bits))
    if len(rows) > SHORTLIST_LIMIT:
        out.append(f"- …and {len(rows) - SHORTLIST_LIMIT} more.")
    return out


def apparel_report(stats):
    """Second tier, only shown when the footwear shortlist came back empty:
    apparel merchants with a current feed. Read by eye — a shoe brand will not
    always say so in its name or its sector."""
    fresh = stats.get("fresh_seen", 0)
    if not fresh:
        # Nothing the key can see is current, so there is no second tier to read.
        return []
    apparel = stats.get("apparel") or []
    n = len(apparel)
    out = ["", f"Of the {stats.get('merchants_fresh', fresh)} merchants with a current feed, "
               f"{n} {'is an apparel or sports merchant' if n == 1 else 'are apparel or sports merchants'}"
               f" — a shoe brand may be among them under a name that does not say so. "
               f"Home region first:"]
    if apparel:
        out.extend(merchant_lines(apparel))
    else:
        out.append("")
        out.append("None. What the key can see with a current feed, by sector: "
                   + "; ".join(f"{name} ({count})" for name, count in stats.get("fresh_sectors", []))
                   + ".")
    return out


def shortlist_report(candidates, stats):
    """The apply-to shortlist. Report only — never committed: it is a scan of
    the network, not a fact about this site, and it changes every day."""
    if not stats:
        return []
    scanned = f"{stats.get('not_joined_seen', 0)} unjoined feeds scanned"
    if not stats.get("not_joined_seen"):
        return ["", "**Merchants worth applying to:** the feed list returned no unjoined "
                    "feeds, so the network cannot be scanned for one from here."]
    out = ["", f"**Footwear merchants with a feed Awin imported in the last {MAX_FEED_AGE_DAYS} days:** "
               f"{len(candidates)} of {scanned}.", ""]
    if not candidates:
        n = stats.get("footwear_any_age", 0)
        out.append(f"None. {n} footwear merchant{'' if n == 1 else 's'} "
                   f"{'was' if n == 1 else 'were'} found at any age.")
        freshest = stats.get("freshest_on_network")
        if freshest:
            out.append(f"The freshest unjoined feed of any kind is {freshest['advertiser']}, "
                       f"imported {freshest['last_imported']} ({freshest['age_days']}d ago) — "
                       + ("so the network is importing normally and the frozen feeds are the "
                          "ShareASale path, not Awin."
                          if freshest["age_days"] <= MAX_FEED_AGE_DAYS else
                          "so nothing this key can see is current, which points at the key's "
                          "own feed access rather than at any one merchant."))
        if stats.get("nearest_footwear"):
            out.append("")
            out.append("Nearest footwear merchants, all too stale to use:")
            for f in stats["nearest_footwear"]:
                out.append("- " + profile_link(f) + f" — imported {f['last_imported']} ({f['age_days']}d ago)")
        out.extend(apparel_report(stats))
        return out
    out.extend(merchant_lines(candidates))
    out.append("")
    out.append("Not joined. Applying starts the approval clock; the run re-checks the "
               "import date before anything from it is published.")
    return out


def write_status(data_dir, checked_at, ours, feeds, feed_error, progs, prog_error):
    lines = [
        "# Written by scripts/awin_status.py every run. What Awin itself says",
        "# about the feed the site pulls and the account's advertiser",
        "# relationships. Committed so the next run can report what changed.",
        "# No click or money figures live here: the repository is public.",
        "",
        f"checked_at: {yaml_str(checked_at)}",
        "feed:",
    ]
    if ours:
        for k in ("advertiser", "feed_id", "feed_name", "last_imported", "last_checked", "products"):
            lines.append(f"  {k}: {yaml_str(ours[k])}")
    else:
        lines.append(f"  error: {yaml_str(feed_error)}")
    lines.append("feeds_visible_to_key:")
    for f in feeds:
        lines.append(f"  - {yaml_str(f['advertiser'] + ' / ' + f['feed_name'] + ' / ' + f['membership'] + ' / last imported ' + f['last_imported'])}")
    lines.append("programmes:")
    if progs is None:
        lines.append(f"  error: {yaml_str(prog_error)}")
    else:
        for pid, p in sorted(progs.items(), key=lambda kv: kv[1]["name"].lower()):
            lines.append(f"  {pid}:")
            lines.append(f"    name: {yaml_str(p['name'])}")
            lines.append(f"    relationship: {yaml_str(p['relationship'])}")
    Path(data_dir, "awin_status.yaml").write_text("\n".join(lines) + "\n")


def main(data_dir):
    checked_at = now()
    feed_url = os.environ.get("AWIN_FEED_URL", "")
    token = os.environ.get("AWIN_API_TOKEN", "").strip()
    region = os.environ.get("AWIN_REGION", "US").strip() or "US"
    report = ["### Awin status", ""]

    ours, feeds, candidates, stats, feed_error = feed_freshness(feed_url)
    if ours:
        report.append(f"**Feed the site pulls:** {ours['advertiser']} — last imported by Awin **{ours['last_imported'] or 'unknown'}**"
                      + (f", last checked {ours['last_checked']}" if ours['last_checked'] else "")
                      + (f", {ours['products']} products" if ours['products'] else "") + ".")
    else:
        report.append(f"**Feed freshness:** not available — {feed_error}.")
    if feeds:
        report.append("")
        report.append("Feeds this key can see:")
        for f in feeds:
            report.append(f"- {f['advertiser']} ({f['membership']}), {f['feed_name']}, last imported {f['last_imported'] or 'unknown'}")
    report.extend(shortlist_report(candidates, stats))

    progs, prog_error = None, None
    report.append("")
    if not token:
        prog_error = "AWIN_API_TOKEN is not set"
        report.append("**Advertiser relationships and clicks:** not configured (no API token).")
    else:
        pub = os.environ.get("AWIN_PUBLISHER_ID", "").strip() or publisher_id_from_catalogue(data_dir)
        if not pub:
            prog_error = "publisher id unknown"
            report.append("**Advertiser relationships:** publisher id could not be determined.")
        else:
            progs, errs = programmes(token, pub)
            if errs and not progs:
                progs, prog_error = None, "; ".join(errs)
                report.append(f"**Advertiser relationships:** the API refused the request ({prog_error}). "
                              "Awin's docs say the token's user needs Admin on the publisher account.")
            else:
                before = previous_programmes(data_dir)
                changes = []
                for pid, p in progs.items():
                    was = before.get(pid, {}).get("relationship")
                    if was and was != p["relationship"]:
                        changes.append(f"**{p['name']}: {was} → {p['relationship']}**")
                    elif not was and before:
                        changes.append(f"**{p['name']}: new, {p['relationship']}**")
                if changes:
                    report.append("🔔 **Advertiser relationship changed since last run:** " + "; ".join(changes))
                    report.append("")
                report.append("Advertiser relationships:")
                for pid, p in sorted(progs.items(), key=lambda kv: kv[1]["name"].lower()):
                    report.append(f"- {p['name']}: {p['relationship']}")
                if errs:
                    report.append(f"- (some lists could not be read: {'; '.join(errs)})")
            try:
                for days in (1, 7):
                    perf = performance(token, pub, region, days)
                    label = "yesterday" if days == 1 else "last 7 days"
                    total_c = sum(a["clicks"] for a in perf["advertisers"])
                    total_t = sum(a["transactions"] for a in perf["advertisers"])
                    report.append("")
                    report.append(f"**Click-throughs {label}** ({perf['from']} to {perf['to']}): {total_c} clicks, {total_t} transactions.")
                    for a in perf["advertisers"]:
                        if a["clicks"] or a["transactions"]:
                            report.append(f"- {a['advertiser']}: {a['clicks']} clicks, {a['transactions']} transactions")
            except (urllib.error.URLError, OSError, ValueError) as e:
                report.append("")
                report.append(f"**Click-throughs:** could not be read ({getattr(e, 'code', None) or e.__class__.__name__}).")

    write_status(data_dir, checked_at, ours, feeds, feed_error, progs, prog_error)
    Path("awin_status_report.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data"))
    except Exception as e:  # never fail the catalogue build over a status check
        Path("awin_status_report.md").write_text(f"### Awin status\n\nStatus check failed: {e.__class__.__name__}.\n")
        print(f"Awin status check failed: {e.__class__.__name__}: {e}")
        sys.exit(0)
