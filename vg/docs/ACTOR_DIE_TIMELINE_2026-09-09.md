# ActionActorDie 타임라인 구현 (2026-09-09)

`python -m vg.analysis.event_timeline <numbered-section.vgr>`의 기본 목록은 이제
`0x0430`을 포함한다. `--opcode 0x0430`으로 단독 선택하고 `--entity 1500` 또는
`--entity 2007`로 피해자 또는 원시 source를 선택할 수 있다.

검증 근거는 [사망 액션 분석](DEATH_EVENTS_2026-09-09.md)의 Windows 실행 파일
SHA256 `659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`이다.
이 필드는 해당 빌드와 관찰된 레이아웃의 해석이다. 타임라인 자체가 입력 리플레이의
클라이언트 빌드를 인증하는 것은 아니다.

| 필드 | 의미 |
|---|---|
| `native_label` / `native_class` | `ActionActorDie` / `Nuo::Kindred::ActionActorDie` |
| `native_type` | `actor_die_action` |
| `ref0` / `native_victim_id` | payload offset 0의 BE32 피해 개체 |
| `ref1` / `native_source_raw` | payload offset 4의 BE32 원시 사망 원인 참조 |
| `native_source_is_sentinel` | 원시 source가 `0xffffffff`인지 여부 |
| `remaining_hex` | 의미를 부여하지 않은 마지막 6바이트 |
| `payload_hex` | 원래 14바이트 전체 |

payload가 정확히 14바이트일 때만 해석한다. `content_length`는 opcode 2바이트를
포함하므로 16이다. 다른 길이는 `unexpected_content_length`로 원문만 보존하고
피해자/source/native 필드를 붙이지 않는다. 잘린 framing은 기존과 같이 오류다.

행의 `timestamp`는 외부 레코드의 기록 시각이다. 게임 시각으로 자동 치환하지 않는다.
숫자 섹션 순서와 원래 레코드 순서를 유지하고, 다른 payload 안의 유사 바이트를
레코드로 취급하지 않는다. 같은 시각의 `041c` 카운터와 후속 `0431` 상태 전환은
각각 별도 행이다. source는 플레이어·비플레이어·sentinel을 원시 값으로 보존한다.
킬 인정 영웅, 소유자, 어시스트, 최종 데스 합계나 완료 판정은 이 액션에서 추론하지 않는다.

회귀 검증: `python -B -m unittest discover -s tests -p test_actor_die_timeline.py -v`.
정상·비플레이어·sentinel·길이 오류·양쪽 참조 필터·위장 레코드·다중 섹션·독립 카운터 및
상태 행·CLI help/정상/잘린 입력을 포함한다.

실제 직접 경기의 121개 섹션을 읽는 CLI에서도 피해자 `1500`, source `2007`의
행을 확인했다. 섹션 97, 레코드 인덱스 2915, byte offset 100334, 기록 시각
`978.1154174804688`, payload `000005dc000007d7000000000000`이다.
피해자 필터는 사망 액션 1행, source 2007 필터는 20행이며 두 출력 모두 이 행을
포함한다. 전체 unittest 327개가 44.024초에 통과했고 CLI help/정상은 exit 0,
누락된 경로와 잘린 본문은 exit 2를 반환했다.
