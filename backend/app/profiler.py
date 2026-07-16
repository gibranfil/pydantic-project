import pandas as pd

from app.models import (
    NumericProfile,
    CategoricalProfile,
    DatasetProfile
)

class DatasetProfiler:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe