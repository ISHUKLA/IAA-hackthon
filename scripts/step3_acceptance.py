"""Real-data acceptance checks for the ignored Step 3 output bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/step3/prepared")
    parser.add_argument("--step2-dir", default="outputs/step2/prepared")
    parser.add_argument("--data-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    manifest = json.loads((output / "target-manifest.json").read_text())
    reconciliation = json.loads((output / "target-reconciliation.json").read_text())
    errors: list[str] = []
    if manifest["status"] != "complete" or not manifest["raw_hashes_unchanged"]:
        errors.append("manifest incomplete or source claim hash changed")
    claims_hash = sha256_file(Path(args.data_dir) / "claims.parquet")
    if claims_hash != manifest["source_claims_sha256_before"]:
        errors.append("current claims file differs from Step 3 input")
    step2 = json.loads((Path(args.step2_dir) / "prepare-manifest.json").read_text())
    if step2["logical_output_digest"] != manifest["step2_manifest_digest"]:
        errors.append("current Step 2 manifest differs from Step 3 input")
    for name, expected in manifest["outputs"].items():
        path = output / name
        if not path.is_file() or sha256_file(path) != expected:
            errors.append(f"output identity failed: {name}")
    checks = reconciliation["identity_checks"]
    if not all(checks.values()):
        errors.append(f"reconciliation identity failed: {checks}")
    expected_rows = 2_409_311
    observed_rows = pq.read_metadata(output / "targets/observed-policy-response.parquet").num_rows
    candidate_rows = pq.read_metadata(output / "targets/target-candidates.parquet").num_rows
    if observed_rows != expected_rows or candidate_rows != expected_rows:
        errors.append(f"policy row count mismatch: observed={observed_rows}, candidates={candidate_rows}")
    expected_counts = {"exactly_one_match": 162_736, "unmatched": 414}
    actual_counts = {name: value["claim_count"] for name, value in reconciliation["by_disposition"].items()}
    if any(actual_counts.get(name) != value for name, value in expected_counts.items()):
        errors.append(f"linkage counts differ from independently audited reference: {actual_counts}")
    expected_minor = 74_433_067_704
    if reconciliation["accepted_total_observed_net_incurred_minor_units"] != expected_minor:
        errors.append("observed total differs from independently audited reference")
    tracked = set(subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines())
    prohibited = sorted(item for item in tracked if item.startswith("outputs/step3/"))
    if prohibited:
        errors.append(f"Step 3 row-level output is tracked: {prohibited}")
    if errors:
        print(json.dumps({"status": "failed", "errors": errors}, indent=2))
        return 1
    print(json.dumps({
        "status": "passed", "source_claim_count": reconciliation["source"]["claim_count"],
        "single_matches": actual_counts["exactly_one_match"], "unmatched": actual_counts["unmatched"],
        "ambiguous": actual_counts.get("ambiguous_multiple_match", 0),
        "policy_rows": observed_rows,
        "zero_claim_policy_rows": reconciliation["zero_claim_policy_row_count"],
        "observed_net_incurred": expected_minor / 100,
        "logical_output_digest": manifest["logical_output_digest"],
        "rerun_matches": manifest["rerun_comparison"]["matches_previous_run"],
        "human_financial_basis_and_scenario_review": "pending",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
