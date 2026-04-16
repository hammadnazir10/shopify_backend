from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import questionnaire

app = FastAPI(
    title="Jewelry Design Assistant API",
    description="Backend for the guided jewelry design questionnaire.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questionnaire.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "docs": "/docs"}
