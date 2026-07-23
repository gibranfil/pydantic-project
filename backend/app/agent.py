from pydantic_ai import Agent
from app.prompts import SYSTEM_PROMPT
from app.models import AIResponse
from app.dependencies import AgentDependencies
from app.tools import create_chart, get_dataset_profile, print_backend_capabilities
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    "google:gemini-3.5-flash-lite",
    deps_type=AgentDependencies,
    output_type=AIResponse,
    instructions=SYSTEM_PROMPT,
)
agent.tool(get_dataset_profile)
agent.tool(create_chart)
print_backend_capabilities()

