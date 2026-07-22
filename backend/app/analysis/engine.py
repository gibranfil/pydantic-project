import pandas as pd

from app.analysis.filtering import (
    filter_between,
    filter_contains,
    filter_equals,
    filter_greater_than,
    filter_in,
    filter_less_than,
    filter_missing,
    filter_not_equals,
    filter_not_missing,
)
from app.analysis.grouping import group_by


class AnalysisEngine:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe

    ##################################################
    # Filtering
    ##################################################

    def filter_equals(self, column, value):
        return filter_equals(self.df, column, value)

    def filter_not_equals(self, column, value):
        return filter_not_equals(self.df, column, value)

    def filter_greater_than(self, column, value):
        return filter_greater_than(self.df, column, value)

    def filter_less_than(self, column, value):
        return filter_less_than(self.df, column, value)

    def filter_between(self, column, minimum, maximum):
        return filter_between(
            self.df,
            column,
            minimum,
            maximum,
        )

    def filter_contains(self, column, text):
        return filter_contains(
            self.df,
            column,
            text,
        )

    def filter_in(self, column, values):
        return filter_in(
            self.df,
            column,
            values,
        )

    def filter_missing(self, column):
        return filter_missing(
            self.df,
            column,
        )

    def filter_not_missing(self, column):
        return filter_not_missing(
            self.df,
            column,
        )

    ##################################################
    # Grouping
    ##################################################

    def group_by(self, by, aggregation="sum", values=None):
        return group_by(
            self.df,
            by,
            aggregation,
            values,
        )