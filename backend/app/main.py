from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import settings

# Don't import routes yet - we'll add them after startup
# from app.api.routes import projects

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    getattr(settings, 'frontend_url', "http://localhost:3000")
]

# Create FastAPI app
app = FastAPI(
    title="AI Video Generation Platform",
    description="Automated AI-generated video creation using multiple specialized agents",
    version="1.0.0"
)

# Configure CORS - must be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Import routes after startup to avoid blocking"""
    from app.api.routes import projects
    app.include_router(projects.router, prefix="/api/projects")
    print("Routes loaded successfully")


@app.get("/")
async def root():
    return {
        "name": "AI Video Generation Platform",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
