# Visualization strategy pattern

Each chart type lives in its own module under the charts package.

To add another chart:

1. Create a new module such as `backend/app/visualization/charts/boxplot.py`.
2. Subclass `BaseChart` and implement:
   - `prepare_series()` to build the data to plot
   - `plot(ax, series)` to draw the chart on the provided axes
   - `name`, `title`, and `ylabel` as needed
3. Import the new class in `backend/app/visualization/charts/__init__.py`.
4. Register it in `backend/app/visualization/chart_factory.py`.

Example skeleton:

```python
from app.visualization.charts.base import BaseChart


class BoxPlotChart(BaseChart):
    name = "boxplot"

    def prepare_series(self):
        return self.dataframe[self.x_column]

    def plot(self, ax, series):
        series.plot.box(ax=ax)

    @property
    def title(self) -> str:
        return f"Box plot of {self.x_column}"

    @property
    def ylabel(self) -> str:
        return self.x_column
```

The `create_chart()` tool can then use this new type through the registry without changing the public API.
