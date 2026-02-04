from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import settings
from app.api.routes import projects

# Create FastAPI app
app = FastAPI(
    title="AI Video Generation Platform",
    description="Automated AI-generated video creation using multiple specialized agents",
    version="1.0.0"
)

# Configure CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
