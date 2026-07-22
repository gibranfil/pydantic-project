from app.agent import agent
from app.dataset_manager import dataset_manager
from app.dependencies import AgentDependencies

deps = AgentDependencies(
    dataset_manager=dataset_manager
)

result = agent.run_sync(
    "What columns are in sales.csv?",
    deps=deps,
)

print(result.output)