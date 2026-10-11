import lint_skill
import pytest
from conftest import rules

SKILL = "skill/SKILL.md"
INTENT = "skill/reference/intents/next.md"


def test_good_fixture_passes(repo):
    assert lint_skill.check(repo.root) == []


def test_no_skill_yet_passes(repo):
    repo.path(SKILL).unlink()
    assert lint_skill.check(repo.root) == []


@pytest.mark.parametrize("name", ["Kiel", "kiel", "Gemini", "Schleswig-Holstein", "München",
                                  "CAU", "Kiel University", "ChatGPT"])
def test_denied_name_in_skill_fails(repo, name):
    text = repo.path(SKILL).read_text(encoding="utf-8")
    repo.write(SKILL, text + f"\nStudents in {name} can ask.\n")
    problems = lint_skill.check(repo.root)
    assert rules(problems) == ["S1 names"]
    expected_line = len(repo.path(SKILL).read_text(encoding="utf-8").splitlines())
    assert problems[0].path.endswith(f"SKILL.md:{expected_line}")
    assert name in problems[0].message


def test_denied_name_in_intent_fails(repo):
    repo.write(INTENT, "# Intent\n\nAsk Copilot.\n")
    (p,) = lint_skill.check(repo.root)
    assert p.rule == "S1 names" and p.path.endswith("next.md:3")


@pytest.mark.parametrize("text", ["the starter kit", "a cause", "Kielce", "gemstone",
                                  "pre-Kiel", "kit and caboodle"])
def test_ordinary_words_pass(repo, text):
    repo.write(INTENT, f"# Intent\n\n{text}\n")
    assert lint_skill.check(repo.root) == []


def test_readme_in_intents_is_skipped(repo):
    assert "Kiel" in repo.path("skill/reference/intents/README.md").read_text(encoding="utf-8")
    assert lint_skill.check(repo.root) == []


def test_missing_guardrail_heading_fails(repo):
    text = repo.path(SKILL).read_text(encoding="utf-8").replace("## Ground rules", "## Rules")
    repo.write(SKILL, text)
    (p,) = lint_skill.check(repo.root)
    assert p.rule == "S2 guardrails"
    assert "docs/ai-guardrails.md" in p.fix


def test_skill_over_budget_fails(repo):
    repo.write(SKILL, repo.path(SKILL).read_text(encoding="utf-8") + "line\n" * 400)
    assert rules(lint_skill.check(repo.root)) == ["S3 size"]


def test_intent_over_budget_fails(repo):
    repo.write(INTENT, "line\n" * 151)
    (p,) = lint_skill.check(repo.root)
    assert p.rule == "S3 size" and "151 lines, budget is 150" in p.message


def test_intent_at_budget_passes(repo):
    repo.write(INTENT, "line\n" * 150)
    assert lint_skill.check(repo.root) == []


def test_repo_denylist_used_when_fixture_has_none(repo):
    assert not repo.path("scripts/skill-denylist.txt").exists()
    names = lint_skill.load_denylist(repo.root)
    assert "Kiel" in names and "Gemini" in names


def test_main_returns_zero_on_repo():
    assert lint_skill.main() == 0
