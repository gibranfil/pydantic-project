from fastapi import FastAPI

app = FastAPI(
    title="AI Data Analyst Assistant",
    version="0.1.0"
)

@app.get("/")
def home():
    return {
        "message": "AI Data Analyst Assistant is running!"
    }