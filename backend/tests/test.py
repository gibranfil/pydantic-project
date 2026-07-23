import pandas as pd

from app.profiler import DatasetProfiler
from app.python_executor.executor import PythonExecutor


def run_executor_checks():
    df = pd.DataFrame({
        "Revenue": [500, 700, 900],
        "Profit": [100, 200, 250],
        "Region": ["East", "West", "North"],
    })

    executor = PythonExecutor(df)

    scalar_result = executor.execute("result = df['Revenue'].mean()")
    print("scalar_result:", scalar_result)
    assert scalar_result == 700.0, scalar_result

    series_result = executor.execute("result = df.groupby('Region')['Revenue'].sum()")
    print("series_result:", series_result)
    assert series_result == {"East": 500, "West": 700, "North": 900}, series_result

    dataframe_result = executor.execute("result = df.describe()")
    print("dataframe_result:", dataframe_result)
    assert isinstance(dataframe_result, list), dataframe_result
    assert dataframe_result[0]["Revenue"] == 3.0, dataframe_result

    try:
        executor.execute("result = __import__('os').system('echo hacked')")
    except ValueError as exc:
        print("unsafe_code_result:", exc)
        assert "unsafe" in str(exc).lower() or "not allowed" in str(exc).lower(), exc
    else:
        raise AssertionError("Unsafe code should have been rejected")

    profiler = DatasetProfiler(df, "sales.csv")
    profile = profiler.build_profile()
    print("profile_filename:", profile.filename)
    assert profile.filename == "sales.csv", profile.filename


if __name__ == "__main__":
    run_executor_checks()
    print("All executor checks passed")



# ##