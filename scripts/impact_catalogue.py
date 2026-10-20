#!/usr/bin/env python3
"""Reads every Impact.com product catalog this account can see and turns the
fresh ones into catalogue records — DARK: nothing here reaches the live site.

Owner-approved 2026-10-19 as a ready-and-waiting importer for the day an
Impact.com store approves this site. It writes two files of its own:

  data/impact_products.yaml — one record per style, in exactly the
                               data/products.yaml shape (SASQUATCH_OS.md
                               section 5b) plus feed_updated, the catalog's own
                               last-updated time.
  data/impact_run.yaml      — a run marker (FEED_HAZARDS.md hazard 5): what was
                               seen, how fresh each catalog was, what was kept
                               and why the rest was skipped.

It never writes data/products.yaml and the site's pages do not read either of
these files yet. Wiring them in is a later step, taken only after a real
catalog has been seen in the run report (SASQUATCH_OS.md section 2c: nothing
publishes from a source that has not been verified).

Credentials come from IMPACT_ACCOUNT_SID and IMPACT_AUTH_TOKEN (repository
secrets, SASQUATCH_OS.md section 5). With either one missing the script says so
and writes nothing. The token and the authenticated addresses are never
printed or written to any file — the run logs and the repository are public.

Every network call goes through fetch_json(), so tests can hand it canned
answers and never touch the network.
"""

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# One set of rules for every network, so an Impact page and an Awin page can
# never disagree on what counts as fresh, kids', a boot or waterproof.
from build_catalogue import (  # noqa: E402
    KIDS_RE,
    MAX_FEED_AGE_DAYS,
    SIZE_FLOOR,
    clean,
    derive_attributes,
    derive_category,
    safe_url,
    tidy_name,
    yaml_str,
)

API_HOST = "https://api.impact.com"
SOURCE = "Impact.com Partner API"
USER_AGENT = "sasquatch-index-catalogue/1.0 (+https://sasquatchindex.com/)"
TIMEOUT = 60
PAGE_SIZE = 1000
# Impact's documentation: listing a catalog's items cannot page past 20,000
# results — a request beyond that is refused. Stop at the limit and say so in
# the run marker, rather than let the refusal look like a broken catalog.
MAX_ITEMS_PER_CATALOG = 20000
MAX_PAGES = MAX_ITEMS_PER_CATALOG // PAGE_SIZE + 1
# Impact's rate limits are counted per hour. A short wait is fine; waiting out
# a whole hour inside the daily build is not. Past this many seconds the
# catalog is recorded as rate-limited and the run moves on.
MAX_RATE_LIMIT_WAIT = 300
MAX_RATE_LIMIT_RETRIES = 3

# The documented StockAvailability values are InStock, OutOfStock and
# PreOrder. SASQUATCH_OS.md section 2b: only what the retailer lists as in
# stock is ever shown, so pre-order counts as not in stock.
IN_STOCK = {"instock"}

# FEED_HAZARDS.md hazard 6 says to prefer a real gender or age-group field over
# the product name when a feed has one. Impact's items carry both, so they are
# read first; the name is checked as well, because a catalog may leave them
# blank.
MEN_GENDERS = {"male", "men", "mens", "man", "m"}
UNISEX_GENDERS = {"unisex", "u", "all"}
WOMEN_GENDERS = {"female", "women", "womens", "woman", "f", "ladies"}
ADULT_AGE_GROUPS = {"", "adult", "adults"}
MENS_NAME_RE = re.compile(r"\b(men'?s?|male|unisex)\b", re.I)
WOMENS_NAME_RE = re.compile(r"\b(women'?s?|womans?|ladies|female)\b", re.I)

# Width words, mapped to the site's small width vocabulary. A marking outside
# this list is skipped and counted, never guessed at (FEED_HAZARDS.md: a feed
# that cannot power the pages honestly is not patched over).
WIDTHS = {
    "": "standard", "D": "standard", "M": "standard", "D(M)": "standard",
    "D M": "standard", "MEDIUM": "standard", "REGULAR": "standard",
    "STANDARD": "standard",
    "W": "wide", "WIDE": "wide", "2E": "wide", "EE": "wide",
    "XW": "extra-wide", "4E": "extra-wide", "EEEE": "extra-wide",
    "6E": "extra-wide", "EEEEEE": "extra-wide", "EXTRA WIDE": "extra-wide",
    "EXTRA-WIDE": "extra-wide", "X-WIDE": "extra-wide", "XWIDE": "extra-wide",
}
# A size number, then whatever is left over as the width marking. Half sizes
# only: every size has to make a clean page address (FEED_HAZARDS.md hazard 3).
SIZE_RE = re.compile(r"^(\d{1,2})(?:\.(0|5))?\s*(.*)$")
# "15 1/2" is a half size written as a fraction, not a dual size.
HALF_FRACTION_RE = re.compile(r"^(\d{1,2})\s+1\s*/\s*2\b\s*(.*)$")
# Country and gender words some stores put around the number; they carry no
# size information once the item's gender field has been checked.
NOISE_RE = re.compile(r"\b(US|USA|MEN'?S|MENS)\b\.?", re.I)


class ImpactError(Exception):
    """A failed call, described without its address or credentials."""


class RateLimited(ImpactError):
    pass


# --- the only code that touches the network --------------------------------

def make_fetch(sid, token, sleep=time.sleep):
    """Returns fetch_json(path) for this account: GET one API path and return
    the decoded JSON. HTTP Basic auth with the account SID and token, JSON
    asked for explicitly (Impact answers in XML otherwise). On a 429 it waits
    for the time Impact's documented Retry-After / RateLimit-Reset headers
    give, if that is short, and tries again."""
    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    headers = {
        "Authorization": "Basic " + auth,
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }

    def fetch_json(path):
        if not path.startswith("/Mediapartners/"):
            # Only ever send the credentials to Impact's own API.
            raise ImpactError("refused to follow a page address outside the API")
        for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
            req = urllib.request.Request(API_HOST + path, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code != 429:
                    raise ImpactError(f"HTTP {e.code}") from None
                h = e.headers or {}
                wait = _seconds(h.get("Retry-After")) or _seconds(h.get("RateLimit-Reset")) or 60
                if wait > MAX_RATE_LIMIT_WAIT or attempt == MAX_RATE_LIMIT_RETRIES:
                    raise RateLimited(f"rate limited, reset in {wait}s") from None
                print(f"  Impact rate limit reached; waiting {wait}s as asked.")
                sleep(wait + 1)
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                reason = getattr(e, "reason", e)
                raise ImpactError(f"network error ({type(reason).__name__})") from None
            except ValueError:
                raise ImpactError("answer was not JSON") from None
        raise RateLimited("rate limited")

    return fetch_json


def _seconds(value):
    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return None


# --- reading the API -------------------------------------------------------

def list_all(fetch_json, path, key):
    """Follows Impact's paging to the end and returns (records, truncated).
    The documented envelope carries @page, @numpages and @nextpageuri; the
    next-page address is followed when given, otherwise Page is counted up to
    @numpages."""
    out = []
    seen = set()
    sep = "&" if "?" in path else "?"
    first = f"{path}{sep}PageSize={PAGE_SIZE}"
    nxt = first
    pages = 0
    while nxt:
        if nxt in seen or pages >= MAX_PAGES:
            return out, True
        seen.add(nxt)
        body = fetch_json(nxt)
        pages += 1
        out.extend(body.get(key) or [])
        if len(out) >= MAX_ITEMS_PER_CATALOG:
            return out[:MAX_ITEMS_PER_CATALOG], True
        link = (body.get("@nextpageuri") or "").strip()
        if link:
            parsed = urllib.parse.urlsplit(link)
            if parsed.netloc and parsed.netloc != urllib.parse.urlsplit(API_HOST).netloc:
                raise ImpactError("next page pointed outside the API")
            nxt = parsed.path + (("?" + parsed.query) if parsed.query else "")
            continue
        page, numpages = _int(body.get("@page")), _int(body.get("@numpages"))
        if page and numpages and page < numpages:
            nxt = f"{first}&Page={page + 1}"
        else:
            nxt = None
    return out, False


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def parse_when(raw):
    """Impact writes DateLastUpdated as ISO 8601. Returns an aware UTC time,
    or None when the value is missing or unreadable — an unknown date is not
    the same as an old one, and is reported as unknown."""
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        when = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc)


# --- the item rules --------------------------------------------------------

def parse_size(raw):
    """Returns (size, width) or a skip reason, the same contract as
    build_catalogue.parse_size. Stores write sizes many ways ("14 2E",
    "13 D(M)", "13 M US", "15 Wide"); each is reduced to a number the URL can
    carry and one of standard / wide / extra-wide. A row naming two sizes
    ("13/14", "M13 W14.5") is skipped — it cannot be put on one size page
    honestly."""
    s = " ".join((raw or "").upper().split())
    if not s:
        return "no_size"
    m = HALF_FRACTION_RE.match(s)
    if m:
        s = f"{m.group(1)}.5 {m.group(2)}".strip()
    if "/" in s or len(re.findall(r"\d+(?:\.\d+)?", re.sub(r"\b[2-6]E\b", "", s))) > 1:
        return "dual_sized_row"
    # "M13" is the men's scale written as a prefix.
    s = re.sub(r"^M\s*(?=\d)", "", s)
    s = " ".join(NOISE_RE.sub(" ", s).split())
    m = SIZE_RE.match(s)
    if not m:
        return "unparseable_size"
    whole, half, rest = m.groups()
    rest = re.sub(r"\s*\(\s*", "(", rest).replace(" )", ")").strip()
    width = WIDTHS.get(rest)
    if width is None:
        width = WIDTHS.get(rest.replace("(", " ").replace(")", " ").strip())
    if width is None:
        return "unexpected_width_marking"
    num = int(whole) + (0.5 if half == "5" else 0)
    size = int(num) if float(num).is_integer() else num
    return size, width


def adult_mens_or_unisex(item, name):
    """Returns None when the item is men's or unisex and adult, else the skip
    reason. A blank gender is accepted only when the merchant's own name says
    men's or unisex: a women's 13 is a men's 11 or so, and listing it on the
    size 13 page would be the hazard 6 failure all over again."""
    age = (item.get("AgeGroup") or "").strip().lower()
    if age not in ADULT_AGE_GROUPS or KIDS_RE.search(name):
        return "kids_size_scale"
    gender = re.sub(r"[^a-z]", "", (item.get("Gender") or "").lower())
    if gender in WOMEN_GENDERS:
        return "womens"
    if gender in MEN_GENDERS or gender in UNISEX_GENDERS:
        if WOMENS_NAME_RE.search(name) and not MENS_NAME_RE.search(name):
            return "womens"
        return None
    if gender:
        return "unrecognised_gender"
    if WOMENS_NAME_RE.search(name) and not MENS_NAME_RE.search(name):
        return "womens"
    if MENS_NAME_RE.search(name):
        return None
    return "gender_not_stated"


def parse_price(raw):
    if raw is None:
        return None
    m = re.search(r"\d+(?:\.\d+)?", str(raw).replace(",", ""))
    return float(m.group(0)) if m else None


def build_styles(catalog, items, skipped, feed_updated):
    """Applies the item rules to one catalog's items and groups what survives
    into one record per style. Grouping is by the store's own parent SKU or
    item group, falling back to the product name."""
    retailer = clean((catalog.get("CampaignName") or catalog.get("AdvertiserName") or "").strip())
    catalog_currency = (catalog.get("Currency") or "").strip().upper()
    groups = {}
    for item in items:
        if str(item.get("IsParent")).lower() == "true":
            # A parent record describes the style, not a size on the shelf.
            skipped["parent_record"] += 1
            continue
        name = clean((item.get("Name") or "").strip())
        link = clean((item.get("Url") or "").strip())
        if not name or not link:
            skipped["incomplete_row"] += 1
            continue
        stock = re.sub(r"[^a-z]", "", (item.get("StockAvailability") or "").lower())
        if stock not in IN_STOCK:
            skipped["out_of_stock_or_not_for_sale"] += 1
            continue
        reason = adult_mens_or_unisex(item, name)
        if reason:
            skipped[reason] += 1
            continue
        currency = (item.get("Currency") or catalog_currency).strip().upper()
        if currency != "USD":
            skipped["not_usd"] += 1
            continue
        price = parse_price(item.get("CurrentPrice"))
        if price is None:
            skipped["no_price"] += 1
            continue
        parsed = parse_size(item.get("Size"))
        if isinstance(parsed, str):
            skipped[parsed] += 1
            continue
        size, width = parsed
        if size < SIZE_FLOOR:
            skipped["below_size_13"] += 1
            continue

        key = (item.get("ParentSku") or item.get("ItemGroupId") or "").strip() or name.lower()
        style = tidy_name(clean((item.get("ParentName") or "").strip()) or name)
        g = groups.setdefault(key, {
            "style": style,
            "brand": clean((item.get("Manufacturer") or "").strip()) or clean((catalog.get("AdvertiserName") or "").strip()),
            "category": clean((item.get("Category") or "").strip()),
            "link": link,
            "image": safe_url(clean((item.get("ImageUrl") or "").strip())),
            "sizes": set(), "widths": set(), "prices": [], "colours": set(),
        })
        g["sizes"].add(size)
        g["widths"].add(width)
        g["prices"].append(price)
        for c in item.get("Colors") or []:
            c = clean(str(c).strip().lower())
            if c:
                g["colours"].add(c)

    records = []
    for g in groups.values():
        category, family = derive_category(g["style"], g["category"])
        records.append({
            "product_type": "shoes",
            "brand": g["brand"],
            "style_name": g["style"],
            "category": category,
            "family": family,
            "sizes": sorted(g["sizes"]),
            "widths": sorted(g["widths"]),
            "attributes": derive_attributes(g["style"]),
            "price_min": min(g["prices"]),
            "price_max": max(g["prices"]),
            "currency": "USD",
            "colours": len(g["colours"]),
            "retailer": retailer,
            "link": g["link"],
            "image": g["image"],
            "feed_updated": feed_updated,
        })
    return records


# --- writing ---------------------------------------------------------------

YAML_RESERVED = {"y", "yes", "n", "no", "true", "false", "on", "off", "null", "~"}


def ystr(s):
    """build_catalogue.yaml_str, plus quoting for values a YAML reader would
    otherwise misread (a leading bracket, a bare "yes", a number). Store
    catalogs are wider than one merchant's feed, and Hugo reads every file in
    data/, so a malformed file here would stop the site building."""
    s = str(s)
    if s and (s[0] in "[]{}!&*|>'%@`,?-" or s.lower() in YAML_RESERVED
              or re.fullmatch(r"[-+.\d][\d._eE+-]*", s)):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return yaml_str(s)


def dump_impact_products(products):
    """Field for field the same record shape build_catalogue.dump_products
    writes, plus feed_updated, so wiring these into the pages later is a merge
    and not a translation."""
    lines = [
        "# Impact.com catalog records — written by scripts/impact_catalogue.py.",
        "#",
        "# NOT read by the site yet. These records sit here until a real Impact",
        "# catalog has been seen in the run report; wiring them into the pages is",
        "# a separate, later step (SASQUATCH_OS.md section 2c). Do not hand-edit —",
        "# the next run overwrites this file.",
        "#",
        "# Same record shape as data/products.yaml (SASQUATCH_OS.md section 5b),",
        "# with one extra field: feed_updated, the time the store last updated",
        "# its catalog at Impact. Only catalogs updated within the freshness",
        "# window are included (MAX_FEED_AGE_DAYS in build_catalogue.py).",
        "",
    ]
    if not products:
        lines.append("products: []")
        return "\n".join(lines) + "\n"
    lines.append("products:")
    for p in products:
        lines.append(f"  - product_type: {ystr(p['product_type'])}")
        lines.append(f"    brand: {ystr(p['brand'])}")
        lines.append(f"    style_name: {ystr(p['style_name'])}")
        lines.append(f"    category: {ystr(p['category'])}")
        lines.append(f"    family: {ystr(p['family'])}")
        lines.append("    sizes: [" + ", ".join(str(s) for s in p["sizes"]) + "]")
        lines.append("    widths: [" + ", ".join(ystr(w) for w in p["widths"]) + "]")
        lines.append("    attributes: [" + ", ".join(ystr(a) for a in p["attributes"]) + "]")
        lines.append(f"    price_min: {p['price_min']:.2f}")
        lines.append(f"    price_max: {p['price_max']:.2f}")
        lines.append(f"    currency: {ystr(p['currency'])}")
        lines.append(f"    colours: {p['colours']}")
        lines.append(f"    retailer: {ystr(p['retailer'])}")
        lines.append(f"    link: {ystr(p['link'])}")
        lines.append(f"    image: {ystr(p['image'])}")
        lines.append("    fit_notes: \"\"")
        lines.append(f"    feed_updated: {ystr(p['feed_updated'])}")
    return "\n".join(lines) + "\n"


def dump_impact_run(run):
    lines = [
        "# Written by scripts/impact_catalogue.py every time it runs with",
        "# credentials (FEED_HAZARDS.md hazard 5). Not read by the site yet.",
        "#",
        "# Per catalog — fresh: updated within max_feed_age_days, its in-stock",
        "# items were read. stale: older than that, nothing read from it.",
        "# unknown: Impact gave no readable update date, nothing read from it.",
        "# error / rate_limited: the items could not be read this run.",
        "",
        f"ran_at: {ystr(run['ran_at'])}",
        f"source: {ystr(run['source'])}",
        f"max_feed_age_days: {run['max_feed_age_days']}",
    ]
    if run.get("error"):
        lines.append(f"error: {ystr(run['error'])}")
    lines.append(f"catalogs_seen: {run['catalogs_seen']}")
    lines.append(f"styles_written: {run['styles_written']}")
    if not run["catalogs"]:
        lines.append("catalogs: []")
    else:
        lines.append("catalogs:")
        for c in run["catalogs"]:
            lines.append(f"  - name: {ystr(c['name'])}")
            lines.append(f"    retailer: {ystr(c['retailer'])}")
            lines.append("    date_last_updated: " + (ystr(c["date_last_updated"]) if c["date_last_updated"] else "null"))
            lines.append("    age_days: " + (str(c["age_days"]) if c["age_days"] is not None else "null"))
            lines.append(f"    status: {ystr(c['status'])}")
            if c.get("note"):
                lines.append(f"    note: {ystr(c['note'])}")
            lines.append(f"    items_read: {c['items_read']}")
            lines.append(f"    items_truncated: {'true' if c['truncated'] else 'false'}")
            lines.append(f"    styles_written: {c['styles_written']}")
    if not run["skipped"]:
        lines.append("skipped: {}")
    else:
        lines.append("skipped:")
        for k, v in run["skipped"].items():
            lines.append(f"  {k}: {v}")
    return "\n".join(lines) + "\n"


# --- the run ---------------------------------------------------------------

def main(data_dir="data", env=None, fetch_json=None, now=None):
    env = os.environ if env is None else env
    sid = (env.get("IMPACT_ACCOUNT_SID") or "").strip()
    token = (env.get("IMPACT_AUTH_TOKEN") or "").strip()
    if not sid or not token:
        print("Impact not configured — skipped")
        return 0
    fetch_json = fetch_json or make_fetch(sid, token)
    now = now or datetime.now(timezone.utc)
    base = f"/Mediapartners/{urllib.parse.quote(sid, safe='')}/"
    run = {
        "ran_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": SOURCE,
        "max_feed_age_days": MAX_FEED_AGE_DAYS,
        "catalogs_seen": 0,
        "styles_written": 0,
        "catalogs": [],
        "skipped": {},
        "error": None,
    }
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    try:
        catalogs, _ = list_all(fetch_json, base + "Catalogs", "Catalogs")
    except ImpactError as e:
        # The catalog list itself failed. Record that it ran and failed;
        # leave any earlier records file as it was.
        run["error"] = f"could not list catalogs: {e}"
        Path(data_dir, "impact_run.yaml").write_text(dump_impact_run(run))
        print(f"Impact: {run['error']}")
        return 1

    skipped = Counter()
    products = []
    for cat in catalogs:
        name = clean(str(cat.get("Name") or cat.get("Id") or "unnamed catalog"))
        retailer = clean((cat.get("CampaignName") or cat.get("AdvertiserName") or "").strip())
        when = parse_when(cat.get("DateLastUpdated"))
        entry = {
            "name": name, "retailer": retailer,
            "date_last_updated": when.strftime("%Y-%m-%dT%H:%M:%SZ") if when else None,
            "age_days": (now - when).days if when else None,
            "status": None, "note": None, "items_read": 0, "truncated": False,
            "styles_written": 0,
        }
        run["catalogs"].append(entry)
        # The freshness rule (SASQUATCH_OS.md section 2b), applied per catalog
        # to the store's own last-updated time, before any item is read.
        if when is None:
            entry["status"] = "unknown"
            entry["note"] = "Impact gave no readable update date; skipped"
            print(f"  {name}: no readable update date — skipped")
            continue
        if entry["age_days"] > MAX_FEED_AGE_DAYS:
            entry["status"] = "stale"
            print(f"  {name}: last updated {entry['date_last_updated']}, {entry['age_days']} days old — stale, skipped")
            continue
        cat_id = str(cat.get("Id") or "").strip()
        if not cat_id:
            entry["status"] = "error"
            entry["note"] = "catalog has no id"
            continue
        try:
            items, truncated = list_all(
                fetch_json, f"{base}Catalogs/{urllib.parse.quote(cat_id, safe='')}/Items", "Items")
        except RateLimited as e:
            entry["status"] = "rate_limited"
            entry["note"] = str(e)
            print(f"  {name}: {e}")
            continue
        except ImpactError as e:
            entry["status"] = "error"
            entry["note"] = str(e)
            print(f"  {name}: could not read items ({e})")
            continue
        entry["status"] = "fresh"
        entry["items_read"] = len(items)
        entry["truncated"] = truncated
        records = build_styles(cat, items, skipped, entry["date_last_updated"])
        entry["styles_written"] = len(records)
        products.extend(records)
        print(f"  {name}: fresh ({entry['age_days']} days), {len(items)} items read, {len(records)} styles kept"
              + (" — stopped at Impact's paging limit" if truncated else ""))

    products.sort(key=lambda p: (p["retailer"].lower(), p["style_name"].lower(), p["link"]))
    run["catalogs_seen"] = len(catalogs)
    run["styles_written"] = len(products)
    run["skipped"] = dict(sorted(skipped.items()))
    Path(data_dir, "impact_products.yaml").write_text(dump_impact_products(products))
    Path(data_dir, "impact_run.yaml").write_text(dump_impact_run(run))

    print(f"Impact catalogs seen: {len(catalogs)}")
    print(f"Impact styles written (not published): {len(products)}")
    if skipped:
        print("Skipped:")
        for k, v in sorted(skipped.items()):
            print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data"))
