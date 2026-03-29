# Election Campaign Management System

선거 캠프 효율화를 위한 조직 관리 및 유세지 추천 플랫폼.

## 프로젝트 개요

- **목표:** Graph DB 기반 지지자 조직 관리 + 실시간 유동인구 데이터를 결합한 유세지 추천
- **개발 환경:** Python(FastAPI) + TypeScript(Next.js) 모노레포

## 아키텍처

```
election-manage/
├── apps/
│   ├── api/          # FastAPI (Python)
│   └── web/          # Next.js + Tailwind CSS
├── packages/
│   └── types/        # 공유 타입 스키마
├── docker-compose.yml
└── CLAUDE.md
```

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | FastAPI (Python 3.12+) |
| Frontend | Next.js (App Router) + Tailwind CSS |
| Primary DB | PostgreSQL + PostGIS |
| Graph DB | Neo4j |
| Map SDK | Kakao Maps API |
| AI/LLM | Anthropic Claude API |
| Container | Docker + docker-compose |

## 핵심 기능

### 1. 위치 기반 유세지 추천
- SKT 데이터허브(Tmap) 실시간 혼잡도 API 연동
- 서울시 생활인구 공공데이터 수집 (공공데이터포털)
- PostGIS 기반 지리 쿼리로 아파트 단지·역세권 매핑
- 스코어링: `(실시간 혼잡도 × 0.4) + (거주 인구 밀도 × 0.3) - (최근 방문 페널티 × 0.3)`
- Claude API로 자연어 전략 리포트 생성

### 2. Graph DB 기반 조직 관리 (Neo4j)
- **Nodes:** `Candidate`, `CoreMember`, `Supporter`, `Organization`
- **Relationships:** `MANAGED_BY`, `INTRODUCED_BY`, `BELONGS_TO`, `VOTER_STATUS`
- react-force-graph로 인맥 트리 시각화
- 공백 지역(지지자 연결 고리 없는 아파트 단지) 자동 탐지

## 개발 규칙

### Python (FastAPI)
- 의존성 관리: `uv` 사용 (pip 대신)
- 패키지 구조: `app/routers/`, `app/models/`, `app/services/`, `app/core/`
- DB 접근: SQLAlchemy 2.0 (async) + asyncpg
- Neo4j 접근: `neo4j` 공식 Python 드라이버 (async 세션)
- 환경변수: `pydantic-settings`로 관리

### TypeScript (Next.js)
- 패키지 관리: `pnpm`
- 스타일: Tailwind CSS + shadcn/ui
- 데이터 페칭: TanStack Query
- 지도: Kakao Maps JS SDK (타입: `@types/kakao.maps.d.ts`)

### 공통
- 모든 API 응답은 `{ data, error, meta }` 구조 통일
- 환경변수는 `.env.example` 파일로 문서화
- Docker로 로컬 개발 환경 구성 (PostgreSQL, Neo4j 컨테이너)

## 환경변수 (필수)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/election
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=

# External APIs
KAKAO_REST_API_KEY=
SKT_TMAP_APP_KEY=
PUBLIC_DATA_API_KEY=   # 공공데이터포털

# AI
ANTHROPIC_API_KEY=
```

## 개발 단계 (Phase)

- [ ] **Phase 1** - 모노레포 초기화 + Docker 환경 구성
- [ ] **Phase 2** - 공공데이터 수집 모듈 (유동인구, 생활인구)
- [ ] **Phase 3** - Neo4j 조직 관리 API + 인맥 트리 UI
- [ ] **Phase 4** - 유세지 스코어링 엔진 + 지도 시각화
- [ ] **Phase 5** - Claude API 연동 전략 리포트 자동 생성
