"""유세지 후보 지점 API"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.campaign_spot import CampaignSpot
from app.services.tmap import tmap_service

router = APIRouter(prefix="/api/spots", tags=["spots"])


class SpotCreate(BaseModel):
    name: str
    address: str | None = None
    lat: float
    lng: float
    spot_type: str = "etc"


class SpotResponse(BaseModel):
    id: int
    name: str
    address: str | None
    lat: float
    lng: float
    spot_type: str
    score: float | None
    congestion_score: float | None
    population_score: float | None
    visit_penalty: float
    last_visited_at: datetime | None
    score_updated_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("")
async def list_spots(db: AsyncSession = Depends(get_db)):
    """유세지 목록 조회 (스코어 내림차순)"""
    result = await db.execute(
        select(CampaignSpot).order_by(CampaignSpot.score.desc().nulls_last())
    )
    spots = result.scalars().all()
    return {
        "data": [SpotResponse.model_validate(s) for s in spots],
        "error": None,
        "meta": {"total": len(spots)},
    }


@router.post("", status_code=201)
async def create_spot(body: SpotCreate, db: AsyncSession = Depends(get_db)):
    """유세지 후보 등록"""
    spot = CampaignSpot(**body.model_dump())
    db.add(spot)
    await db.commit()
    await db.refresh(spot)
    return {"data": SpotResponse.model_validate(spot), "error": None, "meta": {}}


@router.post("/{spot_id}/collect-congestion")
async def collect_congestion(spot_id: int, db: AsyncSession = Depends(get_db)):
    """특정 유세지 혼잡도 수동 수집"""
    spot = await db.get(CampaignSpot, spot_id)
    if not spot:
        raise HTTPException(status_code=404, detail="유세지를 찾을 수 없습니다.")

    record = await tmap_service.collect_and_save(db, spot.id, spot.lat, spot.lng)
    if record is None:
        raise HTTPException(status_code=503, detail="Tmap API 호출 실패 또는 API Key 미설정")

    # 혼잡도 스코어 업데이트
    spot.congestion_score = record.congestion_score
    spot.score_updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "data": {
            "spot_id": spot_id,
            "congestion_level": record.congestion_level,
            "congestion_score": record.congestion_score,
        },
        "error": None,
        "meta": {},
    }
