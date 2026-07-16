from pydantic import BaseModel

class ColumnProfile(BaseModel):
    name: str
    data_type: str
    missing: int


class NumericProfile(ColumnProfile):
    mean: float
    std: float
    minimum: float
    maximum: float

class CategoricalProfile(ColumnProfile):
    unique_values: int
    top_values: dict[str, int]

class DatasetProfile(BaseModel):
    filename: str
    rows: int
    columns: int

    numeric_columns: list[NumericProfile]
    categorical_columns: list[CategoricalProfile]

    sample_rows: list[dict]