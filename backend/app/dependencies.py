from dataclasses import dataclass

from app.dataset_manager import DatasetManager


@dataclass
class AgentDependencies:

    dataset_manager: DatasetManager