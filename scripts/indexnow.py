#!/usr/bin/env python3
"""Notify Bing (and other IndexNow engines) of new or changed pages.

  python scripts/indexnow.py diff     # in the build job, before deploy: compares dist/ with the
                                      # live site, writes indexnow-urls.txt (INDEXNOW_ALL=true: every URL)
  python scripts/indexnow.py submit   # after deploy: sends indexnow-urls.txt to IndexNow
  python scripts/indexnow.py all      # after deploy: sends every sitemap URL (first run, or by hand)

The key file (static/<key>.txt) proves ownership; IndexNow fetches it from the site.
"""
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
LIST = ROOT / "indexnow-urls.txt"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
BASE = CFG["base_url"].rstrip("/")
HOST = BASE.split("://", 1)[1]
KEY = next(p.stem for p in (ROOT / "static").glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem))


def sitemap_urls():
    return re.findall(r"<loc>([^<]+)</loc>", (DIST / "sitemap.xml").read_text(encoding="utf-8"))


def local_file(url):
    path = url[len(BASE):].lstrip("/")
    return DIST / (path + "index.html" if path == "" or path.endswith("/") else path)


def live_bytes(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        return None if exc.code == 404 else b""
    except Exception:
        return b""  # unreachable: treat as changed, resubmitting is harmless


def diff():
    if os.environ.get("INDEXNOW_ALL") == "true":
        changed = sitemap_urls()
    else:
        changed = [u for u in sitemap_urls() if live_bytes(u) != local_file(u).read_bytes()]
    LIST.write_text("\n".join(changed) + ("\n" if changed else ""), encoding="utf-8")
    print(f"{len(changed)} new or changed page(s)")
    for u in changed:
        print("  ", u)


def submit(urls):
    if not urls:
        print("Nothing to submit.")
        return 0
    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"{BASE}/{KEY}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow: HTTP {resp.status}, {len(urls)} URL(s) submitted")
    except urllib.error.HTTPError as exc:
        # 422/403 = key or host problem: report but never fail the deployment for it
        print(f"IndexNow refused: HTTP {exc.code} {exc.read()[:200]!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "submit"
    if mode == "diff":
        diff()
    elif mode == "all":
        sys.exit(submit(sitemap_urls()))
    else:
        sys.exit(submit([u for u in LIST.read_text(encoding="utf-8").split() if u]) if LIST.exists() else 0)
