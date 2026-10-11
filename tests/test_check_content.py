import check_content
import pytest
from conftest import rules

PACK = "knowledge/national/registration.yaml"
CITY = "knowledge/cities/testcity/registration.yaml"
LETTER = "knowledge/national/letters/test-fee.yaml"


def test_good_fixture_passes(repo):
    assert check_content.check(repo.root) == []


def test_good_fixture_passes_on_main(repo, monkeypatch):
    monkeypatch.setenv("GSC_BRANCH", "main")
    assert check_content.check(repo.root) == []


# C1 source
def test_unofficial_domain_fails(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(source_url="https://someblog.example/x"))
    (p,) = check_content.check(repo.root)
    assert p.rule == "C1 source"
    assert "someblog.example" in p.message
    assert p.entry_id == "de.registration.deadline"
    assert "official-domains.txt" in p.fix


def test_subdomain_of_official_domain_passes(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(
        source_url="https://service.bund.example/registration"))
    assert check_content.check(repo.root) == []


def test_lookalike_domain_fails(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(source_url="https://fakebund.example/x"))
    assert rules(check_content.check(repo.root)) == ["C1 source"]


def test_http_source_fails(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(source_url="http://www.bund.example/x"))
    assert rules(check_content.check(repo.root)) == ["C1 source"]


def test_letter_source_checked(repo):
    repo.edit(LETTER, lambda d: d.update(source_url="https://forum.example/thread"))
    (p,) = check_content.check(repo.root)
    assert (p.rule, p.entry_id) == ("C1 source", "de.letters.test-fee")


# C2 last_verified
def test_future_last_verified_fails(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(last_verified="2026-12-01"))
    assert rules(check_content.check(repo.root)) == ["C2 date"]


def test_invalid_last_verified_fails(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(last_verified="2026-02-30"))
    assert rules(check_content.check(repo.root)) == ["C2 date"]


# C3 expiry
def test_default_expiry_six_months(repo, monkeypatch):
    monkeypatch.setenv("GSC_TODAY", "2027-04-01")  # entry verified 2026-10-01 -> ok
    problems = [p for p in check_content.check(repo.root) if p.entry_id.startswith("de.reg")]
    assert problems == []
    monkeypatch.setenv("GSC_TODAY", "2027-04-02")  # one day past the default
    problems = [p for p in check_content.check(repo.root)
                if p.entry_id == "de.registration.deadline"]
    assert rules(problems) == ["C3 expiry"]
    assert "2027-04-01" in problems[0].message


def test_explicit_expiry_passed_fails(repo):
    repo.edit("knowledge/states/teststate/ticket.yaml",
              lambda d: d["entries"][0].update(expires="2026-10-01"))
    assert rules(check_content.check(repo.root)) == ["C3 expiry"]


def test_expiry_before_verified_fails(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(expires="2026-09-01"))
    (p,) = check_content.check(repo.root)
    assert p.rule == "C3 expiry" and "not after" in p.message


def test_invalid_expiry_fails(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(expires="soon"))
    assert rules(check_content.check(repo.root)) == ["C3 expiry"]


# C4 reviewer
def test_empty_reviewer_allowed_on_branch(repo):
    repo.edit(PACK, lambda d: d["entries"][0].update(reviewer=""))
    assert check_content.check(repo.root) == []


@pytest.mark.parametrize("env", [{"GSC_BRANCH": "main"}, {"GITHUB_REF_TYPE": "tag"}])
def test_empty_reviewer_fails_on_main_or_tag(repo, monkeypatch, env):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    repo.edit(PACK, lambda d: d["tasks"][0].update(reviewer=""))
    (p,) = check_content.check(repo.root)
    assert (p.rule, p.entry_id) == ("C4 reviewer", "de.registration.book-appointment")


# C5 layer, scope, id
def test_wrong_layer_for_folder_fails(repo):
    repo.edit(CITY, lambda d: d["entries"][0].update(layer="state"))
    assert rules(check_content.check(repo.root)) == ["C5 layer"]


def test_wrong_scope_for_folder_fails(repo):
    repo.edit(CITY, lambda d: d["entries"][0].update(
        scope="othercity", id="othercity.registration.office"))
    assert rules(check_content.check(repo.root)) == ["C5 scope"]


def test_id_not_matching_scope_topic_fails(repo):
    repo.edit(CITY, lambda d: d["entries"][0].update(id="testcity.housing.office"))
    assert rules(check_content.check(repo.root)) == ["C5 id"]


def test_task_id_not_matching_scope_fails(repo):
    def change(d):
        d["tasks"][0]["task_id"] = "othercity.registration.visit-office"
    repo.edit(CITY, change)
    assert rules(check_content.check(repo.root)) == ["C5 id"]


def test_letter_in_wrong_layer_fails(repo):
    repo.edit(LETTER, lambda d: d.update(layer="city"))
    assert rules(check_content.check(repo.root)) == ["C5 layer"]


# C6 unique ids
def test_duplicate_id_fails(repo):
    repo.edit(PACK, lambda d: d["entries"].append(dict(d["entries"][0])))
    (p,) = check_content.check(repo.root)
    assert p.rule == "C6 unique"


# C7 depends_on
def test_unknown_dependency_fails(repo):
    repo.edit(CITY, lambda d: d["tasks"][0].update(depends_on=["de.registration.nothing"]))
    (p,) = check_content.check(repo.root)
    assert (p.rule, p.entry_id) == ("C7 depends_on", "testcity.registration.visit-office")


def test_malformed_items_are_left_to_schema_check(repo):
    repo.write("knowledge/national/broken.yaml", "entries:\n  - just a string\n")
    repo.write("knowledge/national/list.yaml", "- a\n- b\n")
    repo.write("knowledge/national/bad.yaml", "entries: [\n")
    assert check_content.check(repo.root) == []


def test_files_outside_layer_folders_skip_layer_rules(repo):
    repo.dump("knowledge/misc/x.yaml", repo.load(PACK) | {"tasks": []})
    problems = check_content.check(repo.root)
    assert rules(problems) == ["C6 unique"]  # same id as the national file, no C5 problems


# C8 places
def test_scope_missing_from_places_fails(repo):
    repo.edit("knowledge/places.yaml", lambda d: d["universities"].pop("testuni"))
    (p,) = check_content.check(repo.root)
    assert p.rule == "C8 places"
    assert p.path == "knowledge/universities/testuni/enrolment.yaml"
    assert "university 'testuni'" in p.message


def test_city_with_unknown_state_fails(repo):
    repo.edit("knowledge/places.yaml", lambda d: d["cities"]["testcity"].update(state="nowhere"))
    (p,) = check_content.check(repo.root)
    assert p.rule == "C8 places" and "unknown state 'nowhere'" in p.message


def test_university_with_unknown_city_fails(repo):
    repo.edit("knowledge/places.yaml", lambda d: d["universities"]["testuni"].update(city="x"))
    (p,) = check_content.check(repo.root)
    assert p.rule == "C8 places" and "unknown city 'x'" in p.message


def test_missing_places_file_flags_every_local_scope(repo):
    repo.path("knowledge/places.yaml").unlink()
    problems = check_content.check(repo.root)
    assert sorted(rules(problems)) == ["C8 places"] * 3


def test_unparseable_places_is_left_to_schema_check(repo):
    repo.write("knowledge/places.yaml", "states: [\n")
    assert set(rules(check_content.check(repo.root))) == {"C8 places"}


def test_main_returns_zero_on_repo():
    assert check_content.main() == 0
