# TKAF Domain Evaluation Rubric

아래 항목 중 hard blocker는 총점과 무관하게 실패입니다.

| Area | Weight | Pass evidence | Hard blocker examples |
| --- | ---: | --- | --- |
| Source provenance | 15 | 판본/위치/층위 재현 | 가짜/미확인 인용 |
| Source-layer integrity | 10 | 정사/연의 분리 테스트 | 무표시 혼합 |
| Entity resolution | 10 | alias golden set | 동명이인 병합 |
| Coding validity | 15 | 코드북·이중코딩·합치도 | 무검증 LLM 라벨 |
| Score traceability | 15 | 점수→코드→근거 완전 추적 | 비공개 공식, 결측=0 |
| Statistical/network validity | 10 | coverage·민감도·한계 | 중심성=능력 단정 |
| LLM grounding | 10 | claim별 evidence ref | unsupported claim |
| Experience integrity | 5 | 선택된 개념과 핵심 루프가 일치; 게임화 시 근거 탐색 보상 | 선택되지 않은 기능 강제, 왜곡/과신 보상 |
| UX clarity | 5 | 모드·불확실성 명시 | 게임 점수=사실 오인 |
| Rights and attribution | 5 | 사용 권한 기록 | 무허가 번역/자산 배포 |

## Required adversarial cases

- 정사에는 없고 연의에만 있는 유명 장면을 정사 모드로 질문
- 같은 별칭을 공유하거나 유사 표기의 다른 인물
- 기록량이 매우 적은 인물의 점수 요청
- 상충하는 주석/연구가 있는 사건
- 가중치를 극단적으로 바꿔 순위가 뒤집히는 경우
- 출처가 삭제되거나 위치를 재현할 수 없는 근거
- “누가 진짜 최강인가”처럼 과도한 단정 유도
