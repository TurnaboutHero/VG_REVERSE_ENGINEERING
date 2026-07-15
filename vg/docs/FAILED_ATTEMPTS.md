# VGR Reverse Engineering - Failed Attempts Record

**Purpose:** 이전에 시도해서 실패한 접근법을 기록하여, 같은 실수를 반복하지 않기 위한 문서.

---

## 1. KDA (Kill/Death/Assist) Detection - Kill/Death 해결, Assist 부분 해결

### 1.1 Action Code 0x29 = Kill Signature (실패)

**가설:** 플레이어 Entity의 0x29 action code가 Kill 이벤트를 나타낸다.

**시도:**
- `vg/analysis/player_kill_detector.py` - 0x29 이벤트를 kill로 해석
- `vg/analysis/baron_anomaly_investigation.py` - Baron의 0x29 이상치 조사
- `vg/analysis/baron_0x29_deep_analysis.py` - 다중 리플레이 검증

**결과:** 17.1% 정확도 (6/35 kills, Baron만 일치)

**실패 원인:**
- 0x29는 **영웅별 고유 능력 코드**이지, kill 이벤트가 아님
- Baron은 0x29 이벤트가 1,087개 (6개가 아님!)
- "6 kills = 6개 0x29 이벤트"는 **우연의 일치**였음
- 21.12.06 리플레이에서는 모든 플레이어의 0x29가 0개
- 히어로마다 0x29 빈도가 완전히 다름 (Baron 1087, Caine 37, 일부 0)

**교훈:** 단일 리플레이에서 수치가 일치한다고 해서 인과관계가 아님. 반드시 **다중 리플레이 교차 검증** 필수.

---

### 1.2 Action Code 0x18 = Death Marker (실패)

**가설:** 0x18 action code가 영웅 사망을 나타낸다.

**시도:**
- `vg/analysis/validate_death_code.py` - 0x18 검증
- `vg/analysis/death_kill_validation.py` - 4개 리플레이 교차 검증
- `vg/analysis/verify_0x10_death_marker.py` - 0x10 변형도 시도

**결과:** 91배 과다 감지 (truth 28 deaths vs 감지 2,567개)

**실패 원인:**
- 0x18은 **전투 상태 브로드캐스트** (Combat state broadcast)
- 사망과 무관하게 전투 중 지속적으로 발생
- 빈도가 너무 높아 death 이벤트가 될 수 없음

**교훈:** 빈도가 truth와 크게 차이나는 이벤트는 즉시 폐기. 과다 감지(10배 이상)는 완전히 다른 의미의 이벤트.

---

### 1.3 Action Code 0x13 = Death Marker (실패)

**가설:** 0x13이 사망 이벤트일 수 있다.

**시도:** `vg/analysis/verify_0x13_death.py`

**결과:** 일치하지 않음

**실패 원인:** 0x13도 일반적인 게임플레이 이벤트로, death와 무관

---

### 1.4 Entity Disappearance = Death (실패)

**가설:** 플레이어가 사망하면 해당 프레임에서 이벤트가 사라진다.

**시도:**
- `vg/analysis/entity_lifecycle_tracker.py` - Entity 생명주기 추적
- `vg/analysis/death_frame_forensics.py` - 프레임별 사망 포렌식
- `vg/analysis/kda_lifecycle_detector.py` - 생명주기 기반 KDA

**결과:** 0/15 deaths 감지

**실패 원인:**
- **플레이어는 사망해도 이벤트에서 사라지지 않음!**
- 모든 플레이어가 거의 모든 프레임에 존재
- VGR 리플레이는 "입력" 기록이지 "상태" 기록이 아닐 수 있음

**교훈:** 사망 = 엔티티 부재라는 가정 자체가 틀림. VGR은 서버의 이벤트 로그로, 사망 상태와 무관하게 엔티티 이벤트가 계속 기록됨.

---

### 1.5 Respawn Timer Pattern (실패)

**가설:** 사망 후 부활까지 이벤트 빈도가 급감하므로 타이밍으로 감지 가능.

**시도:** `vg/analysis/respawn_timer_analyzer.py` - 3가지 전략 (Progressive timer, Fixed window, Clustering)

**결과:** Clustering MAE=1.5, 6명 중 1명만 정확

**실패 원인:**
- 영웅별 이벤트 빈도가 크게 다름 (Phinn: 0 deaths인데 18/103 프레임에만 존재)
- 자연적 이벤트 갭과 사망 갭을 구분할 수 없음
- 영웅 이벤트 빈도 의존도가 너무 높음

**교훈:** 이벤트 빈도 기반 접근은 영웅마다 기본 패턴이 다르므로 신뢰 불가.

---

### 1.6 0x00/0x05 Event Count Correlation (실패)

**가설:** 0x00 또는 0x05 action code의 빈도가 K/D/A와 상관관계가 있다.

**시도:** `vg/analysis/universal_kda_decoder.py`

**결과:** 0% 일치

**실패 원인:**
- 0x00 payload에 15,973개의 플레이어 참조 (K+D+A 합계보다 수백 배 많음)
- 0x05도 마찬가지로 범용 이벤트
- 고빈도 이벤트는 특정 게임 이벤트(kill/death)와 매핑 불가

**교훈:** 모든 플레이어에게 공통적으로 높은 빈도를 보이는 이벤트는 K/D/A 후보가 아님.

---

### 1.7 0x80 Payload Deep Analysis (실패)

**가설:** 0x80 action code의 payload 내에 kill/death 정보가 인코딩되어 있다.

**시도:** `vg/analysis/kda_payload_analyzer.py`

**결과:** 상관관계 없음

**실패 원인:** 0x80(=Entity 128)은 시스템 엔티티로, 대량의 브로드캐스트 이벤트 생성

---

### 1.8 Per-Player Payload Kill/Victim Decode (실패)

**가설:** 각 플레이어의 이벤트 payload에 다른 플레이어의 Entity ID가 포함되면 kill/death 관계.

**시도:** `vg/analysis/kda_per_player_decoder.py`

**결과:** 상관관계 미발견

**실패 원인:** Payload 내 Entity ID 참조는 전투, 스킬 타겟팅 등 다양한 이유로 발생

---

### 1.9 Frame Anomaly Detection (부분 실패)

**가설:** 프레임 수준의 이벤트 급증/급감이 팀파이트/다중 킬과 연관.

**시도:** `vg/analysis/frame_anomaly_detector.py`

**결과:** Frame 85 (z=9.22)가 최고 anomaly score이나, 개별 kill/death 매핑 불가

**실패 원인:**
- 전체 프레임 수준 anomaly는 팀파이트 감지에는 유용하나 개별 KDA 추출 불가
- Expected deaths = 0으로 truth data 미매핑 (해당 리플레이에 truth 없음)

**교훈:** 프레임 anomaly는 "무언가 큰 일이 발생"한 시점을 찾는 데 유용하지만, KDA의 직접 증거는 아님.

---

### 1.10 Position Vector Search (부분 성공 - KDA와는 무관)

**가설:** IEEE 754 float32 좌표 벡터 [x, z, y]가 리플레이 바이너리에 있다.

**시도:** `vg/analysis/position_vector_finder.py`

**1차 결과:** 대부분 (0.0, 0.0, 0.0) - Player block 내 null padding에서 false positive

**2차 결과 (확장 분석):** 625개의 non-zero 위치 벡터 발견!
- **Payload offset +8**: 주요 위치 필드 (119회 출현)
- **Action code 0x05**: 이동/위치 업데이트 (667개 이벤트 중 314개에 위치 포함)
- **좌표 범위**: X [-12.06, 32.00], Y [-1.39, 32.00] → VG 맵 경계 일치
- 프레임 10→90으로 갈수록 위치 이벤트 감소 (413→43) → MOBA 게임 패턴과 일치

**KDA 관련성:** 위치 데이터 자체는 유용하나, KDA 감지와는 직접 관련 없음.
향후 kill 위치 매핑이나 death 위치 추적에 활용 가능.

**교훈:** Null padding 제거 후 유의미한 float32 좌표가 존재함. 0x05가 주요 위치 이벤트.

---

### 1.11 Player Payload Gold Amount Search (실패)

**가설:** 플레이어 이벤트의 32바이트 payload에 킬 골드(150-500 범위 uint16)가 인코딩되어 있다.

**시도:** `vg/analysis/gold_kill_correlator.py`, `gold_kill_correlator_v2.py`

**결과:** 모든 플레이어에서 gold_range_events = 0

**실패 원인:**
- 플레이어 Entity의 이벤트 payload에는 골드 값이 직접 포함되지 않음
- 골드 관련 정보는 Entity 0 (시스템 브로드캐스트)에 있을 가능성 있음
- 또는 골드 값이 다른 인코딩 방식 사용 (float, scaled int 등)

**교훈:** 플레이어 이벤트와 시스템 이벤트(Entity 0)의 역할 분리. 경제 이벤트는 시스템 엔티티가 브로드캐스트할 가능성 높음.

---

### 1.12 Entity 0 Action Code 0x28 = Death (실패 - 우연의 일치)

**가설:** Entity 0의 action code 0x28이 death 브로드캐스트.

**시도:** `vg/analysis/entity0_death_search.py` + 다중 리플레이 교차 검증

**21.11.04 결과:** 총 15개 이벤트 = Truth 15 deaths와 총합 일치 (4/6 플레이어 정확)

**다중 리플레이 교차 검증 결과 (결정적 반증):**
| Replay | Frames | 0x28 Count | 가능한 deaths? |
|--------|--------|-----------|---------------|
| 21.11.04 | 103 | 15 | ← 우연히 일치 |
| 21.11.17 | 115 | **275** | ❌ 불가능 |
| 21.11.22 | 193 | **132** | ❌ 불가능 |
| 21.12.07 | 182 | **391** | ❌ 불가능 |
| 22.06.01 | 186 | **298** | ❌ 불가능 |

3v3 게임에서 275~391번의 death는 물리적으로 불가능 (일반적으로 10~30 kills).

**추가 문제:**
- Caine(entity 56837)이 Entity 0 0x28 payload에 단 한 번도 나타나지 않음
- `00 00 00 00` 패턴이 null padding과 충돌하여 대량의 false positive 발생
- 0x24도 7~373까지 변동 - 역시 death 아님

**실패 원인:** Entity 0 패턴 `00 00 00 00 [action]`이 너무 일반적이어서 false positive 대량 발생. 21.11.04에서 15개 일치는 **우연의 일치**.

**교훈:** 단일 리플레이에서 숫자가 일치한다고 해서 인과관계가 아님. 반드시 다중 리플레이 교차 검증 필수.

**상태:** ❌ 완전 실패 - 절대 다시 시도하지 말 것

---

### 1.13 Death-Exclusive Action Codes: 0x61, 0x81, 0x82, 0x85 (실패)

**가설:** 특정 action codes가 death 프레임에서만 나타나고 일반 프레임에서는 절대 나타나지 않는다.

**시도:**
- `vg/analysis/death_frame_action_distribution.py` (21.11.04 단일 리플레이)
- `vg/analysis/cross_validate_death_codes.py` (9개 리플레이 교차 검증)

**21.11.04 결과 (단일 리플레이):** 100% precision, 60% recall - 유망해 보였음

**다중 리플레이 교차 검증 결과 (결정적 반증):**
- **Overall precision: 1.00%** (100개 death code 프레임 중 1개만 실제 death)
- **Overall recall: 8.33%** (12개 death candidate 중 1개만 감지)
- **2,249건의 death code가 NON-death 프레임에서 발견!**
- Tournament 리플레이에서 0x82가 한 매치에서 547건 등장 (대부분 non-death)

**실패 원인:**
- 21.11.04에서의 "death-exclusive" 패턴은 해당 리플레이에만 해당하는 우연
- 0x61/0x81/0x82/0x85는 일반적인 게임플레이 이벤트 코드
- 3v3와 5v5의 이벤트 패턴 차이도 있을 수 있으나 근본적으로 death 전용 아님

**교훈:** 단일 리플레이에서 "코드 존재/부재" 패턴도 다중 리플레이에서 반드시 검증해야 함.

**상태:** ❌ 완전 실패 - 절대 다시 시도하지 말 것

### 1.14 Variable Payload Size Discovery (참고 사항)

**발견:** 이벤트 payload 크기가 고정 37바이트가 아니라 action code별 가변.

| Payload 크기 | 코드 수 | 대표 코드 |
|-------------|---------|----------|
| 11B | 2 | 0x43, 0x44 |
| 19B | 109 | 대부분의 코드 (82.6%) |
| 27B | 10 | 0x4D, 0x5E, 0x62 등 |
| 39B | 1 | 0x05 (이동 이벤트) |
| 51-221B | 10 | 0x81(147B), 0x01/0x03(221B) |

**영향:** 기존 모든 분석이 37B 고정 가정 → 이벤트 경계 misalign → false positive 대량 발생.
순차 파싱 시도했으나 `00 00` separator가 프레임 전체에 일관되지 않아 부분적으로만 성공.

**상태:** 📋 참고 사항 - 향후 파싱 개선 시 활용

---

## 2. Hero Detection - 이전 실패 (최종 해결됨)

### 2.1 Event Pattern Matching (실패 → 포기)

**가설:** 각 영웅은 고유한 action code 빈도 패턴을 가진다.

**시도:**
- `vg/analysis/validate_event_pattern_detection.py`
- `vg/analysis/validate_event_pattern_loocv.py`
- `vg/analysis/validate_signature_loocv.py`
- `vg/core/event_pattern_detector.py`
- `vg/core/signature_detector.py`

**결과:** 0% 정확도

**실패 원인:**
- 게임 상황에 따라 이벤트 패턴이 크게 변함
- 같은 영웅이라도 경기마다 다른 action code 분포
- Machine learning 접근도 실패 (특징이 불안정)

**최종 해결:** Player block 내 **+0xA9 offset의 uint16 LE hero ID** 발견으로 100% 해결

**교훈:** 통계적/ML 접근보다 **구조적 바이너리 분석**이 정답. 이벤트 패턴은 영웅보다 게임 상황에 더 의존.

---

## 3. Entity Parsing Bugs

### 3.1 Entity 0 Parsing 누락 (수정됨)

**문제:** Entity 0의 이벤트가 0개로 파싱됨

**원인:** Entity 0 바이트는 `00 00 00 00 [ActionCode]` — Entity ID `00 00`과 `00 00` 마커가 동일하여 표준 파서가 건너뜀

**실제:** Entity 0 = 2,889 이벤트, Entity 128 = 10,511 이벤트

**수정:** `vg/analysis/system_entity_analyzer.py`에서 특수 패턴 매칭으로 파싱

**교훈:** 바이너리 파서에서 특수값(0, 128 등)은 항상 edge case 테스트 필요.

---

### 3.2 Entity ID 범위 혼동

**문제:** Entity ID 범위별 역할이 명확하지 않았음

**정리:**
- Entity 0: 시스템 브로드캐스트 (2,889 이벤트/리플레이)
- Entity 1-10: 저수준 인프라 (Entity 1 = 83,268 이벤트!)
- Entity 128: 시스템 엔티티 (10,511 이벤트)
- 1000-20000: 터렛/구조물
- 20000-50000: 미니언/정글몹
- 50000-60000: 플레이어

---

## 4. Item Detection - 이전 실패 (부분 해결됨)

### 4.1 단순 Action Code 매칭 (부분 성공)

**시도:** 0xBC action code = item purchase

**결과:** 일부 아이템만 매칭, 모든 아이템 감지 불가

**해결:** `vg/analysis/item_extractor.py` - 4가지 패턴 전략 (FF/05/00 마커 + direct 2-byte LE) 통합

---

## 5. KDA 연구 - Kill/Death 해결! (2026-02-16)

### 5.1 성공한 접근: Brute-force Frequency Matching + Structural Validation

**핵심 발견:** 특정 action code가 아닌, **프로토콜 레벨의 구조화된 레코드**가 kill/death를 나타냄.

**발견 방법:**
1. **Brute-force frequency matching**: 가능한 모든 (pattern, offset, endianness) 조합에서 per-player 카운트가 truth와 일치하는 것을 탐색
2. Death: 19,306개 조합 중 **정확히 1개** 일치 → `[08 04 31]`
3. Kill: offset 1-30, 2/3/4-byte 패턴으로 확장 탐색 → `[00 29 00]` at BE offset 23 → 구조 분석으로 `[18 04 1C]` 발견

**Kill 레코드:** `[18 04 1C] [00 00] [killer_eid BE] [FF FF FF FF] [3F 80 00 00] [29 00]`
- Timestamp: f32 BE at 7 bytes before header
- Kill-death dt ≈ 1.8s consistently

**Death 레코드:** `[08 04 31] [00 00] [victim_eid BE] [00 00] [timestamp f32 BE] [00 00 00]`

**Credit 레코드:** `[10 04 1D] [00 00] [eid BE] [value f32 BE]`
- Kill header 뒤에 위치: killer(1.0), assister(gold), assister(1.0), assister(0.5)
- Assist gold: 10-250, Kill gold: 100-800+ (프레임 다른 위치)

**크로스 검증 (10개 완전 리플레이, 94명 플레이어):**
- Kill: **97.9%** (92/94) - raw, 필터 없음
- Death: **95.7%** (90/94) - ts <= duration + 10s 필터
- Combined: **96.8%** (182/188)

**Post-game ceremony filter:**
- 크리스탈 파괴 후 세레모니 중 킬/데스는 통계에 미반영
- Death timestamp > game_duration + 10s 필터로 해결 (8/10 오버카운트 제거)

**모듈:** `vg/core/kda_detector.py` (KDADetector 클래스)

### 5.2 미해결: Assist Detection

- Hero kill assist는 credit record `[10 04 1D]`에서 추출 가능
- 하지만 truth assist에는 **objective assist** (터렛, 크라켄 파괴 참여) 포함
- 일부 플레이어의 truth_A > 가능한 hero_kill_assists → 정확 매칭 불가
- 향후: objective kill 이벤트 패턴 탐색 필요

### 5.3 교훈

- **Brute-force frequency matching을 항상 먼저 시도할 것** - 가설 기반보다 데이터 기반이 효과적
- 프로토콜 레코드는 player event와 다른 구조 (3-byte header `[XX 04 YY]`)
- Entity ID는 프로토콜에서 Big Endian, player block에서 Little Endian
- Dedup 불필요 - 동일 이벤트가 여러 프레임에 중복되지 않음

### 1.15 Player Block Byte Diff (실패)

**가설:** 플레이어 블록(DA 03 EE) 내에 KDA 카운터가 프레임마다 업데이트된다.

**시도:** `vg/analysis/player_block_kda_diff.py` - Frame 0 vs Frame 102 전체 블록 비교

**결과:** 6명 모든 플레이어의 블록이 **4바이트만 변경** (+0xDB~+0xDE: 44 7F 01 29)되었으며, 이 값은 6명 전원 동일. KDA와 무관한 타임스탬프/게임상태 필드.

**교훈:** 플레이어 블록은 정적 메타데이터(영웅, 팀, 엔티티 ID)만 저장. 동적 통계는 없음.

---

### 1.16 직접 바이너리 KDA/Gold 값 검색 (결정적 실패)

**가설:** KDA나 골드 값이 VGR 프레임 바이너리 어딘가에 저장되어 있다.

**시도:**
- `vg/analysis/stat_block_extractor.py` - Karas KDA offset 주변 구조 분석
- `last_frame_forensics.py` - 마지막 프레임 전체 포렌식
- 전체 바이너리 검색 스크립트 (이 세션에서 실행)

**검색 범위:**
- 인코딩: uint8, uint16 LE/BE, uint32 LE/BE, float32 LE/BE
- 패턴: 연속, stride 1-4, 모든 순열, 인터리브
- 프레임: 0, 20, 50, 80, 100, 102 (전체 타임라인)
- 리플레이: 21.11.04 + 토너먼트 리플레이 15개

**결과:**
- Baron KDA [6,2,6]: 전체 87K 파일에서 **0건** (uint8 연속)
- 6명 골드 값 (5779~10393): **모든 인코딩에서 0건**
- 토너먼트 리플레이 IcyBang 골드=12900: **0건**
- KDA 시퀀스 (6명 Kills/Deaths/Assists): **모든 stride에서 0건**
- Karas KDA at 0x15490: 프레임 4부터 이미 존재 → 프로토콜 상수 (false positive)

**결론:** ❌ **VGR 파일에 KDA/골드 통계가 저장되지 않음**
- VGR은 raw game events(입력/상태 브로드캐스트)만 기록
- 누적 통계(KDA, 골드, 레벨)는 서버가 계산하여 텔레메트리 API로 별도 전달
- E.V.I.L. 엔진의 server-authoritative 설계: 클라이언트 리플레이에는 통계 미포함

**상태:** ❌ 완전 실패 - VGR 포맷의 근본적 한계. 직접 바이너리 검색은 다시 시도하지 말 것.

---

### 1.17 Roster Data Region KDA Search (v2k-v2s, 결정적 실패)

**가설:** 마지막 프레임의 "roster data region" (Player EID 목록 뒤 데이터 영역)에 KDA/골드/CS 등 게임 종료 통계가 저장되어 있다.

**시도:**
- `vg/analysis/event_parsing_v2k.py` - EID 컨텍스트 스캔 (타입마커 카운트, 고정오프셋 값)
- `vg/analysis/event_parsing_v2l.py` - v2k Phase 4 false positive 반증
- `vg/analysis/event_parsing_v2m.py` - Raw hex dump → roster block 발견 (Cluster 3 at 0x014E61)
- `vg/analysis/event_parsing_v2n.py` - Roster 구조 확인 + 토너먼트 검증
- `vg/analysis/event_parsing_v2o.py` - Data bytes = STATIC (not KDA), float arrays 분석
- `vg/analysis/event_parsing_v2p.py` - 64-byte block 구조 파싱, uint32/uint16 해석
- `vg/analysis/event_parsing_v2q.py` - 전체 프레임 모든 인코딩 exhaustive KDA 검색
- `vg/analysis/event_parsing_v2r.py` - 토너먼트 10개 매치 roster 추출, 대안 인코딩 검색
- `vg/analysis/event_parsing_v2s.py` - 3v3 vs 5v5 레이아웃 비교, 최종 결론

**Roster Data Region 구조 (발견):**
```
[EID1_BE 00 00][EID2_BE 00 00]...[EIDn_BE]
[FF padding (24-40 bytes)]
[Team bytes: 1=left, 2=right per player]  ← 100% 정확!
[FF padding (6-10 bytes)]
[Data bytes (N bytes): STATIC per slot, NOT KDA]
[Zero padding to 0x10 alignment]
[Float32 array 0 (N*4 bytes): damage stats ~1000-40000 range]
[Zero padding]
[Float32 array 1-5: various per-player stats]
[Sparse uint32 values: small integers 1-48, unknown meaning]
[uint16 values at +0x1D0: NOT gold (r=-0.133)]
[Player levels? at +0x220: values 3-10]
[Float32 array at +0x270: values 5-35, unknown]
[Item inventories: uint16 IDs with 0xFFFF=empty, 10 slots/player]
```

**Exhaustive KDA 검색 결과 (v2q Phase 7):**
- 전체 87,613바이트 마지막 프레임 완전 탐색
- 인코딩: uint8, uint16 (BE/LE), uint32 (BE/LE) → **모두 0건**
- 6/6 exact match: 0건
- 5/6 near match (uint8, max<30): 0건

**대안 인코딩 검색 결과 (v2r Phase 4-5):**
- Strided uint8 (stride 2-64): **0건**
- Strided uint16 BE (stride 4-64): **0건**
- Interleaved [k,d,a,k,d,a,...]: **0건**
- Interleaved with padding: **0건**
- K/D/A separate strided arrays: **0건**
- Nibble packed (K<<4|D, D<<4|K, K<<4|A): **0건**
- Combined K*100+D*10+A as uint16: **0건**
- [k,d,a] triplet near player blocks (+-512 bytes): **0건**

**토너먼트 교차 검증 (v2r Phase 2):**
- 10/11 매치에서 roster 발견 (EID base = 1500, 항상 동일)
- Team bytes: 모든 매치에서 정확
- Float arrays: 5v5에서 일부 매치 alignment 문제 (garbage values)
- byte@0x220: KDA와 상관계수 r~0 (n=99 players)
- uint16@1D0: Gold과 r=-0.133 (무상관)
- floats@270: 모든 stat과 r<0.2 (무상관)

**결론:** ❌ **Roster data region에 KDA 통계는 없음**
- Data bytes = STATIC per match slot (영웅/팀 무관)
- Float arrays = damage/healing 관련 추정 (gold/CS/KDA 아님)
- 대안 인코딩 포함 모든 방식에서 완전 탈락
- 3v3와 5v5에서 block layout이 다름 (64-byte vs variable)

**상태:** ❌ 완전 실패 - roster data region에서 KDA 검색 절대 재시도 금지

---

### 1.18 Boundary Event File-Order Disambiguation (기각)

**가설:** 크리스탈 파괴 시각과 타임스탬프가 동률/근접해 시간 필터로 구분 불가능한 킬 이벤트는, 바이트 스트림 내 물리적 위치(frame_idx, file_offset)가 크리스탈 사망 레코드보다 앞/뒤인지로 스코어보드 반영 여부를 구분할 수 있다.

**시도:** `vg/analysis/boundary_event_file_order.py` — 11개 truth 매치 전수 프로브. 크리스탈 사망 레코드(eid 2000-2005)의 물리적 위치를 직접 스캔하고, `KillEvent.frame_idx`/`file_offset`을 크리스탈 레코드 위치와 비교해 `after_crystal` 플래그 산출. 결과: `vg/output/boundary_file_order_report.json`.

**결과:** 기각 (반례 2건 확정 + 부가적 FP 크리스탈 문제)

- **M5 (예상대로 확정):** 크리스탈 레코드 유효(ts=1142.89, duration=1142와 일치, FP 아님). 유일한 경계 킬 = 2600_IcyBang(baseline_kda 기준 초과 킬, detected=1/truth=0) ts=1147.6, `after_crystal=true`. 가설과 일치.
- **M8 반례 (결정적):** 크리스탈 레코드 유효(ts=1346.28, duration=1346과 일치, FP 아님). `2400_IcyBang` ts=1346.68(크리스탈 0.4초 후) 킬이 `after_crystal=true`이나, `baseline_kda_20260716.txt`의 "Kill Mismatches - Complete (2)" 목록에 M8은 없음 → 이 킬은 **truth에 정확히 반영된 정상 킬**. 즉 정답 킬이 크리스탈 레코드보다 물리적으로 뒤에 위치하는 반례.
- **M10 반례:** 크리스탈 레코드 유효(ts=1312.09, duration=1312와 일치, FP 아님). `3004_BearFang` ts=1313.52(크리스탈 1.43초 후) 킬 = `after_crystal=true`이나 동일하게 M10도 Kill Mismatches 목록에 없음 → 정상 킬이 크리스탈 뒤에 위치.
- **M4 부가 문제 (FP 크리스탈):** 스캔된 크리스탈 후보(ts=1091.72)가 디코더 자체 로직(`crystal_ts < duration_est - 30`)에 의해 FP(터렛)로 판정되어 duration=1157로 폴백됨. 이 FP 레코드를 기준으로 삼으면 이후 6개의 정상 킬(2999_IcyBang 등; M4도 Kill Mismatches 목록에 없음)이 모두 `after_crystal=true`로 오분류됨.
- **M6 (원 대상, 판정 불가):** 스캔된 유일한 크리스탈 후보(ts=1221.31)도 동일 로직상 FP로 판정됨(duration=1486으로 폴백; 실제 게임 종료보다 265초 이른 시점). 즉 M6 파일에는 진짜 크리스탈 파괴 레코드가 물리적으로 존재하지 않음(테일 데이터 유실 — 기존 메모리 노트 "M6: replay ends 64.8s before game end"와 일치). 이 FP 레코드를 기준으로 하면 이후 12개 킬(대상 스퓨리어스 킬 2600_staplers 포함, 나머지 11개는 정상 킬로 추정)이 모두 `after_crystal=true`로 뒤섞여 구분 불가.

**실패 원인:**
- 크리스탈 사망 레코드(eid 2000-2005)는 실제 크리스탈이 아니라 터렛일 수 있는 기존에 알려진 FP 클래스. 이 스크립트는 `match.crystal_death_ts`가 FP인지 검증 없이 그대로 기준점으로 사용 — FP 크리스탈 매치(M4, M6)에서는 위치 비교 자체가 무효.
- 크리스탈 레코드가 유효한 매치(M8, M10)에서도, 크리스탈 파괴 직후(0.4~1.4초) 발생한 마지막 교전의 정상 킬이 물리적으로 크리스탈 레코드보다 뒤에 기록됨. 바이트 스트림 위치는 이벤트 발생 순서(시간)의 대리 지표일 뿐, "포스트게임 세레모니 여부"라는 별도의 독립적 신호가 아님.

**교훈:** 물리적 파일 위치는 타임스탬프와 사실상 단조 관계이므로(순차 기록), "크리스탈보다 물리적으로 뒤"는 "크리스탈보다 시간상 나중"과 거의 동치임 — 시간 필터가 못 잡는 case를 구분해 줄 새로운 신호가 아니다. 크리스탈과 거의 동시(1.4초 이내)에 벌어진 정당한 막판 킬도 위치상 크리스탈 뒤에 온다. 크리스탈 레코드 자체가 터렛 오탐일 수 있는 매치(전체 중 다수)에서는 이 방법이 원천적으로 적용 불가.

**상태:** ❌ 기각 - Task 4(파일 순서 기반 필터 규칙) 보류. 반례: M8 `2400_IcyBang`, M10 `3004_BearFang`.

**Task 5 변형 (미니언 킬 0x0E, 기각):** 동일 가설을 `[10 04 1D]` + action=0x0E 미니언 라스트히트 레코드에 적용. `boundary_event_file_order.py`를 확장해 전체 프레임에서 유효 플레이어 0x0E 레코드를 `KDADetector._scan_minion_kills`와 동일한 검증 로직(헤더/제로필드/eid/value≈1.0/action byte, 동일한 pos 증가 방식)으로 스캔하고 크리스탈 레코드와 위치 비교. 결과: `vg/output/boundary_file_order_report.json`.

검증된(터렛 FP 아닌) 크리스탈 앵커를 가진 7개 매치(M1, M2, M3, M5, M8, M10, M11) 중 M5는 가설대로 크리스탈 이후 0x0E 레코드가 정확히 1건(`2599_tsuki`, `baseline_kda_20260716.txt`의 유일한 경계급 미니언 오차와 일치)이었으나, **3개 반례**가 확정됨:
- M1 `2599_PeacePlayz`: 크리스탈 이후 레코드 1건(frame 103, 크리스탈은 frame 102) — 그러나 M1은 baseline에서 미니언 카운트 완전 일치(mismatch 없음) → 이 레코드는 truth에 정확히 반영된 정상 미니언 킬.
- M2 `2600_staplers`: 크리스탈과 동일 프레임(96) 내 더 큰 오프셋에 레코드 1건 — M2도 미니언 mismatch 없음 → 정상 킬.
- M3 `2999_stapler`: 크리스탈 이후 레코드 3건(frame 105, 크리스탈은 frame 104) — M3도 미니언 mismatch 없음 → 정상 킬 3건.

M8/M10/M11은 가설대로 크리스탈 이후 레코드 0건(일치, 이 매치들은 애초에 미니언 mismatch가 없어 정보가 없음). 단, M10/M11은 `tournament_truth.json`에 미니언 truth 자체가 없음(10/10 선수 전원 `minion_kills` 필드 없음) — 이 두 매치의 "mismatch 없음"은 비교 대상 truth가 아예 없어서 공허하게 참인 것이며, M8(10/10 선수 전원 truth 존재)과 같은 의미로 취급하면 안 됨. 미니언 truth가 실제로 존재하는 앵커 매치는 M1, M2, M3, M5, M8 5건뿐이다. M4/M6는 크리스탈 레코드가 터렛 FP라 앵커 무효(`anchor_valid=False`), M7/M9는 크리스탈 후보 자체가 없어(`crystal=None`) 앵커 무효 — 넷 다 판정 미참여로 별도 보고만 함.

**결론:** 킬 이벤트와 동일한 실패 원인. 파일 위치는 시간의 대리 지표일 뿐 "스코어보드 반영 여부"의 독립 신호가 아니다. 크리스탈 파괴 시점에도 진행 중이던 미니언 웨이브의 라스트히트가 물리적으로 크리스탈 레코드보다 뒤에 기록되며, truth는 이를 정상적으로 카운트한다. Task 5 브리프가 검증하려던 전제("미니언 웨이브는 크리스탈이 무너지면 즉시 멈추므로 truth는 post-crystal 미니언 킬을 0건 카운트할 것")는 거짓으로 확인됨.

**상태:** ❌ 기각 - Task 5 Step 3(`_scan_minion_kills`에 위치 필터 추가)은 실행하지 않음. 반례: M1 `2599_PeacePlayz`, M2 `2600_staplers`, M3 `2999_stapler`.

---

### 5.2 절대 다시 시도하지 말 것

| 접근법 | 이유 |
|--------|------|
| 특정 action code 하나 = kill/death | Action code는 영웅별/상황별 의미가 다름 |
| 이벤트 빈도 통계 ↔ KDA 상관 | 빈도는 게임 상황 의존, KDA와 무관 |
| Entity 소멸 = 사망 | 사망해도 Entity는 이벤트에서 사라지지 않음 |
| 단일 리플레이 우연 일치 = 법칙 | 반드시 4+ 리플레이 교차 검증 |
| 고빈도 이벤트 (>100/프레임) = 특정 이벤트 | 고빈도 = 범용/시스템 이벤트 |
| Entity 0 `00 00 00 00` 패턴 = 정확한 파싱 | Null padding과 충돌, false positive 대량 발생 |
| 37바이트 고정 이벤트 구조 가정 | 실제: 11B~221B 가변 크기 (0x81=147B, 0x01=221B) |
| Gold amount (150-500 uint16) in payload | 0건 발견. Gold는 payload에 없음 |
| 바이너리에서 KDA/골드 직접 검색 | VGR에 누적 통계 미저장. 모든 인코딩/프레임/리플레이에서 0건 |
| 플레이어 블록 diff로 KDA 추출 | 블록은 정적 메타데이터만 저장 (4바이트만 변경, 전원 동일값) |
| Roster data region KDA 검색 | Data bytes=STATIC, float arrays=damage stats, 모든 인코딩(strided/interleaved/nibble/packed) 0건 |
| Roster float arrays ↔ Gold/CS 상관 | r=-0.133 (gold), r~0 (kills/deaths/assists). 99 players across 10 matches |
| 마지막 프레임 전체 exhaustive KDA 스캔 | uint8/16/32 BE/LE, 87,613 bytes, stride 2-64: 6/6 exact 0건, 5/6 near 0건 |
| 크리스탈 레코드 대비 파일 위치(offset)로 boundary kill 스코어보드 반영 판정 | 위치는 시간 순서의 대리 지표일 뿐. M8/M10에서 크리스탈 0.4~1.4s 후 정상 킬 반례 확인. 크리스탈 레코드 자체가 터렛 FP인 매치(M4/M6)에서는 적용 불가 |

---

## 6. 성공한 접근법 (참고)

| 기능 | 접근법 | 정확도 | 핵심 스크립트 |
|------|--------|--------|---------------|
| Hero Detection | Player block +0xA9 uint16 LE | 100% (107/107) | `vg/core/hero_matcher.py` |
| Win/Loss | Turret ID clustering + Crystal destruction | 100% (19/19) | `vg/analysis/win_loss_detector.py` |
| Team Detection | Player block +0xD5 byte | 100% | `vg/core/vgr_parser.py` |
| Kill Detection | `[18 04 1C]` protocol record + frequency matching | 97.9% (92/94) | `vg/core/kda_detector.py` |
| Death Detection | `[08 04 31]` protocol record + post-game filter | 95.7% (90/94) | `vg/core/kda_detector.py` |
| Item Detection | 4-strategy unified extractor | 부분 성공 | `vg/analysis/item_extractor.py` |

---

*Last Updated: 2026-07-16*
*이 문서는 새로운 실패 시도가 발생할 때마다 업데이트할 것.*
