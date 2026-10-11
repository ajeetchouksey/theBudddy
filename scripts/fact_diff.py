"""Report fact changes between a base ref and HEAD (PR comment in validate.yml).

Lists, per pack entry, task or letter under knowledge/: added, removed, and changed fields
with old -> new values. The id is the match key.

  python scripts/fact_diff.py --base origin/main            # Markdown to stdout
  python scripts/fact_diff.py --base origin/main --out f.md
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PLACES, REPO_ROOT, stringify_dates  # noqa: E402

MARKER = "<!-- fact-diff -->"
MAX_VALUE = 160
MAX_BODY = 60000


@dataclass
class Change:
    path: str
    item_id: str
    kind: str  # added | removed | changed
    fields: dict[str, tuple[object, object]] = field(default_factory=dict)
    new: dict | None = None


def git(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def changed_paths(root: Path, base: str) -> list[str]:
    out = git(root, "diff", "--name-only", "--no-renames", f"{base}...HEAD", "--", "knowledge")
    return sorted(p for p in out.splitlines()
                  if p.endswith((".yaml", ".yml")) and p != PLACES.as_posix())


def load_at(root: Path, ref: str | None, path: str):
    if ref is None:
        target = root / path
        text = target.read_text(encoding="utf-8") if target.is_file() else None
    else:
        result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=root,
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        text = result.stdout if result.returncode == 0 else None
    if text is None:
        return None
    try:
        return stringify_dates(yaml.safe_load(text))
    except yaml.YAMLError:
        return None


def items(data) -> dict[str, dict]:
    if not isinstance(data, dict):
        return {}
    if isinstance(data.get("id"), str) and "senders" in data:  # letter file
        return {data["id"]: data}
    found = {}
    for entry in data.get("entries") or []:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            found[entry["id"]] = entry
    for task in data.get("tasks") or []:
        if isinstance(task, dict) and isinstance(task.get("task_id"), str):
            found[task["task_id"]] = task
    return found


def diff(root: Path, base: str) -> list[Change]:
    changes: list[Change] = []
    for path in changed_paths(root, base):
        old = items(load_at(root, base, path))
        new = items(load_at(root, None, path))
        for item_id in sorted(set(old) | set(new)):
            if item_id not in old:
                changes.append(Change(path, item_id, "added", new=new[item_id]))
            elif item_id not in new:
                changes.append(Change(path, item_id, "removed"))
            elif old[item_id] != new[item_id]:
                keys = sorted(set(old[item_id]) | set(new[item_id]))
                fields = {k: (old[item_id].get(k), new[item_id].get(k)) for k in keys
                          if old[item_id].get(k) != new[item_id].get(k)}
                changes.append(Change(path, item_id, "changed", fields, new[item_id]))
    return changes


def short(value) -> str:
    text = "—" if value is None else " ".join(str(value).split())
    text = text.replace("|", "\\|")
    return text if len(text) <= MAX_VALUE else text[: MAX_VALUE - 1] + "…"


def render(changes: list[Change]) -> str:
    lines = [MARKER, "## Fact diff", ""]
    if not changes:
        lines.append("No pack entries changed.")
        return "\n".join(lines) + "\n"
    counts = {k: sum(1 for c in changes if c.kind == k) for k in ("added", "changed", "removed")}
    lines.append(f"{counts['added']} added · {counts['changed']} changed · "
                 f"{counts['removed']} removed. Reviewers: open each source and confirm.")
    lines.append("")
    for change in changes:
        lines.append(f"### {change.kind}: `{change.item_id}`")
        lines.append(f"`{change.path}`")
        lines.append("")
        if change.kind == "added":
            for key in ("text", "title", "meaning", "source_url", "last_verified", "reviewer"):
                if change.new and key in change.new:
                    lines.append(f"- **{key}:** {short(change.new[key])}")
        elif change.kind == "changed":
            lines += ["| Field | Old | New |", "| --- | --- | --- |"]
            for key, (old, new) in change.fields.items():
                lines.append(f"| {key} | {short(old)} | {short(new)} |")
        lines.append("")
    body = "\n".join(lines).rstrip() + "\n"
    if len(body) > MAX_BODY:
        body = body[:MAX_BODY] + "\n\n…truncated; run scripts/fact_diff.py locally.\n"
    return body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--out")
    parser.add_argument("--root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    body = render(diff(Path(args.root), args.base))
    if args.out:
        Path(args.out).write_text(body, encoding="utf-8", newline="\n")
    else:
        print(body, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
