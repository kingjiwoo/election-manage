"""Neo4j 기반 조직 관리 서비스"""
import logging
from typing import Any

from neo4j import AsyncSession

logger = logging.getLogger(__name__)


class OrgService:

    # ── 노드 생성 ──────────────────────────────────────────────

    async def create_candidate(self, session: AsyncSession, data: dict) -> dict:
        result = await session.run(
            """
            MERGE (c:Candidate {id: $id})
            SET c += {name: $name, district: $district, party: $party}
            RETURN c
            """,
            id=data["id"],
            name=data["name"],
            district=data.get("district", ""),
            party=data.get("party", ""),
        )
        record = await result.single()
        return dict(record["c"])

    async def create_core_member(self, session: AsyncSession, data: dict) -> dict:
        result = await session.run(
            """
            MERGE (m:CoreMember {id: $id})
            SET m += {name: $name, phone: $phone, region: $region, role: $role}
            RETURN m
            """,
            id=data["id"],
            name=data["name"],
            phone=data.get("phone", ""),
            region=data.get("region", ""),
            role=data.get("role", ""),
        )
        record = await result.single()
        return dict(record["m"])

    async def create_supporter(self, session: AsyncSession, data: dict) -> dict:
        result = await session.run(
            """
            MERGE (s:Supporter {id: $id})
            SET s += {name: $name, phone: $phone, address: $address, apt_complex: $apt_complex}
            RETURN s
            """,
            id=data["id"],
            name=data["name"],
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            apt_complex=data.get("apt_complex", ""),
        )
        record = await result.single()
        return dict(record["s"])

    async def create_organization(self, session: AsyncSession, data: dict) -> dict:
        result = await session.run(
            """
            MERGE (o:Organization {id: $id})
            SET o += {name: $name, region: $region, org_type: $org_type}
            RETURN o
            """,
            id=data["id"],
            name=data["name"],
            region=data.get("region", ""),
            org_type=data.get("org_type", ""),
        )
        record = await result.single()
        return dict(record["o"])

    # ── 관계 생성 ──────────────────────────────────────────────

    async def managed_by(
        self, session: AsyncSession, supporter_id: str, core_member_id: str
    ) -> bool:
        """지지자 → 핵심 당원이 관리"""
        result = await session.run(
            """
            MATCH (s:Supporter {id: $s_id}), (m:CoreMember {id: $m_id})
            MERGE (s)-[r:MANAGED_BY]->(m)
            RETURN r
            """,
            s_id=supporter_id,
            m_id=core_member_id,
        )
        return await result.single() is not None

    async def introduced_by(
        self, session: AsyncSession, supporter_id: str, introducer_id: str
    ) -> bool:
        """지지자가 다른 지지자에게 소개됨"""
        result = await session.run(
            """
            MATCH (s:Supporter {id: $s_id}), (i:Supporter {id: $i_id})
            MERGE (s)-[r:INTRODUCED_BY]->(i)
            RETURN r
            """,
            s_id=supporter_id,
            i_id=introducer_id,
        )
        return await result.single() is not None

    async def belongs_to(
        self, session: AsyncSession, member_id: str, org_id: str
    ) -> bool:
        """핵심 당원이 조직에 소속"""
        result = await session.run(
            """
            MATCH (m:CoreMember {id: $m_id}), (o:Organization {id: $o_id})
            MERGE (m)-[r:BELONGS_TO]->(o)
            RETURN r
            """,
            m_id=member_id,
            o_id=org_id,
        )
        return await result.single() is not None

    async def voter_status(
        self, session: AsyncSession, supporter_id: str, status: str
    ) -> bool:
        """지지자 투표 의향 상태 설정"""
        result = await session.run(
            """
            MATCH (s:Supporter {id: $s_id})
            SET s.voter_status = $status
            RETURN s
            """,
            s_id=supporter_id,
            status=status,
        )
        return await result.single() is not None

    # ── 조회 ──────────────────────────────────────────────────

    async def get_tree(self, session: AsyncSession) -> dict:
        """전체 조직 인맥 트리 (force-graph 형식)"""
        nodes_result = await session.run(
            """
            MATCH (n)
            WHERE n:Candidate OR n:CoreMember OR n:Supporter OR n:Organization
            RETURN n, labels(n) AS labels
            """
        )
        edges_result = await session.run(
            """
            MATCH (a)-[r]->(b)
            WHERE (a:Candidate OR a:CoreMember OR a:Supporter OR a:Organization)
              AND (b:Candidate OR b:CoreMember OR b:Supporter OR b:Organization)
            RETURN a.id AS source, b.id AS target, type(r) AS rel_type
            """
        )

        nodes = []
        async for record in nodes_result:
            node = dict(record["n"])
            node["label"] = record["labels"][0]
            nodes.append(node)

        links = []
        async for record in edges_result:
            links.append({
                "source": record["source"],
                "target": record["target"],
                "type": record["rel_type"],
            })

        return {"nodes": nodes, "links": links}

    async def find_blank_regions(self, session: AsyncSession) -> list[str]:
        """공백 지역: 지지자가 없는 아파트 단지 탐지"""
        result = await session.run(
            """
            MATCH (s:Supporter)
            WHERE s.apt_complex IS NOT NULL AND s.apt_complex <> ''
            WITH collect(DISTINCT s.apt_complex) AS covered
            MATCH (spot:CampaignSpot)
            WHERE spot.spot_type = 'apartment' AND NOT spot.name IN covered
            RETURN spot.name AS blank_apt
            """
        )
        blanks = []
        async for record in result:
            blanks.append(record["blank_apt"])
        return blanks


org_service = OrgService()
