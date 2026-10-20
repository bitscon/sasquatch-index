"""Offline tests for scripts/impact_catalogue.py.

Every answer below is canned JSON shaped like Impact's documented Partner API
responses (the paging envelope, the Catalog and Item models), handed to the
importer in place of the network. Nothing here touches the network.

Run: python3 -m unittest tests/test_impact_catalogue.py
"""

import email.message
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import impact_catalogue as ic  # noqa: E402

try:
    import yaml  # only the tests use it; the importer is stdlib-only
except ImportError:  # pragma: no cover
    yaml = None

SID = "IRtestSID123"
TOKEN = "secret-token-value"
ENV = {"IMPACT_ACCOUNT_SID": SID, "IMPACT_AUTH_TOKEN": TOKEN}
NOW = datetime(2026, 10, 19, 12, 0, 0, tzinfo=timezone.utc)
BASE = f"/Mediapartners/{SID}/"


def envelope(key, records, page=1, numpages=1, nextpage=""):
    return {
        "@page": str(page), "@numpages": str(numpages), "@pagesize": "1000",
        "@total": str(len(records)), "@start": "0", "@end": str(len(records)),
        "@uri": "/Mediapartners/x", "@firstpageuri": "", "@previouspageuri": "",
        "@nextpageuri": nextpage, "@lastpageuri": "", key: records,
    }


def catalog(cid, updated, name=None, campaign="Big Feet Outfitters"):
    return {
        "Id": str(cid), "Name": name or f"Catalog {cid}", "Language": "en",
        "AdvertiserId": "999", "AdvertiserName": campaign + " Inc",
        "AdvertiserLocation": "US", "CampaignId": "111", "CampaignName": campaign,
        "NumberOfItems": "10", "DateLastUpdated": updated, "Locations": ["US"],
        "Currency": "USD", "ItemsUri": f"/Mediapartners/{SID}/Catalogs/{cid}/Items",
        "Uri": f"/Mediapartners/{SID}/Catalogs/{cid}",
    }


def item(sku, size, price="99.99", parent="PARENT-1", name="Men's Waterproof Running Shoe",
         stock="InStock", gender="Male", age="Adult", colors=("Black",), currency="USD", **extra):
    d = {
        "Id": f"1-{sku}", "CatalogId": "1", "CampaignId": "111",
        "CampaignName": "Big Feet Outfitters", "CatalogItemId": sku,
        "Name": name, "Description": "", "Manufacturer": "Trailco",
        "Url": f"https://bigfeet.sjv.io/c/1/2/3?u=item-{sku}",
        "ImageUrl": "https://img.example.com/shoe one.jpg",
        "CurrentPrice": price, "OriginalPrice": price, "Currency": currency,
        "StockAvailability": stock, "Category": "Shoes > Running",
        "ParentName": "", "ParentSku": parent, "IsParent": False, "ItemGroupId": "",
        "Colors": list(colors), "Size": size, "Gender": gender, "AgeGroup": age,
    }
    d.update(extra)
    return d


class FakeAPI:
    """Answers fetch_json(path) from a dict of path -> JSON body."""

    def __init__(self, answers):
        self.answers = answers
        self.calls = []

    def __call__(self, path):
        self.calls.append(path)
        if path not in self.answers:
            raise AssertionError(f"unexpected call {path}")
        return json.loads(json.dumps(self.answers[path]))


def run(answers, env=ENV):
    d = tempfile.mkdtemp()
    api = FakeAPI(answers)
    out = io.StringIO()
    with redirect_stdout(out):
        rc = ic.main(d, env=env, fetch_json=api, now=NOW)
    return rc, Path(d), api, out.getvalue()


def load(p):
    text = p.read_text()
    if yaml:
        return yaml.safe_load(text)
    return text


FRESH = "2026-10-10T08:00:00-07:00"
STALE = "2026-08-01T00:00:00Z"


def one_catalog(items, updated=FRESH):
    return {
        BASE + "Catalogs?PageSize=1000": envelope("Catalogs", [catalog(1, updated)]),
        BASE + "Catalogs/1/Items?PageSize=1000": envelope("Items", items),
    }


class NoCredentials(unittest.TestCase):
    def test_skips_and_writes_nothing(self):
        for env in ({}, {"IMPACT_ACCOUNT_SID": SID}, {"IMPACT_AUTH_TOKEN": TOKEN}):
            rc, d, api, out = run({}, env=env)
            self.assertEqual(rc, 0)
            self.assertIn("Impact not configured — skipped", out)
            self.assertEqual(list(d.iterdir()), [])
            self.assertEqual(api.calls, [])


class Freshness(unittest.TestCase):
    def test_stale_and_unknown_catalogs_dropped_without_reading_items(self):
        answers = {
            BASE + "Catalogs?PageSize=1000": envelope("Catalogs", [
                catalog(1, FRESH), catalog(2, STALE), catalog(3, ""), catalog(4, "not a date")]),
            BASE + "Catalogs/1/Items?PageSize=1000": envelope("Items", [item("A", "14")]),
        }
        rc, d, api, out = run(answers)
        self.assertEqual(rc, 0)
        self.assertNotIn(BASE + "Catalogs/2/Items?PageSize=1000", api.calls)
        r = load(d / "impact_run.yaml")
        if yaml:
            statuses = [c["status"] for c in r["catalogs"]]
            self.assertEqual(statuses, ["fresh", "stale", "unknown", "unknown"])
            self.assertEqual(r["catalogs_seen"], 4)
            self.assertEqual(r["catalogs"][0]["age_days"], 8)
            self.assertEqual(r["catalogs"][0]["date_last_updated"], "2026-10-10T15:00:00Z")
            self.assertEqual(r["catalogs"][1]["items_read"], 0)
            self.assertEqual(r["max_feed_age_days"], 30)
            p = load(d / "impact_products.yaml")
            self.assertEqual(len(p["products"]), 1)
            self.assertEqual(p["products"][0]["feed_updated"], "2026-10-10T15:00:00Z")

    def test_uses_build_catalogue_window(self):
        import build_catalogue
        self.assertIs(ic.MAX_FEED_AGE_DAYS, build_catalogue.MAX_FEED_AGE_DAYS)


class ItemFilters(unittest.TestCase):
    def test_stock_gender_kids_currency(self):
        items = [
            item("ok", "14"),
            item("oos", "14", stock="OutOfStock"),
            item("pre", "14", stock="PreOrder"),
            item("w", "14", gender="Female", name="Women's Trail Runner"),
            item("wname", "14", gender="Unisex", name="Women's Trail Runner"),
            item("kid", "14", age="Kids"),
            item("kidname", "14", name="Boys Trail Runner"),
            item("blank", "14", gender="", name="Trail Runner"),
            item("blankmen", "15", gender="", name="Men's Trail Runner", parent="P2"),
            item("uni", "14", gender="Unisex", name="Classic Clog", parent="P3"),
            item("cad", "14", currency="CAD"),
            item("noprice", "14", price=""),
            item("small", "12"),
            item("par", "", IsParent=True),
        ]
        rc, d, api, out = run(one_catalog(items))
        r = load(d / "impact_run.yaml")
        if yaml:
            s = r["skipped"]
            self.assertEqual(s["out_of_stock_or_not_for_sale"], 2)
            self.assertEqual(s["womens"], 2)
            self.assertEqual(s["kids_size_scale"], 2)
            self.assertEqual(s["gender_not_stated"], 1)
            self.assertEqual(s["not_usd"], 1)
            self.assertEqual(s["no_price"], 1)
            self.assertEqual(s["below_size_13"], 1)
            self.assertEqual(s["parent_record"], 1)
            styles = load(d / "impact_products.yaml")["products"]
            self.assertEqual(len(styles), 3)
            self.assertEqual(r["catalogs"][0]["items_read"], len(items))


class Sizes(unittest.TestCase):
    CASES = {
        "13": (13, "standard"), "13.5": (13.5, "standard"), "13.0": (13, "standard"),
        "14 W": (14, "wide"), "15 Wide": (15, "wide"), "14 2E": (14, "wide"),
        "14 4E": (14, "extra-wide"), "15 EE": (15, "wide"), "13 D": (13, "standard"),
        "13 D(M)": (13, "standard"), "13 D (M)": (13, "standard"),
        "16 XW": (16, "extra-wide"), "13 M US": (13, "standard"),
        "US 14": (14, "standard"), "14W": (14, "wide"), "15 EEEE": (15, "extra-wide"),
        "15 6E": (15, "extra-wide"), "15 Extra Wide": (15, "extra-wide"),
        "13 Medium": (13, "standard"), "15 1/2": (15.5, "standard"),
        "M13": (13, "standard"), "Men's 14": (14, "standard"),
    }
    REJECTS = {
        "13/14": "dual_sized_row", "M13 W14.5": "dual_sized_row",
        "13 - 14": "dual_sized_row", "": "no_size", "XL": "unparseable_size",
        "14 B": "unexpected_width_marking", "14 3E": "unexpected_width_marking",
        "13.25": "unexpected_width_marking",
    }

    def test_every_form(self):
        for raw, want in self.CASES.items():
            with self.subTest(raw=raw):
                self.assertEqual(ic.parse_size(raw), want)
        for raw, want in self.REJECTS.items():
            with self.subTest(raw=raw):
                self.assertEqual(ic.parse_size(raw), want)

    def test_sizes_are_url_safe(self):
        for raw in self.CASES:
            size, _ = ic.parse_size(raw)
            self.assertRegex(str(size), r"^\d{1,2}(\.5)?$")

    def test_dual_size_counted_in_run(self):
        rc, d, api, out = run(one_catalog([item("a", "13/14"), item("b", "M13 W14.5"), item("c", "14")]))
        if yaml:
            self.assertEqual(load(d / "impact_run.yaml")["skipped"]["dual_sized_row"], 2)


class Grouping(unittest.TestCase):
    def test_grouping_price_span_and_record_shape(self):
        items = [
            item("a13", "13", price="89.99", colors=("Black",)),
            item("a14w", "14 W", price="94.50", colors=("Black",)),
            item("a15", "15 4E", price="$119.00", colors=("Grey", "Black")),
            item("b14", "14", parent="", ItemGroupId="GRP-9", name="Men's Steel Toe Work Boot",
                 Manufacturer="Bootco", price="150"),
            item("c14", "14", parent="", name="Men's Plain Slip On", Manufacturer=""),
        ]
        rc, d, api, out = run(one_catalog(items))
        self.assertEqual(rc, 0)
        if not yaml:
            return
        products = load(d / "impact_products.yaml")["products"]
        self.assertEqual(len(products), 3)
        by = {p["style_name"]: p for p in products}
        a = by["Men's Waterproof Running Shoe"]
        self.assertEqual(a["sizes"], [13, 14, 15])
        self.assertEqual(a["widths"], ["extra-wide", "standard", "wide"])
        self.assertEqual(a["price_min"], 89.99)
        self.assertEqual(a["price_max"], 119.0)
        self.assertEqual(a["colours"], 2)
        self.assertEqual(a["attributes"], ["waterproof"])
        self.assertEqual(a["category"], "running shoes")
        self.assertEqual(a["brand"], "Trailco")
        self.assertEqual(a["retailer"], "Big Feet Outfitters")
        self.assertEqual(a["currency"], "USD")
        self.assertEqual(a["image"], "https://img.example.com/shoe%20one.jpg")
        self.assertTrue(a["link"].startswith("https://bigfeet.sjv.io/"))
        b = by["Men's Steel Toe Work Boot"]
        self.assertEqual((b["category"], b["family"]), ("work boots", "boots"))
        self.assertIn("steel-toe", b["attributes"])
        self.assertEqual(by["Men's Plain Slip On"]["brand"], "Big Feet Outfitters Inc")
        # Same keys, same order as data/products.yaml, plus feed_updated.
        want = ["product_type", "brand", "style_name", "category", "family", "sizes",
                "widths", "attributes", "price_min", "price_max", "currency", "colours",
                "retailer", "link", "image", "fit_notes", "feed_updated"]
        self.assertEqual(list(a.keys()), want)


class Paging(unittest.TestCase):
    def test_follows_nextpageuri_then_numpages(self):
        nxt = f"/Mediapartners/{SID}/Catalogs/1/Items?PageSize=1000&Page=2"
        answers = {
            BASE + "Catalogs?PageSize=1000": envelope("Catalogs", [catalog(1, FRESH)]),
            BASE + "Catalogs/1/Items?PageSize=1000": envelope("Items", [item("a", "13")], 1, 3, nxt),
            nxt: envelope("Items", [item("b", "14")], 2, 3, ""),
            # No next-page address on page 2, but @numpages says there is a third.
            BASE + "Catalogs/1/Items?PageSize=1000&Page=3": envelope("Items", [item("c", "15")], 3, 3, ""),
        }
        rc, d, api, out = run(answers)
        self.assertEqual(len(api.calls), 4)
        if yaml:
            self.assertEqual(load(d / "impact_run.yaml")["catalogs"][0]["items_read"], 3)
            self.assertEqual(load(d / "impact_products.yaml")["products"][0]["sizes"], [13, 14, 15])

    def test_refuses_next_page_off_the_api(self):
        answers = {
            BASE + "Catalogs?PageSize=1000": envelope("Catalogs", [catalog(1, FRESH)]),
            BASE + "Catalogs/1/Items?PageSize=1000": envelope(
                "Items", [item("a", "13")], 1, 2, "https://evil.example.com/steal"),
        }
        rc, d, api, out = run(answers)
        if yaml:
            self.assertEqual(load(d / "impact_run.yaml")["catalogs"][0]["status"], "error")


class Output(unittest.TestCase):
    def test_yaml_parses_including_awkward_values(self):
        items = [
            item("a", "14", name='[Limited] "Yes": Boot #1', parent="X"),
            item("b", "14", name="yes", parent="Y", Manufacturer="1234"),
        ]
        rc, d, api, out = run(one_catalog(items))
        for f in ("impact_products.yaml", "impact_run.yaml"):
            text = (d / f).read_text()
            self.assertNotIn(TOKEN, text)
            if yaml:
                self.assertIsInstance(yaml.safe_load(text), dict)
            else:
                self.assertTrue(text.endswith("\n"))
        self.assertIn("NOT read by the site yet", (d / "impact_products.yaml").read_text())
        if yaml:
            names = sorted(p["style_name"] for p in load(d / "impact_products.yaml")["products"])
            self.assertEqual(names, ['[Limited] "Yes": Boot #1', "yes"])
            self.assertIn("1234", [p["brand"] for p in load(d / "impact_products.yaml")["products"]])
        self.assertNotIn(TOKEN, out)
        self.assertNotIn(SID, out)

    def test_empty_account_writes_marker(self):
        rc, d, api, out = run({BASE + "Catalogs?PageSize=1000": envelope("Catalogs", [])})
        self.assertEqual(rc, 0)
        if yaml:
            self.assertEqual(load(d / "impact_products.yaml"), {"products": []})
            r = load(d / "impact_run.yaml")
            self.assertEqual((r["catalogs_seen"], r["catalogs"], r["skipped"]), (0, [], {}))

    def test_catalog_list_failure_records_error_and_keeps_old_records(self):
        def boom(path):
            raise ic.ImpactError("HTTP 401")
        d = tempfile.mkdtemp()
        Path(d, "impact_products.yaml").write_text("products: []\n# previous\n")
        with redirect_stdout(io.StringIO()):
            rc = ic.main(d, env=ENV, fetch_json=boom, now=NOW)
        self.assertEqual(rc, 1)
        self.assertIn("# previous", Path(d, "impact_products.yaml").read_text())
        self.assertIn("could not list catalogs: HTTP 401", Path(d, "impact_run.yaml").read_text())


class RealFetch(unittest.TestCase):
    """The one network function, with urlopen replaced."""

    def _resp(self, body):
        r = mock.MagicMock()
        r.read.return_value = json.dumps(body).encode()
        r.__enter__.return_value = r
        return r

    def test_auth_header_and_429_wait(self):
        hdrs = email.message.Message()
        hdrs["Retry-After"] = "2"
        err = urllib.error.HTTPError("https://api.impact.com/x", 429, "Too Many", hdrs, None)
        slept = []
        seen = []

        def fake_urlopen(req, timeout):
            seen.append(req)
            if len(seen) == 1:
                raise err
            return self._resp({"ok": True})

        fetch = ic.make_fetch(SID, TOKEN, sleep=slept.append)
        with mock.patch("urllib.request.urlopen", fake_urlopen), redirect_stdout(io.StringIO()):
            self.assertEqual(fetch(BASE + "Catalogs"), {"ok": True})
        self.assertEqual(slept, [3])
        self.assertEqual(seen[0].get_header("Accept"), "application/json")
        self.assertTrue(seen[0].get_header("Authorization").startswith("Basic "))
        self.assertEqual(seen[0].full_url, "https://api.impact.com" + BASE + "Catalogs")

    def test_long_rate_limit_gives_up_and_errors_hide_address(self):
        hdrs = email.message.Message()
        hdrs["RateLimit-Reset"] = "3000"
        err = urllib.error.HTTPError("https://api.impact.com/x", 429, "Too Many", hdrs, None)
        fetch = ic.make_fetch(SID, TOKEN, sleep=lambda s: self.fail("should not wait an hour"))
        with mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(ic.RateLimited):
                fetch(BASE + "Catalogs")
        err401 = urllib.error.HTTPError("https://api.impact.com/x", 401, "Unauthorized", hdrs, None)
        with mock.patch("urllib.request.urlopen", side_effect=err401):
            with self.assertRaises(ic.ImpactError) as cm:
                fetch(BASE + "Catalogs")
        self.assertEqual(str(cm.exception), "HTTP 401")

    def test_refuses_paths_outside_the_api(self):
        fetch = ic.make_fetch(SID, TOKEN)
        with self.assertRaises(ic.ImpactError):
            fetch("//evil.example.com/x")


if __name__ == "__main__":
    unittest.main()
