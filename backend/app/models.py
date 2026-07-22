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


class DateTimeProfile(ColumnProfile):
    earliest: str
    latest: str
    unique_dates: int


class DatasetProfile(BaseModel):
    filename: str
    rows: int
    columns: int
    numeric_columns: list[NumericProfile]
    categorical_columns: list[CategoricalProfile]
    datetime_columns: list[DateTimeProfile]
    sample_rows: list[dict]


class Dataset(BaseModel):
    filename: str
    profile: DatasetProfile


class UploadResponse(BaseModel):
    dataset: str
    profile: DatasetProfile


class DatasetResponse(BaseModel):
    dataset: str
    profile: DatasetProfile


class DatasetListResponse(BaseModel):
    datasets: list[str]


class ChatRequest(BaseModel):
    message: str
    dataset: str | None = None


class ChatResponse(BaseModel):
    answer: str
    execution_time: float


class AIResponse(BaseModel):
    answer: str
    reasoning: str | None = None