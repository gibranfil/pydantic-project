from app.visualization.charts.bar import BarChart
from app.visualization.charts.histogram import HistogramChart
from app.visualization.charts.line import LineChart
from app.visualization.charts.scatter import ScatterChart


class ChartFactory:
    _registry: dict[str, type] = {}

    @classmethod
    def register(cls, name: str, chart_cls: type) -> None:
        cls._registry[name.lower()] = chart_cls

    @classmethod
    def create(cls, chart_type: str, dataframe, x_column: str, y_column: str | None = None):
        chart_cls = cls._registry.get(chart_type.lower())
        if chart_cls is None:
            supported = ", ".join(sorted(cls._registry))
            raise ValueError(f"Unsupported chart type '{chart_type}'. Supported types: {supported}")
        return chart_cls(dataframe=dataframe, x_column=x_column, y_column=y_column)


for chart_cls in (BarChart, LineChart, HistogramChart, ScatterChart):
    ChartFactory.register(chart_cls.name, chart_cls)
