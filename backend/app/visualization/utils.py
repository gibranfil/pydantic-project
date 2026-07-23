from pathlib import Path


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "uploads" / "charts"


def resolve_output_dir(output_dir: str | None = None) -> Path:
    target_dir = Path(output_dir or str(DEFAULT_OUTPUT_DIR))
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def resolve_output_path(filename: str, x_column: str, chart_type: str, output_dir: str | None = None) -> Path:
    output_dir_path = resolve_output_dir(output_dir)
    chart_filename = f"{Path(filename).stem}_{x_column}_{chart_type}.png"
    return output_dir_path / chart_filename
