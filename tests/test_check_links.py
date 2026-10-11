import io
import urllib.error

import check_links
import pytest
from test_fact_diff import commit, git


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def opener_for(results):
    """results: url -> list of outcomes (int status or exception), consumed per attempt."""
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        assert "theBudddy-link-check" in request.get_header("User-agent")
        outcome = results[request.full_url].pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        if outcome >= 400:
            raise urllib.error.HTTPError(request.full_url, outcome, "x", {}, io.BytesIO())
        return FakeResponse()

    opener.calls = calls
    return opener


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(check_links.time, "sleep", lambda _: None)


@pytest.mark.parametrize("outcomes, expected", [
    ([200], "ok"),
    ([404], "fail"),
    ([410], "fail"),
    ([403], "warn"),
    ([429, 429], "warn"),
    ([503, 200], "ok"),
    ([500, 500], "warn"),
    ([urllib.error.URLError("dns"), urllib.error.URLError("dns")], "fail"),
    ([TimeoutError(), 200], "ok"),
])
def test_probe(outcomes, expected):
    url = "https://www.bund.example/x"
    result, _ = check_links.probe(url, opener_for({url: list(outcomes)}))
    assert result == expected


def test_run_fails_on_broken_link(capsys):
    urls = {"https://a.example/ok": ["a.b.c"], "https://a.example/gone": ["a.b.d"]}
    opener = opener_for({"https://a.example/ok": [200], "https://a.example/gone": [404]})
    assert check_links.run(urls, opener) == 1
    out = capsys.readouterr().out
    assert "fail  HTTP 404" in out and "[a.b.d]" in out
    assert "links: 2 checked, 1 failed" in out


def test_run_with_nothing_to_check(capsys):
    assert check_links.run({}) == 0
    assert "no source_url" in capsys.readouterr().out


def test_collect_all(repo):
    urls = check_links.collect_all(repo.root)
    assert urls["https://www.bund.example/registration"] == [
        "de.registration.deadline", "de.registration.book-appointment"]
    assert "https://www.bund.example/fee" in urls


def test_collect_changed_only_new_values(repo):
    git(repo.root, "init", "-q", "-b", "main")
    commit(repo)
    git(repo.root, "checkout", "-q", "-b", "feature")
    repo.edit("knowledge/national/registration.yaml",
              lambda d: d["entries"][0].update(source_url="https://www.bund.example/new"))
    repo.path("knowledge/national/letters/test-fee.yaml").unlink()
    commit(repo)
    assert check_links.collect_changed(repo.root, "main") == {
        "https://www.bund.example/new": ["de.registration.deadline"]}


def test_main_all(repo, monkeypatch):
    monkeypatch.setattr(check_links, "run", lambda urls: len(urls))
    assert check_links.main(["--all", "--root", str(repo.root)]) == 5  # distinct URLs
