from fastapi import FastAPI, UploadFile, File, HTTPException

from app.dataset_manager import dataset_manager

app = FastAPI(
    title="AI Data Analyst Assistant"
)


@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        return dataset_manager.upload_dataset(file)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@app.get("/datasets")
def list_datasets():
    return dataset_manager.list_datasets()


@app.get("/datasets/{filename}")
def get_dataset(filename: str):
    return dataset_manager.get_profile(filename)


@app.delete("/datasets/{filename}")
def delete_dataset(filename: str):

    dataset_manager.delete_dataset(filename)

    return {
        "message": "Dataset deleted."
    }