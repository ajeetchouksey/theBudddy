import importlib.util
import zipfile
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "make_probe_packages", Path(__file__).resolve().parent.parent / "spike/make_probe_packages.py")
kit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kit)

URL = "https://script.google.com/macros/s/EXAMPLE/exec"


def test_builds_all_packages(tmp_path):
    made = kit.build(URL, "https://example.org/probe-latest.json", tmp_path)
    assert "probe-skill.zip" in made and "limits-answers.md" in made
    with zipfile.ZipFile(tmp_path / "probe-skill.zip") as zf:
        link = zf.read("spike-probe/reference/probe-link.md").decode()
        facts = zf.read("spike-probe/reference/probe-facts.md").decode()
    assert f"{URL}?a=long" in link and "WEBAPP_URL" not in link
    assert "https://example.org/probe-latest.json" in facts
    assert "PROBE-REF-7Q2K" in facts


def test_limits_files_end_with_their_code(tmp_path):
    kit.build(URL, "https://example.org/x.json", tmp_path)
    with zipfile.ZipFile(tmp_path / "limits-files-50.zip") as zf:
        names = [n for n in zf.namelist() if "/fill-" in n]
        last = zf.read("spike-probe/reference/fill-050.md").decode()
    assert len(names) == 50
    assert last.rstrip().endswith(kit.code("limits-files-50/fill-050"))
    with zipfile.ZipFile(tmp_path / "limits-size-1m.zip") as zf:
        assert len(zf.read("spike-probe/reference/fill-001.md")) == 1024 * 1024
    answers = (tmp_path / "limits-answers.md").read_text(encoding="utf-8")
    assert kit.code("limits-size-2m/fill-001") in answers


def test_long_link_pad_is_200_chars():
    text = (kit.SKILL / "reference/probe-link.md").read_text(encoding="utf-8")
    pad = text.split("pad=")[1].split("&")[0]
    assert len(pad) == 200


def test_cli_rejects_http(tmp_path, capsys):
    assert kit.main(["--webapp-url", "http://x", "--out", str(tmp_path)]) == 1
    assert kit.main(["--out", str(tmp_path)]) == 0
    assert "not set" in capsys.readouterr().out
