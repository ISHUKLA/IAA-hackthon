import pandas as pd

from iaa_hackathon.cleaning import standardize_buildings_construction
from iaa_hackathon.step2_repairs import deduplicate_claims


def test_construction_standardization_preserves_raw_and_only_maps_t_to_w():
    result = standardize_buildings_construction(pd.Series(["T", "W", "Brick", None]))
    assert result["construction_type_raw"].tolist()[:3] == ["T", "W", "Brick"]
    assert result["construction_type_standardized"].tolist()[:3] == ["w", "w", "brick"]


def test_claim_deduplication_uses_all_non_id_fields_and_shortest_canonical_id():
    claims = pd.DataFrame({
        "claim_id": ["CL100", "CL01", "CL02"], "policy_id": ["P", "P", "P"],
        "line": ["motor"] * 3, "peril": ["own_damage"] * 3,
        "loss_date": ["2024-01-01"] * 3, "report_date": ["2024-01-02"] * 3,
        "status": ["closed"] * 3, "paid_to_date": [10.0, 10.0, 11.0],
        "incurred_to_date": [10.0, 10.0, 11.0], "recoveries": [0.0] * 3,
    })
    clean, register = deduplicate_claims(claims)
    assert len(clean) == 2 and len(register) == 1
    assert register.loc[0, "canonical_claim_id"] == "CL01"
    assert register.loc[0, "removed_claim_count"] == 1
