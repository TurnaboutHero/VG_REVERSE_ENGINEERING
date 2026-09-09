# 네이티브 개체 종류 근거와 남은 경계

검증된 Actor 리소스를 추가로 제공하면 네이티브 종류 값 0은 `hero`, 2와 3은
`structure`로 연결한다. 이름 목록만 읽거나 다른 종류 값을 읽은 항목은
`unknown`으로 남는다. 이전에 남아 있던 직렬화 타입과 actor 생성 callback의
연결은 아래 초기화 코드와 이름 해시 재계산으로 확인했다. 이번 증거는 정적
분석이며 새 런타임 메모리 관찰이나 화면 대조는 아니다.

검증 빌드 SHA-256:
`659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`.
주소는 Windows VA이며 image base는 `00400000`이다.

`00942480`은 **actor+`0x1c`가 가리키는 설정의 첫 uint32**를 읽고
actor+`0x1e0`에 플래그를 쓴다. 이 값은 actor+`0x180`의 정의 번호와 다르다.

| 설정 값 | 생성 플래그 | 확인 범위 |
|---|---|---|
| 0 | bit 0 | `005b19e0`의 영웅 아이콘, `00541430`의 영웅 처치 안내 경로 |
| 2 또는 3 | bit 12 | 공통 구조물 분기 |
| 2 | bit 15 | 베인 크리스탈 아이콘 분기 |
| 3 | bit 13 또는 14 | native `VainNode` hash 비교로 armory와 turret 분리 |
| 4 | bit 2 | Blackclaw, Ghostwing, Kraken을 포함하는 분기. 모든 값 4의 대상을 포괄하는 분류는 미확정 |
| 1 또는 5 | bit 4 또는 8 | 미니언 아이콘을 공유하며 siege/captain, Treant/TestDummy 등의 하위 분기 존재 |

bit 31은 영웅 외에 FortressMinion에도 설정되므로 영웅 판정에 쓰지 않는다.
문자열 이름의 일부를 보고 타입을 추측하는 규칙도 추가하지 않는다.

## 직렬화 타입에서 종류 필드까지

1. 파일에 저장된 전역 포인터 `01a7524c`는 BSS descriptor `020e9974`를
   가리킨다. 초기화 함수 `004222f0`은 이름 주소 `01266800`의 `Actor`, 크기
   `0x208`(520바이트), 정렬 4, descriptor kind 1을 생성자 `0112bec0`에 넘긴다.
2. 생성자는 이름 길이와 seed `12345678`을 사용해 `004c4450`의 네이티브
   해시를 계산한다. `0112bf02`의 `mov [edi+4],eax`가 descriptor+4, 즉
   `020e9978`에 타입 key를 쓴다. 같은 연산을 재계산한
   `hash(Actor, 12345678)`은 **`2419fb6c`**다. 별개 포인터 타입 `Actor*`의
   해시 `bd869a1f`와 혼동하지 않는다.
3. 생성자는 descriptor를 `020ec99c`의 목록에 등록한다. CFF 로더 `0112c820`은
   이 목록에서 SYMB의 타입 key로 descriptor를 선택한다. SYMB payload는
   `u32 root_offset`, `u32 type_key`, NUL 종료 이름이며 root는 decoded INST
   시작 주소에 root_offset을 더한 주소다.
4. `00954e40`의 `00954f8f` 부근은 위 descriptor+4의 key에 callback
   `00942d90`을 등록한다. 생성 경로 `01129ea0`은 `0112c050`으로 정의 이름을
   조회하고 같은 타입 key의 callback에 root를 넘긴다. callback은 이 포인터를
   새 actor+`0x1c`에 저장한다(`00942daa`).
5. 따라서 Actor SYMB 타입 `2419fb6c`로 확인한 리소스의 root 첫 uint32는
   `00942480`이 읽는 설정 종류 값이다. 실제 크리스탈의 값 2와 영웅의 값 0을
   위 플래그 분기와 연결할 수 있다.

네이티브 로더와 이름 조회는 원래의 직렬화 이름을 같은 해시 함수와 seed로
처리한다. 리더는 Manifest의 `serialized_name`과 SYMB 이름을 바이트 단위로
대조하며 별표를 제거한 표시 이름, 파일명 또는 부분 문자열로 자산을 고르지 않는다.
예를 들어 `*VainNode*`의 등록 해시 `2352b58e`와 표시 이름 `VainNode`의
하위 타입 비교 해시 `20e92aca`는 용도가 다르다.

## 자산 대조와 지원 범위

같은 빌드의 사용자 보유 리소스 9개에서 Actor 타입, architecture 0/code 1,
version 12, root offset 0과 root 필드가 relocation이 아닌 것을 확인했다.
Hero000·SAW·Amael은 값 0, VainCrystal_Away_5v5는 값 2,
VainNode·Turret5v5·OuterTurret5v5는 값 3이었다.
5v5_Ghostwing·5v5_Blackclaw_Uncaptured는 값 4이며 `unknown`을 유지한다.
값 4 전체를 포괄하는 분류와 값 1/5의 하위 분류는 아직 확정하지 않았다.

공개 가능한 주소·해시·대조 결과는
[증거 JSON](evidence/2026-09-09-entity-kind.json)에 있다. 재현 자료는 비공개
작업 산출물 `work/offline-kind-20260909/descriptor-static/`의
`reproduce_descriptor.py`, `reproduced.json`과 `resources/`의
`resource-mapping-proof.json`이다. 게임 바이너리와 원본 리소스는 포함하지 않는다.

DefinitionManifest의 첫 값은 정의 테이블 relocation 포인터다. 그 오프셋을
개체 설정의 enum처럼 읽으면 오분류한다. 구현은 Actor 타입과 root 범위를 먼저
검사한다. 단일 SYMB, 최대 1024바이트 printable ASCII 이름, 이름 뒤 zero padding만
허용하는 조건은 현재 리더의 지원 범위다. 네이티브는 최대 32개의 별도 SYMB를
읽으며, 위 이름 길이와 padding 제약이 네이티브 규칙이라는 증거는 없다.

CLI·라이브러리 계약은 [리소스 종류 연결](ENTITY_RESOURCE_KIND_2026-09-09.md)에
기록했다. 최소 두 종류의 실제 화면 대조, 소유자·킬 귀속, 정확한 수명 및
종료 집계 검증은 별도로 남는다.
