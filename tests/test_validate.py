import subprocess
import sys
from pathlib import Path

import common
import validate

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "validate.py"


def test_good_fixture_passes(repo, capsys):
    assert validate.run(repo.root) == 0
    out = capsys.readouterr().out
    assert "validate: passed" in out
    for label in ("yamllint", "schemas", "content rules", "skill rules", "adapter rules"):
        assert f"{label}: ok" in out


def test_bad_fixture_fails_with_readable_message(repo, capsys):
    repo.edit("knowledge/national/registration.yaml",
              lambda d: d["entries"][0].update(source_url="https://someblog.example/x"))
    assert validate.run(repo.root) == 1
    out = capsys.readouterr().out
    assert "content rules: 1 problem(s)" in out
    assert "knowledge/national/registration.yaml [de.registration.deadline]: C1 source" in out
    assert "fix: Use an official source" in out
    assert "validate: failed with 1 problem(s)" in out


def test_yamllint_error_fails(repo, capsys):
    repo.write("evals/cases/dup.yaml", "schema: 1\nschema: 1\nset: privacy\ncases: []\n")
    assert validate.run(repo.root) == 1
    assert "yamllint" in capsys.readouterr().out


def test_missing_yamllint_reported(repo, monkeypatch):
    monkeypatch.setattr(validate.importlib.util, "find_spec", lambda _: None)
    (p,) = validate.run_yamllint(repo.root)
    assert "not installed" in p.message


def test_cli_accepts_root(repo):
    out = subprocess.run([sys.executable, str(SCRIPT), str(repo.root)],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert out.returncode == 0, out.stdout


def test_problem_str_without_entry():
    text = str(common.Problem("a.yaml", "R1", "broken"))
    assert text == "a.yaml: R1: broken"


def test_add_months_clamps_to_month_end():
    import datetime as dt
    assert common.add_months(dt.date(2026, 8, 31), 6) == dt.date(2027, 2, 28)
    assert common.add_months(dt.date(2026, 10, 1), 6) == dt.date(2027, 4, 1)


def test_current_branch_falls_back_to_git(monkeypatch, tmp_path):
    for var in ("GSC_BRANCH", "GITHUB_HEAD_REF", "GITHUB_REF_NAME", "GITHUB_REF_TYPE"):
        monkeypatch.delenv(var, raising=False)
    assert common.current_branch(tmp_path) == "unknown"  # not a git repo
