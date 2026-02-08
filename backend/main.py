from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to sys.path to allow imports of sibling modules (api, src)
# This works whether running from root (python -m backend.main) or inside backend (python main.py)
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

try:
    from api.routes import router as api_router
except ImportError:
    # Fallback if somehow path setup fails, though the above should catch it
    from backend.api.routes import router as api_router

app = FastAPI(
    title="Traffic Intelligence API",
    version="1.0.0"
)

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend Online"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
