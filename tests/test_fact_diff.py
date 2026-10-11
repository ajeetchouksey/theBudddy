import subprocess

import fact_diff
import pytest

PACK = "knowledge/national/registration.yaml"
LETTER = "knowledge/national/letters/test-fee.yaml"


def git(root, *args):
    subprocess.run(["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid",
                    "-c", "commit.gpgsign=false", *args],
                   cwd=root, check=True, capture_output=True)


@pytest.fixture
def history(repo):
    git(repo.root, "init", "-q", "-b", "main")
    git(repo.root, "add", "-A")
    git(repo.root, "commit", "-q", "-m", "base")
    git(repo.root, "checkout", "-q", "-b", "feature")
    return repo


def commit(repo):
    git(repo.root, "add", "-A")
    git(repo.root, "commit", "-q", "-m", "change")


def test_no_changes(history):
    assert fact_diff.diff(history.root, "main") == []
    assert "No pack entries changed." in fact_diff.render([])


def test_changed_field_shows_old_and_new(history):
    history.edit(PACK, lambda d: d["entries"][0].update(text="New text.",
                                                        last_verified="2026-10-05"))
    commit(history)
    (change,) = fact_diff.diff(history.root, "main")
    assert (change.kind, change.item_id) == ("changed", "de.registration.deadline")
    assert change.fields["last_verified"] == ("2026-10-01", "2026-10-05")
    body = fact_diff.render([change])
    assert body.startswith(fact_diff.MARKER)
    assert "| last_verified | 2026-10-01 | 2026-10-05 |" in body
    assert "0 added · 1 changed · 0 removed" in body


def test_added_and_removed(history):
    def change(d):
        d["entries"][0]["id"] = "de.registration.renamed"
    history.edit(PACK, change)
    commit(history)
    kinds = {(c.kind, c.item_id) for c in fact_diff.diff(history.root, "main")}
    assert kinds == {("added", "de.registration.renamed"),
                     ("removed", "de.registration.deadline")}
    body = fact_diff.render(fact_diff.diff(history.root, "main"))
    assert "### added: `de.registration.renamed`" in body
    assert "- **source_url:** https://www.bund.example/registration" in body


def test_uncommitted_working_tree_is_compared(history):
    history.edit(LETTER, lambda d: d.update(deadline_rule="Within 30 days of the letter date."))
    git(history.root, "add", "-A")  # staged, not committed: diff base...HEAD sees nothing
    assert fact_diff.diff(history.root, "main") == []
    commit(history)
    (change,) = fact_diff.diff(history.root, "main")
    assert change.item_id == "de.letters.test-fee"
    assert "deadline_rule" in change.fields


def test_new_file_and_deleted_file(history):
    history.write("knowledge/national/new.yaml",
                  history.path(PACK).read_text(encoding="utf-8").replace("de.registration.deadline",
                                                         "de.registration.other")
                  .replace("de.registration.book-appointment", "de.registration.other-task"))
    history.path(LETTER).unlink()
    commit(history)
    kinds = {(c.kind, c.item_id) for c in fact_diff.diff(history.root, "main")}
    assert ("added", "de.registration.other") in kinds
    assert ("added", "de.registration.other-task") in kinds
    assert ("removed", "de.letters.test-fee") in kinds


def test_places_and_unparseable_files_are_ignored(history):
    history.edit("knowledge/places.yaml", lambda d: d["states"].update(x={"name": "X"}))
    history.write("knowledge/national/broken.yaml", "entries: [\n")
    commit(history)
    assert fact_diff.diff(history.root, "main") == []


def test_long_values_and_pipes_are_escaped():
    assert fact_diff.short("a | b") == "a \\| b"
    assert fact_diff.short(None) == "—"
    assert len(fact_diff.short("x" * 500)) == fact_diff.MAX_VALUE


def test_body_is_capped(monkeypatch):
    monkeypatch.setattr(fact_diff, "MAX_BODY", 50)
    change = fact_diff.Change("p.yaml", "a.b.c", "removed")
    assert fact_diff.render([change] * 10).endswith("run scripts/fact_diff.py locally.\n")


def test_bad_base_raises(history):
    with pytest.raises(RuntimeError, match="git diff"):
        fact_diff.diff(history.root, "no-such-ref")


def test_cli_writes_file(history, tmp_path, capsys):
    out = tmp_path / "diff.md"
    assert fact_diff.main(["--base", "main", "--root", str(history.root),
                           "--out", str(out)]) == 0
    assert "No pack entries changed." in out.read_text(encoding="utf-8")
    assert fact_diff.main(["--base", "main", "--root", str(history.root)]) == 0
    assert "## Fact diff" in capsys.readouterr().out


def test_non_ascii_text_survives(history):
    history.edit(PACK, lambda d: d["entries"][0].update(text="Bürgeramt: Anmeldung prüfen."))
    commit(history)
    (change,) = fact_diff.diff(history.root, "main")
    assert change.fields["text"][1] == "Bürgeramt: Anmeldung prüfen."
    assert "Bürgeramt: Anmeldung prüfen." in fact_diff.render([change])
