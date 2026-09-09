# 네이티브 개체 종류 근거와 남은 경계

이름 목록만 읽는 현재 카탈로그의 `kind`는 계속 `unknown`이다.
네이티브 종류 값과 UI 플래그의 연결은 확인했지만, 리소스의 직렬화 필드가
런타임 설정 포인터에 연결되는 과정은 아직 확인되지 않았다.

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

보관된 크리스탈 리소스의 decoded INST 첫 uint32는 2지만 이것만으로 해당
직렬화 필드가 actor 설정이라는 연결을 확정하지 않는다. 생성 경로 `01129ea0`은
`0112c050`으로 이름을 조회한 뒤 간접 registration callback을 호출한다.
`0093fba0`이 종류 플래그를 초기화할 때에는 actor+`0x1c`가 이미 존재한다.
후속 추적에서 callback `00942d90`이 세 번째 인자를 새 actor+`0x1c`에
그대로 저장하는 것을 확인했다. `00954e40`의 `00954f8f` 부근에서 이 callback을
등록하며 타입 descriptor는 `01a7524c`를 통해 `020e9974`를 가리킨다.
실제 등록 key는 descriptor+4다. 이 descriptor는 BSS에 있어 현재 정적 파일에서
값을 확인할 수 없었다. 크리스탈 CFF의 SYMB type-id `2419fb6c`와 이 key의
일치가 남은 검증이다. 일반적인 root 전달·포인터 대입을 확인한 것만으로
해당 리소스가 이 actor 타입에 등록된다고 단정하지 않는다.

DefinitionManifest의 첫 값은 정의 테이블 relocation 포인터다. 그 오프셋을
개체 설정의 enum처럼 읽으면 오분류한다. 후속 구현에는 위 타입 key의 연결 증거와
영웅·구조물·몬스터 자산의 대조, 그리고 실제 화면 검증이 필요하다.
