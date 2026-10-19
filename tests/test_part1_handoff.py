"""Adversarial package, readiness and frozen-candidate tests without real data."""
import hashlib
import json
from pathlib import Path

import pytest

from iaa_hackathon.part1_handoff import (
    check_freeze, inspect_package_file, readiness, safe_package_path,
    sha, validate_matrix, verify_inventory,
)


@pytest.mark.parametrize("status", ["fail", "partial", "not_testable"])
def test_critical_gap_never_averaged_away(status):
    rows = [{"status": "pass", "critical": False}] * 100
    rows += [{"status": status, "critical": True}]
    assert readiness(rows, integrity=True, reproduced=True) == "blocked"


def test_all_readiness_states():
    clear = [{"status": "pass", "critical": True}, {"status": "not_applicable", "critical": True}]
    assert readiness(clear, integrity=True, reproduced=True) == "ready_for_part1_upload"
    assert readiness(clear + [{"status": "partial", "critical": False}], integrity=True, reproduced=True) == "ready_with_disclosures"
    assert readiness(clear, integrity=False, reproduced=True) == "failed_verification"
    assert readiness(clear, integrity=True, reproduced=False) == "failed_verification"


def test_frozen_hash_or_rewrite_fails(tmp_path):
    candidate = tmp_path / "frozen.csv"
    candidate.write_text("row_id,prediction\nMsynthetic,1\n")
    original = candidate.read_bytes()
    info = candidate.stat()
    frozen = {"assets_sha256": {str(candidate): sha(candidate)}, "submission": {"path": str(candidate), "bytes": info.st_size, "mtime_ns": info.st_mtime_ns}}
    check_freeze(frozen)
    candidate.write_text("row_id,prediction\nMsynthetic,2\n")
    with pytest.raises(ValueError, match="hash"):
        check_freeze(frozen)
    candidate.write_bytes(original)
    import os
    os.utime(candidate, ns=(info.st_atime_ns, info.st_mtime_ns + 1_000_000))
    with pytest.raises(ValueError, match="rewritten"):
        check_freeze(frozen)


@pytest.mark.parametrize("path", ["../leak.md", "/absolute/readme.md", "data/raw.json", ".env", ".venv/config.py", ".aws/credentials", "submissions/candidate.csv", "models/fitted.joblib", "raw.parquet", "archive.zip", "configs/local-private.json", "a\\..\\file.md"])
def test_unsafe_payload_paths(path):
    with pytest.raises(ValueError):
        safe_package_path(path)


@pytest.mark.parametrize("content", ["token: " + "ghp_" + "a" * 40, "-----BEGIN " + "PRIVATE KEY-----", "/Us" + "ers/synthetic-person/private/data", "/pri" + "vate/var/folders/ab/synthetic-user/cache"])
def test_sensitive_payload_rejected(tmp_path, monkeypatch, content):
    monkeypatch.chdir(tmp_path)
    path = Path("readme.md")
    path.write_text(content)
    with pytest.raises(ValueError, match="secret or machine"):
        inspect_package_file(path)


def test_scanner_own_generic_pattern_is_not_personal_data(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    inspect_package_file(Path("src/iaa_hackathon/part1_handoff.py"))


def test_symlink_and_excessive_payload_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = Path("target.md")
    target.write_text("safe")
    link = Path("alias.md")
    link.symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        inspect_package_file(link)
    target.write_text("x" * (2 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match="excessive"):
        inspect_package_file(target)


def test_inventory_hash_and_payload_tampering(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = Path("readme.md")
    path.write_text("snapshot proxy, human review pending")
    records = [{"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size}]
    digest = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    inventory = {"files": records, "inventory_sha256": digest}
    verify_inventory(inventory)
    path.write_text("changed")
    with pytest.raises(ValueError, match="hash/size"):
        verify_inventory(inventory)
    inventory["inventory_sha256"] = "bad"
    with pytest.raises(ValueError, match="digest"):
        verify_inventory(inventory)


def test_required_criteria_cannot_be_removed(tmp_path):
    config = json.loads((Path(__file__).resolve().parents[1] / "configs/step10_quality_review.json").read_text())
    evidence = tmp_path / "checked-evidence.md"
    evidence.write_text("synthetic evidence for structural tests only")
    rows = [{**row, "evidence": [str(evidence)]} for row in config["rows"]]
    validate_matrix(rows)
    with pytest.raises(ValueError, match="omits"):
        validate_matrix(rows[:-1])
    with pytest.raises(ValueError):
        validate_matrix([])
    rows[0]["status"] = "approved_by_AI"
    with pytest.raises(ValueError, match="invalid"):
        validate_matrix(rows)
