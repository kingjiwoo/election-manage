---
name: score
description: 유세지 후보 목록을 스코어링 공식으로 분석하고 Claude API로 전략 리포트 생성
context: fork
agent: general-purpose
---
스코어링: (혼잡도 × 0.4) + (거주밀도 × 0.3) - (방문 페널티 × 0.3)
분석 후 apps/api/app/services/ 에서 관련 서비스 코드 확인, 개선안 제안.
