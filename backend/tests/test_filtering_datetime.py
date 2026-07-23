import pandas as pd
import pytest

from app.analysis import filtering


def _make_df():
    return pd.DataFrame({
        "date": ["2021-01-01", "2021-01-15", "2021-02-01", None],
        "value": [1, 2, 3, 4],
    })


def test_filter_date_equals():
    df = _make_df()
    res = filtering.filter_date_equals(df, "date", "2021-01-15")
    assert len(res) == 1
    assert int(res.iloc[0]["value"]) == 2


def test_filter_date_before_after_between():
    df = _make_df()

    before = filtering.filter_date_before(df, "date", "2021-01-15")
    assert len(before) == 1
    assert int(before.iloc[0]["value"]) == 1

    after = filtering.filter_date_after(df, "date", "2021-01-15")
    assert len(after) == 1
    assert int(after.iloc[0]["value"]) == 3

    between = filtering.filter_date_between(df, "date", "2021-01-01", "2021-01-31")
    assert len(between) == 2


def test_invalid_column_raises():
    df = _make_df()
    with pytest.raises(ValueError):
        filtering.filter_date_equals(df, "not_a_column", "2021-01-01")
