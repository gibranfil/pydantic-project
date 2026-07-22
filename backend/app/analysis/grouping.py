from __future__ import annotations

import pandas as pd


def _validate_columns(df: pd.DataFrame, columns: str | list[str]):
    """Raise an error if any requested column does not exist."""
    if isinstance(columns, str):
        columns = [columns]

    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Column(s) not found: {', '.join(missing)}")


def group_by(
    df: pd.DataFrame,
    by: str | list[str],
    aggregation: str = "sum",
    values: list[str] | None = None,
) -> pd.DataFrame:
    """
    Group rows by one or more columns and aggregate numeric values.
    """
    _validate_columns(df, by)

    if values is None:
        values = list(df.select_dtypes(include=["number"]).columns)
    else:
        _validate_columns(df, values)

    if not values:
        raise ValueError("No columns available to aggregate.")

    group_keys = [by] if isinstance(by, str) else by
    grouped = df.groupby(group_keys, dropna=False)

    if aggregation == "size":
        result = grouped.size().rename("size").reset_index()
    elif aggregation == "nunique":
        result = grouped[values].nunique().reset_index()
    else:
        result = getattr(grouped[values], aggregation)().reset_index()

    return result


__all__ = ["group_by"]
