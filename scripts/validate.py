"""Run every validation check (make validate). Exit 1 if any check reports a problem."""

from __future__ import annotations

import shutil
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
    exe = shutil.which("yamllint")
    if exe is None:
        return [Problem("(yamllint)", "tool", "yamllint is not installed",
                        "python3 -m pip install -r requirements-dev.txt")]
    targets = [d for d in ("knowledge", "skill", "evals", ".github") if (root / d).exists()]
    config = root / ".yamllint"
    if not config.exists():  # fixtures use the repo's config
        config = REPO_ROOT / ".yamllint"
    out = subprocess.run([exe, "-c", str(config), "-f", "parsable", *targets], cwd=root,
                         capture_output=True, text=True)
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
