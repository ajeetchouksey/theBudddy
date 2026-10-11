"""List pack entries, tasks and letters that expire within N days, grouped by layer.

Used by the weekly freshness.yml workflow, which opens or updates one issue per layer.

  python scripts/freshness.py --days 30            # JSON to stdout
  python scripts/freshness.py --days 30 --markdown
  python scripts/freshness.py --days 30 --issues   # {layer: issue body, "" if all fresh}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import fact_diff  # noqa: E402
from check_content import DEFAULT_EXPIRY_MONTHS  # noqa: E402
from common import (  # noqa: E402
    LAYER_DIRS,
    PLACES,
    REPO_ROOT,
    add_months,
    load_yaml,
    parse_date,
    rel,
    stringify_dates,
    today,
    yaml_files,
)


def expiring(root: Path, days: int) -> dict[str, list[dict]]:
    now = today()
    result: dict[str, list[dict]] = {layer: [] for layer in LAYER_DIRS.values()}
    for path in yaml_files(root, "knowledge"):
        if path == root / PLACES:
            continue
        parts = path.relative_to(root / "knowledge").parts
        if not parts or parts[0] not in LAYER_DIRS:
            continue
        layer = LAYER_DIRS[parts[0]]
        try:
            data = stringify_dates(load_yaml(path))
        except Exception:  # reported by validate
            continue
        for item_id, item in fact_diff.items(data).items():
            verified = parse_date(item.get("last_verified"))
            if verified is None:
                continue
            expires = parse_date(item.get("expires")) or add_months(verified,
                                                                    DEFAULT_EXPIRY_MONTHS)
            left = (expires - now).days
            if left <= days:
                result[layer].append({
                    "id": item_id, "path": rel(path, root), "expires": expires.isoformat(),
                    "days_left": left, "source_url": item.get("source_url", ""),
                })
    for items in result.values():
        items.sort(key=lambda i: (i["expires"], i["id"]))
    return result


def markdown(layer: str, items: list[dict]) -> str:
    lines = [
        f"These **{layer}** pack entries expire soon or have expired. "
        "Expired entries block the next release.",
        "",
        "For each one: open the source. If it is unchanged, bump `last_verified` in a PR. "
        "If it changed, hand it to `pack-author`. If the page is gone, propose retiring "
        "the entry. Never bump a date without opening the source.",
        "",
        "| Entry | Expires | Days left | Source | File |",
        "| --- | --- | --- | --- | --- |",
    ]
    for i in items:
        lines.append(f"| `{i['id']}` | {i['expires']} | {i['days_left']} | {i['source_url']} "
                     f"| `{i['path']}` |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=30)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--markdown", action="store_true")
    mode.add_argument("--issues", action="store_true")
    parser.add_argument("--root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    result = expiring(Path(args.root), args.days)
    if args.issues:
        bodies = {layer: markdown(layer, items) if items else ""
                  for layer, items in result.items()}
        print(json.dumps(bodies, indent=2, sort_keys=True))
    elif args.markdown:
        for layer, items in result.items():
            if items:
                print(f"## {layer}\n\n{markdown(layer, items)}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
