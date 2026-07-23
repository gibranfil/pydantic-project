import time
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.agent import agent
from app.dataset_manager import dataset_manager
from app.dependencies import AgentDependencies
from app.models import ChatRequest, ChatResponse, DatasetListResponse, DatasetResponse, UploadResponse
from app.tools import print_backend_capabilities

app = FastAPI(title="AI Data Analyst Assistant")
print_backend_capabilities()
CHARTS_DIR = Path(__file__).resolve().parent.parent / "uploads" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    try:
        profile = dataset_manager.upload_dataset(file)
        return UploadResponse(dataset=file.filename, profile=profile)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/datasets", response_model=DatasetListResponse)
def list_datasets():
    return DatasetListResponse(datasets=dataset_manager.list_datasets())


@app.get("/datasets/{filename}", response_model=DatasetResponse)
def get_dataset(filename: str):
    profile = dataset_manager.get_profile(filename)
    return DatasetResponse(dataset=filename, profile=profile)


@app.delete("/datasets/{filename}")
def delete_dataset(filename: str):
    dataset_manager.delete_dataset(filename)
    return {"message": "Dataset deleted."}


@app.get("/charts/{filename}")
def get_chart(filename: str):
    chart_path = CHARTS_DIR / filename
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")
    return FileResponse(chart_path)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    started_at = time.perf_counter()

    try:
        if request.dataset:
            profile = dataset_manager.get_profile(request.dataset)
            message = f"Dataset {request.dataset} loaded. Profile: {profile.model_dump_json()}\n\nUser asks: {request.message}"
        else:
            message = request.message

        try:
            deps = AgentDependencies(dataset_manager=dataset_manager)
            result = await agent.run(message, deps=deps)
            answer = result.output.answer
            chart_url = None
            if deps.last_chart_path:
                chart_url = f"/charts/{Path(deps.last_chart_path).name}"
        except Exception as exc:
            import traceback

            traceback.print_exc()
            answer = (
                "The AI service encountered an error while answering. "
                f"Details: {exc}"
            )
            chart_url = None

        execution_time = round(time.perf_counter() - started_at, 3)
        return ChatResponse(answer=answer, execution_time=execution_time, chart_url=chart_url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


