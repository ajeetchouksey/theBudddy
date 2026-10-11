"""Build the spike probe packages into build/spike/ (docs/spike-results.md, tests 1, 14–16).

  python spike/make_probe_packages.py --webapp-url URL --fetch-url URL

Outputs
  probe-skill.zip                Gemini / Claude import (SKILL.md + reference/)
  probe-copilot/instructions.md  Copilot: everything flattened into one file
  probe-copilot/packs.md         Copilot: reference facts as an uploadable file
  limits-files-<n>.zip           n reference files of 20 KB each (count limit)
  limits-size-<s>.zip            one reference file of size s (size limit)
  limits-answers.md              the code at the end of every limits file, to check answers

Placeholders: WEBAPP_URL (Apps Script probe) and FETCH_URL (public probe-latest.json). Without
the options they stay as text, and the matching tests cannot pass.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKILL = HERE / "probe-skill"
OUT = ROOT / "build" / "spike"
STAMP = (2026, 10, 11, 0, 0, 0)
FILE_COUNTS = (10, 25, 50)
SIZES = {"256k": 256 * 1024, "1m": 1024 * 1024, "2m": 2 * 1024 * 1024}
FILLER = ("Filler text for the spike limits test. It carries no facts and no instructions. "
          "Only the code on the last line matters.\n")


def code(label: str) -> str:
    return "PROBE-END-" + hashlib.sha256(label.encode()).hexdigest()[:6].upper()


def filler_file(label: str, size: int) -> str:
    body = FILLER * (size // len(FILLER) + 1)
    tail = f"\nEnd code for {label}: {code(label)}\n"
    return body[: max(0, size - len(tail))] + tail


def core_files(webapp_url: str, fetch_url: str) -> dict[str, str]:
    files = {"SKILL.md": (SKILL / "SKILL.md").read_text(encoding="utf-8")}
    for path in sorted((SKILL / "reference").iterdir()):
        text = path.read_text(encoding="utf-8")
        text = text.replace("WEBAPP_URL", webapp_url).replace("FETCH_URL", fetch_url)
        files[f"reference/{path.name}"] = text
    return files


def write_zip(path: Path, files: dict[str, str], root: str = "spike-probe") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(files):
            info = zipfile.ZipInfo(f"{root}/{name}", date_time=STAMP)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, files[name].encode("utf-8"))


def flatten(files: dict[str, str]) -> str:
    parts = [files["SKILL.md"].rstrip() + "\n"]
    for name in sorted(files):
        if name != "SKILL.md" and name.endswith(".md"):
            parts.append(f"\n<!-- file: {name} -->\n\n{files[name].rstrip()}\n")
    return "".join(parts)


def build(webapp_url: str, fetch_url: str, out: Path = OUT) -> list[str]:
    core = core_files(webapp_url, fetch_url)
    made = []

    write_zip(out / "probe-skill.zip", core)
    made.append("probe-skill.zip")

    copilot = out / "probe-copilot"
    copilot.mkdir(parents=True, exist_ok=True)
    (copilot / "instructions.md").write_text(flatten(core), encoding="utf-8", newline="\n")
    (copilot / "packs.md").write_text(core["reference/probe-facts.md"], encoding="utf-8",
                                      newline="\n")
    made.append("probe-copilot/")

    answers = ["# Limits answers", "",
               "Check `probe last` and `probe end <n>` against these codes.", "",
               "| Package | File | End code |", "| --- | --- | --- |"]
    for count in FILE_COUNTS:
        name = f"limits-files-{count}"
        files = dict(core)
        for i in range(1, count + 1):
            label = f"{name}/fill-{i:03d}"
            files[f"reference/fill-{i:03d}.md"] = filler_file(label, 20 * 1024)
        write_zip(out / f"{name}.zip", files)
        made.append(f"{name}.zip")
        for i in (1, count // 2, count):
            answers.append(f"| {name} | fill-{i:03d}.md | {code(f'{name}/fill-{i:03d}')} |")
    for label_size, size in SIZES.items():
        name = f"limits-size-{label_size}"
        files = dict(core)
        files["reference/fill-001.md"] = filler_file(f"{name}/fill-001", size)
        write_zip(out / f"{name}.zip", files)
        made.append(f"{name}.zip")
        answers.append(f"| {name} | fill-001.md | {code(f'{name}/fill-001')} |")
    (out / "limits-answers.md").write_text("\n".join(answers) + "\n", encoding="utf-8",
                                           newline="\n")
    made.append("limits-answers.md")
    return made


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--webapp-url", default="WEBAPP_URL",
                        help="Apps Script probe web app URL (ends in /exec)")
    parser.add_argument("--fetch-url", default="FETCH_URL",
                        help="public URL of spike/probe-latest.json")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)
    for flag, value, placeholder in (("--webapp-url", args.webapp_url, "WEBAPP_URL"),
                                     ("--fetch-url", args.fetch_url, "FETCH_URL")):
        if value == placeholder:
            print(f"note: {flag} not set; tests that need it cannot pass yet")
        elif not value.startswith("https://"):
            print(f"error: {flag} must be an https:// URL")
            return 1
    made = build(args.webapp_url, args.fetch_url, Path(args.out))
    print(f"spike: wrote {len(made)} item(s) to {args.out}: {', '.join(made)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
