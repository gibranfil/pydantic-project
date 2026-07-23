import pandas as pd

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
