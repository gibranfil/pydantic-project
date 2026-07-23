from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pydantic_ai import RunContext

from app.dependencies import AgentDependencies


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

    if x_column not in dataframe.columns:
        raise ValueError(f"Column '{x_column}' was not found in dataset '{filename}'.")

    output_dir_path = Path(output_dir or str(Path(__file__).resolve().parent.parent / "uploads" / "charts"))
    output_dir_path.mkdir(parents=True, exist_ok=True)

    chart_filename = f"{Path(filename).stem}_{x_column}_{chart_type}.png"
    output_path = output_dir_path / chart_filename

    if y_column is None:
        data = dataframe[x_column].value_counts()
        title = f"Distribution of {x_column}"
        ylabel = "Count"
        if chart_type == "bar":
            data.plot(kind="bar")
        elif chart_type == "line":
            data.plot(kind="line")
        else:
            raise ValueError("Only 'bar' and 'line' chart types are supported.")
    else:
        if y_column not in dataframe.columns:
            raise ValueError(f"Column '{y_column}' was not found in dataset '{filename}'.")

        if chart_type == "bar":
            data = dataframe.groupby(x_column)[y_column].sum()
        elif chart_type == "line":
            data = dataframe.groupby(x_column)[y_column].sum()
        else:
            raise ValueError("Only 'bar' and 'line' chart types are supported.")

        title = f"{y_column} by {x_column}"
        ylabel = y_column
        data.plot(kind=chart_type)

    plt.title(title)
    plt.xlabel(x_column)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return f"Chart saved to {output_path}"