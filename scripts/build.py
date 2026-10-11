"""Build packs, bundled snapshot, per-tool skill packages and latest.json (make build).

Outputs (all deterministic: sorted keys, sorted zip entries, fixed timestamps):
  build/packs/<layer>-<scope>.json      one file per pack scope, entries and tasks sorted by id
  build/packs/resolved-<chain>.json     facts resolved for one place: university -> city ->
                                        state -> national; the most specific entry wins
  skill/reference/packs/*.md            bundled snapshot (Markdown), version-stamped
  build/skill-<tool>.zip                gemini, claude: SKILL.md + reference/ + own adapter
                                        copilot: one flattened instructions.md + packs.md +
                                        adapter
  build/latest.json                     versions, validated against knowledge/_schema/latest.json

Override rule: entries are matched across layers by "<topic>.<slug>" (the id without its scope).
Timestamps come from SOURCE_DATE_EPOCH, else the last commit, else 1980-01-01.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from jsonschema import Draft202012Validator

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    LAYER_DIRS,
    NATIONAL_SCOPE,
    PLACES,
    REPO_ROOT,
    SCHEMA_DIR,
    load_yaml,
    stringify_dates,
    yaml_files,
)

TOOLS = ("gemini", "claude", "copilot")
SKILL_NAME = "germany-companion"
SNAPSHOT_DIR = Path("skill/reference/packs")
BUILD_DIR = Path("build")
LAYER_ORDER = ("university", "city", "state", "national")
PHASE_NAMES = {
    0: "Admission", 1: "Visa and finance", 2: "First 2 weeks", 3: "First 90 days",
    4: "Each semester", 5: "Exams", 6: "Ongoing", 7: "Graduation",
}


class BuildError(Exception):
    pass


@dataclass
class Pack:
    layer: str
    scope: str
    entries: list[dict] = field(default_factory=list)
    tasks: list[dict] = field(default_factory=list)
    letters: list[dict] = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.layer}/{self.scope}"

    @property
    def version(self) -> str | None:
        dates = [i["last_verified"] for i in self.entries + self.tasks + self.letters
                 if i.get("last_verified")]
        return max(dates) if dates else None

    def as_json(self) -> dict:
        return {
            "schema": 1,
            "layer": self.layer,
            "scope": self.scope,
            "version": self.version,
            "entries": sorted(self.entries, key=lambda e: e["id"]),
            "tasks": sorted(self.tasks, key=lambda t: t["task_id"]),
            "letters": sorted(self.letters, key=lambda le: le["id"]),
        }


# ---------------------------------------------------------------- inputs

def source_date(root: Path) -> dt.datetime:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if not epoch:
        try:
            out = subprocess.run(["git", "log", "-1", "--format=%ct"], cwd=root,
                                 capture_output=True, text=True, encoding="utf-8",
                                 errors="replace", check=True)
            epoch = out.stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            epoch = ""
    if epoch:
        return dt.datetime.fromtimestamp(int(epoch), tz=dt.UTC)
    return dt.datetime(1980, 1, 1, tzinfo=dt.UTC)


def scope_for(path: Path, root: Path) -> tuple[str, str] | None:
    parts = path.relative_to(root / "knowledge").parts
    if not parts or parts[0] not in LAYER_DIRS:
        return None
    layer = LAYER_DIRS[parts[0]]
    if layer == "national":
        return layer, NATIONAL_SCOPE
    if len(parts) < 3:
        return None
    return layer, parts[1]


def load_packs(root: Path) -> dict[str, Pack]:
    packs: dict[str, Pack] = {}
    for path in yaml_files(root, "knowledge"):
        if path == root / PLACES:
            continue
        located = scope_for(path, root)
        if located is None:
            continue
        layer, scope = located
        data = stringify_dates(load_yaml(path))
        if not isinstance(data, dict):
            raise BuildError(f"{path}: not a mapping; run make validate")
        pack = packs.setdefault(f"{layer}/{scope}", Pack(layer, scope))
        if "letters" in path.parts:
            pack.letters.append(data)
        else:
            pack.entries.extend(data.get("entries") or [])
            pack.tasks.extend(data.get("tasks") or [])
    return dict(sorted(packs.items()))


def load_places(root: Path) -> dict:
    path = root / PLACES
    data = load_yaml(path) if path.is_file() else None
    return data or {"states": {}, "cities": {}, "universities": {}}


def chains(places: dict) -> dict[str, list[tuple[str, str]]]:
    """Resolution chains, most specific first. 'national' is always present."""
    result = {"national": [("national", NATIONAL_SCOPE)]}
    cities = places.get("cities") or {}
    for uni, info in sorted((places.get("universities") or {}).items()):
        city = info["city"]
        state = cities[city]["state"]
        result[uni] = [("university", uni), ("city", city), ("state", state),
                       ("national", NATIONAL_SCOPE)]
    return result


def override_key(item_id: str) -> str:
    return item_id.split(".", 1)[1]


def resolve(packs: dict[str, Pack], chain: list[tuple[str, str]]) -> dict:
    """Merge packs along a chain; the first (most specific) entry per key wins."""
    entries: dict[str, dict] = {}
    tasks: dict[str, dict] = {}
    letters: dict[str, dict] = {}
    for layer, scope in chain:
        pack = packs.get(f"{layer}/{scope}")
        if pack is None:
            continue
        for e in pack.entries:
            entries.setdefault(override_key(e["id"]), e)
        for t in pack.tasks:
            tasks.setdefault(override_key(t["task_id"]), t)
        for le in pack.letters:
            letters.setdefault(override_key(le["id"]), le)
    return {
        "chain": [f"{layer}/{scope}" for layer, scope in chain],
        "entries": sorted(entries.values(), key=lambda e: (e["phase"], e["topic"], e["id"])),
        "tasks": sorted(tasks.values(), key=lambda t: (t["phase"], t["task_id"])),
        "letters": sorted(letters.values(), key=lambda le: le["id"]),
    }


def read_versions(root: Path) -> dict:
    path = root / "versions.yaml"
    if not path.is_file():
        raise BuildError("versions.yaml is missing")
    data = load_yaml(path) or {}
    return {"skill": str(data.get("skill", "")), "template": str(data.get("template", ""))}


# ---------------------------------------------------------------- writers

def dump_json(data) -> str:
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def clean(root: Path) -> None:
    for folder in (root / BUILD_DIR, root / SNAPSHOT_DIR):
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*"), reverse=True):
            if path.name == "README.md" and path.parent == folder:
                continue
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()


def snapshot_markdown(name: str, title: str, resolved: dict, packs_version: str,
                      built: str) -> str:
    lines = [
        f"# Checked facts: {title}",
        "",
        f"Packs version {packs_version} · built {built} · resolution: "
        + " → ".join(resolved["chain"]),
        "",
        "Use only these facts for Germany-specific answers. Show the source link and the",
        "checked date. If the packs version is more than 90 days old, say so.",
        "",
    ]
    by_phase: dict[int, list[dict]] = {}
    for e in resolved["entries"]:
        by_phase.setdefault(e["phase"], []).append(e)
    for phase in sorted(by_phase):
        lines += [f"## Phase {phase}: {PHASE_NAMES.get(phase, '')}".rstrip(), ""]
        for e in by_phase[phase]:
            lines.append(f"- **{e['id']}** ({e['topic']}): {' '.join(e['text'].split())}")
            lines.append(f"  Source: {e['source_url']} · Checked: {e['last_verified']}")
        lines.append("")
    if resolved["tasks"]:
        lines += ["## Checklist tasks", ""]
        for t in resolved["tasks"]:
            due = t.get("due_offset_days")
            due_text = f" · due: {due:+d} days from semester start" if due is not None else ""
            deps = ", ".join(t.get("depends_on") or []) or "none"
            lines.append(f"- **{t['task_id']}** (phase {t['phase']}): {t['title']}")
            lines.append(f"  Why: {' '.join(t['why'].split())}{due_text} · after: {deps}")
            lines.append(f"  Source: {t['source_url']} · Checked: {t['last_verified']}")
        lines.append("")
    if resolved["letters"]:
        lines += ["## Letters", ""]
        for le in resolved["letters"]:
            senders = "; ".join(
                f"{s['name']} ({', '.join(s.get('domains') or []) or 'no email'})"
                for s in le["senders"])
            lines += [
                f"### {le['name']} ({le['id']})",
                f"- From: {senders}",
                f"- What it means: {' '.join(le['meaning'].split())}",
                f"- Deadline: {le['deadline_rule']}",
                f"- Next step: {' '.join(le['next_step'].split())}",
                f"- If missed: {le['if_missed']}",
                f"- Help: {le['referral']}",
                "- Scam signs: " + "; ".join(le["scam_signs"]),
                f"- Source: {le['source_url']} · Checked: {le['last_verified']}",
                "",
            ]
    return "\n".join(lines).rstrip() + "\n"


def snapshot_index(names: dict[str, str], packs_version: str, built: str,
                   skill_version: str) -> str:
    lines = [
        "# Bundled packs",
        "",
        f"Skill {skill_version} · packs version {packs_version} · built {built}",
        "",
        "Pick the file for the student's university from profile.md. If the university is not",
        "listed, use national.md and say that local facts are not covered yet.",
        "",
        "| File | Place |",
        "| --- | --- |",
    ]
    for file_name, title in names.items():
        lines.append(f"| {file_name} | {title} |")
    return "\n".join(lines) + "\n"


def zip_bytes_entries(path: Path, files: dict[str, bytes], when: dt.datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = max(when, dt.datetime(1980, 1, 1, tzinfo=dt.UTC)).timetuple()[:6]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=stamp)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, files[name])


def skill_sources(root: Path) -> dict[str, bytes]:
    """Core skill files, without folder READMEs, adapters or generated packs."""
    skill = root / "skill"
    files: dict[str, bytes] = {"SKILL.md": (skill / "SKILL.md").read_bytes()}
    ref = skill / "reference"
    if ref.is_dir():
        for path in sorted(ref.rglob("*")):
            relative = path.relative_to(skill).as_posix()
            if (path.is_dir() or path.name == "README.md"
                    or relative.startswith(("reference/adapters/", "reference/packs/"))):
                continue
            files[relative] = path.read_bytes()
    return files


def snapshot_files(root: Path) -> dict[str, bytes]:
    folder = root / SNAPSHOT_DIR
    return {f"reference/packs/{p.name}": p.read_bytes()
            for p in sorted(folder.glob("*.md")) if p.name != "README.md"}


def build_packages(root: Path, when: dt.datetime, log) -> list[str]:
    if not (root / "skill" / "SKILL.md").is_file():
        log("skip skill packages: skill/SKILL.md not written yet (task P9)")
        return []
    core = skill_sources(root)
    packs = snapshot_files(root)
    built = []
    for tool in TOOLS:
        adapter = root / "skill" / "reference" / "adapters" / f"{tool}.yaml"
        if not adapter.is_file():
            log(f"skip skill-{tool}.zip: no adapter at {adapter.relative_to(root).as_posix()}")
            continue
        prefix = f"{SKILL_NAME}/"
        if tool == "copilot":
            files = {
                prefix + "instructions.md": flatten(core),
                prefix + "packs.md": flatten(packs),
                prefix + f"{tool}.yaml": adapter.read_bytes(),
            }
        else:
            files = {prefix + k: v for k, v in {**core, **packs}.items()}
            files[prefix + f"reference/adapters/{tool}.yaml"] = adapter.read_bytes()
        out = root / BUILD_DIR / f"skill-{tool}.zip"
        zip_bytes_entries(out, files, when)
        built.append(out.name)
    return built


def flatten(files: dict[str, bytes]) -> bytes:
    """One Markdown file: SKILL.md first, then every other Markdown file with a marker."""
    order = sorted(files, key=lambda n: (n != "SKILL.md", n))
    parts = []
    for name in order:
        if not name.endswith(".md"):
            continue
        body = files[name].decode("utf-8").rstrip() + "\n"
        parts.append(body if name == "SKILL.md" else f"\n<!-- file: {name} -->\n\n{body}")
    return "".join(parts).encode("utf-8")


def validate_latest(root: Path, latest: dict) -> None:
    schema_path = root / SCHEMA_DIR / "latest.json"
    if not schema_path.exists():
        schema_path = REPO_ROOT / SCHEMA_DIR / "latest.json"
    validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))
    errors = [e.message for e in validator.iter_errors(latest)]
    if errors:
        raise BuildError("latest.json is invalid: " + "; ".join(errors))


# ---------------------------------------------------------------- main

def build(root: Path = REPO_ROOT, log=print) -> dict:
    when = source_date(root)
    built_day = when.date().isoformat()
    versions = read_versions(root)
    packs = load_packs(root)
    places = load_places(root)

    # Check everything that can fail before touching existing output.
    latest = {
        "schema": 1,
        "skill": versions["skill"],
        "template": versions["template"],
        "packs": {p.key: p.version for p in packs.values() if p.version},
        "critical": None,
        "notes": "",
    }
    validate_latest(root, latest)
    resolution = chains(places)

    clean(root)
    out = root / BUILD_DIR / "packs"
    for pack in packs.values():
        write(out / f"{pack.layer}-{pack.scope}.json", dump_json(pack.as_json()))

    all_versions = [p.version for p in packs.values() if p.version]
    packs_version = max(all_versions) if all_versions else built_day

    titles = {"national": "Germany (national only)"}
    for uni, info in (places.get("universities") or {}).items():
        titles[uni] = info["name"]
    index_rows = {}
    for name, chain in resolution.items():
        resolved = resolve(packs, chain)
        write(out / f"resolved-{name}.json", dump_json(resolved))
        write(root / SNAPSHOT_DIR / f"{name}.md",
              snapshot_markdown(name, titles[name], resolved, packs_version, built_day))
        index_rows[f"{name}.md"] = titles[name]
    write(root / SNAPSHOT_DIR / "index.md",
          snapshot_index(index_rows, packs_version, built_day, versions["skill"]))

    write(root / BUILD_DIR / "latest.json", dump_json(latest))

    packages = build_packages(root, when, log)
    summary = {
        "packs": len(packs),
        "chains": sorted(index_rows),
        "packages": packages,
        "packs_version": packs_version,
    }
    log(f"build: {len(packs)} pack(s), snapshot for {', '.join(sorted(index_rows))}, "
        f"{len(packages)} skill package(s), latest.json (packs {packs_version})")
    return summary


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO_ROOT
    try:
        build(root)
    except BuildError as exc:
        print(f"build: failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
