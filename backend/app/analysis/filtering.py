import pandas as pd


def _validate_column(df: pd.DataFrame, column: str):
    """Raise an error if the column does not exist."""
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found.")


def filter_equals(
    df: pd.DataFrame,
    column: str,
    value,
) -> pd.DataFrame:
    """
    Return rows where column == value.
    """
    _validate_column(df, column)

    return df[df[column] == value]


def filter_not_equals(
    df: pd.DataFrame,
    column: str,
    value,
) -> pd.DataFrame:
    """
    Return rows where column != value.
    """
    _validate_column(df, column)

    return df[df[column] != value]


def filter_greater_than(
    df: pd.DataFrame,
    column: str,
    value,
) -> pd.DataFrame:
    """
    Return rows where column > value.
    """
    _validate_column(df, column)

    return df[df[column] > value]


def filter_less_than(
    df: pd.DataFrame,
    column: str,
    value,
) -> pd.DataFrame:
    """
    Return rows where column < value.
    """
    _validate_column(df, column)

    return df[df[column] < value]


def filter_between(
    df: pd.DataFrame,
    column: str,
    minimum,
    maximum,
) -> pd.DataFrame:
    """
    Return rows where minimum <= column <= maximum.
    """
    _validate_column(df, column)

    return df[
        (df[column] >= minimum)
        &
        (df[column] <= maximum)
    ]


def filter_contains(
    df: pd.DataFrame,
    column: str,
    text: str,
) -> pd.DataFrame:
    """
    Return rows whose string representation contains the given text.
    """
    _validate_column(df, column)

    return df[
        df[column]
        .astype(str)
        .str.contains(
            text,
            case=False,
            na=False,
        )
    ]


def filter_in(
    df: pd.DataFrame,
    column: str,
    values: list,
) -> pd.DataFrame:
    """
    Return rows where the column value is in the given list.
    """
    _validate_column(df, column)

    return df[
        df[column].isin(values)
    ]


def filter_missing(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:
    """
    Return rows where the column is missing.
    """
    _validate_column(df, column)

    return df[
        df[column].isna()
    ]


def filter_not_missing(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:
    """
    Return rows where the column is not missing.
    """
    _validate_column(df, column)

    return df[
        df[column].notna()
    ]