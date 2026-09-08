#!/usr/bin/env python3
"""Reads one product feed and reports whether it can honestly power this site.

The gate (APPLICATIONS.md): the pages filter by size AND width together, so a
feed needs structured size values and width that can be read from the data
rather than guessed at.

Columns are found by what they contain, not only by what they are called. Real
feeds put the size in a column named custom_2 (NORTIV 8 does), so a name-only
check reports a false failure on a perfectly usable feed.

This script only reads and reports. It writes nothing to the site, and it never
prints the feed address — the address carries an access key.
"""

import csv
import gzip
import io
import re
import sys
import zipfile
from collections import Counter

SIZE_HINTS = ("size", "shoe_size", "fashion:size")
WIDTH_HINTS = ("width", "fashion:width", "shoe_width")
# A shoe size, optionally carrying a width letter: 13, 9.5, 13W, 10.5EE
SIZE_VALUE = re.compile(r"^(\d{1,2}(?:\.5)?)\s*([A-Za-z]{1,4})?$")
WIDTH_SUFFIX = re.compile(r"^(w|ww|xw|xxw|n|m|d|b|[2-6]e|eee+)$", re.I)
WIDTH_WORDS = re.compile(
    r"\b(narrow|medium|wide|extra[ -]?wide|x-?wide|[2-6]e|eee+)\b", re.I
)
HALF_SIZE = re.compile(r"^\d{1,2}\s+\d\s*[/⁄]\s*\d$")


def load(path):
    raw = open(path, "rb").read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    elif raw[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(raw))
        raw = z.read(z.namelist()[0])
    text = raw.decode("utf-8", errors="replace")
    try:
        dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;|\t")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(io.StringIO(text), dialect=dialect))


def values(rows, col, limit=2000):
    out = []
    for r in rows[:limit]:
        v = (r.get(col) or "").strip()
        if v:
            out.append(v)
    return out


def size_score(vals):
    """How much of this column reads as a shoe size.

    A flag column full of 1s parses as a size too, so a candidate also has to
    show the spread a real size range has: several distinct values, and values
    up in the range shoes are actually sold in.
    """
    if len(vals) < 10:
        return 0.0, 0, 0
    hits = wides = 0
    distinct = set()
    grown_up = 0
    for v in vals:
        m = SIZE_VALUE.match(v)
        if m and 1 <= float(m.group(1)) <= 20:
            hits += 1
            distinct.add(v)
            if float(m.group(1)) >= 6:
                grown_up += 1
            if m.group(2) and WIDTH_SUFFIX.match(m.group(2)):
                wides += 1
    if len(distinct) < 8 or grown_up < hits * 0.3:
        return 0.0, 0, len(distinct)
    return hits / len(vals), wides, len(distinct)


def main(path):
    rows = load(path)
    if not rows:
        print("VERDICT: FAIL — the feed parsed to zero rows.")
        return 0
    cols = list(rows[0].keys())
    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(cols)}")

    by_name_size = [c for c in cols if any(h in c.lower() for h in SIZE_HINTS)]
    by_name_width = [
        c for c in cols if any(h in c.lower() for h in WIDTH_HINTS) and c not in by_name_size
    ]

    # What the columns actually hold.
    size_like = []
    for c in cols:
        vals = values(rows, c)
        score, wides, distinct = size_score(vals)
        if score >= 0.6:
            size_like.append((c, score, wides, len(vals), distinct))
    size_like.sort(key=lambda t: (-t[4], -t[1]))

    print(f"\nColumns named like a size: {by_name_size or 'none'}")
    print(f"Columns named like a width: {by_name_width or 'none'}")
    print("\nColumns whose values read as shoe sizes:")
    if not size_like:
        print("  none")
    for c, score, wides, n, distinct in size_like:
        print(f"  - {c}: {score:.0%} of {n} values, {distinct} distinct, "
              f"{wides} carrying a width letter")

    best = size_like[0][0] if size_like else None
    suffix_widths = size_like[0][2] if size_like else 0

    if best:
        print(f"\nMost common values in '{best}':")
        for v, n in Counter(values(rows, best)).most_common(15):
            print(f"  {n:>6}  {v!r}")
        odd = [v for v in values(rows, best) if not SIZE_VALUE.match(v)]
        print(f"  Values that do not parse as a size: {len(odd)}")
        for v, n in Counter(odd).most_common(5):
            print(f"    {n:>6}  {v!r}  (skip these, and count the skips — hazard 2)")
        halves = [v for v in values(rows, best) if HALF_SIZE.match(v)]
        if halves:
            print(f"  NOTE: {len(halves)} sizes written as fractions, e.g. {halves[0]!r} "
                  "— convert before they become page addresses (hazard 3).")

    real_width_col = None
    for c in by_name_width:
        vals = values(rows, c)
        if vals and any(WIDTH_WORDS.search(v) or WIDTH_SUFFIX.match(v) for v in vals[:200]):
            real_width_col = c
            print(f"\nMost common values in '{c}':")
            for v, n in Counter(vals).most_common(10):
                print(f"  {n:>6}  {v!r}")
            print(f"  Rows with no width value: {len(rows) - len(vals)}/{len(rows)} (hazard 2)")

    print("\n--- GATE ---")
    print(f"Structured size values:  {'YES — ' + best if best else 'NO'}")
    if real_width_col:
        print(f"Width readable:          YES — its own column, '{real_width_col}'")
    elif suffix_widths:
        print(f"Width readable:          YES — a width letter on {suffix_widths} size values")
        print("                         Vocabulary is limited to what those letters carry.")
    else:
        print("Width readable:          NO")

    if best and (real_width_col or suffix_widths):
        print("VERDICT: PASS — size and width can both be read from the data.")
    else:
        print("VERDICT: FAIL — width would have to be guessed. Drop this merchant")
        print("         per APPLICATIONS.md rather than patching around it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
