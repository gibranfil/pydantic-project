from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from app.dataset_manager import dataset_manager


app = FastAPI(
    title="AI Data Analyst Assistant",
    version="0.1.0"
)


@app.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):
    try:

        dataset_manager.validate_file(file.filename)

        path = dataset_manager.save_uploaded_file(file)

        df = dataset_manager.load_dataset(path)

        dataset_manager.save_dataset(file.filename, df)

        return dataset_manager.dataset_summary(df)

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.get("/")
def home():
    return {
        "message": "AI Data Analyst Assistant is running!"
    }