import pandas as pd

from app.models import (
    NumericProfile,
    CategoricalProfile,
    DatasetProfile
)

class DatasetProfiler:

    def __init__(self, dataframe: pd.DataFrame, filename: str):
        self.dataframe = dataframe
        self.filename = filename


    def profile_categorical_columns(self):

        profiles = []

        categorical_df = self.dataframe.select_dtypes(
            exclude="number"
        )

        for column in categorical_df.columns:

            series = categorical_df[column]

            top_values = {
                str(key): int(value)
                for key, value in (
                    series.value_counts()
                    .head(5)
                    .items()
                )
            }

            profile = CategoricalProfile(
                name=column,
                data_type=str(series.dtype),
                missing=int(series.isna().sum()),
                unique_values=int(series.nunique()),
                top_values=top_values,
            )

            profiles.append(profile)

        return profiles

    def profile_numeric_columns(self):

        profiles = []

        numeric_df = self.dataframe.select_dtypes(include="number")

        for column in numeric_df.columns:

            series = numeric_df[column]

            profile = NumericProfile(
                name=column,
                data_type=str(series.dtype),
                missing=int(series.isna().sum()),
                mean=float(series.mean()),
                std=float(series.std()),
                minimum=float(series.min()),
                maximum=float(series.max()),
            )

            profiles.append(profile)

        return profiles
    
    def build_profile(self):

        numeric_columns = self.profile_numeric_columns()

        categorical_columns = self.profile_categorical_columns()

        sample_rows = self.sample_rows()

        return DatasetProfile(
            filename=self.filename,
            rows=len(self.dataframe),
            columns=len(self.dataframe.columns),
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            sample_rows=sample_rows,
        )
    
    def sample_rows(self):
        return self.dataframe.sample(5, random_state=42).to_dict(orient="records")