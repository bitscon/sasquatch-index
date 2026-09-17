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
from datetime import datetime, timedelta, timezone
from pathlib import Path

TIMEOUT = 30
USER_AGENT = "sasquatch-index-status/1.0"
API = "https://api.awin.com"
FEED_LIST = "https://productdata.awin.com/datafeed/list/apikey/{key}/"
RELATIONSHIPS = ("joined", "pending", "suspended", "rejected")


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def yaml_str(s):
    return json.dumps(str(s))


# --- 1. Feed freshness, from the key already in the feed address -----------

def feed_freshness(feed_url):
    """Returns (our_feed, all_feeds, error). our_feed is the row for the feed
    the site actually pulls; all_feeds is every feed the key can see, which
    is also the earliest sign a newly approved advertiser has a feed."""
    key = re.search(r"/apikey/([^/]+)", feed_url or "")
    fid = re.search(r"/fid/(\d+)", feed_url or "")
    if not key:
        return None, [], "the feed address does not carry a product-feed key"
    key = key.group(1)
    print(f"::add-mask::{key}")  # belt and braces: the key must never reach a log
    try:
        body = get(FEED_LIST.format(key=key))
    except (urllib.error.URLError, OSError) as e:
        return None, [], f"feed list could not be downloaded ({getattr(e, 'code', None) or e.__class__.__name__})"
    rows = list(csv.DictReader(io.StringIO(body)))
    if not rows:
        return None, [], "feed list was empty"

    def col(row, *names):
        for k, v in row.items():
            if k and k.strip().lower() in names:
                return (v or "").strip()
        return ""

    feeds = []
    for r in rows:
        # The list carries every feed on the network; only advertisers we have
        # a relationship with are worth recording.
        if col(r, "membership status").lower() in ("not joined", "notjoined"):
            continue
        feeds.append({
            "advertiser": col(r, "advertiser name"),
            "advertiser_id": col(r, "advertiser id"),
            "membership": col(r, "membership status"),
            "feed_id": col(r, "feed id"),
            "feed_name": col(r, "feed name"),
            "last_imported": col(r, "last imported"),
            "last_checked": col(r, "last checked"),
            "products": col(r, "no of products", "number of products", "products"),
        })
    ours = None
    if fid:
        ours = next((f for f in feeds if f["feed_id"] == fid.group(1)), None)
    return ours, feeds, None if ours else "the feed the site pulls was not in the list"


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

    ours, feeds, feed_error = feed_freshness(feed_url)
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
