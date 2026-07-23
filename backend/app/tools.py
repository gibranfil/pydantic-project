from pathlib import Path

from pydantic_ai import RunContext

from app.dependencies import AgentDependencies
from app.visualization.create_chart import create_chart as render_chart


def build_backend_capabilities() -> dict[str, list[str] | str]:
    return {
        "tools": ["dataset_profile", "chart"],
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
):
    dataset_manager = ctx.deps.dataset_manager

    if filename not in dataset_manager.datasets:
        raise ValueError(f"Dataset '{filename}' was not found.")

    dataframe = dataset_manager.get_dataframe(filename)
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