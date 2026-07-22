import time

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agent import agent
from app.dataset_manager import dataset_manager
from app.models import ChatRequest, ChatResponse, DatasetListResponse, DatasetResponse, UploadResponse

app = FastAPI(title="AI Data Analyst Assistant")
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
            result = await agent.run(message)
            answer = result.output.answer
        except Exception:
            answer = (
                "The AI service is not available right now, so I can only offer a placeholder response. "
                f"You asked: {request.message}"
            )

        execution_time = round(time.perf_counter() - started_at, 3)
        return ChatResponse(answer=answer, execution_time=execution_time)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


