"""Run every validation check (make validate). Exit 1 if any check reports a problem."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_adapters  # noqa: E402
import check_content  # noqa: E402
import check_schemas  # noqa: E402
import lint_skill  # noqa: E402
from common import REPO_ROOT, Problem  # noqa: E402

CHECKS = [
    ("schemas", check_schemas.check),
    ("content rules", check_content.check),
    ("skill rules", lint_skill.check),
    ("adapter rules", check_adapters.check),
]


def run_yamllint(root: Path) -> list[Problem]:
    # Run as "python -m yamllint" so it works when the Scripts folder is not on PATH
    # (common with the Microsoft Store Python on Windows).
    if importlib.util.find_spec("yamllint") is None:
        return [Problem("(yamllint)", "tool", "yamllint is not installed",
                        "python -m pip install -r requirements-dev.txt")]
    targets = [d for d in ("knowledge", "skill", "evals", ".github") if (root / d).exists()]
    config = root / ".yamllint"
    if not config.exists():  # fixtures use the repo's config
        config = REPO_ROOT / ".yamllint"
    cmd = [sys.executable, "-m", "yamllint", "-c", str(config), "-f", "parsable", *targets]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}  # Windows consoles default to cp1252
    out = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    problems = []
    for line in out.stdout.splitlines():
        if "[error]" in line:
            location, _, message = line.partition(": ")
            problems.append(Problem(location, "yamllint", message, "Fix the YAML style."))
        elif line.strip():
            print(f"  warning: {line}")
    return problems


def run(root: Path = REPO_ROOT) -> int:
    total = 0
    for label, func in [("yamllint", run_yamllint), *CHECKS]:
        problems = func(root)
        status = "ok" if not problems else f"{len(problems)} problem(s)"
        print(f"{label}: {status}")
        for p in problems:
            print(f"  {p}")
        total += len(problems)
    print("validate: passed" if total == 0 else f"validate: failed with {total} problem(s)")
    return 1 if total else 0


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO_ROOT
    return run(root)


if __name__ == "__main__":
    sys.exit(main())
