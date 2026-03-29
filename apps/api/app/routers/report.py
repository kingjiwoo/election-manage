"""전략 리포트 API"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.report import report_service

router = APIRouter(prefix="/api/report", tags=["report"])


@router.post("")
async def generate_report(
    candidate_name: str = "후보",
    db: AsyncSession = Depends(get_db),
):
    """전략 리포트 생성 (전체 텍스트)"""
    content = await report_service.generate(db, candidate_name)
    return {"data": {"report": content}, "error": None, "meta": {}}


@router.post("/stream")
async def generate_report_stream(
    candidate_name: str = "후보",
    db: AsyncSession = Depends(get_db),
):
    """전략 리포트 스트리밍 생성 (SSE)"""
    async def event_stream():
        async for chunk in report_service.generate_stream(db, candidate_name):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain; charset=utf-8")
