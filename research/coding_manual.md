# Historical Text Coding Manual

Version: `0.1 DRAFT`

## Unit of coding

- 기본 단위: 의미가 유지되는 최소 evidence span
- 하나의 span에 여러 행위가 있으면 별도 coding record로 분리
- 행위자, 대상, 사건, 시점, source layer를 보존

## Code template

| Field | Description |
| --- | --- |
| code_id | 안정적 코드 ID |
| label | 사람이 읽는 이름 |
| construct | 상위 구성개념 |
| definition | 포함되는 의미 |
| include | 명확한 포함 예시 |
| exclude | 혼동하기 쉬운 제외 예시 |
| direction | positive/negative/contextual |
| intensity | 명시적 척도와 anchor |
| ambiguity | 불확실/복수 해석 처리 |

## Starter codes (가설, 검증 전)

| Code | Construct | Working definition | Important exclusion |
| --- | --- | --- | --- |
| TALENT_RECRUIT | leadership | 유능한 인물을 식별·등용한 행위 | 단순 만남/언급 |
| DELEGATE_USE | leadership | 역할을 맡기고 조언/능력을 활용 | 결과만 있고 행위 불명 |
| SURRENDER_INTEGRATE | leadership | 항복 세력을 조직에 편입 | 강제 복속과 혼동 금지 |
| ALLIANCE_BUILD | diplomacy | 상호 조건을 가진 협력 구축 | 단순 동일 진영 |
| COMMAND_DECISION | military | 전투/작전의 명시적 지휘 결정 | 후대 귀속/전설 |
| ADMIN_REFORM | administration | 제도·행정 절차의 변경 | 단발성 명령 |
| PROMISE_KEEP | integrity | 확인 가능한 약속 이행 | 서술자의 추상 칭찬만 |
| BETRAY_OR_DEFECT | integrity | 기존 충성/합의를 깬 행위 | 시대적 소속 변화는 문맥 검토 |

## Context fields

- outcome: success / failure / mixed / unknown
- agency: direct / ordered / attributed / disputed
- narrative stance: neutral / praise / criticism / irony / unknown
- evidence strength: explicit / inferred / ambiguous

## Reliability procedure

1. 20~30개 span으로 codebook calibration
2. 두 코더 독립 코딩
3. 적절한 합치도 지표 선택(명목/순서/다중 라벨 고려)
4. 불일치 사유 분류: 정의, span 경계, entity, source, 해석
5. adjudicator가 결정하고 codebook 버전 갱신
6. 수정된 코드북으로 새 표본 재검증

LLM 코더는 동일 golden set에서 사람 합치도와 오류 유형을 검증하기 전 production label을 만들 수 없습니다.

