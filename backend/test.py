import pandas as pd

from app.profiler import DatasetProfiler

df = pd.DataFrame({
    "Revenue": [500, 700, 900],
    "Profit": [100, 200, 250],
    "Region": ["East", "West", "North"],
})

profiler = DatasetProfiler(df, "sales.csv")

profile = profiler.build_profile()

print(profile.model_dump_json(indent=2))