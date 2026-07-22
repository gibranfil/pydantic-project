from pydantic_ai import RunContext

from app.dependencies import AgentDependencies

def get_dataset_profile(
    ctx: RunContext[AgentDependencies],
    filename: str,
):
    print(f"Tool requested filename: {repr(filename)}")
    print(f"Available datasets: {list(ctx.deps.dataset_manager.datasets.keys())}")
    return ctx.deps.dataset_manager.get_profile(
        filename
    )