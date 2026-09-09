# Opcode별 근거와 이후 검증

## 0x0000 — float 4바이트 읽기와 FUN_004eaf50 호출

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: float 4바이트 읽기와 FUN_004eaf50 호출.
- 미확정: 값의 단위·네트워크 제어 의미를 소비자에서 확인해야 함.
- native 연결: formatter 008179c0: opcode push 008179e3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 float 4바이트 읽기와 FUN_004eaf50 호출: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 391); [개별 발췌](evidence/2026-09-09-binary-events/branches/0000.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0005 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce0c0: opcode push 004ce0e9, length prefix 134, payload 132B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0006 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 429); [개별 발췌](evidence/2026-09-09-binary-events/branches/0006.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03e8 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 56건 / 27개 기록. payload 길이별 횟수: {"70": 56}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 00814bc0: opcode push 00814be3, length prefix 66, payload 64B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x03e9 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 7,870건 / 56개 기록. payload 길이별 횟수: {"101": 7870}.
- 바이너리 분기 복사 크기: [101] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 301); [개별 발췌](evidence/2026-09-09-binary-events/branches/03e9.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03ea — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 514); [개별 발췌](evidence/2026-09-09-binary-events/branches/03ea.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03eb — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 523); [개별 발췌](evidence/2026-09-09-binary-events/branches/03eb.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03ec — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 532); [개별 발췌](evidence/2026-09-09-binary-events/branches/03ec.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03ed — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 196건 / 43개 기록. payload 길이별 횟수: {"78": 196}.
- 바이너리 분기 복사 크기: [72] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 541); [개별 발췌](evidence/2026-09-09-binary-events/branches/03ed.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03ee — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 75,807건 / 56개 기록. payload 길이별 횟수: {"216": 75293, "222": 514}.
- 바이너리 분기 복사 크기: [216] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 578); [개별 발췌](evidence/2026-09-09-binary-events/branches/03ee.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03ef — ActionStartMatch

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 51건 / 51개 기록. payload 길이별 횟수: {"6": 51}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionStartMatch: 0081c400, vtable 0127cc08, store 0081c41b (direct_callee_store); formatter 00818bc0: opcode push 00818be3, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionStartMatch: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 594); [개별 발췌](evidence/2026-09-09-binary-events/branches/03ef.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03f0 — ActionShowMatchPrepSequence

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionShowMatchPrepSequence: 0081c3d0, vtable 0127cc1c, store 0081c3eb (direct_callee_store); formatter 008189c0: opcode push 008189e3, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionShowMatchPrepSequence: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 601); [개별 발췌](evidence/2026-09-09-binary-events/branches/03f0.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03f1 — ActionEndMatch

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 55건 / 55개 기록. payload 길이별 횟수: {"6": 55}.
- 바이너리 분기 복사 크기: [5] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 첫 BE32의 하위1B 승리 팀, +4 reason; reason2=surrender. 큐 액션.
- 미확정: reason0을 자동으로 크리스탈 파괴라 하지 않음. 실제 종료·최종 화면 시점은 별도 확인.
- native 연결: Nuo::Kindred::ActionEndMatch: 0081a680, vtable 0127c834, store 0081a6a7 (direct_callee_store).
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionEndMatch: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 608); [개별 발췌](evidence/2026-09-09-binary-events/branches/03f1.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03f2 — ActionEntitySpawn

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 926,602건 / 56개 기록. payload 길이별 횟수: {"122": 804425, "126": 122177}.
- 바이너리 분기 복사 크기: [122] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 개체 생성 자료를 읽고 ActionEntitySpawn 생성.
- 미확정: section 재전송과 신규 spawn, 정의 ID·팀·좌표와 122/126B 변형을 구별해야 함.
- native 연결: Nuo::Kindred::ActionEntitySpawn: 0081a750, vtable 0127c85c, store 0081a794 (direct_callee_store).
- 오프라인 후속: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 검증 V01: 대상 ActionEntitySpawn: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 619); [개별 발췌](evidence/2026-09-09-binary-events/branches/03f2.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03f3 — ActionHeroSpawn

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 75,316건 / 56개 기록. payload 길이별 횟수: {"746": 74802, "750": 514}.
- 바이너리 분기 복사 크기: [746] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 영웅 초기 상태/스냅샷; helper를 거쳐 ActionHeroSpawn.
- 미확정: 746/750B 변형과 빌드 대응, 반복 snapshot과 실제 영웅 생성/부활의 구별이 필요함.
- native 연결: Nuo::Kindred::ActionHeroSpawn: 004d5930 → 0081ac20, vtable 0127c914, store 0081ac92 (one_helper_callee_store).
- 오프라인 후속: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 검증 V01: 대상 ActionHeroSpawn: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 723); [개별 발췌](evidence/2026-09-09-binary-events/branches/03f3.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03f4 — ActionRequestMoveTo_Client

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 8B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x1d == 0 and object+0x1c == 0.
- native 연결: Nuo::Kindred::ActionRequestMoveTo_Client::vftable: 0052a420 → 004d6540 → 004cf8f0, opcode push 004cf913, payload 8B, 조건 object+0x1d == 0 and object+0x1c == 0 (요청 직렬화; 실제 기록 방향은 미확정); formatter 004cf8f0: opcode push 004cf913, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionRequestMoveTo_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.

## 0x03f5 — ActionRequestMoveTo_Client

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 8B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x1d == 0 and object+0x1c != 0.
- native 연결: Nuo::Kindred::ActionRequestMoveTo_Client::vftable: 0052a420 → 004d6490 → 004cf6f0, opcode push 004cf713, payload 8B, 조건 object+0x1d == 0 and object+0x1c != 0 (요청 직렬화; 실제 기록 방향은 미확정); formatter 004cf6f0: opcode push 004cf713, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionRequestMoveTo_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.

## 0x03f6 — ActionRequestMoveTo_Client

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 8B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x1d != 0.
- native 연결: Nuo::Kindred::ActionRequestMoveTo_Client::vftable: 0052a420 → 004d63f0 → 004cf4f0, opcode push 004cf513, payload 8B, 조건 object+0x1d != 0 (요청 직렬화; 실제 기록 방향은 미확정); formatter 004cf4f0: opcode push 004cf513, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionRequestMoveTo_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.

## 0x03f8 — ActionMoveTo

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 4,949,279건 / 56개 기록. payload 길이별 횟수: {"9": 236343, "14": 4712936}.
- 바이너리 분기 복사 크기: [9] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionMoveTo: 0081bc80, vtable 0127ca68, store 0081bc9f (direct_callee_store); formatter 00815ac0: opcode push 00815ae3, length prefix 11, payload 9B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionMoveTo: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 946); [개별 발췌](evidence/2026-09-09-binary-events/branches/03f8.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03f9 — ActionMoveToServerAuthoritative

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 151,463건 / 54개 기록. payload 길이별 횟수: {"14": 151463}.
- 바이너리 분기 복사 크기: [14] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionMoveToServerAuthoritative: 0081bd50, vtable 0127caa4, store 0081bd6f (direct_callee_store); formatter 00815dc0: opcode push 00815de3, length prefix 16, payload 14B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionMoveToServerAuthoritative: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 980); [개별 발췌](evidence/2026-09-09-binary-events/branches/03f9.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03fa — ActionMoveToAndFace

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 197,182건 / 54개 기록. payload 길이별 횟수: {"22": 197182}.
- 바이너리 분기 복사 크기: [20] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionMoveToAndFace: 0081bcc0, vtable 0127ca7c, store 0081bce5 (direct_callee_store); formatter 00815bc0: opcode push 00815be3, length prefix 22, payload 20B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionMoveToAndFace: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1027); [개별 발췌](evidence/2026-09-09-binary-events/branches/03fa.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03fb — ActionStopActor

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 188,017건 / 54개 기록. payload 길이별 횟수: {"22": 188017}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionStopActor: 0081c470, vtable 0127cc44, store 0081c48f (direct_callee_store); formatter 00815ec0: opcode push 00815ee3, length prefix 19, payload 17B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionStopActor: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1083); [개별 발췌](evidence/2026-09-09-binary-events/branches/03fb.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03fc — ActionResetMovement_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionResetMovement_Client: 0052a600, vtable 0121aa54, store 0052a628 (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionResetMovement_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1133); [개별 발췌](evidence/2026-09-09-binary-events/branches/03fc.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03fd — ActionMoveToPredictive_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [9] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionMoveToPredictive_Client: 00529a80, vtable 0121a974, store 00529a9f (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionMoveToPredictive_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1190); [개별 발췌](evidence/2026-09-09-binary-events/branches/03fd.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03fe — ActionMoveToAuthoritative_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionMoveToAuthoritative_Client: 005298e0, vtable 0121a960, store 00529908 (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionMoveToAuthoritative_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1218); [개별 발췌](evidence/2026-09-09-binary-events/branches/03fe.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x03ff — ActionStopAuthoritative_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [10] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionStopAuthoritative_Client: 0052ab20, vtable 0121aacc, store 0052ab3f (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionStopAuthoritative_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1275); [개별 발췌](evidence/2026-09-09-binary-events/branches/03ff.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0400 — ActionStopNavigating_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [9] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionStopNavigating_Client: 0052ac40, vtable 0121aae0, store 0052ac5f (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionStopNavigating_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1298); [개별 발췌](evidence/2026-09-09-binary-events/branches/0400.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0401 — ActionFaceDir

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 1,667건 / 54개 기록. payload 길이별 횟수: {"22": 1667}.
- 바이너리 분기 복사 크기: [16] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionFaceDir: 0081a9a0, vtable 0127c884, store 0081a9bf (direct_callee_store); formatter 008159c0: opcode push 008159e3, length prefix 18, payload 16B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionFaceDir: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1321); [개별 발췌](evidence/2026-09-09-binary-events/branches/0401.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0402 — ActionAutoActorBounce

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 6,884건 / 49개 기록. payload 길이별 횟수: {"22": 6884}.
- 바이너리 분기 복사 크기: [16] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionAutoActorBounce: 0081a130, vtable 0127c70c, store 0081a166 (direct_callee_store); formatter 008154c0: opcode push 008154e3, length prefix 18, payload 16B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionAutoActorBounce: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1373); [개별 발췌](evidence/2026-09-09-binary-events/branches/0402.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0403 — ActionAutoMoveTo

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 34,973건 / 54개 기록. payload 길이별 횟수: {"22": 34973}.
- 바이너리 분기 복사 크기: [21] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionAutoMoveTo; 위치형 float가 있어도 현재 위치로 단정하지 않음.
- 미확정: 이동 목적지·시간 계수와 현재 위치를 구별하고 기존 cooldown 추정을 사용하지 않음.
- native 연결: Nuo::Kindred::ActionAutoMoveTo: 0081a180, vtable 0127c720, store 0081a1a4 (direct_callee_store); formatter 008155c0: opcode push 008155e3, length prefix 23, payload 21B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionAutoMoveTo: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1409); [개별 발췌](evidence/2026-09-09-binary-events/branches/0403.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0404 — ActionAutoMoveToActorResponse

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 789건 / 14개 기록. payload 길이별 횟수: {"22": 789}.
- 바이너리 분기 복사 크기: [15] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionAutoMoveToActorResponse: 00529240, vtable 0121a8dc, store 0052925e (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionAutoMoveToActorResponse: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1468); [개별 발췌](evidence/2026-09-09-binary-events/branches/0404.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0405 — ActionAutoMoveToLocation_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [21] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionAutoMoveToLocation_Client: 00529380, vtable 0121a8f0, store 0052939e (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionAutoMoveToLocation_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1514); [개별 발췌](evidence/2026-09-09-binary-events/branches/0405.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0406 — ActionAutoOrbit

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 2,084건 / 29개 기록. payload 길이별 횟수: {"38": 2084}.
- 바이너리 분기 복사 크기: [32] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionAutoOrbit: 0081a1d0, vtable 0127c734, store 0081a204 (direct_callee_store); formatter 008156c0: opcode push 008156e3, length prefix 34, payload 32B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionAutoOrbit: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1565); [개별 발췌](evidence/2026-09-09-binary-events/branches/0406.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0407 — ActionCancelAutoOrbit

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 548건 / 20개 기록. payload 길이별 횟수: {"22": 548}.
- 바이너리 분기 복사 크기: [16] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionCancelAutoOrbit: 0081a2f0, vtable 0127c770, store 0081a30f (direct_callee_store); formatter 008157c0: opcode push 008157e3, length prefix 18, payload 16B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionCancelAutoOrbit: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1645); [개별 발췌](evidence/2026-09-09-binary-events/branches/0407.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0408 — ActionAttachToActor_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [6] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionAttachToActor_Client: 00529110, vtable 0121a8c8, store 00529129 (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionAttachToActor_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1697); [개별 발췌](evidence/2026-09-09-binary-events/branches/0408.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0409 — ActionTeleportTo

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 5,579건 / 55개 기록. payload 길이별 횟수: {"22": 5579}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionTeleportTo: 0081c580, vtable 0127cc80, store 0081c59f (direct_callee_store); formatter 00815fc0: opcode push 00815fe3, length prefix 19, payload 17B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionTeleportTo: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1711); [개별 발췌](evidence/2026-09-09-binary-events/branches/0409.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x040a — ActionTeleport_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionTeleport_Client: 0052af50, vtable 0121ab08, store 0052af78 (direct_callee_store).
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionTeleport_Client: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1761); [개별 발췌](evidence/2026-09-09-binary-events/branches/040a.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x040b — ActionEntityDestroy

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 115,602건 / 55개 기록. payload 길이별 횟수: {"6": 115602}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: payload+0 BE32 개체 ID, ActionEntityDestroy.
- 미확정: 예약 정리와 즉시 제거·사망·보상은 별개임.
- native 연결: Nuo::Kindred::ActionEntityDestroy: 0081a6c0, vtable 0127c848, store 0081a6fe (direct_callee_store); formatter 008158c0: opcode push 008158e3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 검증 V01: 대상 ActionEntityDestroy: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1818); [개별 발췌](evidence/2026-09-09-binary-events/branches/040b.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x040d — ActionFireProjectile

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 849,998건 / 56개 기록. payload 길이별 횟수: {"22": 849998}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionFireProjectile: 0081ab10, vtable 0127c898, store 0081ab40 (direct_callee_store); formatter 008161c0: opcode push 008161e3, length prefix 19, payload 17B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionFireProjectile: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1827); [개별 발췌](evidence/2026-09-09-binary-events/branches/040d.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x040e — ActionFireProjectile

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 39,316건 / 54개 기록. payload 길이별 횟수: {"30": 39316}.
- 바이너리 분기 복사 크기: [28] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionFireProjectile: 0081aa90, vtable 0127c898, store 0081aab5 (direct_callee_store); formatter 008163c0: opcode push 008163e3, length prefix 30, payload 28B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionFireProjectile: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1862); [개별 발췌](evidence/2026-09-09-binary-events/branches/040e.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x040f — ActionFireProjectile

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 40,887건 / 53개 기록. payload 길이별 횟수: {"46": 40887}.
- 바이너리 분기 복사 크기: [44] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionFireProjectile: 0081a9e0, vtable 0127c898, store 0081aa0a (direct_callee_store); formatter 008162c0: opcode push 008162e3, length prefix 46, payload 44B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionFireProjectile: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1912); [개별 발췌](evidence/2026-09-09-binary-events/branches/040f.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0410 — ActionDetonateProjectile

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 52,977건 / 54개 기록. payload 길이별 횟수: {"22": 52977}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionDetonateProjectile: 0081a5f0, vtable 0127c80c, store 0081a60f (direct_callee_store); formatter 008152c0: opcode push 008152e3, length prefix 19, payload 17B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionDetonateProjectile: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 1965); [개별 발췌](evidence/2026-09-09-binary-events/branches/0410.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0411 — ActionRequestActivateAbility

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 5B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x28 mode 0 or 3.
- native 연결: Nuo::Kindred::ActionRequestActivateAbility::vftable: 0094c1a0 → 0095c230 → 008181c0, opcode push 008181e3, payload 5B, 조건 object+0x28 mode 0 or 3 (요청 직렬화; 실제 기록 방향은 미확정); formatter 008181c0: opcode push 008181e3, length prefix 7, payload 5B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionRequestActivateAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.

## 0x0412 — ActionRequestActivateAbility

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 13B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x28 mode 1.
- native 연결: Nuo::Kindred::ActionRequestActivateAbility::vftable: 0094c1a0 → 008182c0, opcode push 008182e3, payload 13B, 조건 object+0x28 mode 1 (요청 직렬화; 실제 기록 방향은 미확정); formatter 008182c0: opcode push 008182e3, length prefix 15, payload 13B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionRequestActivateAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.

## 0x0413 — ActionRequestActivateAbility

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 17B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x28 mode 2.
- native 연결: Nuo::Kindred::ActionRequestActivateAbility::vftable: 0094c1a0 → 008183c0, opcode push 008183e3, payload 17B, 조건 object+0x28 mode 2 (요청 직렬화; 실제 기록 방향은 미확정); formatter 008183c0: opcode push 008183e3, length prefix 19, payload 17B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionRequestActivateAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.

## 0x0414 — ActionRequestCancelAbility_Client

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 613건 / 9개 기록. payload 길이별 횟수: {"6": 613}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 2B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: 추가 변형 조건 미기재.
- native 연결: Nuo::Kindred::ActionRequestCancelAbility_Client::vftable: 0052a140 → 004d6470 → 004cf5f0, opcode push 004cf613, payload 2B, 조건 None (요청 직렬화; 실제 기록 방향은 미확정); formatter 004cf5f0: opcode push 004cf613, length prefix 4, payload 2B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionRequestCancelAbility_Client: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.

## 0x0415 — ActionPlayAbility

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 1,261,753건 / 56개 기록. payload 길이별 횟수: {"14": 1261753}.
- 바이너리 분기 복사 크기: [9] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionPlayAbility: 0081bf10, vtable 0127cb08, store 0081bf2f (direct_callee_store); Nuo::Kindred::ActionPlayAbility: 0081bfd0, vtable 0127cb08, store 0081bff5 (direct_callee_store); formatter 00817ac0: opcode push 00817ae3, length prefix 11, payload 9B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionPlayAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2008); [개별 발췌](evidence/2026-09-09-binary-events/branches/0415.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0416 — ActionPlayAbility

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 79,676건 / 54개 기록. payload 길이별 횟수: {"22": 79676}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionPlayAbility; 좌표형 필드가 포함될 수 있음.
- 미확정: 기존 위치 후보에서 실제 시전 주체·능력 ID·목표 위치·단계를 분리해야 함.
- native 연결: Nuo::Kindred::ActionPlayAbility: 0081beb0, vtable 0127cb08, store 0081becf (direct_callee_store); formatter 00817bc0: opcode push 00817be3, length prefix 19, payload 17B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionPlayAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2034); [개별 발췌](evidence/2026-09-09-binary-events/branches/0416.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0417 — ActionPlayAbility

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [21] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionPlayAbility: 0081bf70, vtable 0127cb08, store 0081bf95 (direct_callee_store); formatter 00817cc0: opcode push 00817ce3, length prefix 23, payload 21B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionPlayAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2084); [개별 발췌](evidence/2026-09-09-binary-events/branches/0417.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0418 — ActionPlayVoiceOver

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 로컬 연출과 서버 사건, 개인/팀/전체 수신 범위, 표시 ID와 전투 영향은 별도임.
- native 연결: Nuo::Kindred::ActionPlayVoiceOver: 0081c030, vtable 0127cb1c, store 0081c057 (direct_callee_store); formatter 00817dc0: opcode push 00817de3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: localization/audio/pfx/UI 소비 경로와 수신 범위, 참조 ID·위치·지속시간, 로컬 요청 여부를 확인한다.
- 실행 검증 V09: 대상 ActionPlayVoiceOver: 비공개/연습 환경에서 해당 알림·핑·음성·효과·표시를 하나씩 발생시키고 지원되는 관점별 화면/음향을 비교한다.
- 대조 조건: 로컬 표시/음량 설정 변경, 수신 범위 밖, 유사하지만 다른 알림을 대조한다.
- 통과 기준: ID·대상·범위·표시가 일치하고 로컬 연출을 피해·처치·아이템 획득으로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2139); [개별 발췌](evidence/2026-09-09-binary-events/branches/0418.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0419 — ActionPlayPfxAtLocation

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 5,520건 / 54개 기록. payload 길이별 횟수: {"30": 5520}.
- 바이너리 분기 복사 크기: [24] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 로컬 연출과 서버 사건, 개인/팀/전체 수신 범위, 표시 ID와 전투 영향은 별도임.
- native 연결: Nuo::Kindred::ActionPlayPfxAtLocation: 00529bd0, vtable 0121a988, store 00529bef (direct_callee_store).
- 오프라인 후속: localization/audio/pfx/UI 소비 경로와 수신 범위, 참조 ID·위치·지속시간, 로컬 요청 여부를 확인한다.
- 실행 검증 V09: 대상 ActionPlayPfxAtLocation: 비공개/연습 환경에서 해당 알림·핑·음성·효과·표시를 하나씩 발생시키고 지원되는 관점별 화면/음향을 비교한다.
- 대조 조건: 로컬 표시/음량 설정 변경, 수신 범위 밖, 유사하지만 다른 알림을 대조한다.
- 통과 기준: ID·대상·범위·표시가 일치하고 로컬 연출을 피해·처치·아이템 획득으로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2154); [개별 발췌](evidence/2026-09-09-binary-events/branches/0419.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x041a — ActionOverrideAbility

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 55,144건 / 54개 기록. payload 길이별 횟수: {"14": 55144}.
- 바이너리 분기 복사 크기: [13] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionOverrideAbility: 0081bda0, vtable 0127cab8, store 0081bdd3 (direct_callee_store); formatter 008177c0: opcode push 008177e3, length prefix 15, payload 13B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionOverrideAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2218); [개별 발췌](evidence/2026-09-09-binary-events/branches/041a.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x041b — ActionClearAbilityOverride

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 52,309건 / 53개 기록. payload 길이별 횟수: {"14": 52309}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionClearAbilityOverride: 0081a370, vtable 0127c798, store 0081a397 (direct_callee_store); formatter 00814ac0: opcode push 00814ae3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionClearAbilityOverride: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2242); [개별 발췌](evidence/2026-09-09-binary-events/branches/041b.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x041c — ActionModifyActorAttribute

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 272,490건 / 56개 기록. payload 길이별 횟수: {"22": 272490}.
- 바이너리 분기 복사 크기: [15] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: +0/+4 BE32 참조, +8 float, +12 index, +13 layer, +14 SET/ADD; index41/42는 K/D.
- 미확정: ref1을 가해자로 취급하지 않음. 전체 계층·reset·computed 값과 최종 화면은 별도 확인.
- native 연결: Nuo::Kindred::ActionModifyActorAttribute: 0081b910, vtable 0127c9a0, store 0081b94e (direct_callee_store); formatter 00816dc0: opcode push 00816de3, length prefix 17, payload 15B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: index별 setter→getter→명명된 export/UI 소비 경로와 초기 snapshot·reset·clamp를 추적한다. 상관만으로 자원 이름을 정하지 않는다.
- 실행 검증 V05: 대상 ActionModifyActorAttribute: 대기→구매→판매→단독 막타→근처 공유 처치→정글 처치를 분리한다. 레벨업 후 포인트를 보유했다가 능력 하나만 강화한다.
- 대조 조건: SET 재전송, 무행동 자연 수입, 막타 없는 근접, 거절 구매, 사망 reset을 대조한다.
- 통과 기준: 연산과 snapshot으로 복원한 수치가 각 관측 시점과 일치하고 잔액·총수입·레벨·포인트를 구별한다. 최종 KDA는 결과 화면으로 별도 확인한다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2257); [개별 발췌](evidence/2026-09-09-binary-events/branches/041c.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x041d — ActionModifyActorResource

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 4,606,221건 / 56개 기록. payload 길이별 횟수: {"14": 4606221}.
- 바이너리 분기 복사 크기: [12] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: +0 BE32 참조, +4 float, +8 index, +9 SET/ADD, +10/+11 flags; index11은 assists.
- 미확정: resource14의 화면 이름과 다른 자원 의미·flags·총수입/잔액을 별도로 확인.
- native 연결: Nuo::Kindred::ActionModifyActorResource: 0081b960, vtable 0127c9b4, store 0081b992 (direct_callee_store); formatter 00816ec0: opcode push 00816ee3, length prefix 14, payload 12B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: index별 setter→getter→명명된 export/UI 소비 경로와 초기 snapshot·reset·clamp를 추적한다. 상관만으로 자원 이름을 정하지 않는다.
- 실행 검증 V05: 대상 ActionModifyActorResource: 대기→구매→판매→단독 막타→근처 공유 처치→정글 처치를 분리한다. 레벨업 후 포인트를 보유했다가 능력 하나만 강화한다.
- 대조 조건: SET 재전송, 무행동 자연 수입, 막타 없는 근접, 거절 구매, 사망 reset을 대조한다.
- 통과 기준: 연산과 snapshot으로 복원한 수치가 각 관측 시점과 일치하고 잔액·총수입·레벨·포인트를 구별한다. 최종 KDA는 결과 화면으로 별도 확인한다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2286); [개별 발췌](evidence/2026-09-09-binary-events/branches/041d.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x041e — ActionImpactHealth

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 2,146,087건 / 56개 기록. payload 길이별 횟수: {"22": 2146087}.
- 바이너리 분기 복사 크기: [16] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionImpactHealth: 0081b6b0, vtable 0127c928, store 0081b6f6 (direct_callee_store); formatter 008167c0: opcode push 008167e3, length prefix 18, payload 16B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionImpactHealth: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2318); [개별 발췌](evidence/2026-09-09-binary-events/branches/041e.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x041f — ActionModifyGameModeVar

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 336건 / 56개 기록. payload 길이별 횟수: {"14": 336}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionModifyGameModeVar: 0081bbb0, vtable 0127ca2c, store 0081bbdd (direct_callee_store); formatter 008174c0: opcode push 008174e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionModifyGameModeVar: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2351); [개별 발췌](evidence/2026-09-09-binary-events/branches/041f.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0420 — ActionCreateZoneOfControl

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [29] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionCreateZoneOfControl: 0081a500, vtable 0127c7d0, store 0081a556 (direct_callee_store); formatter 00814ec0: opcode push 00814ee3, length prefix 31, payload 29B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionCreateZoneOfControl: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2368); [개별 발췌](evidence/2026-09-09-binary-events/branches/0420.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0421 — ActionCreateZoneOfControl

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 1,123건 / 35개 기록. payload 길이별 횟수: {"25": 276, "30": 847}.
- 바이너리 분기 복사 크기: [25] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionCreateZoneOfControl: 0081a450, vtable 0127c7d0, store 0081a475 (direct_callee_store); formatter 00814fc0: opcode push 00814fe3, length prefix 27, payload 25B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionCreateZoneOfControl: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2413); [개별 발췌](evidence/2026-09-09-binary-events/branches/0421.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0422 — ActionCreateZoneOfControl

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 201건 / 3개 기록. payload 길이별 횟수: {"24": 66, "30": 135}.
- 바이너리 분기 복사 크기: [24] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionCreateZoneOfControl: 0081a3f0, vtable 0127c7d0, store 0081a41a (direct_callee_store); formatter 00814dc0: opcode push 00814de3, length prefix 26, payload 24B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionCreateZoneOfControl: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2465); [개별 발췌](evidence/2026-09-09-binary-events/branches/0422.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0423 — ActionDestroyZoneOfControl

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 981건 / 36개 기록. payload 길이별 횟수: {"6": 981}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionDestroyZoneOfControl: 0081a5c0, vtable 0127c7f8, store 0081a5e1 (direct_callee_store); formatter 008151c0: opcode push 008151e3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionDestroyZoneOfControl: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2532); [개별 발췌](evidence/2026-09-09-binary-events/branches/0423.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0424 — ActionRequestModifyBasicAttackTarget

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 243,474건 / 54개 기록. payload 길이별 횟수: {"6": 243474}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 5B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: 추가 변형 조건 미기재.
- native 연결: Nuo::Kindred::ActionRequestModifyBasicAttackTarget::vftable: 0052a320 → 004d6510 → 004cf7f0, opcode push 004cf813, payload 5B, 조건 None (요청 직렬화; 실제 기록 방향은 미확정); formatter 004cf7f0: opcode push 004cf813, length prefix 7, payload 5B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionRequestModifyBasicAttackTarget: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.

## 0x0425 — ActionModifyBasicAttackTarget

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 4,713건 / 54개 기록. payload 길이별 횟수: {"6": 4713}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionModifyBasicAttackTarget: 005296f0, vtable 0121a938, store 00529711 (direct_callee_store).
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionModifyBasicAttackTarget: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2541); [개별 발췌](evidence/2026-09-09-binary-events/branches/0425.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0427 — ActionPauseCooldown

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [9] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionPauseCooldown: 0081bde0, vtable 0127cae0, store 0081be0d (direct_callee_store); formatter 008178c0: opcode push 008178e3, length prefix 11, payload 9B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionPauseCooldown: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2550); [개별 발췌](evidence/2026-09-09-binary-events/branches/0427.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0428 — ActionModifyCooldown

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 135,732건 / 54개 기록. payload 길이별 횟수: {"14": 135732}.
- 바이너리 분기 복사 크기: [13] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionModifyCooldown: 0081bb60, vtable 0127ca18, store 0081bb92 (direct_callee_store); formatter 008173c0: opcode push 008173e3, length prefix 15, payload 13B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionModifyCooldown: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2567); [개별 발췌](evidence/2026-09-09-binary-events/branches/0428.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0429 — ActionModifyAbilityCharges

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 1,314건 / 13개 기록. payload 길이별 횟수: {"14": 1314}.
- 바이너리 분기 복사 크기: [13] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionModifyAbilityCharges: 0081b8d0, vtable 0127c98c, store 0081b903 (direct_callee_store); formatter 00816cc0: opcode push 00816ce3, length prefix 15, payload 13B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionModifyAbilityCharges: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2595); [개별 발췌](evidence/2026-09-09-binary-events/branches/0429.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x042b — ActionModifyVisibility

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 4,967,338건 / 56개 기록. payload 길이별 횟수: {"14": 4967338}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionModifyVisibility; BE32 참조와 index/state/mask 바이트.
- 미확정: 클래스 이름이 있어도 각 bit·수신자·팀/안개 상태의 의미는 별도 검증.
- native 연결: Nuo::Kindred::ActionModifyVisibility: 0081bc30, vtable 0127ca54, store 0081bc69 (direct_callee_store); formatter 008176c0: opcode push 008176e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: manifest/kind와 팀 조회, visibility bit/mask, 어그로 대상, 소유 변경과 팀 보상 소비 경로를 연결한다.
- 실행 검증 V07: 대상 ActionModifyVisibility: 수풀/시야 경계 진입·이탈과 어그로 변경을 관측한다. 목표물은 터렛·크리스탈·대형 몬스터를 종류별로 하나씩 양 팀 관점에서 비교한다.
- 대조 조건: 피해만 주고 미처치, 다른 팀 처치, 시야 밖, 포획 없는 소멸을 대조한다.
- 통과 기준: 종류·팀·수신 범위와 처치/포획/소유권/재등장이 일치하고 원시 source를 최종 보상 귀속으로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2621); [개별 발췌](evidence/2026-09-09-binary-events/branches/042b.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x042c — ActionModifySpawnCampVisibility_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 85,867건 / 56개 기록. payload 길이별 횟수: {"6": 85867}.
- 바이너리 분기 복사 크기: [6] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 개체 종류·소유 팀·시야 수신자·원시 source·처치 인정자·보상 수신자는 별개임.
- native 연결: Nuo::Kindred::ActionModifySpawnCampVisibility_Client: 005297f0, vtable 0121a94c, store 0052981d (direct_callee_store).
- 오프라인 후속: manifest/kind와 팀 조회, visibility bit/mask, 어그로 대상, 소유 변경과 팀 보상 소비 경로를 연결한다.
- 실행 검증 V07: 대상 ActionModifySpawnCampVisibility_Client: 수풀/시야 경계 진입·이탈과 어그로 변경을 관측한다. 목표물은 터렛·크리스탈·대형 몬스터를 종류별로 하나씩 양 팀 관점에서 비교한다.
- 대조 조건: 피해만 주고 미처치, 다른 팀 처치, 시야 밖, 포획 없는 소멸을 대조한다.
- 통과 기준: 종류·팀·수신 범위와 처치/포획/소유권/재등장이 일치하고 원시 source를 최종 보상 귀속으로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2637); [개별 발췌](evidence/2026-09-09-binary-events/branches/042c.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x042e — ActionMoveToCorrection

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [12] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionMoveToCorrection: 0081bd10, vtable 0127ca90, store 0081bd2f (direct_callee_store); formatter 00815cc0: opcode push 00815ce3, length prefix 14, payload 12B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionMoveToCorrection: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2652); [개별 발췌](evidence/2026-09-09-binary-events/branches/042e.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x042f — ActionActorUndead

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 18건 / 2개 기록. payload 길이별 횟수: {"6": 18}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 생성·스냅샷 재전송·사망·모델 소멸·부활·ID 재사용을 구별해야 함.
- native 연결: Nuo::Kindred::ActionActorUndead: 00819fb0, vtable 0127c6e4, store 00819fd1 (direct_callee_store); formatter 008143c0: opcode push 008143e3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 검증 V01: 대상 ActionActorUndead: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2692); [개별 발췌](evidence/2026-09-09-binary-events/branches/042f.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0430 — ActionActorDie

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 100,641건 / 56개 기록. payload 길이별 횟수: {"14": 100641}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 앞 8바이트: 사망 개체와 원시 source BE32 두 개; 관측 잔여6B 미해석.
- 미확정: 원시 source≠확정 킬 귀속. 액션 개수≠최종 데스; 종료 전 예외와 비영웅을 구별.
- native 연결: Nuo::Kindred::ActionActorDie: 00819f30, vtable 0127c6bc, store 00819f57 (direct_callee_store); formatter 008141c0: opcode push 008141e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 검증 V01: 대상 ActionActorDie: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2701); [개별 발췌](evidence/2026-09-09-binary-events/branches/0430.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0431 — ActionActorDead

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 97,794건 / 56개 기록. payload 길이별 횟수: {"6": 97794}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionActorDead; 참조 BE32, 기존 apply는 조건부 상태3→4.
- 미확정: 이름만으로 사망 순간으로 재해석하지 않음. 0430·타이머·모델 소멸·부활과 각각 대조.
- native 연결: Nuo::Kindred::ActionActorDead: 00819f00, vtable 0127c6a8, store 00819f21 (direct_callee_store); formatter 008140c0: opcode push 008140e3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 검증 V01: 대상 ActionActorDead: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2716); [개별 발췌](evidence/2026-09-09-binary-events/branches/0431.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0432 — ActionActorRespawn

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 2,084건 / 55개 기록. payload 길이별 횟수: {"22": 2084}.
- 바이너리 분기 복사 크기: [16] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 생성·스냅샷 재전송·사망·모델 소멸·부활·ID 재사용을 구별해야 함.
- native 연결: Nuo::Kindred::ActionActorRespawn: 00819f70, vtable 0127c6d0, store 00819f8f (direct_callee_store); formatter 008142c0: opcode push 008142e3, length prefix 18, payload 16B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 검증 V01: 대상 ActionActorRespawn: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2725); [개별 발췌](evidence/2026-09-09-binary-events/branches/0432.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0433 — ActionStartRespawnTimer

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 생성·스냅샷 재전송·사망·모델 소멸·부활·ID 재사용을 구별해야 함.
- native 연결: Nuo::Kindred::ActionStartRespawnTimer: 0081c430, vtable 0127cc30, store 0081c456 (direct_callee_store); formatter 00818cc0: opcode push 00818ce3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 검증 V01: 대상 ActionStartRespawnTimer: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2775); [개별 발췌](evidence/2026-09-09-binary-events/branches/0433.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0434 — ActionLevelUp

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 7,822건 / 55개 기록. payload 길이별 횟수: {"14": 7822}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionLevelUp 클래스 연결.
- 미확정: 영웅 레벨과 능력 강화 포인트·경험치·연출의 실제 필드를 소비자에서 확인.
- native 연결: Nuo::Kindred::ActionLevelUp: 0081b840, vtable 0127c964, store 0081b867 (direct_callee_store); formatter 00816ac0: opcode push 00816ae3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: index별 setter→getter→명명된 export/UI 소비 경로와 초기 snapshot·reset·clamp를 추적한다. 상관만으로 자원 이름을 정하지 않는다.
- 실행 검증 V05: 대상 ActionLevelUp: 대기→구매→판매→단독 막타→근처 공유 처치→정글 처치를 분리한다. 레벨업 후 포인트를 보유했다가 능력 하나만 강화한다.
- 대조 조건: SET 재전송, 무행동 자연 수입, 막타 없는 근접, 거절 구매, 사망 reset을 대조한다.
- 통과 기준: 연산과 snapshot으로 복원한 수치가 각 관측 시점과 일치하고 잔액·총수입·레벨·포인트를 구별한다. 최종 KDA는 결과 화면으로 별도 확인한다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2796); [개별 발췌](evidence/2026-09-09-binary-events/branches/0434.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0435 — ActionMakeAnnouncement

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [24] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 로컬 연출과 서버 사건, 개인/팀/전체 수신 범위, 표시 ID와 전투 영향은 별도임.
- native 연결: Nuo::Kindred::ActionMakeAnnouncement: 0081b880, vtable 0127c978, store 0081b8bf (direct_callee_store); formatter 00816bc0: opcode push 00816be3, length prefix 26, payload 24B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: localization/audio/pfx/UI 소비 경로와 수신 범위, 참조 ID·위치·지속시간, 로컬 요청 여부를 확인한다.
- 실행 검증 V09: 대상 ActionMakeAnnouncement: 비공개/연습 환경에서 해당 알림·핑·음성·효과·표시를 하나씩 발생시키고 지원되는 관점별 화면/음향을 비교한다.
- 대조 조건: 로컬 표시/음량 설정 변경, 수신 범위 밖, 유사하지만 다른 알림을 대조한다.
- 통과 기준: ID·대상·범위·표시가 일치하고 로컬 연출을 피해·처치·아이템 획득으로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2811); [개별 발췌](evidence/2026-09-09-binary-events/branches/0435.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0436 — ActionRequestUpgradeAbility_Client

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 1B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: 추가 변형 조건 미기재.
- native 연결: Nuo::Kindred::ActionRequestUpgradeAbility_Client::vftable: 0052a5f0 → 004d6600 → 004cfbf0, opcode push 004cfc13, payload 1B, 조건 None (요청 직렬화; 실제 기록 방향은 미확정); formatter 004cfbf0: opcode push 004cfc13, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionRequestUpgradeAbility_Client: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.

## 0x0437 — ActionQuickBuyItem

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함.
- native 연결: Nuo::Kindred::ActionQuickBuyItem: 0081c070, vtable 0127cb30, store 0081c091 (direct_callee_store); formatter 00817fc0: opcode push 00817fe3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionQuickBuyItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2851); [개별 발췌](evidence/2026-09-09-binary-events/branches/0437.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0438 — ActionReorderItem

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 727건 / 54개 기록. payload 길이별 횟수: {"6": 727}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 6B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: 추가 변형 조건 미기재.
- native 연결: Nuo::Kindred::ActionReorderItem::vftable: 0094c0b0 → 008180c0, opcode push 008180e3, payload 6B, 조건 None (요청 직렬화; 실제 기록 방향은 미확정); formatter 008180c0: opcode push 008180e3, length prefix 8, payload 6B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionReorderItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.

## 0x0439 — ActionBuyItem

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionBuyItem 클래스 연결.
- 미확정: 구매 요청/처리·거절과 GrantItem/ConsumeItem의 조합 관계, 금액 차감은 별도 확인.
- native 연결: Nuo::Kindred::ActionBuyItem: 0081a270, vtable 0127cb6c, store 0081a297 (direct_callee_store); formatter 008147c0: opcode push 008147e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionBuyItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2860); [개별 발췌](evidence/2026-09-09-binary-events/branches/0439.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x043a — ActionGrantAbility

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 5,840건 / 55개 기록. payload 길이별 횟수: {"14": 5840}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionGrantAbility: 0081aba0, vtable 0127c8ac, store 0081abc7 (direct_callee_store); formatter 008164c0: opcode push 008164e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionGrantAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2875); [개별 발췌](evidence/2026-09-09-binary-events/branches/043a.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x043b — ActionDowngradeAbility

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionDowngradeAbility: 0081a640, vtable 0127c820, store 0081a667 (direct_callee_store); formatter 008153c0: opcode push 008153e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionDowngradeAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2890); [개별 발췌](evidence/2026-09-09-binary-events/branches/043b.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x043c — ActionCancelAbility

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 91,152건 / 54개 기록. payload 길이별 횟수: {"14": 91152}.
- 바이너리 분기 복사 크기: [10] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionCancelAbility: 0081a2b0, vtable 0127c75c, store 0081a2e3 (direct_callee_store); formatter 008148c0: opcode push 008148e3, length prefix 12, payload 10B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionCancelAbility: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2905); [개별 발췌](evidence/2026-09-09-binary-events/branches/043c.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x043d — ActionGrantItem

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 11,663건 / 56개 기록. payload 길이별 횟수: {"14": 11663}.
- 바이너리 분기 복사 크기: [12] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionGrantItem 클래스 연결.
- 미확정: 아이템 지급 원인이 구매인지 보상인지 미확정. 조합·슬롯·수량을 검증.
- native 연결: Nuo::Kindred::ActionGrantItem: 0081abe0, vtable 0127c8c0, store 0081ac0d (direct_callee_store); formatter 008165c0: opcode push 008165e3, length prefix 14, payload 12B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionGrantItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2923); [개별 발췌](evidence/2026-09-09-binary-events/branches/043d.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x043e — ActionApplyBuff

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 4,320,170건 / 56개 기록. payload 길이별 횟수: {"22": 4320170}.
- 바이너리 분기 복사 크기: [16] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionApplyBuff: 00819fe0, vtable 0127c6f8, store 0081a03c (direct_callee_store); formatter 008145c0: opcode push 008145e3, length prefix 18, payload 16B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionApplyBuff: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2944); [개별 발췌](evidence/2026-09-09-binary-events/branches/043e.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x043f — ActionApplyBuff

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 3,084,299건 / 56개 기록. payload 길이별 횟수: {"34": 2198719, "38": 885580}.
- 바이너리 분기 복사 크기: [34] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionApplyBuff: 00819fe0, vtable 0127c6f8, store 0081a03c (direct_callee_store); formatter 008144c0: opcode push 008144e3, length prefix 36, payload 34B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionApplyBuff: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 2989); [개별 발췌](evidence/2026-09-09-binary-events/branches/043f.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0440 — ActionShowFlyoutText

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 7,554건 / 54개 기록. payload 길이별 횟수: {"14": 7554}.
- 바이너리 분기 복사 크기: [10] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 로컬 연출과 서버 사건, 개인/팀/전체 수신 범위, 표시 ID와 전투 영향은 별도임.
- native 연결: Nuo::Kindred::ActionShowFlyoutText: 0081c390, vtable 0127cbf4, store 0081c3bd (direct_callee_store); formatter 008188c0: opcode push 008188e3, length prefix 12, payload 10B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: localization/audio/pfx/UI 소비 경로와 수신 범위, 참조 ID·위치·지속시간, 로컬 요청 여부를 확인한다.
- 실행 검증 V09: 대상 ActionShowFlyoutText: 비공개/연습 환경에서 해당 알림·핑·음성·효과·표시를 하나씩 발생시키고 지원되는 관점별 화면/음향을 비교한다.
- 대조 조건: 로컬 표시/음량 설정 변경, 수신 범위 밖, 유사하지만 다른 알림을 대조한다.
- 통과 기준: ID·대상·범위·표시가 일치하고 로컬 연출을 피해·처치·아이템 획득으로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3059); [개별 발췌](evidence/2026-09-09-binary-events/branches/0440.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0441 — ActionModifyBuffDuration

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 15,353건 / 46개 기록. payload 길이별 횟수: {"14": 15353}.
- 바이너리 분기 복사 크기: [12] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionModifyBuffDuration: 0081b9b0, vtable 0127c9c8, store 0081b9dc (direct_callee_store); formatter 00816fc0: opcode push 00816fe3, length prefix 14, payload 12B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionModifyBuffDuration: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3079); [개별 발췌](evidence/2026-09-09-binary-events/branches/0441.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0442 — ActionModifyBuffMaxStacks

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [12] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionModifyBuffMaxStacks: 0081b9f0, vtable 0127c9dc, store 0081ba1d (direct_callee_store); formatter 008170c0: opcode push 008170e3, length prefix 14, payload 12B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionModifyBuffMaxStacks: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3106); [개별 발췌](evidence/2026-09-09-binary-events/branches/0442.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0443 — ActionModifyBuffStack

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 122,176건 / 54개 기록. payload 길이별 횟수: {"14": 122176}.
- 바이너리 분기 복사 크기: [12] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionModifyBuffStack: 0081ba30, vtable 0127c9f0, store 0081ba63 (direct_callee_store); formatter 008171c0: opcode push 008171e3, length prefix 14, payload 12B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionModifyBuffStack: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3127); [개별 발췌](evidence/2026-09-09-binary-events/branches/0443.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0444 — ActionModifyItemStack

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [12] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함.
- native 연결: Nuo::Kindred::ActionModifyItemStack: 0081bbf0, vtable 0127ca40, store 0081bc1d (direct_callee_store); formatter 008175c0: opcode push 008175e3, length prefix 14, payload 12B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionModifyItemStack: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3149); [개별 발췌](evidence/2026-09-09-binary-events/branches/0444.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0445 — ActionCancelBuff

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 139,309건 / 56개 기록. payload 길이별 횟수: {"14": 139309}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionCancelBuff: 0081a330, vtable 0127c784, store 0081a357 (direct_callee_store); formatter 008149c0: opcode push 008149e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionCancelBuff: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3170); [개별 발췌](evidence/2026-09-09-binary-events/branches/0445.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0446 — ActionTimeoutBuff

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 8,094건 / 54개 기록. payload 길이별 횟수: {"14": 8094}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionTimeoutBuff: 0081c5d0, vtable 0127cc94, store 0081c5f7 (direct_callee_store); formatter 00818ec0: opcode push 00818ee3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionTimeoutBuff: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3185); [개별 발췌](evidence/2026-09-09-binary-events/branches/0446.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0447 — ActionDecrementBuffStack

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 586건 / 6개 기록. payload 길이별 횟수: {"14": 586}.
- 바이너리 분기 복사 크기: [12] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionDecrementBuffStack: 0081a580, vtable 0127c7e4, store 0081a5ad (direct_callee_store); formatter 008150c0: opcode push 008150e3, length prefix 14, payload 12B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionDecrementBuffStack: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3200); [개별 발췌](evidence/2026-09-09-binary-events/branches/0447.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0448 — ActionRequestActivateItem

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 11,711건 / 55개 기록. payload 길이별 횟수: {"6": 11711}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 4B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x24 mode 3.
- native 연결: Nuo::Kindred::ActionRequestActivateItem::vftable: 00529ff0 → 0095bda0 → 00813dc0, opcode push 00813de3, payload 4B, 조건 object+0x24 mode 3 (요청 직렬화; 실제 기록 방향은 미확정); formatter 00813dc0: opcode push 00813de3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionRequestActivateItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.

## 0x0449 — ActionRequestActivateItem

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 31건 / 14개 기록. payload 길이별 횟수: {"14": 31}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 8B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x24 mode 0.
- native 연결: Nuo::Kindred::ActionRequestActivateItem::vftable: 00529ff0 → 0095bea0 → 00813fc0, opcode push 00813fe3, payload 8B, 조건 object+0x24 mode 0 (요청 직렬화; 실제 기록 방향은 미확정); formatter 00813fc0: opcode push 00813fe3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionRequestActivateItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.

## 0x044a — ActionRequestActivateItem

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 6,084건 / 54개 기록. payload 길이별 횟수: {"22": 6084}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 16B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: object+0x24 mode 1.
- native 연결: Nuo::Kindred::ActionRequestActivateItem::vftable: 00529ff0 → 0095bdd0 → 00813ec0, opcode push 00813ee3, payload 16B, 조건 object+0x24 mode 1 (요청 직렬화; 실제 기록 방향은 미확정); formatter 00813ec0: opcode push 00813ee3, length prefix 18, payload 16B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionRequestActivateItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.

## 0x044b — ActionConsumeItem

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 7,327건 / 55개 기록. payload 길이별 횟수: {"14": 7327}.
- 바이너리 분기 복사 크기: [10] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionConsumeItem 클래스 연결; C의 case1099에 대응.
- 미확정: 소모품 사용·조합 소비·기타 제거를 구별. 과거 판매 후보 라벨을 확정하지 않음.
- native 연결: Nuo::Kindred::ActionConsumeItem: 0081a3b0, vtable 0127c7ac, store 0081a3dd (direct_callee_store); formatter 00814cc0: opcode push 00814ce3, length prefix 12, payload 10B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionConsumeItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3221); [개별 발췌](evidence/2026-09-09-binary-events/branches/044b.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x044c — ActionItemActivated

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 17,438건 / 55개 기록. payload 길이별 횟수: {"22": 17438}.
- 바이너리 분기 복사 크기: [21] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함.
- native 연결: Nuo::Kindred::ActionItemActivated: 0081b740, vtable 0127c950, store 0081b764 (direct_callee_store); Nuo::Kindred::ActionItemActivated: 0081b790, vtable 0127c950, store 0081b7ba (direct_callee_store); Nuo::Kindred::ActionItemActivated: 0081b7f0, vtable 0127c950, store 0081b81a (direct_callee_store); formatter 008169c0: opcode push 008169e3, length prefix 23, payload 21B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionItemActivated: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3239); [개별 발췌](evidence/2026-09-09-binary-events/branches/044c.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x044d — ActionSellItem

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 326건 / 47개 기록. payload 길이별 횟수: {"14": 326}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionSellItem 클래스 연결.
- 미확정: 판매 가능 조건·수량·슬롯·환급액과 실패 요청을 별도 확인.
- native 연결: Nuo::Kindred::ActionSellItem: 0081c200, vtable 0127cb80, store 0081c227 (direct_callee_store); formatter 008186c0: opcode push 008186e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionSellItem: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3281); [개별 발췌](evidence/2026-09-09-binary-events/branches/044d.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x044e — ActionPing

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [22] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 로컬 연출과 서버 사건, 개인/팀/전체 수신 범위, 표시 ID와 전투 영향은 별도임.
- native 연결: Nuo::Kindred::ActionPing: 0081be50, vtable 0127caf4, store 0081be69 (direct_callee_store); formatter 00817ec0: opcode push 00817ee3, length prefix 24, payload 22B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: localization/audio/pfx/UI 소비 경로와 수신 범위, 참조 ID·위치·지속시간, 로컬 요청 여부를 확인한다.
- 실행 검증 V09: 대상 ActionPing: 비공개/연습 환경에서 해당 알림·핑·음성·효과·표시를 하나씩 발생시키고 지원되는 관점별 화면/음향을 비교한다.
- 대조 조건: 로컬 표시/음량 설정 변경, 수신 범위 밖, 유사하지만 다른 알림을 대조한다.
- 통과 기준: ID·대상·범위·표시가 일치하고 로컬 연출을 피해·처치·아이템 획득으로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3296); [개별 발췌](evidence/2026-09-09-binary-events/branches/044e.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x044f — ActionHUDQuickMessage

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 1,896건 / 54개 기록. payload 길이별 횟수: {"22": 1896}.
- 바이너리 분기 복사 크기: [17] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 로컬 연출과 서버 사건, 개인/팀/전체 수신 범위, 표시 ID와 전투 영향은 별도임.
- native 연결: Nuo::Kindred::ActionHUDQuickMessage: 005294c0, vtable 0121a904, store 005294f8 (direct_callee_store); formatter 008166c0: opcode push 008166e3, length prefix 19, payload 17B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: localization/audio/pfx/UI 소비 경로와 수신 범위, 참조 ID·위치·지속시간, 로컬 요청 여부를 확인한다.
- 실행 검증 V09: 대상 ActionHUDQuickMessage: 비공개/연습 환경에서 해당 알림·핑·음성·효과·표시를 하나씩 발생시키고 지원되는 관점별 화면/음향을 비교한다.
- 대조 조건: 로컬 표시/음량 설정 변경, 수신 범위 밖, 유사하지만 다른 알림을 대조한다.
- 통과 기준: ID·대상·범위·표시가 일치하고 로컬 연출을 피해·처치·아이템 획득으로 오인하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3335); [개별 발췌](evidence/2026-09-09-binary-events/branches/044f.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0451 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3373); [개별 발췌](evidence/2026-09-09-binary-events/branches/0451.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0452 — method_onPacket_LevelControllerOnEnterPostGame

- 근거 단계: 콜백명 연결; 현재 수신기 개별 처리: True.
- 관측: 50건 / 50개 기록. payload 길이별 횟수: {"6": 50}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: LevelControllerOnEnterPostGame 콜백 이름; 분기는1B를 복사, 나머지5B 미해석.
- 미확정: 모든 callback 실행·서버 점수 중단을 증명하지 않음. 같은 시각 뒤의 정상 점수14건을 버리지 않음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 method_onPacket_LevelControllerOnEnterPostGame: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3385); [개별 발췌](evidence/2026-09-09-binary-events/branches/0452.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0453 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [32] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3446); [개별 발췌](evidence/2026-09-09-binary-events/branches/0453.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0454 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [68] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3474); [개별 발췌](evidence/2026-09-09-binary-events/branches/0454.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0455 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce3f0: opcode push 004ce413, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0456 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004cf0f0: opcode push 004cf113, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0458 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 20건 / 14개 기록. payload 길이별 횟수: {"6": 20}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce5f0: opcode push 004ce613, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0459 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [2584] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3495); [개별 발췌](evidence/2026-09-09-binary-events/branches/0459.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x045a — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [2584] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3529); [개별 발췌](evidence/2026-09-09-binary-events/branches/045a.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x045b — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [2134] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3563); [개별 발췌](evidence/2026-09-09-binary-events/branches/045b.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x045c — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 771건 / 51개 기록. payload 길이별 횟수: {"102": 771}.
- 바이너리 분기 복사 크기: [96] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3615); [개별 발췌](evidence/2026-09-09-binary-events/branches/045c.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x045d — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ceff0: opcode push 004cf013, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x045e — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004cebf0: opcode push 004cec13, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x045f — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ceef0: opcode push 004cef13, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0461 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004cedf0: opcode push 004cee13, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0462 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce9f0: opcode push 004cea13, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0463 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ceaf0: opcode push 004ceb13, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0464 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce8f0: opcode push 004ce913, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0465 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce4f0: opcode push 004ce513, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0466 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004cf1f0: opcode push 004cf213, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0467 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004cecf0: opcode push 004ced13, length prefix 4, payload 2B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0468 — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce7f0: opcode push 004ce813, length prefix 4, payload 2B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x046b — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce6f0: opcode push 004ce713, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x046c — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3636); [개별 발췌](evidence/2026-09-09-binary-events/branches/046c.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x046d — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 387건 / 56개 기록. payload 길이별 횟수: {"6": 387}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce2f0: opcode push 004ce313, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x046e — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 252건 / 56개 기록. payload 길이별 횟수: {"6": 252}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004ce1f0: opcode push 004ce213, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x046f — 69B 변형의 +64 BE float가 game clock인 경로 확인

- 근거 단계: 기존 명명 소비 경로 근거; 현재 수신기 개별 처리: True.
- 관측: 7,870건 / 56개 기록. payload 길이별 횟수: {"69": 7870}.
- 바이너리 분기 복사 크기: [69] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 69B 변형의 +64 BE float가 game clock인 경로 확인.
- 미확정: outer record time과 UI time을 구별. 길이·빌드와 clock acceptance를 먼저 확인.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 69B 변형의 +64 BE float가 game clock인 경로 확인: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3641); [개별 발췌](evidence/2026-09-09-binary-events/branches/046f.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0470 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 8,029건 / 56개 기록. payload 길이별 횟수: {"1": 7870, "6": 159}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3686); [개별 발췌](evidence/2026-09-09-binary-events/branches/0470.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0471 — 미명명 패킷 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 212건 / 53개 기록. payload 길이별 횟수: {"6": 212}.
- 바이너리 분기 복사 크기: [5] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004cf3f0: opcode push 004cf413, length prefix 7, payload 5B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3710); [개별 발췌](evidence/2026-09-09-binary-events/branches/0471.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0472 — ActionSetSurrenderStateRequest

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 1B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: 추가 변형 조건 미기재.
- native 연결: Nuo::Kindred::ActionSetSurrenderStateRequest::vftable: 0052a9a0 → 0095c2b0 → 008187c0, opcode push 008187e3, payload 1B, 조건 None (요청 직렬화; 실제 기록 방향은 미확정); formatter 008187c0: opcode push 008187e3, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionSetSurrenderStateRequest: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.

## 0x0473 — ActionTeamSurrenderStateChanged

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [151] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionTeamSurrenderStateChanged: 0081c500, vtable 0127cc6c, store 0081c529 (direct_callee_store).
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionTeamSurrenderStateChanged: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3735); [개별 발췌](evidence/2026-09-09-binary-events/branches/0473.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0474 — ActionSpectatorExitMatchRequest

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 1B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: slot4 is thunk_FUN_0095c2d0.
- native 연결: Nuo::Kindred::ActionSpectatorExitMatchRequest::vftable: 0052aa20 → 00818ac0, opcode push 00818ae3, payload 1B, 조건 slot4 is thunk_FUN_0095c2d0 (요청 직렬화; 실제 기록 방향은 미확정); formatter 00818ac0: opcode push 00818ae3, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionSpectatorExitMatchRequest: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.

## 0x0475 — ActionPauseTutorial

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionPauseTutorial: 0081be20, vtable 0127cacc, store 0081be41 (direct_callee_store); formatter 004cf2f0: opcode push 004cf313, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionPauseTutorial: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3769); [개별 발췌](evidence/2026-09-09-binary-events/branches/0475.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0476 — ActionSetSimulationSpeed

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionSetSimulationSpeed: 0081c350, vtable 0127cbcc, store 0081c370 (direct_callee_store).
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionSetSimulationSpeed: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3793); [개별 발췌](evidence/2026-09-09-binary-events/branches/0476.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0477 — ActionSetPlayerAsSpectator

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [5] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionSetPlayerAsSpectator: 0081c2d0, vtable 0127cbe0, store 0081c2f7 (direct_callee_store).
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionSetPlayerAsSpectator: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3818); [개별 발췌](evidence/2026-09-09-binary-events/branches/0477.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0478 — ActionSetMinimapSpawnPhase_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 6,715건 / 56개 기록. payload 길이별 횟수: {"14": 6715}.
- 바이너리 분기 복사 크기: [9] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 개체 종류·소유 팀·시야 수신자·원시 source·처치 인정자·보상 수신자는 별개임.
- native 연결: Nuo::Kindred::ActionSetMinimapSpawnPhase_Client: 0052a860, vtable 0121aa7c, store 0052a88d (direct_callee_store).
- 오프라인 후속: manifest/kind와 팀 조회, visibility bit/mask, 어그로 대상, 소유 변경과 팀 보상 소비 경로를 연결한다.
- 실행 검증 V07: 대상 ActionSetMinimapSpawnPhase_Client: 수풀/시야 경계 진입·이탈과 어그로 변경을 관측한다. 목표물은 터렛·크리스탈·대형 몬스터를 종류별로 하나씩 양 팀 관점에서 비교한다.
- 대조 조건: 피해만 주고 미처치, 다른 팀 처치, 시야 밖, 포획 없는 소멸을 대조한다.
- 통과 기준: 종류·팀·수신 범위와 처치/포획/소유권/재등장이 일치하고 원시 source를 최종 보상 귀속으로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3829); [개별 발췌](evidence/2026-09-09-binary-events/branches/0478.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0479 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [66] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3868); [개별 발췌](evidence/2026-09-09-binary-events/branches/0479.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x047a — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3931); [개별 발췌](evidence/2026-09-09-binary-events/branches/047a.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x047b — 미명명 패킷 후보

- 근거 단계: 패킷 직렬화 경로 확인; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 고정 header의 u16 길이/opcode 상수와 payload 복사 크기, 공통 전달 함수 호출 확인; payload 의미와 기록 방향은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: formatter 004cfaf0: opcode push 004cfb13, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 패킷 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x047c — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3949); [개별 발췌](evidence/2026-09-09-binary-events/branches/047c.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x047d — ActionTutorialStateChangedResponse

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionTutorialStateChangedResponse: 0052b060, vtable 0121ab1c, store 0052b081 (direct_callee_store).
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionTutorialStateChangedResponse: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3971); [개별 발췌](evidence/2026-09-09-binary-events/branches/047d.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x047e — ActionStateChange_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님.
- native 연결: Nuo::Kindred::ActionStateChange_Client: 0052aa30, vtable 0121aab8, store 0052aa49 (direct_callee_store).
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 ActionStateChange_Client: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 3994); [개별 발췌](evidence/2026-09-09-binary-events/branches/047e.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x047f — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4011); [개별 발췌](evidence/2026-09-09-binary-events/branches/047f.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0480 — 미명명 후보

- 근거 단계: 처리 분기만 확인; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [82] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 미명명 후보: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4060); [개별 발췌](evidence/2026-09-09-binary-events/branches/0480.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0481 — ActionEquipTalent

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 2건 / 2개 기록. payload 길이별 횟수: {"6": 2}.
- 바이너리 분기 복사 크기: [6] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함.
- native 연결: Nuo::Kindred::ActionEquipTalent: 0081a960, vtable 0127c870, store 0081a98d (direct_callee_store); formatter 008160c0: opcode push 008160e3, length prefix 8, payload 6B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionEquipTalent: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4088); [개별 발췌](evidence/2026-09-09-binary-events/branches/0481.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0482 — ActionUnequipTalent

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함.
- native 연결: Nuo::Kindred::ActionUnequipTalent: 0081c610, vtable 0127cca8, store 0081c631 (direct_callee_store); formatter 00818fc0: opcode push 00818fe3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionUnequipTalent: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4099); [개별 발췌](evidence/2026-09-09-binary-events/branches/0482.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0483 — ActionInvalidateTalent

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [4] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함.
- native 연결: Nuo::Kindred::ActionInvalidateTalent: 0081b710, vtable 0127c93c, store 0081b731 (direct_callee_store); formatter 008168c0: opcode push 008168e3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionInvalidateTalent: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4106); [개별 발췌](evidence/2026-09-09-binary-events/branches/0483.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0484 — ActionRequestEquipTalent

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 2건 / 2개 기록. payload 길이별 횟수: {"6": 2}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 4B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: 추가 변형 조건 미기재.
- native 연결: Nuo::Kindred::ActionRequestEquipTalent::vftable: 0052a1e0 → 0095c260 → 008184c0, opcode push 008184e3, payload 4B, 조건 None (요청 직렬화; 실제 기록 방향은 미확정); formatter 008184c0: opcode push 008184e3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionRequestEquipTalent: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.

## 0x0485 — ActionRequestRecommendedBuildPath

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 465건 / 54개 기록. payload 길이별 횟수: {"6": 465}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 1B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: 추가 변형 조건 미기재.
- native 연결: Nuo::Kindred::ActionRequestRecommendedBuildPath::vftable: 0052a560 → 004d65c0 → 004cf9f0, opcode push 004cfa13, payload 1B, 조건 None (요청 직렬화; 실제 기록 방향은 미확정); formatter 004cf9f0: opcode push 004cfa13, length prefix 3, payload 1B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionRequestRecommendedBuildPath: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.

## 0x0486 — ActionRequestLevelLogicEvent_Client

- 근거 단계: 요청 직렬화 클래스 연결; 현재 수신기 개별 처리: False.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 요청 formatter의 opcode 상수와 직렬화 payload 길이 확인: 4B. 바깥 VGR framing과 구별.
- 미확정: 요청 생성/전송과 서버 수락·실제 행동 성공은 별개. 변형 조건: 추가 변형 조건 미기재.
- native 연결: Nuo::Kindred::ActionRequestLevelLogicEvent_Client::vftable: 0052a280 → 0095c280 → 008185c0, opcode push 008185e3, payload 4B, 조건 None (요청 직렬화; 실제 기록 방향은 미확정); formatter 008185c0: opcode push 008185e3, length prefix 6, payload 4B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 검증 V00: 대상 ActionRequestLevelLogicEvent_Client: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다. 실제 송신 bytes와 수신/리플레이 방향을 독립 확인한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

## 0x0487 — ActionSetBuildPath

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [99] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함.
- native 연결: Nuo::Kindred::ActionSetBuildPath: 0081c240, vtable 0127cba4, store 0081c278 (direct_callee_store).
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionSetBuildPath: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4131); [개별 발췌](evidence/2026-09-09-binary-events/branches/0487.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0488 — ActionSetRecommendedBuildPath

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 543건 / 56개 기록. payload 길이별 횟수: {"6": 543}.
- 바이너리 분기 복사 크기: [5] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함.
- native 연결: Nuo::Kindred::ActionSetRecommendedBuildPath: 0081c310, vtable 0127cbb8, store 0081c337 (direct_callee_store).
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionSetRecommendedBuildPath: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4163); [개별 발췌](evidence/2026-09-09-binary-events/branches/0488.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0489 — ActionSyncAbilityBehavior

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [10] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionSyncAbilityBehavior: 0081c4c0, vtable 0127cc58, store 0081c4f3 (direct_callee_store); formatter 00818dc0: opcode push 00818de3, length prefix 12, payload 10B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionSyncAbilityBehavior: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4174); [개별 발췌](evidence/2026-09-09-binary-events/branches/0489.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x048a — ActionSyncCooldown_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 971,766건 / 56개 기록. payload 길이별 횟수: {"22": 971766}.
- 바이너리 분기 복사 크기: [22] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함.
- native 연결: Nuo::Kindred::ActionSyncCooldown_Client: 0052ad40, vtable 0121aaf4, store 0052ad69 (direct_callee_store).
- 오프라인 후속: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 검증 V03: 대상 ActionSyncCooldown_Client: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4198); [개별 발췌](evidence/2026-09-09-binary-events/branches/048a.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x048b — ActionModifyBuffVar

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 586건 / 3개 기록. payload 길이별 횟수: {"30": 586}.
- 바이너리 분기 복사 크기: [29] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함.
- native 연결: Nuo::Kindred::ActionModifyBuffVar: 0081ba70, vtable 0127ca04, store 0081ba9d (direct_callee_store); formatter 008172c0: opcode push 008172e3, length prefix 31, payload 29B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 검증 V04: 대상 ActionModifyBuffVar: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4253); [개별 발췌](evidence/2026-09-09-binary-events/branches/048b.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x048c — ActionSendAggroState_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 27,235건 / 56개 기록. payload 길이별 횟수: {"14": 27235}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 개체 종류·소유 팀·시야 수신자·원시 source·처치 인정자·보상 수신자는 별개임.
- native 연결: Nuo::Kindred::ActionSendAggroState_Client: 0052a750, vtable 0121aa68, store 0052a788 (direct_callee_store).
- 오프라인 후속: manifest/kind와 팀 조회, visibility bit/mask, 어그로 대상, 소유 변경과 팀 보상 소비 경로를 연결한다.
- 실행 검증 V07: 대상 ActionSendAggroState_Client: 수풀/시야 경계 진입·이탈과 어그로 변경을 관측한다. 목표물은 터렛·크리스탈·대형 몬스터를 종류별로 하나씩 양 팀 관점에서 비교한다.
- 대조 조건: 피해만 주고 미처치, 다른 팀 처치, 시야 밖, 포획 없는 소멸을 대조한다.
- 통과 기준: 종류·팀·수신 범위와 처치/포획/소유권/재등장이 일치하고 원시 source를 최종 보상 귀속으로 단정하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4334); [개별 발췌](evidence/2026-09-09-binary-events/branches/048c.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x048d — 1612B 누적 통계 구조, 피해·아이템·팀 통계의 명명 소비 경로

- 근거 단계: 기존 명명 소비 경로 근거; 현재 수신기 개별 처리: True.
- 관측: 55건 / 55개 기록. payload 길이별 횟수: {"1614": 55}.
- 바이너리 분기 복사 크기: [1612] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 1612B 누적 통계 구조, 피해·아이템·팀 통계의 명명 소비 경로.
- 미확정: 개별 피해/처치 이벤트나 직접 최종 KDA 패킷이 아님. 필드별 단위·결과 화면 대조 필요.
- native 연결: 직접 연결된 Action 클래스 없음; 미명명 분기/콜백 근거 유지.
- 오프라인 후속: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 검증 V08: 대상 1612B 누적 통계 구조, 피해·아이템·팀 통계의 명명 소비 경로: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4371); [개별 발췌](evidence/2026-09-09-binary-events/branches/048d.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x048f — ActionRejectBuyItem_Client

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 11건 / 9개 기록. payload 길이별 횟수: {"6": 11}.
- 바이너리 분기 복사 크기: [1] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: ActionRejectBuyItem_Client가 dispatcher 안에서 직접 설치됨.
- 미확정: 읽는1B·거절 사유·관련 구매 요청의 연결은 별도 확인.
- native 연결: Nuo::Kindred::ActionRejectBuyItem_Client: 004cfec0, vtable 01215f1c, store 004d4fbc (inline_dispatcher_store).
- 오프라인 후속: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 검증 V06: 대상 ActionRejectBuyItem_Client: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4395); [개별 발췌](evidence/2026-09-09-binary-events/branches/048f.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.

## 0x0490 — ActionBroadcastSwapTarget

- 근거 단계: 클래스명 연결; 현재 수신기 개별 처리: True.
- 관측: 0건 / 0개 기록. payload 길이별 횟수: {}.
- 바이너리 분기 복사 크기: [8] bytes. 이는 완전한 wire layout 크기 보장이 아니다.
- 필드 근거: 분기 복사 크기·byte order helper·생성자 저장 위치를 근거에 보존; 필드 이름은 미확정.
- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함.
- native 연결: Nuo::Kindred::ActionBroadcastSwapTarget: 0081a230, vtable 0127c748, store 0081a257 (direct_callee_store); formatter 008146c0: opcode push 008146e3, length prefix 10, payload 8B; 고정 header와 공통 전달 함수 호출.
- 오프라인 후속: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 검증 V02: 대상 ActionBroadcastSwapTarget: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.
- 원본 분기: [dispatcher 분기 metadata](evidence/2026-09-09-binary-events/source-branches.json) (비공개 원본 line 4420); [개별 발췌](evidence/2026-09-09-binary-events/branches/0490.c.txt). 함수 연결은 후보 근거이며 모든 조건의 실행을 보장하지 않는다.
