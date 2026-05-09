"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.lifespan import lifespan
from app.routers import designs, questionnaire, users


def create_app() -> FastAPI:
    app = FastAPI(
        title="Jewelry Design Assistant API",
        description="Backend for the guided jewelry design questionnaire.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(questionnaire.router)
    app.include_router(users.router)
    app.include_router(designs.router)

    @app.get("/", tags=["Health"])
    def root():
        return {"status": "ok", "docs": "/docs"}

    return app


app = create_app()
