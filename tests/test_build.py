import hashlib
import json
import zipfile

import pytest

import build

EPOCH = "1791590400"  # 2026-10-10 00:00 UTC


@pytest.fixture
def built(repo, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", EPOCH)
    return repo


def add_adapters(repo):
    text = repo.path("skill/reference/adapters/gemini.yaml").read_text(encoding="utf-8")
    for tool in ("claude", "copilot"):
        repo.write(f"skill/reference/adapters/{tool}.yaml", text.replace("tool: gemini",
                                                                         f"tool: {tool}"))


def digest(root):
    out = {}
    for folder in ("build", "skill/reference/packs"):
        for path in sorted((root / folder).rglob("*")):
            if path.is_file():
                out[path.relative_to(root).as_posix()] = hashlib.sha256(
                    path.read_bytes()).hexdigest()
    return out


def test_build_is_deterministic(built):
    add_adapters(built)
    build.build(built.root, log=lambda _: None)
    first = digest(built.root)
    build.build(built.root, log=lambda _: None)
    assert digest(built.root) == first
    assert "build/skill-copilot.zip" in first


def test_outputs(built):
    add_adapters(built)
    summary = build.build(built.root, log=lambda _: None)
    assert summary["packs"] == 4
    assert summary["chains"] == ["national.md", "testuni.md"]
    assert summary["packages"] == ["skill-gemini.zip", "skill-claude.zip", "skill-copilot.zip"]
    assert summary["packs_version"] == "2026-10-01"
    names = {p.name for p in (built.root / "build/packs").iterdir()}
    assert names == {"national-de.json", "state-teststate.json", "city-testcity.json",
                     "university-testuni.json", "resolved-national.json",
                     "resolved-testuni.json"}


def test_latest_json(built):
    build.build(built.root, log=lambda _: None)
    latest = json.loads((built.root / "build/latest.json").read_text(encoding="utf-8"))
    assert latest == {
        "schema": 1, "skill": "0.1.0", "template": "1.0", "critical": None, "notes": "",
        "packs": {"city/testcity": "2026-10-01", "national/de": "2026-10-01",
                  "state/teststate": "2026-09-15", "university/testuni": "2026-10-01"},
    }


def test_most_specific_entry_wins(built):
    def add_city_override(d):
        d["entries"].append({
            "id": "testcity.registration.deadline", "layer": "city", "scope": "testcity",
            "topic": "registration", "phase": 2, "text": "City override.",
            "source_url": "https://www.testcity.example/deadline",
            "last_verified": "2026-10-02", "reviewer": "test-reviewer"})
    built.edit("knowledge/cities/testcity/registration.yaml", add_city_override)
    build.build(built.root, log=lambda _: None)
    resolved = json.loads(
        (built.root / "build/packs/resolved-testuni.json").read_text(encoding="utf-8"))
    ids = [e["id"] for e in resolved["entries"]]
    assert "testcity.registration.deadline" in ids
    assert "de.registration.deadline" not in ids
    national = json.loads(
        (built.root / "build/packs/resolved-national.json").read_text(encoding="utf-8"))
    assert [e["id"] for e in national["entries"]] == ["de.registration.deadline"]
    assert resolved["chain"] == ["university/testuni", "city/testcity", "state/teststate",
                                 "national/de"]


def test_snapshot_markdown(built):
    build.build(built.root, log=lambda _: None)
    text = (built.root / "skill/reference/packs/testuni.md").read_text(encoding="utf-8")
    assert text.startswith("# Checked facts: Test University")
    assert "Packs version 2026-10-01 · built 2026-10-10" in text
    assert "Source: https://www.testcity.example/office · Checked: 2026-10-01" in text
    assert "due: +7 days from semester start" in text
    assert "### Test fee letter (Testbeitrag) (de.letters.test-fee)" in text
    index = (built.root / "skill/reference/packs/index.md").read_text(encoding="utf-8")
    assert "| testuni.md | Test University |" in index
    assert "Skill 0.1.0" in index


def test_gemini_zip_contents(built):
    build.build(built.root, log=lambda _: None)
    with zipfile.ZipFile(built.root / "build/skill-gemini.zip") as zf:
        names = zf.namelist()
        infos = zf.infolist()
    assert names == sorted(names)
    assert "germany-companion/SKILL.md" in names
    assert "germany-companion/reference/adapters/gemini.yaml" in names
    assert "germany-companion/reference/packs/testuni.md" in names
    assert not any(n.endswith("README.md") for n in names)
    assert all(i.date_time == (2026, 10, 10, 0, 0, 0) for i in infos)


def test_copilot_zip_is_flattened(built):
    add_adapters(built)
    build.build(built.root, log=lambda _: None)
    with zipfile.ZipFile(built.root / "build/skill-copilot.zip") as zf:
        assert zf.namelist() == ["germany-companion/copilot.yaml",
                                 "germany-companion/instructions.md",
                                 "germany-companion/packs.md"]
        instructions = zf.read("germany-companion/instructions.md").decode()
        packs = zf.read("germany-companion/packs.md").decode()
    assert instructions.startswith("---\nname: test-companion")
    assert "<!-- file: reference/intents/next.md -->" in instructions
    assert "<!-- file: reference/packs/testuni.md -->" in packs


def test_skips_tools_without_adapter(built):
    messages = []
    build.build(built.root, log=messages.append)
    assert any("skip skill-claude.zip" in m for m in messages)
    assert not (built.root / "build/skill-claude.zip").exists()


def test_skips_packages_without_skill(built):
    built.path("skill/SKILL.md").unlink()
    messages = []
    summary = build.build(built.root, log=messages.append)
    assert summary["packages"] == []
    assert any("SKILL.md not written yet" in m for m in messages)


def test_clean_removes_stale_outputs(built):
    built.write("build/old.zip", "stale")
    built.write("skill/reference/packs/gone.md", "stale")
    built.write("skill/reference/packs/README.md", "keep")
    build.build(built.root, log=lambda _: None)
    assert not built.path("build/old.zip").exists()
    assert not built.path("skill/reference/packs/gone.md").exists()
    assert built.path("skill/reference/packs/README.md").read_text(encoding="utf-8") == "keep"


def test_missing_versions_fails(built):
    built.path("versions.yaml").unlink()
    with pytest.raises(build.BuildError, match="versions.yaml"):
        build.build(built.root, log=lambda _: None)


def test_bad_version_fails_latest_schema(built):
    built.write("versions.yaml", "skill: one\ntemplate: '1.0'\n")
    with pytest.raises(build.BuildError, match="latest.json is invalid"):
        build.build(built.root, log=lambda _: None)


def test_non_mapping_pack_fails(built):
    built.write("knowledge/national/broken.yaml", "- a\n")
    with pytest.raises(build.BuildError, match="not a mapping"):
        build.build(built.root, log=lambda _: None)


def test_main_reports_failure(built, monkeypatch, capsys):
    built.path("versions.yaml").unlink()
    monkeypatch.setattr("sys.argv", ["build.py", str(built.root)])
    assert build.main() == 1
    assert "build: failed" in capsys.readouterr().out


def test_main_succeeds(built, monkeypatch):
    monkeypatch.setattr("sys.argv", ["build.py", str(built.root)])
    assert build.main() == 0


def test_source_date_fallbacks(tmp_path, monkeypatch):
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    assert build.source_date(tmp_path).year == 1980  # no git history
    monkeypatch.setenv("SOURCE_DATE_EPOCH", EPOCH)
    assert build.source_date(tmp_path).date().isoformat() == "2026-10-10"


def test_files_outside_layers_and_places_are_ignored(built):
    built.write("knowledge/misc/x.yaml", "schema: 1\nentries: []\n")
    built.write("knowledge/states/loose.yaml", "schema: 1\nentries: []\n")
    summary = build.build(built.root, log=lambda _: None)
    assert summary["packs"] == 4


def test_failed_build_keeps_previous_output(built):
    build.build(built.root, log=lambda _: None)
    before = digest(built.root)
    built.write("versions.yaml", "skill: one\ntemplate: '1.0'\n")
    with pytest.raises(build.BuildError):
        build.build(built.root, log=lambda _: None)
    assert digest(built.root) == before
