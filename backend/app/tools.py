from pathlib import Path

from pydantic_ai import RunContext

from app.dependencies import AgentDependencies
from app.visualization.create_chart import create_chart as render_chart
from app.analysis import AnalysisEngine
from typing import Any


def build_backend_capabilities() -> dict[str, list[str] | str]:
    return {
        "tools": ["dataset_profile", "chart", "filter_dataset"],
        "analysis": ["filtering", "grouping"],
        "add_tool_hint": (
            "Add a new tool by defining a function in app/tools.py and "
            "registering it with agent.tool(...) in app/agent.py."
        ),
    }

    
def print_backend_capabilities() -> None:
    capabilities = build_backend_capabilities()
    print("[Backend capabilities]")
    print(f"- Tools: {', '.join(capabilities['tools'])}")
    print(f"- Analysis: {', '.join(capabilities['analysis'])}")
    print(f"- {capabilities['add_tool_hint']}")


def get_dataset_profile(
    ctx: RunContext[AgentDependencies],
    filename: str,
):
    print(f"Tool requested filename: {repr(filename)}")
    print(f"Available datasets: {list(ctx.deps.dataset_manager.datasets.keys())}")

    if not filename:
        raise ValueError("A dataset name or column name is required.")

    dataset_manager = ctx.deps.dataset_manager
    if filename in dataset_manager.datasets:
        return dataset_manager.get_profile(filename)

    if len(dataset_manager.datasets) == 1:
        only_dataset = next(iter(dataset_manager.datasets.keys()))
        return dataset_manager.get_profile(only_dataset)

    normalized_name = filename.strip().lower()
    for dataset_name, record in dataset_manager.datasets.items():
        profile = record.profile
        column_names = {
            column.name.lower()
            for column in (
                profile.numeric_columns + profile.categorical_columns + profile.datetime_columns
            )
        }
        if normalized_name in column_names:
            return profile

    raise ValueError(
        f"Dataset or column '{filename}' was not found in the loaded datasets."
    )


def create_chart(
    ctx: RunContext[AgentDependencies],
    filename: str,
    x_column: str,
    y_column: str | None = None,
    chart_type: str = "bar",
    output_dir: str | None = None,
    filters: list[dict[str, Any]] | dict[str, Any] | None = None,
):
    dataset_manager = ctx.deps.dataset_manager

    if filename not in dataset_manager.datasets:
        raise ValueError(f"Dataset '{filename}' was not found.")

    dataframe = dataset_manager.get_dataframe(filename)
    # apply filters if provided
    if filters:
        engine = AnalysisEngine(dataframe)

        if isinstance(filters, dict):
            filters = [filters]

        op_map = {
            "equals": engine.filter_equals,
            "not_equals": engine.filter_not_equals,
            "greater_than": engine.filter_greater_than,
            "less_than": engine.filter_less_than,
            "between": engine.filter_between,
            "contains": engine.filter_contains,
            "in": engine.filter_in,
            "missing": engine.filter_missing,
            "not_missing": engine.filter_not_missing,
            "date_equals": engine.filter_date_equals,
            "date_before": engine.filter_date_before,
            "date_after": engine.filter_date_after,
            "date_between": engine.filter_date_between,
        }

        filtered = dataframe
        for f in filters:
            op = f.get("op") or f.get("operation") or f.get("name")
            if not op:
                raise ValueError("Each filter must include an 'op' field.")

            func = op_map.get(op)
            if func is None:
                raise ValueError(f"Unsupported filter operation: {op}")

            if op in {"between", "date_between"}:
                start = f.get("minimum") or f.get("start")
                end = f.get("maximum") or f.get("end")
                if start is None or end is None:
                    raise ValueError(f"Filter '{op}' requires both 'start' and 'end' (or 'minimum'/'maximum').")
                filtered = func(f.get("column"), start, end)
            elif op in {"equals", "not_equals", "greater_than", "less_than", "contains", "date_equals", "date_before", "date_after"}:
                value = f.get("value") or f.get("text")
                if value is None:
                    raise ValueError(f"Filter '{op}' requires a 'value' field.")
                filtered = func(f.get("column"), value)
            elif op == "in":
                values = f.get("values")
                if not isinstance(values, (list, tuple)):
                    raise ValueError("Filter 'in' requires a 'values' list.")
                filtered = func(f.get("column"), values)
            elif op in {"missing", "not_missing"}:
                filtered = func(f.get("column"))
            else:
                raise ValueError(f"Unhandled operation: {op}")

        dataframe = filtered
    output_path = render_chart(
        dataframe=dataframe,
        filename=filename,
        x_column=x_column,
        y_column=y_column,
        chart_type=chart_type,
        output_dir=output_dir,
    )
    ctx.deps.last_chart_path = str(output_path)

    return f"Chart saved to {output_path}"


def filter_dataset(
    ctx: RunContext[AgentDependencies],
    filename: str,
    filters: list[dict[str, Any]] | dict[str, Any] | None = None,
    sample_size: int = 5,
):
    """
    Apply a sequence of filters to `filename` and return a small preview.

    `filters` should be either a dict or a list of dicts with this shape:
      {"op": "equals", "column": "col", "value": 123}

    Supported ops: equals, not_equals, greater_than, less_than, between,
    contains, in, missing, not_missing, date_equals, date_before, date_after, date_between
    """
    if filename not in ctx.deps.dataset_manager.datasets:
        raise ValueError(f"Dataset '{filename}' was not found.")

    df = ctx.deps.dataset_manager.get_dataframe(filename)
    engine = AnalysisEngine(df)

    if not filters:
        filtered = df
    else:
        if isinstance(filters, dict):
            filters = [filters]

        op_map = {
            "equals": engine.filter_equals,
            "not_equals": engine.filter_not_equals,
            "greater_than": engine.filter_greater_than,
            "less_than": engine.filter_less_than,
            "between": engine.filter_between,
            "contains": engine.filter_contains,
            "in": engine.filter_in,
            "missing": engine.filter_missing,
            "not_missing": engine.filter_not_missing,
            "date_equals": engine.filter_date_equals,
            "date_before": engine.filter_date_before,
            "date_after": engine.filter_date_after,
            "date_between": engine.filter_date_between,
        }

        filtered = df
        for f in filters:
            op = f.get("op") or f.get("operation") or f.get("name")
            if not op:
                raise ValueError("Each filter must include an 'op' field.")

            func = op_map.get(op)
            if func is None:
                raise ValueError(f"Unsupported filter operation: {op}")

            # call function with appropriate args
            if op in {"between", "date_between"}:
                start = f.get("minimum") or f.get("start")
                end = f.get("maximum") or f.get("end")
                if start is None or end is None:
                    raise ValueError(f"Filter '{op}' requires both 'start' and 'end' (or 'minimum'/'maximum').")
                filtered = func(f.get("column"), start, end)
            elif op in {"equals", "not_equals", "greater_than", "less_than", "contains", "date_equals", "date_before", "date_after"}:
                value = f.get("value") or f.get("text")
                if value is None:
                    raise ValueError(f"Filter '{op}' requires a 'value' field.")
                filtered = func(f.get("column"), value)
            elif op == "in":
                values = f.get("values")
                if not isinstance(values, (list, tuple)):
                    raise ValueError("Filter 'in' requires a 'values' list.")
                filtered = func(f.get("column"), values)
            elif op in {"missing", "not_missing"}:
                filtered = func(f.get("column"))
            else:
                raise ValueError(f"Unhandled operation: {op}")

    # normalize output: number of rows and a small sample
    total = len(filtered)
    sample = filtered.head(sample_size).to_dict(orient="records")

    return {"dataset": filename, "rows": int(total), "sample": sample}