"""Check that source_url links of added or changed facts still work (validate.yml).

  python scripts/check_links.py --base origin/main    # only facts changed since base
  python scripts/check_links.py --all                 # every source_url in knowledge/

Results: 2xx/3xx ok. 404 and 410, DNS and connection errors fail. 401, 403, 405, 429 and
5xx only warn: some official sites block automated requests, so a human checks those.
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import fact_diff  # noqa: E402
from common import PLACES, REPO_ROOT, load_yaml, stringify_dates, yaml_files  # noqa: E402

USER_AGENT = "theBudddy-link-check/1.0 (+https://github.com/ajeetchouksey/theBudddy)"
FAIL_STATUSES = {404, 410}
TIMEOUT = 20
ATTEMPTS = 2


def collect_all(root: Path) -> dict[str, list[str]]:
    urls: dict[str, list[str]] = {}
    for path in yaml_files(root, "knowledge"):
        if path == root / PLACES:
            continue
        data = stringify_dates(load_yaml(path))
        for item_id, item in fact_diff.items(data).items():
            if isinstance(item.get("source_url"), str):
                urls.setdefault(item["source_url"], []).append(item_id)
    return urls


def collect_changed(root: Path, base: str) -> dict[str, list[str]]:
    urls: dict[str, list[str]] = {}
    for change in fact_diff.diff(root, base):
        if change.kind == "removed" or not change.new:
            continue
        url = change.new.get("source_url")
        if isinstance(url, str):
            urls.setdefault(url, []).append(change.item_id)
    return urls


def probe(url: str, opener=urllib.request.urlopen) -> tuple[str, str]:
    """Return (result, detail) where result is ok, warn or fail."""
    last = ""
    for attempt in range(ATTEMPTS):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with opener(request, timeout=TIMEOUT) as response:
                return "ok", str(response.status)
        except urllib.error.HTTPError as exc:
            if exc.code in FAIL_STATUSES:
                return "fail", f"HTTP {exc.code}"
            last = f"HTTP {exc.code}"
            if exc.code < 500 and exc.code != 429:
                return "warn", last
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = f"{type(exc).__name__}: {getattr(exc, 'reason', exc)}"
        if attempt + 1 < ATTEMPTS:
            time.sleep(2)
    if last.startswith("HTTP"):
        return "warn", last
    return "fail", last


def run(urls: dict[str, list[str]], opener=urllib.request.urlopen) -> int:
    if not urls:
        print("links: no source_url to check")
        return 0
    failed = 0
    for url in sorted(urls):
        result, detail = probe(url, opener)
        ids = ", ".join(sorted(urls[url]))
        print(f"{result:4}  {detail:12}  {url}  [{ids}]")
        failed += result == "fail"
    print(f"links: {len(urls)} checked, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--base")
    group.add_argument("--all", action="store_true")
    parser.add_argument("--root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    root = Path(args.root)
    urls = collect_all(root) if args.all or not args.base else collect_changed(root, args.base)
    return run(urls)


if __name__ == "__main__":
    sys.exit(main())
