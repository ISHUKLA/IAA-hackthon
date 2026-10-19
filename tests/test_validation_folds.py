import pandas as pd
import pytest

from iaa_hackathon.validation_folds import FoldError, build_membership, membership_digest


def cfg():
    return {"input_universe":{"policy_bundle":"repairs"}, "folds":[{"id":"F2022","train_years":[2021],"validation_year":2022},{"id":"F2023","train_years":[2021,2022],"validation_year":2023},{"id":"F2024","train_years":[2021,2022,2023],"validation_year":2024}]}


def data():
    return pd.DataFrame({"row_id":["a","b","c","d","t"],"policy_id":["p"]*5,"customer_id":["c"]*5,"line":["motor"]*5,"period_start":["2021-01-01","2022-01-01","2023-01-01","2024-02-29","2025-01-01"],"period_end":["2021-12-31","2022-12-31","2023-12-31","2024-12-31","2025-12-31"],"exposure_clean":[1]*5})


def test_calendar_roles_exclude_test_and_are_order_invariant():
    one=build_membership(data(),cfg()); two=build_membership(data().sample(frac=1,random_state=1),cfg())
    assert "t" not in set(one.row_id)
    assert not one.duplicated(["fold_id","row_id"]).any()
    assert membership_digest(one)==membership_digest(two)


def test_cross_year_and_duplicate_rows_fail():
    bad=data(); bad.loc[0,"period_end"]="2022-01-01"
    with pytest.raises(FoldError,match="cross-year"): build_membership(bad,cfg())
    bad=data(); bad.loc[1,"row_id"]="a"
    with pytest.raises(FoldError,match="unique"): build_membership(bad,cfg())
