from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

from app.visualization.chart_factory import ChartFactory
from app.visualization.utils import resolve_output_path


def create_chart(dataframe, filename: str, x_column: str, y_column: str | None = None, chart_type: str = "bar", output_dir: str | None = None) -> str:
    if x_column not in dataframe.columns:
        raise ValueError(f"Column '{x_column}' was not found in dataset '{filename}'.")

    if y_column is not None and y_column not in dataframe.columns:
        raise ValueError(f"Column '{y_column}' was not found in dataset '{filename}'.")

    strategy = ChartFactory.create(chart_type=chart_type, dataframe=dataframe, x_column=x_column, y_column=y_column)
    output_path = resolve_output_path(filename=filename, x_column=x_column, chart_type=chart_type, output_dir=output_dir)
    strategy.create(output_path)
    return str(output_path)
