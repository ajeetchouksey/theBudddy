import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

GOOD = Path(__file__).parent / "fixtures" / "good"


class Repo:
    """A copy of the good fixture tree that a test can break one rule at a time."""

    def __init__(self, root: Path):
        self.root = root

    def path(self, relative: str) -> Path:
        return self.root / relative

    def load(self, relative: str):
        return yaml.safe_load(self.path(relative).read_text(encoding="utf-8"))

    def dump(self, relative: str, data) -> None:
        target = self.path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
                          encoding="utf-8")

    def edit(self, relative: str, func) -> None:
        data = self.load(relative)
        func(data)
        self.dump(relative, data)

    def write(self, relative: str, text: str) -> None:
        target = self.path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path, monkeypatch) -> Repo:
    root = tmp_path / "repo"
    shutil.copytree(GOOD, root)
    monkeypatch.setenv("GSC_TODAY", "2026-10-10")
    monkeypatch.setenv("GSC_BRANCH", "feat/1-test")
    monkeypatch.delenv("GITHUB_REF_TYPE", raising=False)
    return Repo(root)


def rules(problems) -> list[str]:
    return [p.rule for p in problems]
