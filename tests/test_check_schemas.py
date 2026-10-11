import json

import check_schemas
import pytest
from conftest import rules

PACK = "knowledge/national/registration.yaml"
LETTER = "knowledge/national/letters/test-fee.yaml"
ADAPTER = "skill/reference/adapters/gemini.yaml"
EVALS = "evals/cases/prompt_injection.yaml"


def test_good_fixture_passes(repo):
    assert check_schemas.check(repo.root) == []


def test_every_schema_is_valid_draft_2020_12(repo):
    for kind in check_schemas.SCHEMA_FOR:
        check_schemas.load_validator(repo.root, kind)  # raises if the schema is invalid


def test_targets_cover_every_kind(repo):
    kinds = {kind for _, kind in check_schemas.targets(repo.root)}
    assert kinds == {"fact", "letter", "adapter", "eval", "latest", "places"}


@pytest.mark.parametrize(
    "mutate, needle",
    [
        (lambda d: d["entries"][0].pop("source_url"), "'source_url' is a required property"),
        (lambda d: d["entries"][0].update(id="Bad Id"), "does not match"),
        (lambda d: d["entries"][0].update(layer="county"), "is not one of"),
        (lambda d: d["entries"][0].update(phase=9), "is greater than the maximum"),
        (lambda d: d["entries"][0].update(extra="x"), "Additional properties"),
        (lambda d: d["entries"][0].update(source_url="http://www.bund.example/x"),
         "does not match"),
        (lambda d: d.update(schema=2), "1 was expected"),
        (lambda d: d["tasks"][0].pop("why"), "'why' is a required property"),
    ],
)
def test_bad_pack_fails(repo, mutate, needle):
    repo.edit(PACK, mutate)
    problems = check_schemas.check(repo.root)
    assert problems, "expected a schema problem"
    assert any(needle in p.message for p in problems), [str(p) for p in problems]
    assert all(p.rule == "schema:fact.json" for p in problems)


def test_problem_names_the_entry(repo):
    repo.edit(PACK, lambda d: d["entries"][0].pop("text"))
    (problem,) = check_schemas.check(repo.root)
    assert problem.entry_id == "de.registration.deadline"
    assert "entries/0" in problem.message
    assert "knowledge/_schema/fact.json" in problem.fix


def test_bad_letter_fails(repo):
    repo.edit(LETTER, lambda d: d.update(id="de.letter.test-fee"))
    problems = check_schemas.check(repo.root)
    assert rules(problems) == ["schema:letter.json"]
    assert problems[0].entry_id == "de.letter.test-fee"


def test_bad_adapter_flag_fails(repo):
    repo.edit(ADAPTER, lambda d: d["plans"]["free"].update(fetch_url="maybe"))
    assert rules(check_schemas.check(repo.root)) == ["schema:adapter.json"]


def test_adapter_unknown_capability_fails(repo):
    repo.edit(ADAPTER, lambda d: d["plans"]["free"].update(telepathy="no"))
    assert rules(check_schemas.check(repo.root)) == ["schema:adapter.json"]


def test_adapter_yaml_booleans_are_normalised(repo):
    data = repo.load(ADAPTER)
    assert data["plans"]["free"]["drive_read"] is True  # YAML 1.1 reads 'yes' as True
    assert check_schemas.check(repo.root) == []


def test_bad_eval_case_fails(repo):
    repo.edit(EVALS, lambda d: d["cases"][0].update(rules=["rule-6"]))
    problems = check_schemas.check(repo.root)
    assert rules(problems) == ["schema:eval-case.json"]
    assert problems[0].entry_id == "inj-001"


def test_bad_latest_json_fails(repo):
    path = repo.path("site/latest.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["critical"] = {"message": "Something changed", "issued": "2026-10-10",
                        "incident": "https://github.com/example/1"}
    path.write_text(json.dumps(data), encoding="utf-8")
    problems = check_schemas.check(repo.root)
    assert rules(problems) == ["schema:latest.json"]


def test_parse_error_is_reported(repo):
    repo.write(PACK, "schema: 1\nentries: [\n")
    (problem,) = check_schemas.check(repo.root)
    assert problem.rule == "parse"


def test_main_returns_zero_on_repo(capsys):
    assert check_schemas.main() == 0


def test_bad_places_fails(repo):
    repo.edit("knowledge/places.yaml", lambda d: d["cities"]["testcity"].pop("state"))
    assert rules(check_schemas.check(repo.root)) == ["schema:places.json"]
