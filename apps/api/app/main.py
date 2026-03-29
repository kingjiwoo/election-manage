from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.neo4j import close_driver
from app.routers import spots, population, org, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_driver()


app = FastAPI(
    title="Election Campaign Management API",
    version="0.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(spots.router)
app.include_router(population.router)
app.include_router(org.router)
app.include_router(report.router)


@app.get("/health")
async def health_check():
    return {"data": {"status": "ok"}, "error": None, "meta": {}}
