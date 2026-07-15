# 100% 정확도 로드맵 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** VG 리플레이 디코더의 파이프라인 출력을 "출력한 값은 전부 정확, 구할 수 없는 값은 명시적 unknown + 사유 표기" 기준의 100% 정확도로 끌어올린다.

**Architecture:** 2채널 융합 전략. (1) 바이너리 디코더에서 마지막 개선 여지(경계 이벤트의 파일 물리 순서)를 짜내고, (2) 게임 클라이언트 주입-재생-OCR 진실 루프를 제2 관측 채널로 완성해 바이너리로 불가능한 필드(절단 데이터, 팀 좌/우, 미확인 아이템 ID)를 보정한다. 모든 보정값에는 provenance(binary/ocr/truth)를 기록한다.

**Tech Stack:** Python 3.13 (unittest), easyocr, vgrplay.exe (리플레이 주입), 기존 `vg/core` 디코더 스택.

## Global Constraints

- 테스트 실행: `python -m unittest discover -s tests` (**pytest 미설치** — 설치하지 말고 unittest 유지)
- 현재 테스트 상태: `Ran 197 tests ... OK` — 모든 태스크는 이 그린 상태를 유지해야 함
- 리플레이 파일 위치: `D:\Desktop\My Folder\Game\VG\vg replay\`
- 진실 데이터: `vg/output/tournament_truth.json`
- 검증 명령: `python -m vg.analysis.truth_comparison`
- 실패한 가설은 반드시 `vg/docs/FAILED_ATTEMPTS.md`에 기록 (이 프로젝트의 핵심 관행)
- 커밋 메시지: 기존 스타일(`feat:`/`docs:`/`fix:` prefix, 영어) + `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`
- 메모리의 정확도 수치(292/297, kill_buffer=3s 등)는 **최신 코드(commit 56083eb 이후 튜닝: kill_buffer=20s, death rescue path)보다 오래된 것** — 반드시 Task 2에서 베이스라인을 재측정하고 그 결과를 기준으로 삼을 것

---

## 로드맵 개요 (5 Phase + 게이트)

| Phase | 목표 | 산출물 | 진행 게이트 |
|---|---|---|---|
| 0 | WIP 커밋 + 베이스라인 재측정 | 클린 트리, 현재 mismatch 목록 | 테스트 그린 |
| 1 | 경계 이벤트 파일 순서 실험 | 프로브 리포트, (성공 시) 디코더 필터 | 프로브가 가설 확정/기각 |
| 2 | OCR 진실 루프 완성 | 자동 주입→재생→캡처→OCR→보정 병합 | `다시보기` 좌표 확정, OCR 자체 정확도 100% 검증 |
| 3 | 절단 감지기 + 정직한 결측 | `data_complete` 플래그, per-field provenance | M6가 truncated로 플래그됨 |
| 4 | 미확인 아이템 ID 7종 해독 | `vgr_mapping.py` 갱신 | Phase 2 루프 가동 |
| 5 | 검증 세트 확장 (45+ 리플레이) | 확장 truth 세트, 전체 재검증 | Phase 2 루프 가동 |

Phase 0–1은 본 문서에 상세 태스크로 기술. Phase 2–5는 게이트 통과 시 별도 상세 계획을 작성한다(각 Phase가 독립 서브시스템이므로 계획 분리).

---

### Task 1: WIP 커밋 (OCR 폴백 + 주입 검증 도구)

현재 작업 트리에 결과 화면 OCR 폴백(`result_screen_image_kda_correction.py`)과 주입 무결성 검증(`vgrplay_inject.py`의 `find_live_temp_replay`/`verify_injected_frames`)이 미커밋 상태로 남아 있다. 테스트는 이미 전부 통과하므로 커밋만 하면 된다.

**Files:**
- 신규: `vg/tools/result_screen_image_kda_correction.py`, `tests/test_result_screen_image_kda_correction.py`
- 수정: `vg/tools/vgrplay_inject.py`, `vg/tools/result_screen_kda_validation.py`, `vg/tools/result_screen_kda_correction_bundle.py`, `vg/tools/result_screen_kda_correction_autobundle.py`, `tests/test_vgrplay_inject.py`, `tests/test_result_screen_kda_validation.py`, `tests/test_result_screen_kda_correction_bundle.py`

- [ ] **Step 1: 테스트 그린 확인**

```powershell
python -m unittest discover -s tests
```

기대: `Ran 197 tests ... OK`

- [ ] **Step 2: 커밋**

```powershell
git add vg/tools/result_screen_image_kda_correction.py tests/test_result_screen_image_kda_correction.py vg/tools/vgrplay_inject.py vg/tools/result_screen_kda_validation.py vg/tools/result_screen_kda_correction_bundle.py vg/tools/result_screen_kda_correction_autobundle.py tests/test_vgrplay_inject.py tests/test_result_screen_kda_validation.py tests/test_result_screen_kda_correction_bundle.py
git commit -m @'
feat: add screenshot OCR kda fallback and injection frame verification

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@
```

---

### Task 2: 베이스라인 재측정

메모리/문서의 수치(KDA 292/297, M5 +1 킬, M5 미니언 +1, M6 절단)는 `56083eb` 튜닝(kill_buffer 20s, death rescue path) 이전 기준일 수 있다. 현재 코드로 mismatch 목록을 재확보해 Phase 1의 표적을 확정한다.

**Files:**
- 생성: `vg/output/baseline_kda_20260716.txt` (truth_comparison 출력 캡처)

**Interfaces:**
- Produces: 현재 mismatch 경기/필드 목록 → Task 3의 대상 경기 선정 입력

- [ ] **Step 1: 검증 실행 및 캡처**

```powershell
python -m vg.analysis.truth_comparison > vg/output/baseline_kda_20260716.txt 2>&1
Get-Content vg/output/baseline_kda_20260716.txt -Tail 40
```

기대: 요약부에 K/D/A 일치율과 MISMATCH 라인 목록. 각 MISMATCH의 경기 번호·플레이어·필드·(detected vs truth)를 기록.

- [ ] **Step 2: mismatch 목록 정리**

출력에서 `MISMATCH` 라인을 추출해 아래 형식으로 이 계획서의 부록 또는 커밋 메시지에 기록:

```
M<n> <player> <field>: detected=<x> truth=<y>  (분류: boundary | truncation | 기타)
```

분류 기준: 경기의 crystal_death_ts 부근(±5s) 이벤트가 원인이면 boundary, 리플레이 마지막 이벤트 ts가 truth duration보다 크게(>30s) 이르면 truncation.

- [ ] **Step 3: 커밋**

```powershell
git add vg/output/baseline_kda_20260716.txt
git commit -m @'
docs: capture kda baseline before boundary file-order experiment

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@
```

---

### Task 3: 경계 이벤트 파일 순서 프로브

**가설:** 크리스탈 파괴 시각과 타임스탬프가 동률/근접해 시간 필터로 구분 불가능한 킬·미니언킬 이벤트는, 바이트 스트림 내 물리적 위치(frame_idx, file_offset)가 크리스탈 사망 레코드보다 앞/뒤인지로 스코어보드 반영 여부를 구분할 수 있다.

`KillEvent`/`DeathEvent`는 이미 `frame_idx`와 `file_offset`을 보존하므로(`vg/core/kda_detector.py:42-57`) 새 스캔 없이 위치 비교만 추가하면 된다. 크리스탈 사망 레코드의 위치는 이 스크립트에서 직접 스캔한다(`_detect_crystal_death`는 ts/eid만 반환).

**Files:**
- 생성: `vg/analysis/boundary_event_file_order.py`
- 생성(실행 산출물): `vg/output/boundary_file_order_report.json`

**Interfaces:**
- Consumes: `UnifiedDecoder(path)`, `UnifiedDecoder._load_frames(frame_dir, frame_name)`, `UnifiedDecoder._scan_kda_events(frames, all_players)` → `(detector, eid_map, team_map, duration_est)`, `detector.kill_events` (각 원소: `killer_eid`, `timestamp`, `frame_idx`, `file_offset`)
- Produces: 경기별 경계 이벤트 위치 리포트 JSON → Task 4 필터 규칙의 근거

- [ ] **Step 1: 프로브 스크립트 작성**

```python
"""Boundary event file-order probe.

For each truth match, locate the crystal death record's physical position
(frame_idx, byte offset) and list every kill event within +/-BOUNDARY_WINDOW
seconds of the crystal timestamp, annotated with whether it physically
precedes or follows the crystal record in the byte stream.

Hypothesis: scoreboard-counted boundary kills precede the crystal record;
post-game ceremony kills follow it, even when timestamps tie exactly.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from vg.core.unified_decoder import UnifiedDecoder

DEATH_HEADER = bytes([0x08, 0x04, 0x31])
MINION_CREDIT = bytes([0x10, 0x04, 0x1D])
BOUNDARY_WINDOW = 5.0
TRUTH_PATH = Path(__file__).resolve().parent.parent / "output" / "tournament_truth.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "output" / "boundary_file_order_report.json"


def find_crystal_records(frames):
    """Scan death headers for eid 2000-2005; return [(ts, eid, frame_idx, offset)]."""
    hits = []
    for frame_idx, data in frames:
        pos = 0
        while True:
            pos = data.find(DEATH_HEADER, pos)
            if pos == -1:
                break
            if pos + 13 > len(data) or data[pos+3:pos+5] != b"\x00\x00" or data[pos+7:pos+9] != b"\x00\x00":
                pos += 1
                continue
            eid = struct.unpack_from(">H", data, pos + 5)[0]
            ts = struct.unpack_from(">f", data, pos + 9)[0]
            if 2000 <= eid <= 2005 and 60 < ts < 2400:
                hits.append({"ts": round(ts, 2), "eid": eid, "frame_idx": frame_idx, "offset": pos})
            pos += 1
    return hits


def probe_match(replay_file):
    decoder = UnifiedDecoder(replay_file)
    match = decoder.decode()

    replay_path = Path(replay_file)
    frame_dir = replay_path.parent
    frame_name = replay_path.stem.rsplit(".", 1)[0]
    frames = decoder._load_frames(frame_dir, frame_name)

    all_players = match.players
    detector, eid_map, team_map, _ = decoder._scan_kda_events(frames, all_players)
    if detector is None:
        return {"replay": str(replay_file), "error": "no valid entity ids"}

    crystals = find_crystal_records(frames)
    crystal_ts = match.crystal_death_ts
    # pick the scanned record matching the decoder's chosen crystal ts
    crystal = None
    if crystal_ts is not None:
        for rec in crystals:
            if abs(rec["ts"] - crystal_ts) < 1.0:
                crystal = rec
                break
    if crystal is None and crystals:
        crystal = max(crystals, key=lambda r: r["ts"])

    def position(ev):
        return (ev.frame_idx, ev.file_offset)

    def after_crystal(ev):
        if crystal is None:
            return None
        return position(ev) > (crystal["frame_idx"], crystal["offset"])

    boundary_kills = []
    ref_ts = crystal["ts"] if crystal else (match.duration_seconds or 0)
    for kev in detector.kill_events:
        if kev.timestamp is None:
            continue
        if abs(kev.timestamp - ref_ts) <= BOUNDARY_WINDOW or kev.timestamp > ref_ts:
            player = eid_map.get(kev.killer_eid)
            boundary_kills.append({
                "player": getattr(player, "name", None),
                "killer_eid": kev.killer_eid,
                "ts": round(kev.timestamp, 2),
                "frame_idx": kev.frame_idx,
                "offset": kev.file_offset,
                "after_crystal": after_crystal(kev),
            })

    return {
        "replay": str(replay_file),
        "crystal": crystal,
        "crystal_candidates": len(crystals),
        "duration": match.duration_seconds,
        "boundary_kills": sorted(boundary_kills, key=lambda k: (k["frame_idx"], k["offset"])),
    }


def main():
    truth = json.loads(TRUTH_PATH.read_text(encoding="utf-8"))
    report = []
    for truth_match in truth["matches"]:
        replay_file = truth_match["replay_file"]
        print(f"probing {replay_file} ...")
        try:
            report.append(probe_match(replay_file))
        except Exception as exc:
            report.append({"replay": replay_file, "error": repr(exc)})
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT_PATH} ({len(report)} matches)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 실행**

```powershell
python -m vg.analysis.boundary_event_file_order
```

기대: 전 truth 경기 순회 후 `vg/output/boundary_file_order_report.json` 생성, 에러 경기 0건.

- [ ] **Step 3: 가설 판정**

Task 2의 boundary 분류 mismatch 경기에 대해 리포트를 검토:

- **확정 조건:** 초과 검출된 킬(truth에 없는 킬)은 전부 `after_crystal: true`이고, truth에 반영된 경계 킬은 전부 `after_crystal: false`. 그리고 **비-mismatch 경기에서 이 규칙을 적용해도 정답 킬이 하나도 제거되지 않아야 함** (regression 체크 — 리포트의 boundary_kills 전수 검사).
- **기각 조건:** 초과 킬이 크리스탈 레코드보다 앞에 있거나, 정답 킬이 뒤에 있는 반례 존재.

- [ ] **Step 4: 결과 기록 및 커밋**

기각 시 `vg/docs/FAILED_ATTEMPTS.md`에 반례와 함께 기록하고 Task 4를 건너뛴다. 확정 시 그대로 Task 4 진행.

```powershell
git add vg/analysis/boundary_event_file_order.py vg/output/boundary_file_order_report.json
git commit -m @'
feat: add boundary event file-order probe

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@
```

---

### Task 4: 파일 순서 필터 구현 (Task 3 확정 시에만)

**게이트:** Task 3 Step 3에서 가설 확정된 경우에만 수행.

`KDADetector.get_results()`에 크리스탈 레코드 위치 마커를 전달해, 경계 윈도우 내 타임스탬프 동률 이벤트를 물리 순서로 판정한다. 시간 필터(kill_buffer)는 유지하되, 크리스탈 마커가 주어지면 **마커 이후 위치**를 post-game 판정의 우선 근거로 쓴다.

**Files:**
- 수정: `vg/core/kda_detector.py` (`get_results` 시그니처 확장)
- 수정: `vg/core/unified_decoder.py` (크리스탈 레코드 위치를 스캔해 마커 전달)
- 테스트: `tests/test_kda_boundary_filter.py` (신규)

**Interfaces:**
- Produces: `KDADetector.get_results(..., crystal_marker: Optional[Tuple[int, int]] = None)` — `(frame_idx, file_offset)` 튜플. 마커가 None이면 기존 동작과 완전 동일해야 함(하위 호환).

- [ ] **Step 1: 실패하는 테스트 작성**

```python
import unittest

from vg.core.kda_detector import KDADetector, KILL_HEADER


def make_kill_record(eid_be: int, ts: float) -> bytes:
    import struct
    return (
        struct.pack(">f", ts) + b"\x00\x00\x00"  # ts 7 bytes before header
        + KILL_HEADER + b"\x00\x00"
        + struct.pack(">H", eid_be)
        + b"\xFF\xFF\xFF\xFF" + b"\x3F\x80\x00\x00" + b"\x29"
    )


class TestBoundaryFileOrderFilter(unittest.TestCase):
    def test_kill_after_crystal_marker_with_tied_timestamp_is_dropped(self) -> None:
        eid = 0x05DC
        crystal_ts = 1200.0
        pre = make_kill_record(eid, crystal_ts)     # before marker: keep
        post = make_kill_record(eid, crystal_ts)    # after marker: drop
        frame = pre + b"\x00" * 64 + post

        detector = KDADetector(valid_entity_ids={eid})
        detector.process_frame(1, frame)

        marker = (1, len(pre) + 32)  # crystal record sits between the two kills
        results = detector.get_results(
            game_duration=crystal_ts, crystal_marker=marker,
        )
        self.assertEqual(results[eid].kills, 1)

    def test_no_marker_keeps_legacy_behaviour(self) -> None:
        eid = 0x05DC
        frame = make_kill_record(eid, 1200.0) + b"\x00" * 64 + make_kill_record(eid, 1200.0)
        detector = KDADetector(valid_entity_ids={eid})
        detector.process_frame(1, frame)
        results = detector.get_results(game_duration=1200.0)
        self.assertEqual(results[eid].kills, 2)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 테스트 실패 확인**

```powershell
python -m unittest tests.test_kda_boundary_filter -v
```

기대: FAIL (`get_results() got an unexpected keyword argument 'crystal_marker'`)

- [ ] **Step 3: 최소 구현**

`get_results` 킬 집계 루프(현재 `vg/core/kda_detector.py:264-270` 부근)를 다음과 같이 확장:

```python
def get_results(self, game_duration=None, death_buffer=3.0, kill_buffer=20.0,
                team_map=None, crystal_marker=None):
    ...
    max_kill_ts = (game_duration + kill_buffer) if game_duration else 9999
    for kev in self._kill_events:
        if kev.killer_eid in results:
            if kev.timestamp is not None and kev.timestamp > max_kill_ts:
                continue  # Post-game ceremony kill
            if (crystal_marker is not None
                    and kev.timestamp is not None
                    and game_duration is not None
                    and kev.timestamp >= game_duration - 1.0
                    and (kev.frame_idx, kev.file_offset) > crystal_marker):
                continue  # Physically after crystal death record: ceremony kill
            results[kev.killer_eid].kills += 1
            results[kev.killer_eid].kill_events.append(kev)
```

주의: 경계 조건 상수(`game_duration - 1.0`)는 Task 3 리포트의 실측 분포로 확정할 것. Task 3에서 "truth에 반영된 post-crystal 킬"이 관찰됐다면(현 kill_buffer=20s 튜닝의 존재 이유) 위치 필터는 **동률(±1s) 구간에만** 적용해야 한다 — 위 코드의 `>= game_duration - 1.0` 조건이 그 안전장치이며, 리포트가 다른 경계를 가리키면 그 값으로 조정한다.

`unified_decoder.py`에는 Task 3의 `find_crystal_records`와 동일한 스캔으로 채택된 크리스탈 ts에 대응하는 `(frame_idx, offset)`을 구해 `get_results` 호출부에 전달하는 코드를 추가한다 (`_detect_crystal_death`가 위치도 반환하도록 확장하는 것이 중복 스캔을 피하는 올바른 위치).

- [ ] **Step 4: 신규 + 전체 테스트 통과 확인**

```powershell
python -m unittest tests.test_kda_boundary_filter -v
python -m unittest discover -s tests
```

기대: 신규 2건 PASS, 전체 199건 OK.

- [ ] **Step 5: truth 재검증 (회귀 게이트)**

```powershell
python -m vg.analysis.truth_comparison > vg/output/kda_after_file_order_filter.txt 2>&1
```

기대: Task 2 베이스라인 대비 boundary 분류 mismatch 감소, **기존 일치 항목의 회귀 0건**. 회귀 발생 시 필터 조건을 좁히거나 롤백하고 FAILED_ATTEMPTS.md에 기록.

- [ ] **Step 6: 커밋**

```powershell
git add vg/core/kda_detector.py vg/core/unified_decoder.py tests/test_kda_boundary_filter.py vg/output/kda_after_file_order_filter.txt
git commit -m @'
feat: filter boundary-tied kills by crystal record file order

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@
```

---

### Task 5: 미니언 킬 경계 케이스에 동일 규칙 적용 검토

tsuki +1 미니언 킬(0x0E가 crystal_ts 정각에 발화)이 현 코드에서 여전히 mismatch인지 Task 2 베이스라인으로 확인 후, mismatch라면 Task 3 프로브에 0x0E 레코드 위치 스캔을 추가(`MINION_CREDIT` 헤더 + value 1.0 + action 0x0E, 크리스탈 마커와 위치 비교)하고 Task 4와 같은 패턴으로 `_scan_minion_kills`에 위치 필터를 넣는다.

- [ ] **Step 1:** Task 2 베이스라인에서 미니언 mismatch 잔존 여부 확인 (없으면 이 태스크 종료)
- [ ] **Step 2:** `boundary_event_file_order.py`에 0x0E 위치 리포트 추가 → 재실행 → 판정 (Task 3 Step 3과 동일 기준)
- [ ] **Step 3:** 확정 시 `KDADetector._scan_minion_kills`가 위치를 보존하도록 수정(현재 counter만 유지 → `(eid, frame_idx, offset)` 리스트로 변경) 후 `get_results`에서 마커 필터 적용. 테스트는 Task 4 Step 1과 동일 패턴의 synthetic frame으로 작성.
- [ ] **Step 4:** 전체 테스트 + truth 재검증 + 커밋 (Task 4 Step 4–6과 동일 절차)

---

## Phase 2: OCR 진실 루프 완성 (게이트 통과 후 별도 상세 계획)

바이너리로 불가능한 모든 필드의 진실 소스. **현재 최우선 병목이며, Phase 4·5의 선행 조건.**

핵심 작업 (상세 계획 작성 시 태스크화):

1. **`다시보기` 좌표 확정** — `handoff.md`의 미해결 항목. 절차: 연습경기 → `Tb`(2848,1768) → `항복`(185,1092) → vgrplay 주입 → 오버레이 스크린샷 캡처 → 좌표 기록 → `handoff.md` 갱신. 주입 직후 `vgrplay_inject.verify_injected_frames`(이번 WIP에서 추가)로 SHA-256 무결성 확인 후에만 클릭 진행.
2. **재생 → 결과 화면 도달** — 타임라인 점프가 불안정하므로 1차 구현은 자동 재생 완주(경기당 15–30분). 점프 좌표/드래그는 후속 최적화.
3. **OCR 자체 정확도 검증 (중요)** — truth가 이미 있는 토너먼트 경기 결과 화면으로 OCR 파이프라인(`result_screen_image_kda_correction.py`)을 돌려 OCR 출력 vs truth 100% 일치를 먼저 증명. OCR이 새로운 오류원이 되면 안 됨. 불일치 토큰은 confidence 임계/전처리(crop, 대비)로 해소.
4. **보정 병합 및 provenance** — `result_screen_kda_correction_pipeline.py` → export에 per-field `source: binary|ocr|truth` 기록. 검증 세트 KDA 100% 리포트 산출.

**주의(구조적 한계):** 절단 리플레이(M6 유형)는 주입-재생해도 절단 시점의 결과 화면이 나오므로 이 루프로 복원 불가. 해당 경기는 Phase 3의 절단 플래그 + 외부 truth로만 처리.

## Phase 3: 절단 감지기 + 정직한 결측 (별도 상세 계획)

"100%"의 정의를 완성하는 단계: 복원 불가능한 값을 조용히 틀리는 대신 명시적으로 표기.

1. **바이너리측 절단 휴리스틱** — 크리스탈 사망 레코드 부재 + 최종 프레임의 마지막 이벤트 ts 기록 → `data_complete: false` 후보 플래그.
2. **OCR 교차 검증** — 결과 화면의 경기 시간 vs 바이너리 마지막 이벤트 ts 격차 > 15s → 절단 확정. (Phase 2 의존)
3. **Export 스키마 확장** — `DecodedMatch`/export에 `data_complete`, per-field provenance, 절단 시 KDA를 "하한값(lower bound)"으로 표기. 커밋 `59c67d1`의 provenance 노출을 일반화.
4. **수용 기준:** M6 리플레이가 truncated로 자동 플래그되고, truth 병합 후 최종 출력이 100% 정확 + 결측 사유 표기.

## Phase 4: 미확인 아이템 ID 7종 해독 (별도 상세 계획, Phase 2 의존)

ID 3(WP T3), 4(Def T3), 6(Def T3), 18(consumable?), 224(WP T3), 233(consumable), 239(vision?) — 샘플 부족 문제이므로 해독 가능.

1. 45+ 리플레이에서 해당 ID 구매자가 등장하는 경기 큐 생성 (`result_screen_capture_queue.py` 활용, ID별 최소 2경기).
2. 주입-재생 후 결과 화면의 **최종 빌드 패널** 캡처 → 아이템 아이콘 대조 → 바이너리 구매 이벤트와 교차 확인으로 ID 확정.
3. `vg/core/vgr_mapping.py`의 ID 맵과 `UPGRADE_TREE` 갱신, `vg/docs/ITEM_LIST_KR_EN.md` 반영.
4. 같은 캡처로 Echo/Protector Contract/Minion's Foot/Stormguard Banner 미매핑 4종의 구매 경기를 식별해 바이너리 ID 탐색 재시도.

## Phase 5: 검증 세트 확장 (별도 상세 계획, Phase 2 의존)

현재 100%들은 n=19~107 기준. 규칙의 통계적 신뢰를 위해:

1. 45+ 개인 리플레이 전체에 진실 루프 실행 → OCR 기반 truth 레코드 생성 (`kda_truth_loop.py` 큐 활용).
2. 확장 세트로 전체 디코더 재검증. KDA n≈300 → n≈1500.
3. 깨지는 규칙 발견 시 각각을 새 mismatch 클래스로 분류해 Phase 1과 같은 실험 사이클 반복.
4. 최종 수용 기준: **완전한(비절단) 리플레이에서 전 필드 100%, 절단 리플레이는 100% 플래그 + 하한값 표기.**

---

## 부록: 오차 클래스별 도달 경로 요약

| 오차 클래스 | 바이너리 해결 | 진실 루프 해결 | 담당 Phase |
|---|---|---|---|
| 경계 킬/미니언킬 (ts 동률) | 파일 순서 필터 (실험) | 가능 (보정) | 1, 2 |
| 절단 리플레이 (M6 유형) | 불가 (데이터 부재) | **불가** — 플래그+외부 truth만 | 3 |
| 미확인 아이템 ID 7종 | 샘플 확보 시 가능 | 최종 빌드 화면 대조 | 4 |
| Aegis/ScoutPak 구매 이벤트 부재 | 불가 | 최종 빌드 화면이 유일 소스 | 2, 4 |
| >6 아이템 오버플로 (sell/rebuy) | 부분적 (sell 1건 한계) | 최종 빌드 화면 대조 | 2, 4 |
| 팀 좌/우 라벨 | 불가 (포맷에 없음, 확정) | 결과 화면 좌/우 판독 | 2 |
| 골드 잔여 오차 (±5% 밖 2경기) | 튜닝 한계 도달 | 통계 화면 표시 여부 확인 후 OCR | 2 |
