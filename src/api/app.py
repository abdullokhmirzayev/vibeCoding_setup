from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

def create_app() -> FastAPI:
    app = FastAPI(
        title="VibeCoding Agent API",
        description="Production-grade API for Governed Autonomous AI Agents (Skills, Hooks, Tools, Memory, Observability)",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "version": "0.1.0",
            "governance": "active"
        }

    app.include_router(router)
    return app

app = create_app()
