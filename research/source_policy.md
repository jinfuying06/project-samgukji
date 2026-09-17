# Source and Edition Policy

## Source layers

| Code | Meaning | Can support historical claim? | UI label |
| --- | --- | --- | --- |
| HISTORY_BASE | 정사 본문 | 조건부 yes | 정사 |
| HISTORY_ANNOTATION | 주석 및 인용 사료 | provenance와 충돌 표시 | 정사 주석 |
| ROMANCE | 문학 작품 | historical claim에는 no | 연의 |
| LATER_INTERPRETATION | 현대 연구/후대 해석 | 연구 주장으로만 | 연구/해석 |
| GAME_DATA | 게임 시스템/수치 | historical claim에는 no | 게임 |

## Evidence span required fields

- `evidence_id`, `source_id`, `source_layer`
- work title, edition, volume/chapter, locator
- original language text status
- translation type: publisher / project / paraphrase
- text or permitted excerpt, checksum
- person/event refs
- extraction reviewer and review status
- confidence and ambiguity note

## Edition and translation rules

- 같은 구절의 판본 차이를 덮어쓰지 않습니다.
- 현대 번역은 권리와 인용 한계를 기록합니다.
- 프로젝트 자체 번역은 검토자와 버전을 표시합니다.
- 불명확한 온라인 텍스트는 authoritative source로 승격하지 않습니다.
- 위치를 재확인할 수 없는 문장은 사용자에게 직접 인용으로 노출하지 않습니다.

## Conflict handling

상충 사료는 하나를 자동 선택하지 않고 다음을 기록합니다.

- source layer와 작성 시기
- 각 주장의 evidence ID
- 직접 충돌/세부 차이/한쪽 침묵
- 프로젝트의 표시 방식
- 결론 유보 여부

