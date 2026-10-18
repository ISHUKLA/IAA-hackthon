"""Small end-to-end synthetic test for atomic Step 2 preparation."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from iaa_hackathon.prepare import prepare_data, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _write_inputs(root: Path) -> Path:
    root.mkdir()
    pd.DataFrame({"customer_id": ["00000123"]}).to_parquet(root / "customers.parquet", index=False)
    pd.DataFrame({"address_id": ["a1"]}).to_parquet(root / "addresses.parquet", index=False)
    pd.DataFrame(
        {"address_id": ["a1", "a1"], "year": [2021, 2025], "rainfall_mm": [10.0, 11.0]}
    ).to_parquet(root / "weather.parquet", index=False)

    names = [
        "policies_motor.parquet", "test_motor.parquet",
        "policies_buildings.parquet", "test_buildings.parquet",
        "policies_contents.parquet", "test_contents.parquet",
    ]
    for offset, name in enumerate(names):
        test = name.startswith("test_")
        line = "motor" if "motor" in name else "buildings" if "buildings" in name else "contents"
        year = 2025 if test else 2021
        frame = pd.DataFrame(
            {
                "row_id": [f"r{offset}"],
                "policy_id": [f"p{offset}"],
                "customer_id": ["123" if line == "motor" else "00000123"],
                "address_id": ["a1"],
                "period_start": [pd.Timestamp(year, 1, 1).date()],
                "period_end": [pd.Timestamp(year, 12, 31).date()],
                "exposure": [1.0],
                "written_premium": [100.0 + offset],
            }
        )
        if line == "motor":
            frame["telematics_opt_in"] = False
            frame["telematics_score"] = float("nan")
            frame["driver_age"] = 30
            frame["years_licensed"] = 10
        else:
            frame["sum_insured"] = 100_000.0
        frame.to_parquet(root / name, index=False)
    pd.DataFrame({"claim_id": ["c1"]}).to_parquet(root / "claims.parquet", index=False)
    pd.DataFrame({"row_id": ["r1"], "prediction": [0.0]}).to_parquet(root / "sample_submission.parquet", index=False)

    file_names = sorted(path.name for path in root.glob("*.parquet"))
    manifest = {
        "files": [
            {"filename": name, "sha256": sha256_file(root / name), "rows": 0, "columns": 0}
            for name in file_names
        ]
    }
    manifest_path = root.parent / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    return manifest_path


def test_prepare_data_is_reproducible_and_preserves_sources(tmp_path: Path) -> None:
    data = tmp_path / "raw"
    manifest = _write_inputs(data)
    before = {path.name: sha256_file(path) for path in data.glob("*.parquet")}
    output = tmp_path / "prepared"
    first = prepare_data(
        data_dir=data,
        output_dir=output,
        cleaning_config_path=ROOT / "configs/cleaning.json",
        reference_manifest_path=manifest,
        project_root=ROOT,
    )
    second = prepare_data(
        data_dir=data,
        output_dir=output,
        cleaning_config_path=ROOT / "configs/cleaning.json",
        reference_manifest_path=manifest,
        project_root=ROOT,
    )
    after = {path.name: sha256_file(path) for path in data.glob("*.parquet")}
    assert first["logical_output_digest"] == second["logical_output_digest"]
    assert before == after
    assert first["raw_hashes_unchanged"] is True
    clean = pd.read_parquet(output / "data/policies_motor_clean.parquet")
    assert clean.loc[0, "customer_id"] == "123"
    assert clean.loc[0, "customer_id_clean"] == "00000123"
    assert clean.loc[0, "exposure_clean"] == 1.0
    assert clean.loc[0, "customer_join_status"] == "matched"
    assert clean.loc[0, "weather_join_status"] == "matched"
    reconciliation = json.loads((output / "reconciliation.json").read_text())
    assert reconciliation["claims_transformed"] is False
    assert reconciliation["dimensions_transformed"] is False

