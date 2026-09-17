# Threat and Misuse Model

## Assets

- Source/edition metadata and permitted text
- Adjudicated codes and score models
- API/LLM credentials
- User account and activity data
- Public trust in source distinctions

## Key threats

| Threat | Example | Control |
| --- | --- | --- |
| Prompt injection from source text | 원문/메모가 LLM 명령처럼 작동 | content/instruction isolation, allowlisted tools |
| Source-layer leakage | 정사 모드에 연의 장면 포함 | retrieval filter + response validator + golden tests |
| Citation laundering | 위치 없는 문장이 근거처럼 표시 | evidence schema and resolver validation |
| Entity poisoning | alias로 다른 인물 병합 | reviewed canonical registry, collision tests |
| Score manipulation | 커스텀 가중치를 기본 점수로 공유 | signed/versioned score metadata and labels |
| Data exfiltration | 로그/프롬프트에 키·사용자 데이터 | minimization, redaction, secret storage |
| Rights violation | 현대 번역/게임 이미지 무단 노출 | rights registry and publication gate |
| Popularity gaming | 사용자 투표가 역사 지표 오염 | separate community layer, no silent merge |

## Human approval

- new source/translation publication
- codebook or default weight change
- adjudication of disputed high-impact evidence
- public release of external game comparison/assets
- high-risk moderation or community feature

## Open items

- Authentication/authorization design `[TBD]`
- Abuse rate limits `[TBD]`
- Incident and takedown process `[TBD]`
- Backup/rollback `[TBD]`

