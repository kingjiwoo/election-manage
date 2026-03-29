"""생활인구 데이터 수집 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.population import population_service

router = APIRouter(prefix="/api/population", tags=["population"])


class CollectRequest(BaseModel):
    district_code: str
    target_date: str  # YYYYMMDD


@router.post("/collect")
async def collect_population(body: CollectRequest, db: AsyncSession = Depends(get_db)):
    """생활인구 데이터 수동 수집"""
    records = await population_service.collect_and_save(
        db, body.district_code, body.target_date
    )
    return {
        "data": {"collected": len(records)},
        "error": None,
        "meta": {},
    }
