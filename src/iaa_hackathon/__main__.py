"""Command-line entry points for the IAA workflow."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="IAA workflow scaffold")
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="Check input file presence only")
    doctor.add_argument("--data-dir", default=None)
    doctor.add_argument("--config", default="configs/project.json")
    inventory = commands.add_parser(
        "inventory", help="Read Parquet metadata, required columns, hashes and key coverage"
    )
    inventory.add_argument("--data-dir", default=None)
    inventory.add_argument("--config", default="configs/project.json")
    inventory.add_argument("--manifest", default="docs/evidence/expected-manifest.json")
    inventory.add_argument("--output", default="outputs/step1/data-inventory.json")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text())
    except (OSError, ValueError) as exc:
        parser.error(f"Cannot read project configuration: {exc}")
    directory = args.data_dir or os.environ.get(config["data_dir_env"])
    if not directory:
        print(json.dumps({"status": "not_configured", "action": "Set IAA_DATA_DIR or --data-dir"}))
        return 2
    root = Path(directory).expanduser().resolve()
    if args.command == "inventory":
        try:
            from iaa_hackathon.inventory import build_inventory, write_inventory

            result, passed = build_inventory(root, Path(args.config), Path(args.manifest))
            write_inventory(result, Path(args.output))
        except (ImportError, OSError, ValueError, KeyError) as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
            return 2
        print(json.dumps({
            "status": result["status"],
            "output": str(Path(args.output).resolve()),
            "acceptance": result["acceptance"],
        }, indent=2))
        return 0 if passed else 1
    missing = [name for name in config["expected_files"] if not (root / name).is_file()]
    print(json.dumps({
        "status": "missing_files" if missing else "files_present",
        "data_dir": str(root),
        "expected_file_count": len(config["expected_files"]),
        "missing": missing,
        "scope": "File presence only; Parquet contents and row counts were not inspected by this command.",
    }, indent=2))
    return 2 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
