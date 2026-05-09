from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import questionnaire, users, designs
from app.database import create_tables

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
app.include_router(users.router)
app.include_router(designs.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    create_tables()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "docs": "/docs"}
