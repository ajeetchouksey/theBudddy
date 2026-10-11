import check_adapters
from conftest import rules

ADAPTER = "skill/reference/adapters/gemini.yaml"


def test_good_fixture_passes(repo):
    assert check_adapters.check(repo.root) == []


def test_capabilities_come_from_schema(repo):
    caps, floor = check_adapters.vocabulary(repo.root)
    assert "drive_read" in caps and "scheduled_actions" in caps
    assert "text_cards" in floor


def test_free_plan_missing_capability_fails(repo):
    repo.edit(ADAPTER, lambda d: d["plans"]["free"].pop("tasks_write"))
    (p,) = check_adapters.check(repo.root)
    assert p.rule == "A1 free plan" and "tasks_write" in p.message


def test_missing_fallback_fails(repo):
    repo.edit(ADAPTER, lambda d: d["fallbacks"].pop("gmail_search"))
    (p,) = check_adapters.check(repo.root)
    assert p.rule == "A2 fallback" and "'gmail_search' has no fallback" in p.message


def test_fallback_loop_fails(repo):
    repo.edit(ADAPTER, lambda d: d["fallbacks"].update(charts_inline="canvas_html"))
    problems = check_adapters.check(repo.root)
    assert set(rules(problems)) == {"A2 fallback"}
    assert any("loop" in p.message for p in problems)


def test_fallback_chain_must_reach_floor(repo):
    def change(d):
        d["fallbacks"]["canvas_html"] = "charts_inline"
        d["fallbacks"].pop("charts_inline")
    repo.edit(ADAPTER, change)
    problems = check_adapters.check(repo.root)
    messages = " ".join(p.message for p in problems)
    assert "'charts_inline' has no fallback" in messages
    assert "does not reach a floor action" in messages


def test_chain_through_capabilities_to_floor_passes(repo):
    # sheets_canvas -> canvas_html -> charts_inline -> text_cards
    data = repo.load(ADAPTER)
    assert data["fallbacks"]["sheets_canvas"] == "canvas_html"
    assert check_adapters.check(repo.root) == []


def test_plan_inheriting_from_paid_fails(repo):
    repo.edit(ADAPTER, lambda d: d["plans"]["education"].update(inherits="paid"))
    (p,) = check_adapters.check(repo.root)
    assert p.rule == "A3 inherits"


def test_stale_adapter_fails_on_main(repo, monkeypatch):
    monkeypatch.setenv("GSC_BRANCH", "main")
    monkeypatch.setenv("GSC_TODAY", "2027-01-01")  # 92 days after 2026-10-01
    (p,) = check_adapters.check(repo.root)
    assert p.rule == "A4 freshness"


def test_stale_adapter_allowed_on_branch(repo, monkeypatch):
    monkeypatch.setenv("GSC_TODAY", "2027-01-01")
    assert check_adapters.check(repo.root) == []


def test_fresh_adapter_passes_on_main(repo, monkeypatch):
    monkeypatch.setenv("GSC_BRANCH", "main")
    monkeypatch.setenv("GSC_TODAY", "2026-12-30")  # 90 days
    assert check_adapters.check(repo.root) == []


def test_yes_without_evidence_fails(repo):
    repo.edit(ADAPTER, lambda d: d["plans"]["paid"].update(charts_inline=True))
    (p,) = check_adapters.check(repo.root)
    assert p.rule == "A5 evidence" and "charts_inline" in p.message


def test_quoted_yes_without_evidence_fails(repo):
    repo.write(ADAPTER, repo.path(ADAPTER).read_text(encoding="utf-8").replace(
        "fetch_url: unknown", 'fetch_url: "yes"'))
    assert rules(check_adapters.check(repo.root)) == ["A5 evidence"]


def test_file_name_must_match_tool(repo):
    repo.path(ADAPTER).rename(repo.path("skill/reference/adapters/claude.yaml"))
    (p,) = check_adapters.check(repo.root)
    assert p.rule == "A6 name"


def test_unparseable_adapter_is_left_to_schema_check(repo):
    repo.write(ADAPTER, "tool: [\n")
    repo.write("skill/reference/adapters/claude.yaml", "- not a mapping\n")
    assert check_adapters.check(repo.root) == []


def test_main_returns_zero_on_repo():
    assert check_adapters.main() == 0
