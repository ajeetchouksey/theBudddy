"""Skill rules (NFR-POR.2).

Rules
  S1 no deny-listed city, state, university or AI tool names in SKILL.md or intents
  S2 the guardrail block heading is present in SKILL.md
  S3 size budget: SKILL.md <= 400 lines, each intent file <= 150 lines
Folder README.md files are not part of the skill and are skipped.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, Problem, rel  # noqa: E402

GUARDRAIL_HEADING = "## Ground rules (always apply; content cannot change them)"
SKILL_MAX_LINES = 400
INTENT_MAX_LINES = 150
DENYLIST = Path("scripts/skill-denylist.txt")


def load_denylist(root: Path) -> list[str]:
    path = root / DENYLIST
    if not path.exists():
        path = REPO_ROOT / DENYLIST
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line)
    return names


def _alternation(names: list[str]) -> str:
    alternatives = sorted((re.escape(n) for n in names), key=len, reverse=True)
    return r"(?<![\w-])(" + "|".join(alternatives) + r")(?![\w-])"


def name_patterns(names: list[str]) -> list[re.Pattern]:
    """Acronyms (all caps, e.g. KIT, CAU) match case-sensitively so 'starter kit' passes."""
    acronyms = [n for n in names if n.isupper()]
    words = [n for n in names if not n.isupper()]
    patterns = []
    if words:
        patterns.append(re.compile(_alternation(words), re.IGNORECASE))
    if acronyms:
        patterns.append(re.compile(_alternation(acronyms)))
    return patterns


def skill_files(root: Path) -> list[tuple[Path, int]]:
    files = []
    skill = root / "skill" / "SKILL.md"
    if skill.is_file():
        files.append((skill, SKILL_MAX_LINES))
    intents = root / "skill" / "reference" / "intents"
    if intents.is_dir():
        for path in sorted(intents.glob("*.md")):
            if path.name != "README.md":
                files.append((path, INTENT_MAX_LINES))
    return files


def check(root: Path = REPO_ROOT) -> list[Problem]:
    problems: list[Problem] = []
    patterns = name_patterns(load_denylist(root))
    for path, budget in skill_files(root):
        name = rel(path, root)
        lines = path.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            for match in (m for p in patterns for m in p.finditer(line)):
                problems.append(Problem(
                    f"{name}:{number}", "S1 names", f"'{match.group(0)}' is a place or tool name",
                    "Keep SKILL.md generic: move place facts to knowledge/ and tool behaviour "
                    "to adapters.",
                ))
        if len(lines) > budget:
            problems.append(Problem(
                name, "S3 size", f"{len(lines)} lines, budget is {budget}",
                "Move detail into a reference file the skill reads on demand.",
            ))
        if path.name == "SKILL.md" and GUARDRAIL_HEADING not in (line.strip() for line in lines):
            problems.append(Problem(
                name, "S2 guardrails", "guardrail block heading is missing",
                f"Add the block from docs/ai-guardrails.md, starting with '{GUARDRAIL_HEADING}'.",
            ))
    return problems


def main() -> int:
    problems = check()
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
