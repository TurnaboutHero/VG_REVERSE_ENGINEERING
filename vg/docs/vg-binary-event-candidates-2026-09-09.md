# 바이너리 이벤트 후보 전체 목록과 이후 검증

고정 Windows 바이너리에서 열거 가능한 후보를 먼저 모으고, 실제 행동과 필드 의미를 어떻게 검증할지 붙인 목록이다. 클래스 이름 연결과 게임 화면 검증을 같은 단계로 취급하지 않는다.

- 검사 파일 SHA-256: `659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`. VA image base `00400000`.
- 수신 처리기 `004cfec0`의 개별 처리 코드 **123개**: switch 120개와 별도 0000·0006·03e9. raw PE 점프 테이블과 소스 분기 집합이 일치한다.
- 원본 56개 / 7,870 sections / 30,729,156 records에서 관측된 opcode **85개**. 수신·출력·관측을 합친 목록 **161개**.
- 추가로 native 요청 클래스 12개에서 opcode **18개**의 직렬화 경로를 확인했다. 전체 목록은 수신·요청 직렬화·리플레이 관측의 합집합이다.
- `htons` 참조 함수 133개를 전수 조사해 고정 header와 공통 전달 함수 호출이 있는 formatter **111개 코드**를 확인했다. 분류하지 못한 참조 함수 **22개**도 하단/JSON에 보존한다. 포트 변환 등 비이벤트 코드가 섞일 수 있다.
- 현재 수신기에서 개별 처리되지 않는 관측 코드 **12개**, 현재 수신 분기는 있지만 관측되지 않은 코드 **50개**도 모두 남겼다.
- 관련 native vtable **147개**를 별도로 보존했다. 이 중 Nuo::Kindred::Action 클래스는 **106개**이며, 기반 클래스·UI·연출 클래스까지 모두 네트워크 사건이라고 주장하지 않는다.
- 모든 원본 해시는 이전 감사와 일치했고 읽기 전후에도 같았다. 기존 clock 판정 accepted 53 / unsupported 2 / mixed 1을 유지한다. 게임은 실행하지 않았다.

[상세 검증 문서](vg-binary-event-candidates-2026-09-09-details.md) · [전체 CSV](vg-binary-event-candidates-2026-09-09.csv) · [구조화 JSON](vg-binary-event-candidates-2026-09-09.json) · [전체 native 후보 CSV](vg-binary-event-candidates-2026-09-09-native.csv)

## 근거 수준과 범위

`클래스명 연결`은 dispatcher의 직접 또는 한 단계 helper 호출에서 정확한 vtable 상수를 저장하는 경로를 찾았다는 뜻이다. 이름만으로 모든 payload 필드, 원인, 보상 귀속, 화면 시점을 확정하지 않는다. JSON에는 연결 경로·store VA·vtable slots·원본 분기와 모든 관측 길이를 보존했다.

opcode는 BE16이며 전체 65,536값 중 이 처리기가 개별 처리하는 값만 123개다. switch 내부 기본 경로 47개와 하위/상위 범위는 coverage에 남겼다. 기본 경로는 이 처리기에서의 사실이며 전역 미사용·예약·서버 전용이라는 뜻은 아니다. 출력 조사는 이 파일의 `htons` IAT 0120a648을 참조하고 고정 header 및 공통 전달 경로가 확인되는 범위다. 다른 변환 구현·미복구 참조·동적 opcode·서버 전용 코드와 다른 빌드까지 모두 해명했다는 뜻은 아니다.

관측된 12개 수신 기본 경로 코드도 모두 formatter 후보에 존재한다. 그중 8개는 요청 클래스 이름까지 연결되고, 03e8·0458·046d·046e의 행동 의미는 미명명이다. native 출력 경로가 있어도 특정 리플레이 레코드의 실제 송수신 방향과 수락 여부는 별도 검증한다. 미명명 코드를 지우지 않으며, 길이가 둘인 8개 opcode도 동일 layout으로 병합하지 않았다. 분기 복사 크기·formatter payload·관측 VGR payload 길이는 서로 다른 열이다.

## 새 이름 연결이 바꾸는 검증 순서

- `0416` → ActionPlayAbility. 위치형 필드가 있어도 단순 현재 좌표 이벤트로 확정하지 않는다.
- `0439` → ActionBuyItem, `043d` → ActionGrantItem, `044b` → ActionConsumeItem, `044d` → ActionSellItem. 거래 요청/처리·지급·소비·판매를 분리해 검증한다.
- `0434` → ActionLevelUp, `043a` → ActionGrantAbility, `043b` → ActionDowngradeAbility. 레벨과 능력 강화/변경을 분리한다.
- `0431`의 이름은 ActionActorDead지만 기존 apply는 조건부 3→4 전환이다. 사망 순간인 0430이나 최종 데스 수와 합치지 않는다.
- `0452`의 postgame 콜백 뒤 같은 시각의 정상 점수 갱신을 보존한다. 후보 목록은 최종 점수 보정 규칙이 아니다.

## 전체 opcode 목록

길이는 record header와 opcode를 제외한 payload bytes다. 관측 0건도 후보에서 제외하지 않았다. 검증 ID는 아래 계획과 연결되며, 모든 후보의 고유 미확정 사항과 구체 시나리오는 상세 문서/CSV에도 들어 있다.

| Opcode | Native 이름 / 후보 | 근거 | 수신 분기 | 관측 건수 / 기록수 | 길이 B | 검증 |
|---|---|---|---|---:|---|---|
| 0x0000 | float 4바이트 읽기와 FUN_004eaf50 호출 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x0005 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0006 | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x03e8 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 56 / 27 | 70 | V00 |
| 0x03e9 | 미명명 후보 | 처리 분기만 확인 | 있음 | 7,870 / 56 | 101 | V00 |
| 0x03ea | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x03eb | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x03ec | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x03ed | 미명명 후보 | 처리 분기만 확인 | 있음 | 196 / 43 | 78 | V00 |
| 0x03ee | 미명명 후보 | 처리 분기만 확인 | 있음 | 75,807 / 56 | 216/222 | V00 |
| 0x03ef | ActionStartMatch | 클래스명 연결 | 있음 | 51 / 51 | 6 | V08 |
| 0x03f0 | ActionShowMatchPrepSequence | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V08 |
| 0x03f1 | ActionEndMatch | 클래스명 연결 | 있음 | 55 / 55 | 6 | V08 |
| 0x03f2 | ActionEntitySpawn | 클래스명 연결 | 있음 | 926,602 / 56 | 122/126 | V01 |
| 0x03f3 | ActionHeroSpawn | 클래스명 연결 | 있음 | 75,316 / 56 | 746/750 | V01 |
| 0x03f4 | ActionRequestMoveTo_Client | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V02 |
| 0x03f5 | ActionRequestMoveTo_Client | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V02 |
| 0x03f6 | ActionRequestMoveTo_Client | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V02 |
| 0x03f8 | ActionMoveTo | 클래스명 연결 | 있음 | 4,949,279 / 56 | 9/14 | V02 |
| 0x03f9 | ActionMoveToServerAuthoritative | 클래스명 연결 | 있음 | 151,463 / 54 | 14 | V02 |
| 0x03fa | ActionMoveToAndFace | 클래스명 연결 | 있음 | 197,182 / 54 | 22 | V02 |
| 0x03fb | ActionStopActor | 클래스명 연결 | 있음 | 188,017 / 54 | 22 | V02 |
| 0x03fc | ActionResetMovement_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x03fd | ActionMoveToPredictive_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x03fe | ActionMoveToAuthoritative_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x03ff | ActionStopAuthoritative_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x0400 | ActionStopNavigating_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x0401 | ActionFaceDir | 클래스명 연결 | 있음 | 1,667 / 54 | 22 | V02 |
| 0x0402 | ActionAutoActorBounce | 클래스명 연결 | 있음 | 6,884 / 49 | 22 | V02 |
| 0x0403 | ActionAutoMoveTo | 클래스명 연결 | 있음 | 34,973 / 54 | 22 | V02 |
| 0x0404 | ActionAutoMoveToActorResponse | 클래스명 연결 | 있음 | 789 / 14 | 22 | V02 |
| 0x0405 | ActionAutoMoveToLocation_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x0406 | ActionAutoOrbit | 클래스명 연결 | 있음 | 2,084 / 29 | 38 | V02 |
| 0x0407 | ActionCancelAutoOrbit | 클래스명 연결 | 있음 | 548 / 20 | 22 | V02 |
| 0x0408 | ActionAttachToActor_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x0409 | ActionTeleportTo | 클래스명 연결 | 있음 | 5,579 / 55 | 22 | V02 |
| 0x040a | ActionTeleport_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x040b | ActionEntityDestroy | 클래스명 연결 | 있음 | 115,602 / 55 | 6 | V01 |
| 0x040d | ActionFireProjectile | 클래스명 연결 | 있음 | 849,998 / 56 | 22 | V03 |
| 0x040e | ActionFireProjectile | 클래스명 연결 | 있음 | 39,316 / 54 | 30 | V03 |
| 0x040f | ActionFireProjectile | 클래스명 연결 | 있음 | 40,887 / 53 | 46 | V03 |
| 0x0410 | ActionDetonateProjectile | 클래스명 연결 | 있음 | 52,977 / 54 | 22 | V03 |
| 0x0411 | ActionRequestActivateAbility | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V03 |
| 0x0412 | ActionRequestActivateAbility | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V03 |
| 0x0413 | ActionRequestActivateAbility | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V03 |
| 0x0414 | ActionRequestCancelAbility_Client | 요청 직렬화 클래스 연결 | 기본 경로 | 613 / 9 | 6 | V03 |
| 0x0415 | ActionPlayAbility | 클래스명 연결 | 있음 | 1,261,753 / 56 | 14 | V03 |
| 0x0416 | ActionPlayAbility | 클래스명 연결 | 있음 | 79,676 / 54 | 22 | V03 |
| 0x0417 | ActionPlayAbility | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V03 |
| 0x0418 | ActionPlayVoiceOver | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V09 |
| 0x0419 | ActionPlayPfxAtLocation | 클래스명 연결 | 있음 | 5,520 / 54 | 30 | V09 |
| 0x041a | ActionOverrideAbility | 클래스명 연결 | 있음 | 55,144 / 54 | 14 | V03 |
| 0x041b | ActionClearAbilityOverride | 클래스명 연결 | 있음 | 52,309 / 53 | 14 | V03 |
| 0x041c | ActionModifyActorAttribute | 클래스명 연결 | 있음 | 272,490 / 56 | 22 | V05 |
| 0x041d | ActionModifyActorResource | 클래스명 연결 | 있음 | 4,606,221 / 56 | 14 | V05 |
| 0x041e | ActionImpactHealth | 클래스명 연결 | 있음 | 2,146,087 / 56 | 22 | V03 |
| 0x041f | ActionModifyGameModeVar | 클래스명 연결 | 있음 | 336 / 56 | 14 | V08 |
| 0x0420 | ActionCreateZoneOfControl | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V04 |
| 0x0421 | ActionCreateZoneOfControl | 클래스명 연결 | 있음 | 1,123 / 35 | 25/30 | V04 |
| 0x0422 | ActionCreateZoneOfControl | 클래스명 연결 | 있음 | 201 / 3 | 24/30 | V04 |
| 0x0423 | ActionDestroyZoneOfControl | 클래스명 연결 | 있음 | 981 / 36 | 6 | V04 |
| 0x0424 | ActionRequestModifyBasicAttackTarget | 요청 직렬화 클래스 연결 | 기본 경로 | 243,474 / 54 | 6 | V03 |
| 0x0425 | ActionModifyBasicAttackTarget | 클래스명 연결 | 있음 | 4,713 / 54 | 6 | V03 |
| 0x0427 | ActionPauseCooldown | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V03 |
| 0x0428 | ActionModifyCooldown | 클래스명 연결 | 있음 | 135,732 / 54 | 14 | V03 |
| 0x0429 | ActionModifyAbilityCharges | 클래스명 연결 | 있음 | 1,314 / 13 | 14 | V03 |
| 0x042b | ActionModifyVisibility | 클래스명 연결 | 있음 | 4,967,338 / 56 | 14 | V07 |
| 0x042c | ActionModifySpawnCampVisibility_Client | 클래스명 연결 | 있음 | 85,867 / 56 | 6 | V07 |
| 0x042e | ActionMoveToCorrection | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |
| 0x042f | ActionActorUndead | 클래스명 연결 | 있음 | 18 / 2 | 6 | V01 |
| 0x0430 | ActionActorDie | 클래스명 연결 | 있음 | 100,641 / 56 | 14 | V01 |
| 0x0431 | ActionActorDead | 클래스명 연결 | 있음 | 97,794 / 56 | 6 | V01 |
| 0x0432 | ActionActorRespawn | 클래스명 연결 | 있음 | 2,084 / 55 | 22 | V01 |
| 0x0433 | ActionStartRespawnTimer | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V01 |
| 0x0434 | ActionLevelUp | 클래스명 연결 | 있음 | 7,822 / 55 | 14 | V05 |
| 0x0435 | ActionMakeAnnouncement | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V09 |
| 0x0436 | ActionRequestUpgradeAbility_Client | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V03 |
| 0x0437 | ActionQuickBuyItem | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V06 |
| 0x0438 | ActionReorderItem | 요청 직렬화 클래스 연결 | 기본 경로 | 727 / 54 | 6 | V06 |
| 0x0439 | ActionBuyItem | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V06 |
| 0x043a | ActionGrantAbility | 클래스명 연결 | 있음 | 5,840 / 55 | 14 | V03 |
| 0x043b | ActionDowngradeAbility | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V03 |
| 0x043c | ActionCancelAbility | 클래스명 연결 | 있음 | 91,152 / 54 | 14 | V03 |
| 0x043d | ActionGrantItem | 클래스명 연결 | 있음 | 11,663 / 56 | 14 | V06 |
| 0x043e | ActionApplyBuff | 클래스명 연결 | 있음 | 4,320,170 / 56 | 22 | V04 |
| 0x043f | ActionApplyBuff | 클래스명 연결 | 있음 | 3,084,299 / 56 | 34/38 | V04 |
| 0x0440 | ActionShowFlyoutText | 클래스명 연결 | 있음 | 7,554 / 54 | 14 | V09 |
| 0x0441 | ActionModifyBuffDuration | 클래스명 연결 | 있음 | 15,353 / 46 | 14 | V04 |
| 0x0442 | ActionModifyBuffMaxStacks | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V04 |
| 0x0443 | ActionModifyBuffStack | 클래스명 연결 | 있음 | 122,176 / 54 | 14 | V04 |
| 0x0444 | ActionModifyItemStack | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V06 |
| 0x0445 | ActionCancelBuff | 클래스명 연결 | 있음 | 139,309 / 56 | 14 | V04 |
| 0x0446 | ActionTimeoutBuff | 클래스명 연결 | 있음 | 8,094 / 54 | 14 | V04 |
| 0x0447 | ActionDecrementBuffStack | 클래스명 연결 | 있음 | 586 / 6 | 14 | V04 |
| 0x0448 | ActionRequestActivateItem | 요청 직렬화 클래스 연결 | 기본 경로 | 11,711 / 55 | 6 | V06 |
| 0x0449 | ActionRequestActivateItem | 요청 직렬화 클래스 연결 | 기본 경로 | 31 / 14 | 14 | V06 |
| 0x044a | ActionRequestActivateItem | 요청 직렬화 클래스 연결 | 기본 경로 | 6,084 / 54 | 22 | V06 |
| 0x044b | ActionConsumeItem | 클래스명 연결 | 있음 | 7,327 / 55 | 14 | V06 |
| 0x044c | ActionItemActivated | 클래스명 연결 | 있음 | 17,438 / 55 | 22 | V06 |
| 0x044d | ActionSellItem | 클래스명 연결 | 있음 | 326 / 47 | 14 | V06 |
| 0x044e | ActionPing | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V09 |
| 0x044f | ActionHUDQuickMessage | 클래스명 연결 | 있음 | 1,896 / 54 | 22 | V09 |
| 0x0451 | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x0452 | method_onPacket_LevelControllerOnEnterPostGame | 콜백명 연결 | 있음 | 50 / 50 | 6 | V08 |
| 0x0453 | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x0454 | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x0455 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0456 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0458 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 20 / 14 | 6 | V00 |
| 0x0459 | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x045a | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x045b | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x045c | 미명명 후보 | 처리 분기만 확인 | 있음 | 771 / 51 | 102 | V00 |
| 0x045d | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x045e | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x045f | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0461 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0462 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0463 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0464 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0465 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0466 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0467 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0468 | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x046b | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x046c | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x046d | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 387 / 56 | 6 | V00 |
| 0x046e | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 252 / 56 | 6 | V00 |
| 0x046f | 69B 변형의 +64 BE float가 game clock인 경로 확인 | 기존 명명 소비 경로 근거 | 있음 | 7,870 / 56 | 69 | V08 |
| 0x0470 | 미명명 후보 | 처리 분기만 확인 | 있음 | 8,029 / 56 | 1/6 | V00 |
| 0x0471 | 미명명 패킷 후보 | 처리 분기만 확인 | 있음 | 212 / 53 | 6 | V00 |
| 0x0472 | ActionSetSurrenderStateRequest | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V08 |
| 0x0473 | ActionTeamSurrenderStateChanged | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V08 |
| 0x0474 | ActionSpectatorExitMatchRequest | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V08 |
| 0x0475 | ActionPauseTutorial | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V08 |
| 0x0476 | ActionSetSimulationSpeed | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V08 |
| 0x0477 | ActionSetPlayerAsSpectator | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V08 |
| 0x0478 | ActionSetMinimapSpawnPhase_Client | 클래스명 연결 | 있음 | 6,715 / 56 | 14 | V07 |
| 0x0479 | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x047a | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x047b | 미명명 패킷 후보 | 패킷 직렬화 경로 확인 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x047c | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x047d | ActionTutorialStateChangedResponse | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V08 |
| 0x047e | ActionStateChange_Client | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V08 |
| 0x047f | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x0480 | 미명명 후보 | 처리 분기만 확인 | 있음 | 0 / 0 | 미관측 | V00 |
| 0x0481 | ActionEquipTalent | 클래스명 연결 | 있음 | 2 / 2 | 6 | V06 |
| 0x0482 | ActionUnequipTalent | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V06 |
| 0x0483 | ActionInvalidateTalent | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V06 |
| 0x0484 | ActionRequestEquipTalent | 요청 직렬화 클래스 연결 | 기본 경로 | 2 / 2 | 6 | V06 |
| 0x0485 | ActionRequestRecommendedBuildPath | 요청 직렬화 클래스 연결 | 기본 경로 | 465 / 54 | 6 | V06 |
| 0x0486 | ActionRequestLevelLogicEvent_Client | 요청 직렬화 클래스 연결 | 기본 경로 | 0 / 0 | 미관측 | V00 |
| 0x0487 | ActionSetBuildPath | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V06 |
| 0x0488 | ActionSetRecommendedBuildPath | 클래스명 연결 | 있음 | 543 / 56 | 6 | V06 |
| 0x0489 | ActionSyncAbilityBehavior | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V03 |
| 0x048a | ActionSyncCooldown_Client | 클래스명 연결 | 있음 | 971,766 / 56 | 22 | V03 |
| 0x048b | ActionModifyBuffVar | 클래스명 연결 | 있음 | 586 / 3 | 30 | V04 |
| 0x048c | ActionSendAggroState_Client | 클래스명 연결 | 있음 | 27,235 / 56 | 14 | V07 |
| 0x048d | 1612B 누적 통계 구조, 피해·아이템·팀 통계의 명명 소비 경로 | 기존 명명 소비 경로 근거 | 있음 | 55 / 55 | 1614 | V08 |
| 0x048f | ActionRejectBuyItem_Client | 클래스명 연결 | 있음 | 11 / 9 | 6 | V06 |
| 0x0490 | ActionBroadcastSwapTarget | 클래스명 연결 | 있음 | 0 / 0 | 미관측 | V02 |

## 이후 검증 계획

공통 조건: 같은 빌드에서 단일 행동과 대조 조건을 각각 확보하고, 원본 seq·offset·timestamp와 개체/정의 ID를 유지한다. 화면 시간과 기록 시간은 검증된 clock으로 연결한다. 원시 참조와 최종 크레딧·결과 화면은 별도 확인한다.

### V00 — 미분류·기록/빌드 차이

- 미확정: 처리 분기 또는 native 이름만으로 목적·필드·통신 방향·사용 조건을 확정할 수 없음
- 오프라인: 모든 직접 호출과 serializer 역참조, RTTI/apply, 문자열·호출자를 조사한다. 관측 길이별로 비교하고 수신기 기본 경로인 경우 다른 방향/빌드를 먼저 확인한다.
- 실행 실험: 소비 경로로 행동 후보를 좁힌 다음 후보 행동을 하나씩 독립 기록하고 가능하면 실제 송수신 경로와 함께 대조한다.
- 대조 조건: 무행동, 비슷한 다른 행동, 다른 모드/상태/빌드를 대조한다.
- 통과 기준: 특정 행동과 필드 해석을 지지하는 사례와 반증 대조를 함께 확보하기 전에는 unknown을 유지한다. 미관측을 미사용/예약 코드로 단정하지 않는다.

### V01 — 개체 생명주기

- 미확정: 생성·스냅샷 재전송·사망·모델 소멸·부활·ID 재사용을 구별해야 함
- 오프라인: 해당 클래스 생성자→apply의 ID 조회와 상태 전이를 추적하고 이전 spawn 정의·ID 수명·후속 snapshot을 연결한다.
- 실행 실험: 영웅과 미니언 각각 생성→사망→소멸→부활/재생성을 기록하고 부활 시 조작 가능 시점을 별도 표시한다.
- 대조 조건: 살아 있는 효과 개체의 정상 제거와 section 경계 snapshot 재전송을 대조한다.
- 통과 기준: 대상 ID와 실제 생명주기 단계가 일치하며 snapshot 반복을 신규 생성으로, 제거를 처치로 오인하지 않는다.

### V02 — 이동·방향·위치

- 미확정: 현재 위치·목적지·보정 위치·효과 위치, 축·단위·지속시간을 구별해야 함
- 오프라인: 벡터 필드가 위치 setter·경로·보간 중 어디에 들어가는지 추적하고 참조 대상과 좌표 변환을 확인한다.
- 실행 실험: 정지→알려진 두 지점 사이 직선 이동→중지→돌진/순간이동을 각각 단독 수행한다.
- 대조 조건: 제자리 방향 전환, 이동 실패, 위치 고정 스킬을 대조한다.
- 통과 기준: 개체·축·단위가 관측과 일치하고 현재 위치와 목적지가 분리된다. 예측/보정·취소·중지에서도 오탐하지 않는다.

### V03 — 능력·공격·체력·투사체

- 미확정: 요청·시전·적중·효과·취소, 공격자·소유자·대상, 피해와 회복·보호막을 구별해야 함
- 오프라인: 생성자→apply의 참조와 ability/projectile 정의, HP 처리·쿨다운·charge 소비 경로를 추적한다.
- 실행 실험: 기본 공격과 A/B/C를 각각 단독 사용하고 헛발·적중·취소를 분리한다. 체력 관련 후보는 단일 피해·회복·보호막을 따로 비교한다.
- 대조 조건: 무행동, 범위 밖, 쿨다운 중 재입력, 빗나간 투사체를 대조한다.
- 통과 기준: 서로 다른 영웅 2종 이상에서 개체·능력·단계가 일치하고 실패 요청을 성공 시전/적중으로 세지 않는다.

### V04 — 버프·스택·장판

- 미확정: 부여·스택 변경·변수 변경·해제·자연 만료와 장판의 생성/제거를 구별해야 함
- 오프라인: buff/zone 정의 ID와 대상 조회, duration·stack·mask·variable setter 및 종료 경로를 추적한다.
- 실행 실험: 동일 버프를 한 번 부여한 뒤 재부여·중첩·강제 해제·자연 만료를 각각 기록한다. 장판은 진입과 이탈을 분리한다.
- 대조 조건: 대상 밖, 면역 상태, 스택 상한 도달, 같은 효과의 갱신을 대조한다.
- 통과 기준: 버프 ID·대상·스택·남은 시간과 종료 이유가 일치하고 갱신을 신규 효과나 처치로 중복 집계하지 않는다.

### V05 — 능력치·자원·경제·레벨

- 미확정: index/layer/SET/ADD, 현재 값과 누적 값, 경험치·영웅 레벨·강화 포인트·처치 수를 구별해야 함
- 오프라인: index별 setter→getter→명명된 export/UI 소비 경로와 초기 snapshot·reset·clamp를 추적한다. 상관만으로 자원 이름을 정하지 않는다.
- 실행 실험: 대기→구매→판매→단독 막타→근처 공유 처치→정글 처치를 분리한다. 레벨업 후 포인트를 보유했다가 능력 하나만 강화한다.
- 대조 조건: SET 재전송, 무행동 자연 수입, 막타 없는 근접, 거절 구매, 사망 reset을 대조한다.
- 통과 기준: 연산과 snapshot으로 복원한 수치가 각 관측 시점과 일치하고 잔액·총수입·레벨·포인트를 구별한다. 최종 KDA는 결과 화면으로 별도 확인한다.

### V06 — 아이템·인벤토리·재능·빌드

- 미확정: 구매 요청·허용/거절·지급·조합 소비·사용·판매·슬롯 이동·재능 장착의 필드를 구별해야 함
- 오프라인: item/talent/slot/stack/recipe 참조와 생성자→apply, 금액 차감·지급·거절 사유 소비 경로를 추적한다.
- 실행 실험: 부품 구매→조합→판매→소모품 사용→슬롯 이동을 각각 분리한다. 재능과 추천 빌드는 지원 모드에서 장착/해제/변경한다.
- 대조 조건: 돈 부족·슬롯 가득·상점 밖·쿨다운 중 사용·잘못된 재능 모드의 거절을 대조한다.
- 통과 기준: 아이템/슬롯/수량과 실제 인벤토리·금액 변화가 일치하며 요청/지급/소비/거절을 중복 집계하지 않는다.

### V07 — 시야·팀·목표물·어그로

- 미확정: 개체 종류·소유 팀·시야 수신자·원시 source·처치 인정자·보상 수신자는 별개임
- 오프라인: manifest/kind와 팀 조회, visibility bit/mask, 어그로 대상, 소유 변경과 팀 보상 소비 경로를 연결한다.
- 실행 실험: 수풀/시야 경계 진입·이탈과 어그로 변경을 관측한다. 목표물은 터렛·크리스탈·대형 몬스터를 종류별로 하나씩 양 팀 관점에서 비교한다.
- 대조 조건: 피해만 주고 미처치, 다른 팀 처치, 시야 밖, 포획 없는 소멸을 대조한다.
- 통과 기준: 종류·팀·수신 범위와 처치/포획/소유권/재등장이 일치하고 원시 source를 최종 보상 귀속으로 단정하지 않는다.

### V08 — 경기·시계·튜토리얼·통계

- 미확정: 수신·큐 적용·경기 상태·화면 표시·최종 집계 고정은 별개이며 outer timestamp는 UI 시계가 아님
- 오프라인: 상태 getter/setter·queue·reason 분기와 이름이 있는 소비 경로를 추적한다. 같은 시각 후속 연산과 지원되지 않는 시계를 보존한다.
- 실행 실험: 시작·준비·관전자 전환·튜토리얼 상태를 분리하고 정상 비항복 종료와 항복 종료를 각각 기록한다. 종료 직전 전투와 최종 화면도 함께 확보한다.
- 대조 조건: 종료 전 비슷한 시각의 대기, 무시/실패 reason, 지원되지 않는 모드와 시계 정지·재개를 대조한다.
- 통과 기준: 해당 상태와 표시가 일치하고 동시각 후속 점수를 보존한다. 결과 화면으로 최종 수치를 확인하기 전 완료/보정 기준으로 승격하지 않는다.

### V09 — 화면·음향·알림·소셜

- 미확정: 로컬 연출과 서버 사건, 개인/팀/전체 수신 범위, 표시 ID와 전투 영향은 별도임
- 오프라인: localization/audio/pfx/UI 소비 경로와 수신 범위, 참조 ID·위치·지속시간, 로컬 요청 여부를 확인한다.
- 실행 실험: 비공개/연습 환경에서 해당 알림·핑·음성·효과·표시를 하나씩 발생시키고 지원되는 관점별 화면/음향을 비교한다.
- 대조 조건: 로컬 표시/음량 설정 변경, 수신 범위 밖, 유사하지만 다른 알림을 대조한다.
- 통과 기준: ID·대상·범위·표시가 일치하고 로컬 연출을 피해·처치·아이템 획득으로 오인하지 않는다.

## Native 이름 후보 중 현재 opcode 미연결 항목

연결되지 않았다는 것은 사용되지 않는다는 뜻이 아니다. 게임 내부 행동·UI 기반 클래스 등이 섞여 있으므로 슬롯과 xref에서 사용처를 추가 확인한다. 수신·요청 직렬화에 연결한 항목을 포함한 전체 147개 metadata는 JSON과 native CSV에 있다.

| Native 이름 | vtable | 범위 | 검증 |
|---|---|---|---|
| Nuo::Kindred::IGameAction | 01215f08 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V00 |
| Nuo::Platform::PlatformQueryNotifyPlayerAction | 0121838c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V00 |
| Nuo::Kindred::BtN_Action_Tutorial_SetPause | 0121ae1c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V08 |
| Nuo::Kindred::BtN_Action_Tutorial_SetSoftPause | 0121ae58 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V08 |
| Nuo::Kindred::BtN_Action_Tutorial_ShowOnScreenDirections | 0121af0c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V08 |
| Nuo::Kindred::BtN_Action_Tutorial_StartCutscene | 0121af48 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V08 |
| Nuo::Kindred::BtN_Action_Tutorial_StartSidebarConversation | 0121af84 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V08 |
| Nuo::Kindred::BtN_Action_Tutorial_RequestServer | 0121affc | 기타 관련 기반/연출/UI/플랫폼 클래스 | V08 |
| Nuo::Composite::Action_Delay | 0121c240 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_FadeIn | 0121c25c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_FadeOut | 0121c278 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_Show | 0121cd60 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_Hide | 0121cd7c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_CallbackInstant | 0121cfc0 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_Unactive | 0121e6c4 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Kindred::Action_PlaySound | 01228e04 | Nuo::Kindred::Action 클래스 | V09 |
| Nuo::Kindred::Action_MoveToEasing | 01228ff0 | Nuo::Kindred::Action 클래스 | V02 |
| Nuo::Kindred::Action_PlayAnimation | 0122e338 | Nuo::Kindred::Action 클래스 | V09 |
| Nuo::Kindred::Action_PlayPfx | 0122e354 | Nuo::Kindred::Action 클래스 | V09 |
| Nuo::Composite::Action_Destroy | 01254930 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Kindred::RecentFriendActionWidget | 01255524 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Kindred::FriendRequestActionWidget | 012555c0 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Kindred::KindredPacketRecorder | 0127ccec | 기타 관련 기반/연출/UI/플랫폼 클래스 | V00 |
| Nuo::Kindred::BtN_Action_DeclareVariable | 0128828c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V00 |
| Nuo::Kindred::BtN_Action_ModifyFlag | 012882c8 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V00 |
| Nuo::Composite::Action_SetVisible | 0129a420 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_SetHittable | 0129a43c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_Interval | 0129a458 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_Spawn | 0129a474 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_Sequence | 0129a490 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_MoveBy | 0129a4ac | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_MoveByTrajectory | 0129a4c8 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_MoveTo | 0129a4e4 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_AlphaTo | 0129a500 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_TintTo | 0129a51c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_TextColorTo | 0129a538 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_ScaleBy | 0129a554 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_RotateTo | 0129a570 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_SizeTo | 0129a58c | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_TextureSizeTo | 0129a5a8 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_AnimAttr1f | 0129a5c4 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_CallbackContinuous | 0129a5e0 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action_DispatchEvent | 0129a5fc | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::Action | 0129b034 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |
| Nuo::Composite::ActionManager | 0129b7e4 | 기타 관련 기반/연출/UI/플랫폼 클래스 | V09 |

## Opcode를 부여하지 않은 변환 참조 함수

고정 길이/opcode/payload header와 공통 전달 함수 호출 조건을 만족하지 않은 htons 참조다. 다음 표 전체를 미해결 자료로 유지한다. 모든 항목에 대해 입력 값의 호출자/데이터 흐름과 포트·주소·가변 패킷 처리를 먼저 구별한다. 게임 행동 실험은 사건 후보가 좁혀진 뒤 수행하며, 현재는 이벤트라고 단정하지 않는다.

| 함수 VA | 이름 | 이번 분류 결과 | 이후 검증 |
|---|---|---|---|
| 0049e520 | gloox::DNS::connect | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 004cb030 | FUN_004cb030 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 004caa20 | FUN_004caa20 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 004cd440 | FUN_004cd440 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 004ca310 | FUN_004ca310 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 004cb6a0 | FUN_004cb6a0 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 004cbc90 | FUN_004cbc90 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 00949b60 | FUN_00949b60 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 0094a400 | FUN_0094a400 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 0094ab80 | FUN_0094ab80 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 0095bf20 | FUN_0095bf20 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 0094af20 | FUN_0094af20 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 0094c450 | FUN_0094c450 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 011603c0 | FUN_011603c0 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 01161850 | FUN_01161850 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 011897e0 | FUN_011897e0 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 0117e140 | FUN_0117e140 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 0119a690 | FUN_0119a690 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 011aa820 | FUN_011aa820 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 011a6500 | FUN_011a6500 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 01190ae0 | FUN_01190ae0 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |
| 0119e990 | FUN_0119e990 | 고정 packet header + 공통 전달 경로 미확인 | V00: 호출자→변환 입력→출력 버퍼/포트 사용처 확인 |

## 저장소에 포함한 근거

[근거·재현 범위](evidence/2026-09-09-binary-events/README.md) · [파일 해시](evidence/2026-09-09-binary-events/manifest.json) · [0452 후속 분석](POSTGAME_OFFLINE_2026-09-09.md)

이 공개본은 원본 리플레이·실행 파일·전체 디컴파일을 포함하지 않는다. 후보 161개, native metadata 147개, 미분류 참조 22개와 검증 조건은 유지하며 파일 경로만 이 저장소 기준으로 옮겼다.
