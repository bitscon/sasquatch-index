#!/usr/bin/env python3
"""Turns one downloaded product feed into the site's data files.

Reads the feed exactly the way scripts/feed_check.py does (same loader, same
column names — no drift between the check and the real import), applies the
NORTIV 8 rules from APPLICATIONS.md, and the skip-and-count guards from
FEED_HAZARDS.md. Writes two files:

  data/products.yaml   — one record per style, per SASQUATCH_OS.md section 5b.
  data/feed_run.yaml    — a run marker (FEED_HAZARDS.md hazard 5), so the site
                           can tell "no feed ever ran" apart from "the feed ran
                           and matched nothing."

This script never receives or prints the feed address — it only ever sees the
file already downloaded to disk by the workflow.
"""

import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from feed_check import load  # same loader as the hand-run check

BRAND = "NORTIV 8"
RETAILER = "NORTIV 8"
SOURCE = "NORTIV 8 via Awin"
SIZE_FLOOR = 13  # SASQUATCH_OS.md section 1: this site is size 13 and up, full stop.
SIZE_RE = re.compile(r"^(\d{1,2}(?:\.5)?)\s*([A-Za-z]*)$")
TRUE_WORDS = {"1", "true", "yes", "y"}


def parse_size(raw):
    """Returns (size, width) on success. On failure returns a reason string
    instead of a bare None, so the run report can say *why* a row was
    skipped rather than lumping every rejection together — a dual-sized row,
    a width letter outside this merchant's vocabulary, and plain garbage are
    three different things worth telling apart.

    Only ever returns values already safe to put in a URL and to match
    consistently (FEED_HAZARDS.md hazards 1 and 3) — anything that doesn't
    cleanly parse is rejected here, not patched later."""
    raw = raw.strip()
    m = SIZE_RE.match(raw)
    if not m:
        return "dual_sized_row" if "/" in raw else "unparseable_size"
    num = float(m.group(1))
    suffix = m.group(2).upper()
    if suffix == "":
        width = "standard"
    elif suffix == "W":
        width = "wide"
    else:
        return "unexpected_width_marking"  # vocabulary is standard/wide only — APPLICATIONS.md
    size = int(num) if num.is_integer() else num
    return size, width


def clean(s):
    """Strips control characters a real feed should never contain but this one
    does: some image filenames carry mangled bytes from a broken transcode at
    the source (a Chinese filename fragment turns into a literal control
    character). YAML rejects a bare control character outright — even inside
    a quoted string — so the build fails loudly rather than skip the row. That
    is exactly the kind of loud, avoidable failure this importer should not
    hand downstream: strip it here, once, for every field pulled from a row."""
    return "".join(c for c in s if unicodedata.category(c) != "Cc")


def yaml_str(s):
    s = str(s)
    if s == "" or any(c in s for c in ':#"\n') or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def dump_products(products):
    lines = [
        "# Sasquatch Index — the data file the whole site is generated from.",
        "#",
        "# Written by scripts/build_catalogue.py from the NORTIV 8 feed. Do not",
        "# hand-edit — the next import overwrites this file. See APPLICATIONS.md",
        "# for the field mapping and FEED_HAZARDS.md for the guards applied.",
        "#",
        "# Records arrive from an affiliate product feed only — never by hand, never",
        "# scraped (SASQUATCH_OS.md constraint 2).",
        "",
    ]
    if not products:
        lines.append("products: []")
        return "\n".join(lines) + "\n"
    lines.append("products:")
    for p in products:
        lines.append(f"  - product_type: {yaml_str(p['product_type'])}")
        lines.append(f"    brand: {yaml_str(p['brand'])}")
        lines.append(f"    style_name: {yaml_str(p['style_name'])}")
        lines.append(f"    category: {yaml_str(p['category'])}")
        lines.append("    sizes: [" + ", ".join(str(s) for s in p["sizes"]) + "]")
        lines.append("    widths: [" + ", ".join(yaml_str(w) for w in p["widths"]) + "]")
        lines.append("    attributes: []")
        lines.append(f"    retailer: {yaml_str(p['retailer'])}")
        lines.append(f"    link: {yaml_str(p['link'])}")
        lines.append(f"    image: {yaml_str(p['image'])}")
        lines.append("    fit_notes: \"\"")
    return "\n".join(lines) + "\n"


def dump_run(run):
    lines = [
        "# Written by scripts/build_catalogue.py every time it runs, whether or",
        "# not it found anything to publish. FEED_HAZARDS.md hazard 5: this is",
        "# what lets the site tell 'no feed ever ran' apart from 'the feed ran",
        "# and matched nothing' — both would otherwise leave products.yaml empty",
        "# and look identical to a visitor.",
        "",
        f"ran_at: {yaml_str(run['ran_at'])}",
        f"source: {yaml_str(run['source'])}",
        f"rows_in_feed: {run['rows_in_feed']}",
        f"products_written: {run['products_written']}",
        "sizes_covered: [" + ", ".join(str(s) for s in run["sizes_covered"]) + "]",
        "skipped:",
    ]
    for k, v in run["skipped"].items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines) + "\n"


def main(feed_path, data_dir):
    rows = load(feed_path)
    skipped = Counter()
    groups = {}

    for row in rows:
        style = clean((row.get("product_name") or "").strip())
        link = clean((row.get("aw_deep_link") or "").strip())
        image = clean((row.get("merchant_image_url") or "").strip() or (row.get("aw_image_url") or "").strip())
        category = clean((row.get("merchant_category") or "").strip())
        label = (row.get("custom_1") or "").strip()
        size_raw = (row.get("custom_2") or "").strip()
        in_stock = (row.get("in_stock") or "").strip().lower()
        for_sale = (row.get("is_for_sale") or "").strip().lower()

        if not style or not link:
            skipped["incomplete_row"] += 1
            continue
        if "size" not in label.lower():
            skipped["unrecognized_size_label"] += 1
            continue
        if in_stock not in TRUE_WORDS or for_sale not in TRUE_WORDS:
            skipped["out_of_stock_or_not_for_sale"] += 1
            continue

        parsed = parse_size(size_raw)
        if isinstance(parsed, str):
            skipped[parsed] += 1
            continue

        size, width = parsed
        if size < SIZE_FLOOR:
            skipped["below_size_13"] += 1
            continue

        g = groups.setdefault(style, {
            "sizes": set(), "widths": set(), "category": category,
            "link": link, "image": image,
        })
        g["sizes"].add(size)
        g["widths"].add(width)

    products = []
    for style in sorted(groups):
        g = groups[style]
        products.append({
            "product_type": "shoes",
            "brand": BRAND,
            "style_name": style,
            "category": g["category"],
            "sizes": sorted(g["sizes"]),
            "widths": sorted(g["widths"]),
            "retailer": RETAILER,
            "link": g["link"],
            "image": g["image"],
        })

    all_sizes = sorted({s for p in products for s in p["sizes"]})

    Path(data_dir).mkdir(parents=True, exist_ok=True)
    Path(data_dir, "products.yaml").write_text(dump_products(products))
    run = {
        "ran_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": SOURCE,
        "rows_in_feed": len(rows),
        "products_written": len(products),
        "sizes_covered": all_sizes,
        "skipped": dict(sorted(skipped.items())),
    }
    Path(data_dir, "feed_run.yaml").write_text(dump_run(run))

    print(f"Rows in feed: {len(rows)}")
    print(f"Styles written: {len(products)}")
    print(f"Sizes covered: {all_sizes}")
    print("Skipped:")
    for k, v in sorted(skipped.items()):
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "data"))
