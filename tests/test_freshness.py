import json

import freshness


def test_nothing_expiring(repo):
    result = freshness.expiring(repo.root, 30)
    assert result == {"national": [], "state": [], "city": [], "university": []}


def test_default_expiry_counts(repo, monkeypatch):
    monkeypatch.setenv("GSC_TODAY", "2027-03-15")  # verified 2026-10-01 -> expires 2027-04-01
    result = freshness.expiring(repo.root, 30)
    assert [i["id"] for i in result["university"]] == ["testuni.enrolment.deadline"]
    assert result["university"][0]["days_left"] == 17
    assert result["state"][0]["expires"] == "2027-01-15"  # explicit expires, already passed
    assert result["state"][0]["days_left"] < 0
    national = [i["id"] for i in result["national"]]
    assert national == ["de.letters.test-fee", "de.registration.book-appointment",
                        "de.registration.deadline"]


def test_markdown(repo, monkeypatch):
    monkeypatch.setenv("GSC_TODAY", "2027-03-15")
    items = freshness.expiring(repo.root, 30)["state"]
    text = freshness.markdown("state", items)
    assert "**state** pack entries" in text
    assert "| `teststate.ticket.semester` | 2027-01-15 |" in text


def test_skips_unparseable_and_undated(repo, monkeypatch):
    monkeypatch.setenv("GSC_TODAY", "2027-03-15")
    repo.write("knowledge/national/broken.yaml", "entries: [\n")
    repo.edit("knowledge/national/registration.yaml",
              lambda d: d["entries"][0].update(last_verified="not a date"))
    repo.write("knowledge/misc/x.yaml", "schema: 1\n")
    ids = [i["id"] for i in freshness.expiring(repo.root, 30)["national"]]
    assert "de.registration.deadline" not in ids


def test_cli(repo, monkeypatch, capsys):
    monkeypatch.setenv("GSC_TODAY", "2027-03-15")
    assert freshness.main(["--root", str(repo.root), "--days", "30"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert set(data) == {"national", "state", "city", "university"}
    assert freshness.main(["--root", str(repo.root), "--markdown"]) == 0
    assert "## state" in capsys.readouterr().out


def test_cli_issues_mode(repo, monkeypatch, capsys):
    monkeypatch.setenv("GSC_TODAY", "2027-03-15")
    assert freshness.main(["--root", str(repo.root), "--issues"]) == 0
    bodies = json.loads(capsys.readouterr().out)
    assert "teststate.ticket.semester" in bodies["state"]
    monkeypatch.setenv("GSC_TODAY", "2026-10-10")
    assert freshness.main(["--root", str(repo.root), "--issues"]) == 0
    assert set(json.loads(capsys.readouterr().out).values()) == {""}
