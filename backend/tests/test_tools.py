import pandas as pd
import pytest

from app.tools import build_backend_capabilities, create_chart


class DummyDatasetManager:
    def __init__(self, dataframe):
        self.datasets = {"demo.csv": type("DatasetRecord", (), {"dataframe": dataframe})()}

    def get_dataframe(self, filename):
        return self.datasets[filename].dataframe


class DummyContext:
    def __init__(self, dataframe):
        self.deps = type("Deps", (), {"dataset_manager": DummyDatasetManager(dataframe)})()


def test_build_backend_capabilities_reports_available_features():
    capabilities = build_backend_capabilities()

    assert "dataset_profile" in capabilities["tools"]
    assert "chart" in capabilities["tools"]
    assert "filtering" in capabilities["analysis"]
    assert "grouping" in capabilities["analysis"]


def test_create_chart_saves_png_file(tmp_path):
    dataframe = pd.DataFrame({"Category": ["A", "A", "B"], "Value": [1, 2, 3]})
    context = DummyContext(dataframe)

    result = create_chart(
        context,
        "demo.csv",
        "Category",
        chart_type="bar",
        output_dir=str(tmp_path),
    )

    assert "Chart saved" in result
    assert any(tmp_path.glob("*.png"))


def test_create_chart_supports_histogram_style(tmp_path):
    dataframe = pd.DataFrame({"Value": [1, 2, 2, 3, 3, 3]})
    context = DummyContext(dataframe)

    result = create_chart(
        context,
        "demo.csv",
        "Value",
        chart_type="histogram",
        output_dir=str(tmp_path),
    )

    assert "Chart saved" in result
    assert any(tmp_path.glob("*.png"))


def test_create_chart_with_filters_requires_parameters(tmp_path):
    dataframe = pd.DataFrame({"date": ["2021-01-01", "2021-01-15"], "value": [1, 2]})
    context = DummyContext(dataframe)

    # missing 'end' should raise a clear ValueError
    with pytest.raises(ValueError) as exc:
        create_chart(
            context,
            "demo.csv",
            "date",
            chart_type="bar",
            output_dir=str(tmp_path),
            filters={"op": "date_between", "column": "date", "start": "2021-01-01"},
        )

    assert "requires both 'start' and 'end'" in str(exc.value)


def test_create_chart_with_filters_applies_filters(tmp_path):
    dataframe = pd.DataFrame({"date": ["2021-01-01", "2021-01-15", "2021-02-01"], "value": [1, 2, 3]})
    context = DummyContext(dataframe)

    result = create_chart(
        context,
        "demo.csv",
        "date",
        chart_type="bar",
        output_dir=str(tmp_path),
        filters={"op": "date_between", "column": "date", "start": "2021-01-01", "end": "2021-01-31"},
    )

    assert "Chart saved" in result
    assert any(tmp_path.glob("*.png"))
