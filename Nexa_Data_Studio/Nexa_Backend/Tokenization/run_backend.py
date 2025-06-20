import uvicorn
import os

if __name__ == "__main__":
    os.makedirs("tmp", exist_ok=True)
    print("Starting FastAPI backend at http://localhost:8000 ...")
    uvicorn.run(
        "Tokenization.app:fastapi_app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
