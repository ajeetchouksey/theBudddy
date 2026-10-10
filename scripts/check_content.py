"""Content rules for knowledge packs and letters (NFR-ACC.1, NFR-ACC.2, FR-3.2).

Rules
  C1 source_url is https and its host is on knowledge/_schema/official-domains.txt
  C2 last_verified is a real date and not in the future
  C3 expires defaults to last_verified + 6 months, must be after last_verified, and must
     not have passed
  C4 reviewer is set (empty allowed only on non-main branches)
  C5 layer and scope match the file's folder; id starts with <scope>.<topic>
  C6 ids are unique across all packs
  C7 depends_on points to an existing task_id
Structure is checked separately by check_schemas.py; malformed items are skipped here.
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    LAYER_DIRS,
    NATIONAL_SCOPE,
    REPO_ROOT,
    SCHEMA_DIR,
    Problem,
    add_months,
    current_branch,
    load_yaml,
    parse_date,
    rel,
    today,
    yaml_files,
)

DEFAULT_EXPIRY_MONTHS = 6


def load_allowlist(root: Path) -> set[str]:
    path = root / SCHEMA_DIR / "official-domains.txt"
    if not path.exists():
        path = REPO_ROOT / SCHEMA_DIR / "official-domains.txt"
    domains = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            domains.add(line)
    return domains


def host_allowed(url: str, allowlist: set[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in allowlist)


def expected_layer_scope(path: Path, root: Path) -> tuple[str | None, str | None]:
    parts = path.relative_to(root / "knowledge").parts
    if not parts or parts[0] not in LAYER_DIRS:
        return None, None
    layer = LAYER_DIRS[parts[0]]
    if layer == "national":
        return layer, NATIONAL_SCOPE
    scope = parts[1] if len(parts) > 2 else None
    return layer, scope


class Checker:
    def __init__(self, root: Path):
        self.root = root
        self.allowlist = load_allowlist(root)
        self.today = today()
        self.strict = current_branch(root) == "main"
        self.problems: list[Problem] = []
        self.seen_ids: dict[str, str] = {}
        self.task_ids: set[str] = set()
        self.depends: list[tuple[str, str, str]] = []

    def add(self, path, rule, message, fix="", entry_id=""):
        self.problems.append(Problem(path, rule, message, fix, entry_id))

    def common(self, name: str, item: dict, item_id: str) -> None:
        url = item.get("source_url")
        if isinstance(url, str):
            if not url.startswith("https://"):
                self.add(name, "C1 source", f"source_url is not https: {url}",
                         "Use the https:// address of the official page.", item_id)
            elif not host_allowed(url, self.allowlist):
                host = urlparse(url).hostname
                self.add(name, "C1 source", f"'{host}' is not an official domain",
                         "Use an official source, or ask a maintainer to add the domain to "
                         "knowledge/_schema/official-domains.txt.", item_id)

        verified = parse_date(item.get("last_verified"))
        if item.get("last_verified") is not None and verified is None:
            self.add(name, "C2 date", f"last_verified is not a date: {item.get('last_verified')}",
                     "Use YYYY-MM-DD.", item_id)
        elif verified and verified > self.today:
            self.add(name, "C2 date", f"last_verified {verified} is in the future",
                     "Set the date you actually checked the source.", item_id)

        if verified:
            raw = item.get("expires")
            expires = parse_date(raw) if raw is not None else add_months(
                verified, DEFAULT_EXPIRY_MONTHS)
            if raw is not None and expires is None:
                self.add(name, "C3 expiry", f"expires is not a date: {raw}", "Use YYYY-MM-DD.",
                         item_id)
            elif expires <= verified:
                self.add(name, "C3 expiry", f"expires {expires} is not after last_verified",
                         "Set expires after last_verified, or remove it for the 6-month default.",
                         item_id)
            elif expires < self.today:
                self.add(name, "C3 expiry", f"expired on {expires}",
                         "Re-check the source and update last_verified, or retire the entry.",
                         item_id)

        reviewer = item.get("reviewer")
        if self.strict and reviewer == "":
            self.add(name, "C4 reviewer", "reviewer is empty on main",
                     "A human reviewer for this layer sets reviewer before merge.", item_id)

    def claim_id(self, name: str, item_id: str) -> None:
        if item_id in self.seen_ids:
            self.add(name, "C6 unique", f"id also used in {self.seen_ids[item_id]}",
                     "Give each entry and task its own id.", item_id)
        else:
            self.seen_ids[item_id] = name

    def layer_scope(self, path, name, item, item_id, exp_layer, exp_scope) -> None:
        if exp_layer and item.get("layer") not in (None, exp_layer):
            self.add(name, "C5 layer", f"layer '{item.get('layer')}' but file is in a "
                     f"{exp_layer} folder", f"Set layer: {exp_layer} or move the file.", item_id)
        if exp_scope and item.get("scope") not in (None, exp_scope):
            self.add(name, "C5 scope", f"scope '{item.get('scope')}' but folder is "
                     f"'{exp_scope}'", f"Set scope: {exp_scope} or move the file.", item_id)

    def pack(self, path: Path, data: dict) -> None:
        name = rel(path, self.root)
        exp_layer, exp_scope = expected_layer_scope(path, self.root)
        for item in data.get("entries") or []:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            item_id = item["id"]
            self.claim_id(name, item_id)
            self.layer_scope(path, name, item, item_id, exp_layer, exp_scope)
            prefix = f"{item.get('scope')}.{item.get('topic')}."
            if not item_id.startswith(prefix):
                self.add(name, "C5 id", f"id should start with '{prefix}'",
                         "Use <scope>.<topic>.<slug>.", item_id)
            self.common(name, item, item_id)
        for task in data.get("tasks") or []:
            if not isinstance(task, dict) or not isinstance(task.get("task_id"), str):
                continue
            task_id = task["task_id"]
            self.claim_id(name, task_id)
            self.task_ids.add(task_id)
            if exp_scope and not task_id.startswith(exp_scope + "."):
                self.add(name, "C5 id", f"task_id should start with '{exp_scope}.'",
                         "Use <scope>.<topic>.<slug>.", task_id)
            for dep in task.get("depends_on") or []:
                self.depends.append((name, task_id, dep))
            self.common(name, task, task_id)

    def letter(self, path: Path, data: dict) -> None:
        name = rel(path, self.root)
        item_id = data.get("id") if isinstance(data.get("id"), str) else ""
        if item_id:
            self.claim_id(name, item_id)
        exp_layer, exp_scope = expected_layer_scope(path, self.root)
        self.layer_scope(path, name, data, item_id, exp_layer, exp_scope)
        self.common(name, data, item_id)

    def finish(self) -> list[Problem]:
        for name, task_id, dep in self.depends:
            if dep not in self.task_ids:
                self.add(name, "C7 depends_on", f"unknown task '{dep}'",
                         "Point depends_on at an existing task_id.", task_id)
        return self.problems


def check(root: Path = REPO_ROOT) -> list[Problem]:
    checker = Checker(root)
    for path in yaml_files(root, "knowledge"):
        try:
            data = load_yaml(path)
        except Exception:  # reported by check_schemas.py
            continue
        if not isinstance(data, dict):
            continue
        if "letters" in path.parts:
            checker.letter(path, data)
        else:
            checker.pack(path, data)
    return checker.finish()


def main() -> int:
    problems = check()
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
