"""Adapter rules (NFR-REL.2, NFR-MAI.1).

Rules
  A1 the free plan sets every capability (yes, no or unknown)
  A2 every capability has a fallback, and the chain ends in a floor action with no loop
  A3 paid and education plans inherit only from free
  A4 last_verified is within 90 days (on main)
  A5 a capability set to yes has an evidence link (https) in notes
  A6 the file name matches the tool (gemini.yaml for tool: gemini)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    REPO_ROOT,
    SCHEMA_DIR,
    Problem,
    current_branch,
    load_yaml,
    normalise_flags,
    parse_date,
    rel,
    today,
    yaml_files,
)

MAX_AGE_DAYS = 90


def vocabulary(root: Path) -> tuple[list[str], set[str]]:
    path = root / SCHEMA_DIR / "adapter.json"
    if not path.exists():
        path = REPO_ROOT / SCHEMA_DIR / "adapter.json"
    defs = json.loads(path.read_text(encoding="utf-8"))["$defs"]
    return list(defs["capability"]["enum"]), set(defs["floor_action"]["enum"])


def check_file(path: Path, root: Path, caps: list[str], floor: set[str],
               strict: bool) -> list[Problem]:
    name = rel(path, root)
    problems: list[Problem] = []

    def add(rule, message, fix):
        problems.append(Problem(name, rule, message, fix))

    try:
        data = normalise_flags(load_yaml(path))
    except Exception:  # reported by check_schemas.py
        return problems
    if not isinstance(data, dict):
        return problems

    tool = data.get("tool")
    if tool and path.stem != tool:
        add("A6 name", f"file is {path.name} but tool is '{tool}'", f"Rename to {tool}.yaml.")

    plans = data.get("plans") or {}
    free = plans.get("free") or {}
    for cap in caps:
        if cap not in free:
            add("A1 free plan", f"plans.free does not set '{cap}'",
                f"Add '{cap}: unknown' until the spike records a result.")

    for plan_name, plan in plans.items():
        if plan_name == "free" or not isinstance(plan, dict):
            continue
        if plan.get("inherits") != "free":
            add("A3 inherits", f"plans.{plan_name} inherits from '{plan.get('inherits')}'",
                "Plans may only inherit from free: set 'inherits: free'.")

    fallbacks = data.get("fallbacks") or {}
    for cap in caps:
        seen = [cap]
        current = fallbacks.get(cap)
        if current is None:
            add("A2 fallback", f"'{cap}' has no fallback",
                "Add a fallback: another capability or a floor action.")
            continue
        while current not in floor:
            if current in seen:
                add("A2 fallback", f"fallback loop: {' -> '.join(seen + [current])}",
                    "End the chain in a floor action such as text_cards or status_link.")
                break
            seen.append(current)
            nxt = fallbacks.get(current)
            if nxt is None:
                add("A2 fallback", f"chain {' -> '.join(seen)} does not reach a floor action",
                    f"Give '{current}' a fallback.")
                break
            current = nxt

    notes = data.get("notes") or {}
    yes_caps = sorted({c for p in plans.values() if isinstance(p, dict)
                       for c, v in p.items() if v == "yes"})
    for cap in yes_caps:
        if "https://" not in str(notes.get(cap, "")):
            add("A5 evidence", f"'{cap}' is yes without an evidence link",
                f"Add notes.{cap} with a link to the spike result, or set it to unknown.")

    verified = parse_date(data.get("last_verified"))
    if strict and verified and (today() - verified).days > MAX_AGE_DAYS:
        add("A4 freshness", f"last_verified {verified} is over {MAX_AGE_DAYS} days old",
            "Re-run the spike tests for this tool and update the flags.")
    return problems


def check(root: Path = REPO_ROOT) -> list[Problem]:
    caps, floor = vocabulary(root)
    strict = current_branch(root) == "main"
    problems: list[Problem] = []
    for path in yaml_files(root, "skill/reference/adapters"):
        problems.extend(check_file(path, root, caps, floor, strict))
    return problems


def main() -> int:
    problems = check()
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
