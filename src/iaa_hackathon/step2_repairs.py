"""Expanded, source-preserving Step 2 repair build including claim deduplication."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

from iaa_hackathon.claim_targets import add_observed_components, build_claim_crosswalk
from iaa_hackathon.prepare import POLICY_METADATA, prepare_data, sha256_file


def deduplicate_claims(claims: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Deduplicate on every supplied non-ID field; shortest then lexical ID wins."""
    if claims["claim_id"].isna().any() or not claims["claim_id"].is_unique:
        raise ValueError("source claim_id must be unique and non-null")
    fields = [column for column in claims.columns if column != "claim_id"]
    canonical = (claims.assign(_id_length=claims["claim_id"].str.len())
                 .sort_values(["_id_length", "claim_id"], kind="stable")
                 .drop_duplicates(fields, keep="first").drop(columns="_id_length"))
    registers: list[dict[str, Any]] = []
    for _, group in claims.groupby(fields, dropna=False, sort=False):
        if len(group) > 1:
            ordered = group.assign(_id_length=group["claim_id"].str.len()).sort_values(["_id_length", "claim_id"], kind="stable")
            row = {field: ordered.iloc[0][field] for field in fields}
            row.update({"canonical_claim_id": ordered.iloc[0]["claim_id"], "source_claim_ids_json": json.dumps(sorted(ordered["claim_id"].tolist())), "duplicate_group_size": len(ordered), "removed_claim_count": len(ordered) - 1})
            registers.append(row)
    return canonical.sort_values("claim_id", kind="stable").reset_index(drop=True), pd.DataFrame(registers)


def run_step2_repairs(*, data_dir: Path, output_dir: Path, project_root: Path) -> dict[str, Any]:
    """Build policy repairs plus deduplicated/linkable claims atomically outside Git."""
    data_dir, output_dir, project_root = data_dir.resolve(), output_dir.resolve(), project_root.resolve()
    reference = project_root / "docs/evidence/expected-manifest.json"
    before = {item["filename"]: sha256_file(data_dir / item["filename"]) for item in json.loads(reference.read_text())["files"]}
    previous = None
    if (output_dir / "repair-audit.json").is_file(): previous = json.loads((output_dir / "repair-audit.json").read_text()).get("logical_digest")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.staging-", dir=output_dir.parent))
    try:
        policy_dir = staging / "policy-layer"
        prepare_data(data_dir=data_dir, output_dir=policy_dir, cleaning_config_path=project_root / "configs/cleaning.json", reference_manifest_path=reference, project_root=project_root)
        policies: dict[str, pd.DataFrame] = {}
        all_policies: list[pd.DataFrame] = []
        for source, (line, split) in POLICY_METADATA.items():
            relative = json.loads((project_root / "configs/cleaning.json").read_text())["outputs"]["policy_tables"][source]
            table = pd.read_parquet(policy_dir / relative)
            all_policies.append(table)
            if split == "train": policies[line] = table
        raw_claims = pd.read_parquet(data_dir / "claims.parquet")
        claims, register = deduplicate_claims(raw_claims)
        crosswalk = build_claim_crosswalk(claims, policies, cutoff="2024-12-31", source_claims_sha256=before["claims.parquet"], strict=True)
        extra = [c for c in claims.columns if c not in crosswalk.columns]
        crosswalk = crosswalk.merge(claims[["claim_id", *extra]], on="claim_id", how="left", validate="one_to_one")
        enriched = add_observed_components(crosswalk)
        matched, quarantined = enriched.loc[enriched.disposition.eq("exactly_one_match")].copy(), enriched.loc[enriched.disposition.ne("exactly_one_match")].copy()
        accepted = matched.loc[matched.accepted_for_observed]
        aggregate = accepted.groupby("matched_row_id", sort=False).agg(observed_claim_count=("claim_id", "size"), observed_incurred=("incurred_to_date", "sum"), observed_recoveries=("recoveries", "sum"), observed_net_incurred=("observed_net_incurred", "sum")).reset_index().rename(columns={"matched_row_id":"row_id"})
        train = pd.concat([p for p in all_policies if p["split"].iloc[0] == "train"], ignore_index=True).merge(aggregate, on="row_id", how="left", validate="one_to_one")
        test = pd.concat([p for p in all_policies if p["split"].iloc[0] == "test"], ignore_index=True)
        for frame in (train,): frame[["observed_claim_count","observed_incurred","observed_recoveries","observed_net_incurred"]] = frame[["observed_claim_count","observed_incurred","observed_recoveries","observed_net_incurred"]].fillna(0)
        excluded = ["renewal_decision", "customer_service_contacts"]
        (staging / "claims").mkdir(); (staging / "model").mkdir()
        claims.to_parquet(staging / "claims/claims_clean.parquet", index=False); register.to_parquet(staging / "claims/duplicate-register.parquet", index=False)
        matched.to_parquet(staging / "claims/matched.parquet", index=False); quarantined.to_parquet(staging / "claims/quarantined.parquet", index=False)
        train.drop(columns=excluded, errors="ignore").to_parquet(staging / "model/training-model-table.parquet", index=False); test.drop(columns=excluded, errors="ignore").to_parquet(staging / "model/test-model-table.parquet", index=False)
        (staging / "model/feature-exclusions.json").write_text(json.dumps({"excluded":excluded,"reason":{"renewal_decision":"training-only post-period outcome","customer_service_contacts":"timing unavailable; excluded from default model table"}},indent=2)+"\n")
        after = {name: sha256_file(data_dir / name) for name in before}
        outputs = {str(p.relative_to(staging)): sha256_file(p) for p in sorted(staging.rglob("*")) if p.is_file()}
        digest = hashlib.sha256(json.dumps(outputs, sort_keys=True).encode()).hexdigest()
        audit = {"status":"complete","raw_hashes_unchanged":before==after,"source_hashes_before":before,"source_hashes_after":after,"train_rows":len(train),"test_rows":len(test),"raw_claim_rows":len(raw_claims),"clean_claim_rows":len(claims),"duplicate_claim_groups":len(register),"removed_duplicate_copies":int(register.removed_claim_count.sum()),"matched_clean_claim_rows":len(matched),"quarantined_clean_claim_rows":len(quarantined),"matched_accepted_net_incurred":float(accepted.observed_net_incurred.sum()),"outputs":outputs,"logical_digest":digest,"rerun_matches":previous==digest if previous else None,"deviation":"Ported patch behavior into existing pandas/pyarrow pipeline; omitted polars duplicate dependency and compiled artifacts."}
        (staging / "repair-audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True)+"\n")
        if output_dir.exists(): shutil.rmtree(output_dir)
        staging.rename(output_dir)
        return audit
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise
