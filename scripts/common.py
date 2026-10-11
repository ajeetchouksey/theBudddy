"""Shared helpers for the validation scripts.

Every check returns a list of Problem objects; scripts/validate.py prints them and sets the
exit code. Paths are relative to a repo root so tests can run against fixture trees.
"""

from __future__ import annotations

import datetime as dt
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = Path("knowledge/_schema")

LAYER_DIRS = {
    "national": "national",
    "states": "state",
    "cities": "city",
    "universities": "university",
}
NATIONAL_SCOPE = "de"
PLACES = Path("knowledge/places.yaml")


@dataclass(frozen=True)
class Problem:
    path: str
    rule: str
    message: str
    fix: str = ""
    entry_id: str = ""

    def __str__(self) -> str:
        where = f"{self.path} [{self.entry_id}]" if self.entry_id else self.path
        out = f"{where}: {self.rule}: {self.message}"
        if self.fix:
            out += f"\n    fix: {self.fix}"
        return out


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def normalise_flags(value):
    """YAML 1.1 reads unquoted yes/no as booleans; adapters mean the strings."""
    if value is True:
        return "yes"
    if value is False:
        return "no"
    if isinstance(value, dict):
        return {k: normalise_flags(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalise_flags(v) for v in value]
    return value


def parse_date(value) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def as_iso(value) -> str:
    """PyYAML turns unquoted dates into date objects; schemas expect strings."""
    if isinstance(value, dt.date):
        return value.isoformat()
    return value


def stringify_dates(value):
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: stringify_dates(v) for k, v in value.items()}
    if isinstance(value, list):
        return [stringify_dates(v) for v in value]
    return value


def add_months(day: dt.date, months: int) -> dt.date:
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    # clamp to the last valid day of the target month
    for d in (day.day, 30, 29, 28):
        try:
            return dt.date(year, month, d)
        except ValueError:
            continue
    raise ValueError(day)  # pragma: no cover


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:  # pragma: no cover
        return path.as_posix()


def yaml_files(root: Path, sub: str) -> list[Path]:
    base = root / sub
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*") if p.suffix in (".yaml", ".yml") and p.is_file())


def current_branch(root: Path) -> str:
    """Branch the checks run for. 'main' or a tag means strict rules."""
    if os.environ.get("GITHUB_REF_TYPE") == "tag":
        return "main"
    for var in ("GSC_BRANCH", "GITHUB_HEAD_REF", "GITHUB_REF_NAME"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            check=True,
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def today() -> dt.date:
    override = os.environ.get("GSC_TODAY")
    return dt.date.fromisoformat(override) if override else dt.date.today()
