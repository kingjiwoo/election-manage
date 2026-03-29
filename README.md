# Election Campaign Management System

선거 캠프 효율화를 위한 조직 관리 및 유세지 추천 플랫폼

## 개요

- **조직 관리**: Neo4j Graph DB 기반 후보자·핵심 조직원·지지자 인맥 트리 시각화
- **유세지 추천**: 실시간 혼잡도 + 생활인구 데이터를 결합한 스코어링 엔진
- **전략 리포트**: Claude / GPT-4o / Gemini 중 선택하여 AI 리포트 스트리밍 생성

## 기술 스택

| 구분 | 기술 |
|---|---|
| Backend | FastAPI (Python 3.12) |
| Frontend | Next.js (App Router) + Tailwind CSS |
| Primary DB | PostgreSQL 16 + PostGIS |
| Graph DB | Neo4j 5 |
| Map | Kakao Maps JS SDK |
| AI/LLM | Claude (claude-sonnet-4-6) / GPT-4o / Gemini-2.0-flash |
| Container | Docker + Docker Compose |

## 빠른 시작

### 1. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일에 아래 API 키를 입력합니다.

| 변수 | 설명 |
|---|---|
| `KAKAO_REST_API_KEY` | 카카오 REST API 키 |
| `SKT_TMAP_APP_KEY` | SK Tmap 혼잡도 API 키 |
| `PUBLIC_DATA_API_KEY` | 공공데이터포털 인증키 |
| `ANTHROPIC_API_KEY` | Claude API 키 |
| `OPENAI_API_KEY` | OpenAI API 키 (선택) |
| `GEMINI_API_KEY` | Google Gemini API 키 (선택) |

### 2. 실행

```bash
docker compose up --build
```

| 서비스 | 주소 |
|---|---|
| Next.js 프론트엔드 | http://localhost:3000 |
| FastAPI 백엔드 | http://localhost:8000 |
| API 문서 (Swagger) | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |

## 로컬 개발 (Docker 없이)

**Backend**

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd apps/web
pnpm install
pnpm dev
```

## 스코어링 공식

```
종합 스코어 = (실시간 혼잡도 × 0.4) + (거주 인구 밀도 × 0.3) − (방문 페널티 × 0.3)
```

- 방문 페널티: 7일 이내 방문 시 선형 감소 적용
- 스코어 범위: 0.0 ~ 1.0 (소수점 4자리)

## 주요 API

| Method | 경로 | 설명 |
|---|---|---|
| GET | `/api/spots` | 유세지 목록 (스코어 내림차순) |
| POST | `/api/spots` | 유세지 등록 |
| POST | `/api/spots/score-all` | 전체 스코어 갱신 |
| POST | `/api/spots/{id}/visit` | 방문 처리 |
| GET | `/api/org/tree` | 인맥 트리 (force-graph 형식) |
| GET | `/api/org/blank-regions` | 공백 지역 탐지 |
| POST | `/api/report/stream?llm=claude` | AI 전략 리포트 스트리밍 |

## 프로젝트 구조

```
election-manage/
├── apps/
│   ├── api/               # FastAPI
│   │   ├── app/
│   │   │   ├── routers/   # API 라우터
│   │   │   ├── models/    # SQLAlchemy 모델
│   │   │   ├── services/  # 비즈니스 로직
│   │   │   └── core/      # 설정, DB 연결
│   │   └── alembic/       # DB 마이그레이션
│   └── web/               # Next.js
│       ├── app/
│       │   ├── page.tsx       # 대시보드
│       │   ├── org/           # 조직 관리
│       │   ├── map/           # 유세지 지도
│       │   └── report/        # 전략 리포트
│       └── components/
├── packages/
│   └── types/             # 공유 타입
└── docker-compose.yml
```
