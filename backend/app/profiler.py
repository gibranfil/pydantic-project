import pandas as pd

from app.models import (
    NumericProfile,
    CategoricalProfile,
    DateTimeProfile,
    DatasetProfile,
)

DATE_KEYWORDS = {
    "date",
    "time",
    "timestamp",
    "created",
    "updated",
    "modified",
    "dob",
    "birthday",
}


class DatasetProfiler:

    def __init__(self, dataframe: pd.DataFrame, filename: str):
        self.filename = filename

        # Work on a copy so we don't modify the original dataframe
        self.dataframe = dataframe.copy()

    ####################################################################
    # Helper Functions
    ####################################################################

    def convert_datetime_columns(self):
        """
        Convert object columns that are likely dates into datetime columns.
        """

        for column in self.dataframe.columns:

            column_name = column.lower()

            if any(keyword in column_name for keyword in DATE_KEYWORDS):

                self.dataframe[column] = pd.to_datetime(
                    self.dataframe[column],
                    errors="coerce"
                )

    ####################################################################
    # Numeric Profiling
    ####################################################################

    def profile_numeric_columns(self):

        profiles = []

        numeric_df = self.dataframe.select_dtypes(include="number")

        for column in numeric_df.columns:

            series = numeric_df[column]

            profile = NumericProfile(
                name=column,
                dtype=str(series.dtype),
                missing=int(series.isna().sum()),
                mean=float(series.mean()),
                median=float(series.median()),
                std=float(series.std()),
                minimum=float(series.min()),
                maximum=float(series.max()),
                q1=float(series.quantile(0.25)),
                q3=float(series.quantile(0.75)),
            )

            profiles.append(profile)

        return profiles

    ####################################################################
    # Categorical Profiling
    ####################################################################

    def profile_categorical_columns(self):

        profiles = []

        categorical_df = self.dataframe.select_dtypes(
            include=["object", "category"]
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
                dtype=str(series.dtype),
                missing=int(series.isna().sum()),
                unique_values=int(series.nunique()),
                top_values=top_values,
            )

            profiles.append(profile)

        return profiles

    ####################################################################
    # Datetime Profiling
    ####################################################################

    def profile_datetime_columns(self):

        profiles = []

        datetime_df = self.dataframe.select_dtypes(
            include=["datetime64[ns]", "datetimetz"]
        )

        for column in datetime_df.columns:

            series = datetime_df[column]

            profile = DateTimeProfile(
                name=column,
                dtype=str(series.dtype),
                missing=int(series.isna().sum()),
                earliest=series.min().isoformat(),
                latest=series.max().isoformat(),
                unique_dates=int(series.nunique()),
            )

            profiles.append(profile)

        return profiles

    ####################################################################
    # Sample Rows
    ####################################################################

    def sample_rows(self):

        n = min(5, len(self.dataframe))

        sample = self.dataframe.sample(
            n=n,
            random_state=42
        )

        return sample.to_dict(orient="records")

    ####################################################################
    # Build Dataset Profile
    ####################################################################

    def build_profile(self):

        self.convert_datetime_columns()

        return DatasetProfile(
            filename=self.filename,
            rows=len(self.dataframe),
            columns=len(self.dataframe.columns),
            numeric_columns=self.profile_numeric_columns(),
            categorical_columns=self.profile_categorical_columns(),
            datetime_columns=self.profile_datetime_columns(),
            sample_rows=self.sample_rows(),
        )