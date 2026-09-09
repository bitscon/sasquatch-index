#!/usr/bin/env python3
"""Checks that every affiliate link currently in data/products.yaml resolves.

Phase 4 (SASQUATCH_OS.md section 8): the scheduled job has to verify links,
not just publish them blind. Reads data/products.yaml by line — the file is
machine-written by build_catalogue.py in a fixed, single-field-per-line
format (see dump_products there), so a small line parser here is enough and
avoids adding a YAML dependency this project doesn't otherwise carry.

A broken link is reported, never fatal — a merchant-side outage on one
product shouldn't block an otherwise-good catalogue rebuild. Prints a
summary to stdout and writes the same summary to link_check_result.txt for
the workflow's report step to fold into the run report. Writes nothing
under data/ and is never committed.
"""

import sys
import urllib.error
import urllib.request
from pathlib import Path

TIMEOUT = 15
USER_AGENT = "sasquatch-index-linkcheck/1.0"


def read_products(path):
    """Yields (style_name, link) pairs in file order."""
    style = None
    for line in Path(path).read_text().splitlines():
        if line.startswith("    style_name: "):
            style = _unquote(line[len("    style_name: "):])
        elif line.startswith("    link: "):
            yield style, _unquote(line[len("    link: "):])


def _unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return s


def _request(url, method):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status


def check(url):
    """Returns an HTTP status code, or None if the request never got one."""
    try:
        return _request(url, "HEAD")
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            # Some servers reject HEAD outright — retry with GET before
            # calling the link broken.
            try:
                return _request(url, "GET")
            except urllib.error.HTTPError as e2:
                return e2.code
            except Exception:
                return None
        return e.code
    except Exception:
        return None


def main(products_path):
    results = [(style, link, check(link)) for style, link in read_products(products_path)]
    broken = [(style, link, status) for style, link, status in results
              if status is None or not (200 <= status < 400)]

    lines = [f"{len(results)} checked, {len(broken)} broken"]
    for style, link, status in broken:
        lines.append(f"- BROKEN ({status}): {style}")
    summary = "\n".join(lines) + "\n"

    print(summary, end="")
    Path("link_check_result.txt").write_text(summary)
    return 0  # a dead link is reported, not a build failure


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data/products.yaml"))
