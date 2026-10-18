"""Check scaffold consistency and prevent accidental tracked data publication."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    required = [
        "README.md", "AGENTS.md", "CLAUDE.md", "context.md", "what-good-looks-like.md",
        "PROMPT_ALGORITHM.md", "PROMPT_LOGS.md", "docs/status.md", "docs/assumptions.md",
        "docs/evidence/known-findings.md", "docs/evidence/competition-sources.md",
        "src/iaa_hackathon/__main__.py", ".gitignore",
    ]
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f"Missing scaffold file: {name}")
    for number in range(8):
        if len(list((ROOT / "prompts").glob(f"{number:02d}-*.md"))) != 1:
            errors.append(f"Expected exactly one prompt numbered {number:02d}")
    try:
        config = json.loads((ROOT / "configs/project.json").read_text())
        manifest = json.loads((ROOT / "docs/evidence/expected-manifest.json").read_text())
        if set(config["expected_files"]) != {f["filename"] for f in manifest["files"]}:
            errors.append("Project file list and audit manifest differ")
        if config["expected_test_rows"] != 626639 or config["metric_power"] != 1.5:
            errors.append("Project metadata contradicts the verified competition contract")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Invalid project metadata: {exc}")

    git_root = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=False,
    )
    if git_root.returncode == 0 and Path(git_root.stdout.strip()).resolve() == ROOT:
        tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z"])
        banned = {".parquet", ".pq", ".arrow", ".feather", ".zip", ".csv", ".pkl", ".pickle", ".joblib"}
        for encoded in tracked.split(b"\0"):
            if not encoded:
                continue
            name = encoded.decode("utf-8")
            path = Path(name)
            synthetic_csv = name.startswith("tests/fixtures/synthetic/") and path.suffix == ".csv"
            if path.suffix.lower() in banned and not synthetic_csv:
                errors.append(f"Prohibited tracked data/output file: {name}")
            if path.name.startswith(".env") or name.startswith("configs/local"):
                errors.append(f"Prohibited tracked local configuration: {name}")
            if name.startswith(("data/", "outputs/")) and path.name != "README.md":
                errors.append(f"Prohibited tracked working file: {name}")
        print("Git index policy: checked")
    else:
        print("Git index policy: not checked; initialize Git in this directory before committing")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Step 0 scaffold checks passed. Step 1 behavior is not certified by this command.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
