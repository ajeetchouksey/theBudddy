"""Validate packs, letters, adapters, eval cases and latest.json against knowledge/_schema/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    PLACES,
    REPO_ROOT,
    SCHEMA_DIR,
    Problem,
    load_yaml,
    normalise_flags,
    rel,
    stringify_dates,
    yaml_files,
)

SCHEMA_FOR = {
    "fact": "fact.json",
    "letter": "letter.json",
    "adapter": "adapter.json",
    "eval": "eval-case.json",
    "latest": "latest.json",
    "places": "places.json",
}


def load_validator(root: Path, name: str) -> Draft202012Validator:
    path = root / SCHEMA_DIR / SCHEMA_FOR[name]
    if not path.exists():  # fixtures reuse the real schemas
        path = REPO_ROOT / SCHEMA_DIR / SCHEMA_FOR[name]
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def targets(root: Path) -> list[tuple[Path, str]]:
    found: list[tuple[Path, str]] = []
    for path in yaml_files(root, "knowledge"):
        if path == root / PLACES:
            kind = "places"
        elif "letters" in path.parts:
            kind = "letter"
        else:
            kind = "fact"
        found.append((path, kind))
    for path in yaml_files(root, "skill/reference/adapters"):
        found.append((path, "adapter"))
    for path in yaml_files(root, "evals/cases"):
        found.append((path, "eval"))
    for candidate in ("site/latest.json", "build/latest.json"):
        if (root / candidate).is_file():
            found.append((root / candidate, "latest"))
    return found


def _location(error) -> str:
    return "/".join(str(p) for p in error.absolute_path) or "(top level)"


def _entry_id(data, error) -> str:
    """Best effort: name the entry or case the error sits in."""
    path = list(error.absolute_path)
    if len(path) >= 2 and isinstance(data, dict) and path[0] in ("entries", "tasks", "cases"):
        try:
            item = data[path[0]][path[1]]
            return str(item.get("id") or item.get("task_id") or "")
        except (IndexError, KeyError, TypeError, AttributeError):
            return ""
    if isinstance(data, dict) and isinstance(data.get("id"), str):
        return data["id"]
    return ""


def check(root: Path = REPO_ROOT) -> list[Problem]:
    problems: list[Problem] = []
    validators: dict[str, Draft202012Validator] = {}
    for path, kind in targets(root):
        name = rel(path, root)
        try:
            if path.suffix == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
            else:
                data = load_yaml(path)
        except Exception as exc:  # yaml.YAMLError, json.JSONDecodeError
            problems.append(Problem(name, "parse", str(exc).splitlines()[0], "Fix the syntax."))
            continue
        data = stringify_dates(data)
        if kind == "adapter":
            data = normalise_flags(data)
        validator = validators.setdefault(kind, load_validator(root, kind))
        for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
            problems.append(
                Problem(
                    name,
                    f"schema:{SCHEMA_FOR[kind]}",
                    f"at {_location(error)}: {error.message}",
                    f"Match knowledge/_schema/{SCHEMA_FOR[kind]}.",
                    _entry_id(data, error),
                )
            )
    return problems


def main() -> int:
    problems = check()
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
