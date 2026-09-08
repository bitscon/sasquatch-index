#!/usr/bin/env python3
"""Reads one product feed and reports whether it can honestly power this site.

The gate (APPLICATIONS.md): the pages filter by size AND width together, so a
feed needs structured size values and a separate width field. A feed that fails
is dropped, not patched around.

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
WIDTH_WORDS = re.compile(
    r"\b(narrow|medium|wide|extra[ -]?wide|x-?wide|xxw|xw|ww|[2-6]e|eee+|\bd\b|\bb\b|\bm\b)\b",
    re.I,
)
FRACTION = re.compile(r"[/⁄]|\s\d/\d")


def load(path):
    raw = open(path, "rb").read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    elif raw[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(raw))
        raw = z.read(z.namelist()[0])
    text = raw.decode("utf-8", errors="replace")
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;|\t")
    except csv.Error:
        dialect = csv.excel
    return list(csv.DictReader(io.StringIO(text), dialect=dialect))


def matching(cols, hints):
    return [c for c in cols if any(h in c.lower() for h in hints)]


def sample_values(rows, col, limit=15):
    seen = Counter(
        (r.get(col) or "").strip() for r in rows if (r.get(col) or "").strip()
    )
    return seen.most_common(limit)


def main(path):
    rows = load(path)
    if not rows:
        print("VERDICT: FAIL — the feed parsed to zero rows.")
        return 1
    cols = list(rows[0].keys())

    print(f"Rows: {len(rows)}")
    print(f"Columns ({len(cols)}):")
    for c in cols:
        filled = sum(1 for r in rows if (r.get(c) or "").strip())
        print(f"  - {c}  [{filled}/{len(rows)} filled]")

    size_cols = matching(cols, SIZE_HINTS)
    width_cols = [c for c in matching(cols, WIDTH_HINTS) if c not in size_cols]
    print(f"\nSize-ish columns: {size_cols or 'NONE'}")
    print(f"Width-ish columns: {width_cols or 'NONE'}")

    for c in size_cols:
        vals = sample_values(rows, c)
        print(f"\nMost common values in '{c}':")
        for v, n in vals:
            print(f"  {n:>6}  {v!r}")
        joined = " ".join(v for v, _ in vals)
        if WIDTH_WORDS.search(joined):
            print(f"  NOTE: width language appears inside '{c}' values.")
        if FRACTION.search(joined):
            print(f"  NOTE: fractional sizes present in '{c}' (hazard 3: URL safety).")

    for c in width_cols:
        print(f"\nMost common values in '{c}':")
        for v, n in sample_values(rows, c):
            print(f"  {n:>6}  {v!r}")
        missing = sum(1 for r in rows if not (r.get(c) or "").strip())
        print(f"  Rows with no width value: {missing}/{len(rows)} (hazard 2)")

    # The gate itself.
    has_size = bool(size_cols)
    has_width = bool(width_cols) and any(
        sum(1 for r in rows if (r.get(c) or "").strip()) > 0 for c in width_cols
    )
    print("\n--- GATE ---")
    print(f"Structured size field:  {'YES' if has_size else 'NO'}")
    print(f"Separate width field:   {'YES' if has_width else 'NO'}")
    if has_size and has_width:
        print("VERDICT: PASS — this feed can power size-and-width pages.")
        return 0
    print("VERDICT: FAIL — drop this merchant per APPLICATIONS.md, do not patch around it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
