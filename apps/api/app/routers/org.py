"""조직 관리 API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.neo4j import get_neo4j_session
from app.services.org import org_service

router = APIRouter(prefix="/api/org", tags=["org"])


# ── 요청 스키마 ────────────────────────────────────────────────

class CandidateIn(BaseModel):
    id: str
    name: str
    district: str = ""
    party: str = ""


class CoreMemberIn(BaseModel):
    id: str
    name: str
    phone: str = ""
    region: str = ""
    role: str = ""


class SupporterIn(BaseModel):
    id: str
    name: str
    phone: str = ""
    address: str = ""
    apt_complex: str = ""


class OrganizationIn(BaseModel):
    id: str
    name: str
    region: str = ""
    org_type: str = ""


class RelationIn(BaseModel):
    from_id: str
    to_id: str


class VoterStatusIn(BaseModel):
    supporter_id: str
    status: str  # "strong", "likely", "undecided", "unlikely"


# ── 엔드포인트 ────────────────────────────────────────────────

@router.get("/tree")
async def get_tree(session=Depends(get_neo4j_session)):
    """인맥 트리 전체 조회 (force-graph 형식)"""
    tree = await org_service.get_tree(session)
    return {"data": tree, "error": None, "meta": {}}


@router.get("/blank-regions")
async def get_blank_regions(session=Depends(get_neo4j_session)):
    """공백 지역(지지자 없는 아파트 단지) 탐지"""
    blanks = await org_service.find_blank_regions(session)
    return {"data": blanks, "error": None, "meta": {"count": len(blanks)}}


@router.post("/candidates")
async def create_candidate(body: CandidateIn, session=Depends(get_neo4j_session)):
    node = await org_service.create_candidate(session, body.model_dump())
    return {"data": node, "error": None, "meta": {}}


@router.post("/core-members")
async def create_core_member(body: CoreMemberIn, session=Depends(get_neo4j_session)):
    node = await org_service.create_core_member(session, body.model_dump())
    return {"data": node, "error": None, "meta": {}}


@router.post("/supporters")
async def create_supporter(body: SupporterIn, session=Depends(get_neo4j_session)):
    node = await org_service.create_supporter(session, body.model_dump())
    return {"data": node, "error": None, "meta": {}}


@router.post("/organizations")
async def create_organization(body: OrganizationIn, session=Depends(get_neo4j_session)):
    node = await org_service.create_organization(session, body.model_dump())
    return {"data": node, "error": None, "meta": {}}


@router.post("/relations/managed-by")
async def set_managed_by(body: RelationIn, session=Depends(get_neo4j_session)):
    ok = await org_service.managed_by(session, body.from_id, body.to_id)
    if not ok:
        raise HTTPException(status_code=404, detail="노드를 찾을 수 없습니다.")
    return {"data": {"created": True}, "error": None, "meta": {}}


@router.post("/relations/introduced-by")
async def set_introduced_by(body: RelationIn, session=Depends(get_neo4j_session)):
    ok = await org_service.introduced_by(session, body.from_id, body.to_id)
    if not ok:
        raise HTTPException(status_code=404, detail="노드를 찾을 수 없습니다.")
    return {"data": {"created": True}, "error": None, "meta": {}}


@router.post("/relations/belongs-to")
async def set_belongs_to(body: RelationIn, session=Depends(get_neo4j_session)):
    ok = await org_service.belongs_to(session, body.from_id, body.to_id)
    if not ok:
        raise HTTPException(status_code=404, detail="노드를 찾을 수 없습니다.")
    return {"data": {"created": True}, "error": None, "meta": {}}


@router.patch("/supporters/voter-status")
async def update_voter_status(body: VoterStatusIn, session=Depends(get_neo4j_session)):
    ok = await org_service.voter_status(session, body.supporter_id, body.status)
    if not ok:
        raise HTTPException(status_code=404, detail="지지자를 찾을 수 없습니다.")
    return {"data": {"updated": True}, "error": None, "meta": {}}
