"""Step 10 evidence/package controls; never changes the frozen model or CSV."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from iaa_hackathon.final_submission import (
    build_csv, build_model, check_hashes, environment, preflight, read_json,
    save_json, sha,
)
from iaa_hackathon.baselines import score_vector


QUALITY_STATUSES = {"pass", "partial", "fail", "not_applicable", "not_testable"}
READINESS_STATUSES = {"ready_for_part1_upload", "ready_with_disclosures", "blocked", "failed_verification"}
REQUIRED_CRITERIA = set("O01 O02 O03 O04 A01 A02 A03 A04 A05 A06 A07 A08 A09 P01 P02 P03 P04 P05 P06 P07 P08 U01 U02 U03 U04 U05 G01 G02 G03 G04 G05 G06 G07 G08 C01 C02 C03 C04 C05 C06 C07 H01 H02 H03".split())
SECRETS = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}|sk-proj-[A-Za-z0-9_-]{25,}")
MACHINE_PATH = re.compile(r"/(?:Users|home)/[^/\s'\"]+/|/private/var/folders/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/")
FORBIDDEN_SUFFIXES = {".csv", ".parquet", ".pq", ".arrow", ".feather", ".joblib", ".pkl", ".pickle", ".zip", ".pyc"}


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def relative(path: str | Path, root: Path | None = None) -> str:
    root = (root or Path.cwd()).resolve()
    return str(Path(path).resolve().relative_to(root))


def check_freeze(frozen: dict) -> None:
    check_hashes(frozen["assets_sha256"])
    info = Path(frozen["submission"]["path"]).stat()
    if info.st_size != frozen["submission"]["bytes"] or info.st_mtime_ns != frozen["submission"]["mtime_ns"]:
        raise ValueError("frozen candidate file was rewritten or resized")


def freeze_candidate(output: Path) -> dict:
    path = output / "frozen-candidate.json"
    if path.exists():
        frozen = read_json(path)
        check_freeze(frozen)
        return frozen
    manifest_path = Path("outputs/step9/submission-manifest.json")
    manifest, status = read_json(manifest_path), read_json(Path("outputs/step9/status.json"))
    if manifest["status"] != "ready_for_human_review" or status["status"] != "ready_for_human_review":
        raise ValueError("Step 9 is not ready_for_human_review")
    if sha(manifest_path) != status["manifest_sha256"]:
        raise ValueError("Step 9 manifest/status hash mismatch")
    decision = read_json(Path("outputs/step8/decision.json"))
    cfg_path = Path("configs/final_model.json")
    cfg = read_json(cfg_path)
    if decision["decision"] != "retain_benchmark" or cfg["model_id"] != decision["benchmark"]:
        raise ValueError("selected model conflicts with the Step 8 authority")
    csv = Path(manifest["csv_path"])
    csv_relative = relative(csv)
    assets = {str(manifest_path): sha(manifest_path), str(cfg_path): manifest["config_sha256"], csv_relative: manifest["csv_sha256"], "outputs/step9/status.json": sha(Path("outputs/step9/status.json")), "outputs/step9/model-manifest.json": manifest["model_manifest_sha256"], cfg["environment_lock"]: sha(Path(cfg["environment_lock"]))}
    assets.update(cfg["code_sha256"])
    assets.update({str(Path("outputs/step9") / p): h for p, h in manifest["model_artifacts_sha256"].items()})
    check_hashes(assets)
    if manifest["upload_status"] != "not_uploaded" or manifest["final_kaggle_selection"] != "pending":
        raise ValueError("unexpected external-action status; obtain verifiable evidence")
    info = csv.stat()
    frozen = {"created_utc": stamp(), "step9_manifest_sha256": sha(manifest_path), "model_id": cfg["model_id"], "response_version": cfg["response_version"], "config_id": cfg["config_id"], "assets_sha256": assets, "submission": {"path": csv_relative, "sha256": manifest["csv_sha256"], "rows": manifest["rows"], "prediction_total": manifest["prediction_total"], "totals_by_line": manifest["prediction_totals_by_line"], "bytes": info.st_size, "mtime_ns": info.st_mtime_ns}, "upload_status": "not_uploaded", "human_review": "pending"}
    save_json(path, frozen, exclusive=True)
    return frozen


def verify_candidate(output: Path, data_dir: Path) -> dict:
    start = time.perf_counter()
    frozen = freeze_candidate(output)
    result = subprocess.run([sys.executable, "scripts/step9.py", "verify", "--data-dir", str(data_dir)], text=True, capture_output=True, check=True)
    actual = json.loads(result.stdout)
    if actual["csv_sha256"] != frozen["submission"]["sha256"] or actual["rows"] != 626639:
        raise ValueError("Step 9 verification differs from frozen candidate")
    if not np.isclose(actual["prediction_total"], frozen["submission"]["prediction_total"], rtol=0, atol=1e-7):
        raise ValueError("frozen financial total mismatch")
    for line, expected in frozen["submission"]["totals_by_line"].items():
        if not np.isclose(actual["prediction_totals_by_line"][line], expected, rtol=0, atol=1e-7):
            raise ValueError("frozen line total mismatch")
    check_freeze(frozen)
    # A committed state may follow the historical dirty generation snapshot.
    # Check recorded numerical code, not equality of today's HEAD with old HEAD.
    original = read_json(Path("outputs/step9/submission-manifest.json"))
    check_hashes(original["code_sha256"])
    check_hashes(original["git"]["snapshot_artifacts_sha256"])
    actual["csv_path"] = frozen["submission"]["path"]
    report = {"status": "passed", "checked_utc": stamp(), "runtime_seconds": time.perf_counter() - start, "command": "make verify-submission PYTHON=.venv/bin/python DATA_DIR='<official-public-directory>'", "verification": actual, "frozen_assets_unchanged": True, "historical_git_snapshot_verified": True, "environment": environment(Path("requirements/step7-py312.lock")), "stderr_warning_count": result.stderr.count("warning") + result.stderr.count("IOError"), "note": "Original absolute-path manifest is preserved as historical private evidence; this report uses repository-relative references."}
    save_json(output / "candidate-verification.json", report)
    return report


def reproduce_candidate(output: Path, data_dir: Path) -> dict:
    start = time.perf_counter()
    frozen = freeze_candidate(output)
    preflight(Path("configs/final_model.json"), data_dir)
    fresh = Path(tempfile.mkdtemp(prefix="clean-reproduction-", dir=output))
    cfg = read_json(Path("configs/final_model.json"))
    # Faithful numerical-code snapshot plus a new empty artifact namespace.
    for name, expected in cfg["code_sha256"].items():
        destination = fresh / "code-snapshot" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(name, destination)
        if sha(destination) != expected:
            raise ValueError("numerical code snapshot mismatch")
    model = build_model(Path("configs/final_model.json"), data_dir, fresh)
    result = build_csv(Path("configs/final_model.json"), data_dir, fresh, fresh / "submissions")
    if result["csv_sha256"] != frozen["submission"]["sha256"]:
        raise ValueError("rebuild is not byte-for-byte identical; do not replace the candidate")
    original = read_json(Path("outputs/step9/model-manifest.json"))
    if model["artifacts_sha256"] != original["artifacts_sha256"]:
        raise ValueError("saved fitted artifacts do not reproduce exactly")
    check_freeze(frozen)
    report = {"status": "passed", "checked_utc": stamp(), "mode": "exact_byte_for_byte", "csv_sha256": result["csv_sha256"], "models_and_schemas_byte_identical": True, "original_candidate_untouched": True, "fresh_fit_count": 3, "fresh_artifact_directory": relative(fresh), "code_snapshot_sha256": cfg["code_sha256"], "runtime_seconds": time.perf_counter() - start, "command": "make reproduce-part1 PYTHON=.venv/bin/python DATA_DIR='<official-public-directory>'", "scope": "one unchanged controlled refit per line, solely reproducibility; no model selection or target development"}
    save_json(output / "reproduction.json", report)
    return report


def safe_package_path(name: str) -> None:
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name or not p.parts:
        raise ValueError(f"unsafe package path: {name}")
    if any(part in {".git", ".venv", "venv", "__pycache__", "data", "submissions", ".aws", "credentials", "id_rsa", "id_ed25519"} or part.startswith(".env") for part in p.parts):
        raise ValueError(f"excluded package path: {name}")
    if p.suffix.lower() in FORBIDDEN_SUFFIXES or p.name.startswith("local") and p.suffix == ".json":
        raise ValueError(f"excluded package type: {name}")


def inspect_package_file(path: Path) -> None:
    safe_package_path(path.as_posix())
    if path.is_symlink() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError(f"symlink or excessive package file: {path}")
    text = path.read_text(encoding="utf-8")
    if SECRETS.search(text) or MACHINE_PATH.search(text):
        raise ValueError(f"secret or machine-specific home path in package file: {path}")


def validate_matrix(rows: list[dict]) -> None:
    required = {"id", "domain", "requirement", "source", "status", "evidence", "verification", "limitation", "action", "owner", "critical"}
    seen = set()
    for row in rows:
        if required - row.keys() or row["status"] not in QUALITY_STATUSES or row["id"] in seen:
            raise ValueError("incomplete, duplicate or invalid quality criterion")
        seen.add(row["id"])
        if not row["evidence"] or not row["verification"] or not row["owner"]:
            raise ValueError("criterion lacks evidence/verification/ownership")
        for evidence in row["evidence"]:
            path = Path(evidence.split("#", 1)[0])
            if not path.is_file():
                raise ValueError(f"criterion evidence missing: {path}")
    if REQUIRED_CRITERIA - seen:
        raise ValueError("quality matrix omits required criteria; critical gaps cannot be deleted")


def readiness(rows: list[dict], *, integrity: bool, reproduced: bool) -> str:
    if not integrity or not reproduced:
        return "failed_verification"
    if any(r["critical"] and r["status"] not in {"pass", "not_applicable"} for r in rows):
        return "blocked"
    if any(r["status"] in {"partial", "fail", "not_testable"} for r in rows):
        return "ready_with_disclosures"
    return "ready_for_part1_upload"


def matrix_markdown(rows: list[dict]) -> str:
    text = "# Step 10 quality-bar matrix\n\nAI/automated review, not independent human approval. A pass requires inspected evidence, not document presence. Critical gaps are never averaged away. Historical official extracts are dated 18 October 2026; current retrieval failed.\n\n"
    for domain in dict.fromkeys(r["domain"] for r in rows):
        text += f"## {domain}\n\n| ID / requirement | Source | Status | Evidence / section | Verification performed | Limitation | Required action / owner |\n| --- | --- | --- | --- | --- | --- | --- |\n"
        for r in rows:
            if r["domain"] == domain:
                fields = [r["id"] + (" CRITICAL" if r["critical"] else "") + " — " + r["requirement"], r["source"], r["status"], "; ".join(r["evidence"]), r["verification"], r["limitation"], r["action"] + " / " + r["owner"]]
                text += "| " + " | ".join(str(f).replace("|", "/").replace("\n", " ") for f in fields) + " |\n"
        text += "\n"
    return text


def aggregate_review(output: Path, data_dir: Path) -> dict:
    frozen = freeze_candidate(output)
    preflight(Path("configs/final_model.json"), data_dir)
    base = pd.read_parquet("outputs/step2/repairs/model/training-model-table.parquet", columns=["row_id", "address_id", "line", "period_start", "observed_net_incurred", "exposure_clean"])
    addresses = pd.read_parquet(data_dir / "addresses.parquet", columns=["address_id", "region"])
    if addresses.address_id.isna().any() or addresses.address_id.duplicated().any() or addresses.region.isna().any():
        raise ValueError("unsafe region dimension")
    regions = []
    years = pd.to_datetime(base.period_start).dt.year
    for fold, year in (("F2023", 2023), ("F2024", 2024)):
        valid = base[years.eq(year)]
        pred = pd.read_parquet(f"outputs/step6/features/predictions/{fold}-selected.parquet")
        if pred.row_id.isna().any() or pred.row_id.duplicated().any() or set(pred.row_id) != set(valid.row_id):
            raise ValueError("region review prediction coverage differs")
        if not pred.response_version.eq(frozen["response_version"]).all() or not pred.fold_id.eq(fold).all() or not pred.prediction_unit.eq("policy_period_cost").all():
            raise ValueError("region review response/units differ")
        joined = valid.merge(pred[["row_id", "prediction"]], on="row_id", validate="one_to_one").merge(addresses, on="address_id", validate="many_to_one", how="left")
        if len(joined) != len(valid) or joined.region.isna().any():
            raise ValueError("region join multiplied or lost rows")
        for (line, region), group in joined.groupby(["line", "region"]):
            regions.append({"fold": fold, "line": line, "region": region, "exposure": float(group.exposure_clean.sum()), **score_vector(group.observed_net_incurred.to_numpy(float), group.prediction.to_numpy(float))})
    claims = pd.read_parquet("outputs/step2/repairs/claims/matched.parquet", columns=["line", "peril", "loss_date", "status", "accepted_for_observed", "observed_net_incurred", "case_reserve"])
    selected = claims[claims.accepted_for_observed & ((claims.line.eq("motor") & claims.peril.eq("bodily_injury")) | (claims.line.eq("buildings") & claims.peril.eq("subsidence")))].copy()
    selected["year"] = pd.to_datetime(selected.loss_date).dt.year
    maturity = []
    for (line, peril, year), group in selected.groupby(["line", "peril", "year"]):
        maturity.append({"line": line, "peril": peril, "year": int(year), "accepted_known_claims": len(group), "open_claims": int(group.status.eq("open").sum()), "open_share": float(group.status.eq("open").mean()), "observed_net_incurred": float(group.observed_net_incurred.sum()), "case_balance": float(group.case_reserve.sum()), "case_0p8_reference_delta": float(-.2 * group.case_reserve.sum()), "case_1p2_reference_delta": float(.2 * group.case_reserve.sum())})
    if not maturity or not any(r["peril"] == "bodily_injury" for r in maturity) or not any(r["peril"] == "subsidence" for r in maturity):
        raise ValueError("expected immature peril labels missing; do not invent matches")
    check_freeze(frozen)
    schema_identifiers = {}
    for name in ("outputs/step2/repairs/model/training-model-table.parquet", "outputs/step2/repairs/model/test-model-table.parquet", "outputs/step2/repairs/claims/matched.parquet"):
        schema = pq.read_schema(name)
        schema_identifiers[name] = {"file_sha256": sha(Path(name)), "arrow_schema_sha256": hashlib.sha256(schema.serialize().to_pybytes()).hexdigest(), "schema_hash_semantics": "pyarrow 26 serialized schema including metadata", "columns": [{"name": f.name, "type": str(f.type), "nullable": f.nullable} for f in schema]}
    report = {"status": "passed", "response_version": frozen["response_version"], "region_calibration": regions, "peril_maturity": maturity, "schema_identifiers": schema_identifiers, "purpose": "post-selection aggregate review only; unchanged predictions; case stresses are reference arithmetic, not ultimate estimates or refitted scenario forecasts"}
    save_json(output / "aggregate-review.json", report)
    return report


def inventory(output: Path) -> dict:
    names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"]).decode().split("\0")
    roots = ("src/", "scripts/", "tests/", "configs/", "schemas/", "requirements/", "docs/", "reports/", "prompts/", ".github/")
    top = {"README.md", "AGENTS.md", "CLAUDE.md", "context.md", "what-good-looks-like.md", "Makefile", "pyproject.toml", ".gitignore", "MODEL_CARD.md", "DATA_CARD.md", "SYSTEM_CARD.md", "PROMPT_LOGS.md", "LICENSE", "LICENSE.md"}
    files = set(n for n in names if n and (n.startswith(roots) or n in top) and Path(n).suffix.lower() not in FORBIDDEN_SUFFIXES)
    files.update(str(output / name) for name in ("frozen-candidate.json", "candidate-verification.json", "reproduction.json", "aggregate-review.json", "tests.json"))
    records = []
    for name in sorted(files):
        path = Path(name)
        inspect_package_file(path)
        records.append({"path": name, "sha256": sha(path), "bytes": path.stat().st_size})
    digest = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    report = {"status": "passed", "format": "local inventory, not an archive or competition upload", "inventory_sha256": digest, "files": records, "excluded": ["raw data", "row-level CSV/Parquet and fitted objects (referenced separately, not payload)", "private historical manifests containing absolute paths", "caches/environments/credentials/archives", "unnecessary fitted search artifacts"], "limitations": "Text and credential/home-path checks are bounded safeguards, not a legal or exhaustive privacy certification. Restricted inputs/evidence remain separately controlled."}
    save_json(output / "package-inventory.json", report)
    return report


def verify_inventory(value: dict) -> None:
    records = value["files"]
    if not records or len({r["path"] for r in records}) != len(records):
        raise ValueError("empty or duplicate package inventory")
    expected = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if expected != value["inventory_sha256"]:
        raise ValueError("package inventory digest differs")
    for record in records:
        inspect_package_file(Path(record["path"]))
        if sha(Path(record["path"])) != record["sha256"] or Path(record["path"]).stat().st_size != record["bytes"]:
            raise ValueError(f"package payload hash/size differs: {record['path']}")


def git_identity() -> dict:
    def git(*args):
        return subprocess.check_output(["git", *args])
    patch = git("diff", "HEAD", "--binary")
    untracked = {n: sha(Path(n)) for n in git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0") if n}
    return {"head": git("rev-parse", "HEAD").decode().strip(), "branch": git("branch", "--show-current").decode().strip(), "origin": git("remote", "get-url", "origin").decode().strip(), "dirty": bool(git("status", "--porcelain")), "tracked_patch_sha256": hashlib.sha256(patch).hexdigest(), "untracked_files_sha256": untracked, "combined_worktree_sha256": hashlib.sha256(patch + json.dumps(untracked, sort_keys=True).encode()).hexdigest()}


def build_handoff(output: Path) -> dict:
    frozen = freeze_candidate(output)
    rows = read_json(Path("configs/step10_quality_review.json"))["rows"]
    verified, reproduced, tested = (read_json(output / p) for p in ("candidate-verification.json", "reproduction.json", "tests.json"))
    integrity = verified["status"] == "passed" and verified["verification"]["csv_sha256"] == frozen["submission"]["sha256"]
    exact = reproduced["status"] == "passed" and reproduced["csv_sha256"] == frozen["submission"]["sha256"] and reproduced["mode"] == "exact_byte_for_byte"
    if tested["status"] != "passed" or tested["passed_tests"] <= 0:
        raise ValueError("meaningful current test evidence missing")
    check_hashes(tested["code_sha256"])
    status = readiness(rows, integrity=integrity, reproduced=exact)
    critical = [r for r in rows if r["critical"] and r["status"] not in {"pass", "not_applicable"}]
    counts = {d: dict(Counter(r["status"] for r in rows if r["domain"] == d)) for d in dict.fromkeys(r["domain"] for r in rows)}
    report = f"# Step 10 final readiness\n\nStatus: **`{status}`**. This is an AI/automated quality review, not independent human approval. Correct CSV structure does not settle target adequacy or current official requirements.\n\n"
    report += f"Selected model: `{frozen['model_id']}`; response `{frozen['response_version']}`; CSV SHA-256 `{frozen['submission']['sha256']}`. {frozen['submission']['rows']:,} policy-period rows, {frozen['submission']['prediction_total']:.8f} CU. Frozen Step 9 assets remain unchanged.\n\n## Critical gaps\n\n"
    for r in critical:
        report += f"- {r['id']} ({r['status']}): {r['requirement']}. {r['action']} Owner: {r['owner']}.\n"
    report += "\nNo averaging is used to hide these gaps. The observed snapshot proxy is honestly labelled but does not satisfy the ultimate-target quality bar. Human acceptance of disclosure alone cannot manufacture monetary ultimate evidence. Any change to target/model/predictions goes back to the relevant earlier step and a new Step 9 candidate.\n\n## Quality by domain\n\n```json\n" + json.dumps(counts, indent=2) + "\n```\n\n"
    report += f"## Actual machine verification\n\nSelected tests: {tested['passed_tests']} passed in {tested['runtime_seconds']:.3f} seconds. Frozen-file verification passed in {verified['runtime_seconds']:.3f} seconds, including the existing Step 9 validator and saved-model equivalence. Fresh three-model reproduction passed in {reproduced['runtime_seconds']:.3f} seconds with identical CSV, model and schema bytes. Raw/source hashes and the historical dirty-state numerical provenance were verified; current Git publication history is not substituted into the old manifest. Region and peril review is post-selection only.\n\n"
    report += "Commands actually executed: `make step10-check`, `make verify-submission`, `make reproduce-part1`, `make verify-part1-package`; all used the pinned local Python and the caller's private official-data directory where needed. `make step10-acceptance` verifies the resulting package and frozen asset hashes; its actual result is saved separately in outputs/step10/acceptance.json. A machine acceptance pass is NOT an upload-readiness pass.\n\n"
    report += "## Handoff and next decisions\n\nThe seven Part 1 narrative/audit files, unchecked human checklist, quality matrix, source-access record, triaged issues and Part 2 handoff are the review package. It is a local inventory, not a new archive, final paginated report or video. Current official deliverable timing, deadlines and limits were not retrieved. Complete real human target/basis/model review, verify current rules, and confirm final report/video requirements; then separately authorise upload and final entry selection if appropriate. All checklist items remain unchecked. No professional compliance, leaderboard result, independent sign-off or time-savings claim is invented.\n\nThe submission file has not been uploaded to Kaggle.\nNo final Kaggle entry has been selected.\nPart 2 has not been executed.\n\nStop after Step 10. Next action is resolution of the listed human/rules/earlier-methodology decisions, not automatic Step 11 or Part 2.\n"
    Path("reports/step10").mkdir(parents=True, exist_ok=True)
    Path("reports/step10/final-readiness.md").write_text(report)
    Path("reports/step10/quality-bar-matrix.md").write_text(matrix_markdown(rows))
    payload = inventory(output)
    validate_matrix(rows)
    verify_inventory(payload)
    cfg = read_json(Path("configs/final_model.json"))
    rules = read_json(Path("reports/step10/official-rules-check.json"))
    result = {"status": status, "stage": "S10", "generated_utc": stamp(), "frozen_submission": frozen["submission"], "selected_model": frozen["model_id"], "response_version": frozen["response_version"], "final_config_id": cfg["config_id"], "final_config_sha256": sha(Path("configs/final_model.json")), "step9_manifest_sha256": frozen["step9_manifest_sha256"], "git": git_identity(), "environment": verified["environment"], "environment_lock_sha256": sha(Path(cfg["environment_lock"])), "inventory_sha256": payload["inventory_sha256"], "inventory_path": str(output / "package-inventory.json"), "included_files": payload["files"], "quality_review_sha256": sha(Path("configs/step10_quality_review.json")), "quality_statuses": rows, "domain_results": counts, "critical_gaps": critical, "issues": read_json(Path("reports/step10/issues.json"))["issues"], "assumptions_register_sha256": sha(Path("docs/assumptions.md")), "rules_check": rules, "commands": ["make step10-check PYTHON=.venv/bin/python", "make reproduce-part1 PYTHON=.venv/bin/python DATA_DIR='<official-public-directory>'", "make verify-part1-package step10-acceptance PYTHON=.venv/bin/python DATA_DIR='<official-public-directory>'"], "external_prerequisites": "Controlled original public inputs plus matching repaired/frozen Steps 2–9 artifacts. Git source alone is not a self-contained data/model bundle; no private assets are published.", "upload_status": "not_uploaded", "final_kaggle_selection": "pending", "human_review": "pending", "part2_execution": "not_started", "archive_created": False}
    encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    archived = output / "package-records" / f"{digest}.json"
    if not archived.exists():
        save_json(archived, result, exclusive=True)
    save_json(output / "part1-handoff-manifest.json", result)
    save_json(output / "status.json", {"status": status, "manifest_sha256": digest, "inventory_sha256": payload["inventory_sha256"], "candidate_sha256": frozen["submission"]["sha256"], "machine_verification": "passed" if integrity and exact else "failed", "critical_gap_ids": [r["id"] for r in critical], "human_review": "pending", "upload_status": "not_uploaded", "final_kaggle_selection": "pending", "part2_execution": "not_started"})
    return {"status": status, "inventory_files": len(payload["files"]), "inventory_sha256": payload["inventory_sha256"], "manifest_sha256": digest, "domain_results": counts, "critical_gap_ids": [r["id"] for r in critical]}


def accept_handoff(output: Path) -> dict:
    frozen = freeze_candidate(output)
    manifest = read_json(output / "part1-handoff-manifest.json")
    state = read_json(output / "status.json")
    if sha(output / "part1-handoff-manifest.json") != state["manifest_sha256"]:
        raise ValueError("handoff manifest hash changed")
    payload = read_json(output / "package-inventory.json")
    verify_inventory(payload)
    if payload["inventory_sha256"] != manifest["inventory_sha256"]:
        raise ValueError("handoff inventory changed")
    rows = read_json(Path("configs/step10_quality_review.json"))["rows"]
    validate_matrix(rows)
    check_hashes(read_json(output / "tests.json")["code_sha256"])
    if rows != manifest["quality_statuses"] or manifest["frozen_submission"] != frozen["submission"]:
        raise ValueError("quality or candidate evidence differs from package")
    expected = readiness(rows, integrity=True, reproduced=True)
    if state["status"] != expected or manifest["status"] != expected:
        raise ValueError("readiness status hides a critical gap")
    for key, value in {"upload_status": "not_uploaded", "final_kaggle_selection": "pending", "human_review": "pending", "part2_execution": "not_started"}.items():
        if manifest[key] != value:
            raise ValueError("invented external action or human decision")
    if re.search(r"- \[[xX]\]", Path("docs/part1/human-review-checklist.md").read_text()):
        raise ValueError("unverified human checklist completion")
    report = {"status": "passed", "meaning": "quality/package acceptance, NOT permission or analytic readiness to upload", "readiness_status": expected, "candidate_sha256": frozen["submission"]["sha256"], "manifest_sha256": state["manifest_sha256"], "inventory_files": len(payload["files"]), "frozen_assets_unchanged": True, "all_criteria_evidence_linked": True, "critical_gaps_block_readiness": True, "all_human_items_unchecked": True, "no_part2_or_external_action": True, "checked_utc": stamp()}
    save_json(output / "acceptance.json", report)
    return report
