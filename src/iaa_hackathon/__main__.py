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
    prepare = commands.add_parser(
        "prepare-data", help="Build source-preserving Step 2 policy tables and evidence"
    )
    prepare.add_argument("--data-dir", default=None)
    prepare.add_argument("--config", default="configs/project.json")
    prepare.add_argument("--cleaning-config", default="configs/cleaning.json")
    prepare.add_argument("--manifest", default="docs/evidence/expected-manifest.json")
    prepare.add_argument("--output-dir", default="outputs/step2/prepared")
    targets = commands.add_parser(
        "build-targets", help="Build Step 3 linkage, observed targets and maturity diagnostics"
    )
    targets.add_argument("--data-dir", default=None)
    targets.add_argument("--config", default="configs/project.json")
    targets.add_argument("--step2-dir", default="outputs/step2/prepared")
    targets.add_argument("--target-config", default="configs/target_construction.json")
    targets.add_argument("--scenario-config", default="configs/reserving_scenarios.json")
    targets.add_argument("--output-dir", default="outputs/step3/prepared")
    repairs = commands.add_parser("repair-step2", help="Build auditable Step 2 policy and claim repairs")
    repairs.add_argument("--data-dir", default=None)
    repairs.add_argument("--config", default="configs/project.json")
    repairs.add_argument("--output-dir", default="outputs/step2/repairs")
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
    if args.command == "repair-step2":
        try:
            from iaa_hackathon.step2_repairs import run_step2_repairs
            result = run_step2_repairs(data_dir=root, output_dir=Path(args.output_dir).resolve(), project_root=Path.cwd())
        except (ImportError, OSError, ValueError, KeyError) as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2)); return 2
        print(json.dumps({"status": result["status"], "output_dir": str(Path(args.output_dir).resolve()), "logical_digest": result["logical_digest"], "raw_hashes_unchanged": result["raw_hashes_unchanged"]}, indent=2)); return 0
    if args.command == "build-targets":
        try:
            from iaa_hackathon.targets_pipeline import build_targets

            result = build_targets(
                data_dir=root,
                step2_dir=Path(args.step2_dir).resolve(),
                output_dir=Path(args.output_dir).resolve(),
                target_config_path=Path(args.target_config).resolve(),
                scenario_config_path=Path(args.scenario_config).resolve(),
                project_root=Path.cwd(),
            )
        except (ImportError, OSError, ValueError, KeyError) as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
            return 2
        print(json.dumps({
            "status": result["status"],
            "output_dir": str(Path(args.output_dir).resolve()),
            "logical_output_digest": result["logical_output_digest"],
            "raw_hashes_unchanged": result["raw_hashes_unchanged"],
            "rerun_matches": result["rerun_comparison"]["matches_previous_run"],
        }, indent=2))
        return 0
    if args.command == "prepare-data":
        try:
            from iaa_hackathon.prepare import prepare_data

            result = prepare_data(
                data_dir=root,
                output_dir=Path(args.output_dir),
                cleaning_config_path=Path(args.cleaning_config).resolve(),
                reference_manifest_path=Path(args.manifest).resolve(),
                project_root=Path.cwd(),
            )
        except (ImportError, OSError, ValueError, KeyError) as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
            return 2
        print(json.dumps({
            "status": result["status"],
            "output_dir": str(Path(args.output_dir).resolve()),
            "logical_output_digest": result["logical_output_digest"],
            "raw_hashes_unchanged": result["raw_hashes_unchanged"],
        }, indent=2))
        return 0
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
