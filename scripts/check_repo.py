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
    # The original Step 0/1 prompts remain the scaffold contract. Later
    # versioned prompt sets may coexist without being mistaken for replacements.
    for name in (
        "00-scaffold.md", "01-sources.md", "02-data-inventory.md",
        "03-prediction-contract.md", "04-metric.md", "05-submission-contract.md",
        "06-challenge.md", "07-handoff.md",
    ):
        if not (ROOT / "prompts" / name).is_file():
            errors.append(f"Missing scaffold prompt: {name}")
    allowed_source_paths: set[str] = set()
    try:
        config = json.loads((ROOT / "configs/project.json").read_text())
        manifest = json.loads((ROOT / "docs/evidence/expected-manifest.json").read_text())
        if set(config["expected_files"]) != {f["filename"] for f in manifest["files"]}:
            errors.append("Project file list and audit manifest differ")
        if config["expected_test_rows"] != 626639 or config["metric_power"] != 1.5:
            errors.append("Project metadata contradicts the verified competition contract")
        # Explicit user-authorized source-data copies. Other inputs and all
        # generated row-level outputs remain prohibited in the index.
        allowed_source_paths = {f"data/public/{name}" for name in config["expected_files"]}
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
            source_input = name in allowed_source_paths
            if path.suffix.lower() in banned and not synthetic_csv and not source_input:
                errors.append(f"Prohibited tracked data/output file: {name}")
            if path.name.startswith(".env") or name.startswith("configs/local"):
                errors.append(f"Prohibited tracked local configuration: {name}")
            if (name.startswith(("data/", "outputs/")) and path.name != "README.md"
                    and not source_input and name != "data/public/manifest.json"):
                errors.append(f"Prohibited tracked working file: {name}")
            if source_input:
                pointer = subprocess.check_output(
                    ["git", "-C", str(ROOT), "show", f":{name}"], text=True,
                )
                if not pointer.startswith("version https://git-lfs.github.com/spec/v1\n"):
                    errors.append(f"Source input must use Git LFS: {name}")
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
