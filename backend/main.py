from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory AND its parent to sys.path
# This ensures we can import `api.routes` (if CWD is backend) AND `backend.api.routes` (if CWD is root)
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))
if str(backend_dir.parent) not in sys.path:
    sys.path.append(str(backend_dir.parent))

try:
    # Try importing as if we are inside the package (e.g. from api.routes)
    from api.routes import router as api_router
except ImportError:
    # Try importing as effective root (e.g. from backend.api.routes)
    try:
        from backend.api.routes import router as api_router
    except ImportError as e:
        # Last ditch: try absolute import if running from within backend but without package structure
        import api.routes as api_routes_module
        api_router = api_routes_module.router

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
