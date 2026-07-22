from .engine import AnalysisEngine


def describe(dataframe):
    return AnalysisEngine(dataframe).describe()


def missing_values(dataframe):
    return AnalysisEngine(dataframe).missing_values()


def value_counts(dataframe, column: str, top_n: int = 10):
    return AnalysisEngine(dataframe).value_counts(column, top_n)


def summary(dataframe):
    return AnalysisEngine(dataframe).summary()


__all__ = ["describe", "missing_values", "value_counts", "summary"]
