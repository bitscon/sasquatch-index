#!/usr/bin/env python3
"""Reads a Rakuten publisher product catalogue file and speaks the site's column names.

Why this exists: Awin hands the site one feed with named columns
(`product_name`, `custom_2`, `in_stock` …) and every other script in this
repository reads those names. Rakuten hands out a different file entirely —
often pipe-delimited, sometimes with no header row at all, with its own field
names. Rather than teach every script two dialects, this one translates a
Rakuten file into the names the rest of the repository already understands.

What it does NOT do: decide anything. It does not judge freshness, it does not
write site data, it does not know which merchant it is reading. Those stay with
build_catalogue.py and the freshness rule (SASQUATCH_OS.md section 2b), exactly
as they are today.

Two file shapes are handled, because the publisher download has appeared as
both and the site cannot see a real one until a merchant approves us:

  * A file with a header row — columns are matched by name.
  * A headerless pipe-delimited file in Rakuten's long-standing Merchandiser
    field order, optionally wrapped in HDR/TRL marker lines.

Anything it cannot place is reported rather than guessed at. A column this site
needs and the file does not carry is the answer "this merchant's feed cannot
power the site", which is a legitimate outcome — see scripts/feed_check.py.

Run `python3 scripts/rakuten_feed.py --selftest` to exercise both shapes
offline; no network, no credentials, no real feed needed.
"""

import csv
import gzip
import io
import sys
import zipfile
from pathlib import Path

# Rakuten's Merchandiser field order, used only when the file carries no header
# row. Names here are Rakuten's own, lowercased.
MERCHANDISER_ORDER = [
    "productid", "productname", "sku", "primarycategory", "secondarycategory",
    "producturl", "imageurl", "buyurl", "shortdescription", "longdescription",
    "discount", "discounttype", "saleprice", "retailprice", "begindate",
    "enddate", "brand", "shipping", "keywords", "manufacturerpartnumber",
    "manufacturername", "shippinginformation", "availability", "universalid",
    "classid", "currency", "m1", "pixel",
]

# Rakuten field -> the name the rest of this repository reads. Several Rakuten
# names can feed one site name; the first one present wins, in this order.
FIELD_MAP = {
    "product_name": ["productname", "product_name", "name", "title"],
    "aw_deep_link": ["buyurl", "buy_url", "link", "producturl", "product_url"],
    "merchant_image_url": ["imageurl", "image_url", "image", "imagelink"],
    "search_price": ["saleprice", "sale_price", "price", "retailprice"],
    "currency": ["currency", "currencycode", "currency_code"],
    "merchant_category": ["primarycategory", "primary_category", "category",
                          "producttype", "product_type"],
    "custom_3": ["color", "colour", "productcolor"],
    "custom_2": ["size", "shoesize", "shoe_size", "fashion:size"],
    "custom_1": ["sizelabel", "size_label", "sizetype", "size_type"],
    "width": ["width", "shoewidth", "shoe_width", "fashion:width"],
    "availability": ["availability", "instock", "in_stock", "stockstatus",
                     "stock_status"],
}

# Rakuten states availability in words; the site's builder expects a flag it
# recognises as true (build_catalogue.TRUE_WORDS).
IN_STOCK_WORDS = {"in stock", "instock", "in_stock", "available", "1", "true", "yes", "y"}

# Columns the site cannot do without. Everything else is optional enrichment.
REQUIRED = ("product_name", "aw_deep_link")


def _decompress(raw):
    if raw[:2] == b"\x1f\x8b":
        return gzip.decompress(raw)
    if raw[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(raw))
        return z.read(z.namelist()[0])
    return raw


def _strip_markers(lines):
    """Drop Rakuten's HDR/TRL wrapper lines if this file uses them."""
    out = [ln for ln in lines if ln.strip()]
    if out and out[0].split("|", 1)[0].strip().upper() in ("HDR", "HDR1"):
        out = out[1:]
    if out and out[-1].split("|", 1)[0].strip().upper() in ("TRL", "TRL1"):
        out = out[:-1]
    return out


def _norm(name):
    return "".join(ch for ch in str(name).lower() if ch.isalnum() or ch == ":")


def _looks_like_header(fields):
    """A header row is text, not data: no bare URLs, no prices, several words."""
    joined = " ".join(fields).lower()
    if "http" in joined:
        return False
    known = {_norm(f) for f in fields}
    wanted = {"productname", "buyurl", "imageurl", "saleprice", "availability",
              "product_name", "price", "size"}
    return bool(known & {_norm(w) for w in wanted})


def read(path):
    """Return (rows, notes). Rows use this repository's column names."""
    raw = _decompress(Path(path).read_bytes())
    text = raw.decode("utf-8", errors="replace")
    lines = _strip_markers(text.splitlines())
    if not lines:
        return [], ["The file held no data rows."]

    try:
        dialect = csv.Sniffer().sniff("\n".join(lines[:20]), delimiters="|,;\t")
        delim = dialect.delimiter
    except csv.Error:
        delim = "|" if lines[0].count("|") > lines[0].count(",") else ","

    reader = csv.reader(io.StringIO("\n".join(lines)), delimiter=delim)
    records = list(reader)
    if not records:
        return [], ["The file held no data rows."]

    notes = []
    if _looks_like_header(records[0]):
        header = [_norm(c) for c in records[0]]
        body = records[1:]
        notes.append("Read a header row from the file.")
    else:
        header = MERCHANDISER_ORDER[:]
        body = records
        notes.append("No header row; read using Rakuten's Merchandiser field order.")
        if len(records[0]) != len(MERCHANDISER_ORDER):
            notes.append(
                f"Field count is {len(records[0])}, expected "
                f"{len(MERCHANDISER_ORDER)} — columns past the mismatch may be wrong."
            )

    index = {name: i for i, name in enumerate(header)}
    resolved, missing = {}, []
    for site_name, candidates in FIELD_MAP.items():
        for c in candidates:
            if _norm(c) in index:
                resolved[site_name] = index[_norm(c)]
                break
        else:
            missing.append(site_name)

    for name in REQUIRED:
        if name not in resolved:
            notes.append(f"MISSING REQUIRED COLUMN: {name}")
    if missing:
        notes.append("Not present in this file: " + ", ".join(sorted(missing)))

    rows = []
    for rec in body:
        row = {}
        for site_name, i in resolved.items():
            row[site_name] = rec[i].strip() if i < len(rec) else ""
        # The builder tests stock and for-sale separately because Awin states
        # them separately. Rakuten states one availability word, so both site
        # flags are answered from it and nothing is invented.
        avail = row.pop("availability", "").strip().lower()
        flag = "1" if avail in IN_STOCK_WORDS else "0"
        row["in_stock"] = flag
        row["is_for_sale"] = flag
        # The builder only trusts a size column that is labelled as a size.
        if row.get("custom_2") and not row.get("custom_1"):
            row["custom_1"] = "Size"
        row.setdefault("currency", "USD")
        rows.append(row)

    return rows, notes


def _selftest():
    import tempfile

    ok = True
    tmp = Path(tempfile.mkdtemp())

    # Shape one: headerless pipe file in Merchandiser order, HDR/TRL wrapped.
    def merch_row(name, price, avail):
        f = [""] * len(MERCHANDISER_ORDER)
        f[MERCHANDISER_ORDER.index("productname")] = name
        f[MERCHANDISER_ORDER.index("buyurl")] = "https://click.linksynergy.com/x?id=1"
        f[MERCHANDISER_ORDER.index("imageurl")] = "https://img.example/x.jpg"
        f[MERCHANDISER_ORDER.index("saleprice")] = price
        f[MERCHANDISER_ORDER.index("availability")] = avail
        f[MERCHANDISER_ORDER.index("currency")] = "USD"
        f[MERCHANDISER_ORDER.index("primarycategory")] = "Shoes"
        return "|".join(f)

    p1 = tmp / "headerless.txt"
    p1.write_text("\n".join([
        "HDR|Rakuten|20260919",
        merch_row("Mens Work Boot", "129.99", "in stock"),
        merch_row("Mens Dress Shoe", "89.00", "out of stock"),
        "TRL|2",
    ]))
    rows, notes = read(p1)
    if len(rows) != 2:
        print(f"FAIL headerless: expected 2 rows, got {len(rows)}"); ok = False
    elif rows[0]["in_stock"] != "1" or rows[1]["in_stock"] != "0":
        print("FAIL headerless: availability not translated"); ok = False
    elif rows[0]["product_name"] != "Mens Work Boot":
        print("FAIL headerless: product name not mapped"); ok = False
    else:
        print("ok  headerless pipe file, HDR/TRL stripped, availability translated")
    if not any("Merchandiser field order" in n for n in notes):
        print("FAIL headerless: shape not reported"); ok = False

    # Shape two: a file with a header row, including size and width.
    p2 = tmp / "headed.csv"
    p2.write_text(
        "productname,buyurl,imageurl,saleprice,currency,availability,size,width,color\n"
        "Trail Runner,https://click.linksynergy.com/y,https://img/y.jpg,110.00,USD,in stock,14,EE,black\n"
        "Trail Runner,https://click.linksynergy.com/y,https://img/y.jpg,110.00,USD,preorder,15,EE,black\n"
    )
    rows, notes = read(p2)
    if len(rows) != 2:
        print(f"FAIL headed: expected 2 rows, got {len(rows)}"); ok = False
    elif rows[0]["custom_2"] != "14" or rows[0]["custom_1"].lower() != "size":
        print("FAIL headed: size column not presented as a labelled size"); ok = False
    elif rows[0]["in_stock"] != "1" or rows[1]["in_stock"] != "0":
        print("FAIL headed: preorder must not count as in stock"); ok = False
    elif rows[0]["width"] != "EE":
        print("FAIL headed: width not carried through"); ok = False
    else:
        print("ok  header row, size and width carried, preorder excluded")

    # Shape three: gzip, because the download arrives compressed.
    p3 = tmp / "headed.csv.gz"
    p3.write_bytes(gzip.compress(p2.read_bytes()))
    rows, _ = read(p3)
    if len(rows) != 2:
        print("FAIL gzip: compressed file not read"); ok = False
    else:
        print("ok  gzip file read")

    # Shape four: a file missing the link column must say so, not guess.
    p4 = tmp / "nolink.csv"
    p4.write_text("productname,saleprice,availability\nA Shoe,10.00,in stock\n")
    rows, notes = read(p4)
    if not any("MISSING REQUIRED COLUMN: aw_deep_link" in n for n in notes):
        print("FAIL missing-column: a feed with no link column was not reported"); ok = False
    else:
        print("ok  missing link column reported rather than guessed")

    print("SELFTEST PASSED" if ok else "SELFTEST FAILED")
    return 0 if ok else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        return _selftest()
    if len(argv) < 2:
        print("usage: rakuten_feed.py <feed file> | --selftest")
        return 2
    rows, notes = read(argv[1])
    for n in notes:
        print(n)
    print(f"Rows read: {len(rows)}")
    if rows:
        have = [k for k, v in rows[0].items() if v]
        print("Columns carrying data on the first row: " + ", ".join(sorted(have)))
        in_stock = sum(1 for r in rows if r.get("in_stock") == "1")
        print(f"Rows the feed lists as in stock: {in_stock}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
