# 원본 Android APK와 VG:NA 대조 결과

2026-09-07. **이번에 확인한 Android 4.13.4(147219) APK에서도 네 이벤트의 핵심 처리와 킬·사망·어시스트 필드 연결이 대응한다.** VG:NA에서만 붙인 이름에 기대던 상태에서, 별도로 확보한 Android APK의 수신 코드까지 대조한 상태로 진전했다.

쉽게 말하면 두 프로그램에서 같은 번호의 명령을 따라가 봤고, 이번에 조사한 범위에서는 같은 종류의 숫자를 바꾸고 있었다. 다만 모든 버전·모든 이벤트를 해독했다거나 최종 경기 점수가 완성됐다는 뜻은 아니다.

## 무엇과 무엇을 비교했나

| 대상 | 실제 확보한 파일 | 식별 정보 |
|---|---|---|
| Android 원본 패키지 보관본 | APKMirror가 Super Evil Megacorp 서명본으로 등록한 `com.superevilmegacorp.game`, 4.13.4(147219) | APK 30,497,305바이트, APK Signature v1·v2 검증 통과 |
| Android 엔진 | 위 APK의 `lib/arm64-v8a/libGameKindred.so` | 45,062,040바이트, ELF ARM64 |
| VG:NA 엔진 | 앞서 확보한 커뮤니티 변조·재배포 iOS IPA의 `GameKindredEngine` | 26,503,168바이트, Mach-O ARM64 |

Android APK는 [APKMirror의 147219 보관 페이지](https://www.apkmirror.com/apk/super-evil-megacorp/vainglory/vainglory-4-13-4-147219-release/vainglory-4-13-4-147219-android-apk-download/)에서 Chrome의 일반 다운로드 절차로 받았다. 실제 파일 SHA-256 및 서명 인증서 SHA-256이 해당 페이지와 일치했다. 서명 인증서는 [2020년 4.13.0 보관 페이지](https://www.apkmirror.com/apk/super-evil-megacorp/vainglory/vainglory-4-13-0-102405-release/vainglory-4-13-0-102405-android-apk-download/)에 게시된 값과도 같았다. 오래된 APK 자체를 추가로 내려받아 검사한 것은 아니다.

여기서 ‘원본 APK’는 이 서명과 보관 이력으로 식별한 Android 패키지를 뜻한다. 개발사 서버에서 직접 받거나 개발사가 별도로 발표한 해시와 대조한 것은 아니며, 게시자의 귀속은 보관소의 서명 이력에 의존한다. VG:NA를 공식 배포본으로 취급하지 않는다.

```text
APK SHA-256
e82a6beed517db32536cd0f85a703d84dda84e1d184c990728dfb7c87d561d2d

APK 서명 인증서 SHA-256
358a74b85ea8839de3f5d1b87cc84a2906dcd3a40099479ef957819fda54a90b

Android 엔진 SHA-256
cd1b8831f82c469274613fc30f1f1f6e78c788102cdad7db5db2c04b96580a47
ELF build ID
b6ed0857c01ae2162d71fed102493f250973bcdc

VG:NA iOS 엔진 SHA-256
c23b2e9eb201f47694c7e71ab39d2c8c96850beb4ddf489745def23927fcd891
```

APK와 엔진은 설치하거나 실행하지 않았다. APK 서명 도구, ZIP CRC 검사, ELF·Mach-O 구조 해석 및 기계어 디스어셈블만 사용했다.

## 네 이벤트의 대조

| 기록 | Android APK에서 확인한 처리 | VG:NA와의 대조 |
|---|---|---|
| `0x041C` | 능력치 번호·층·값을 읽고, mode가 0이면 더하고 0이 아니면 대입한다. | 필드 위치와 SET/ADD 선택, 네 층의 저장 위치가 대응한다. |
| `0x041D` | 자원 번호·값·mode를 읽는다. 핵심 값 갱신은 SET `max(값,0)`, ADD `max(기존값+값,0)`이다. | 자원 배열 위치와 핵심 연산이 대응한다. 자원 0·6 관련 예외 분기도 구분해 확인했다. |
| `0x042B` | 인덱스별 상태 바이트와 두 마스크를 갱신한다. | 세 저장 위치와 관련 조건이 대응한다. 각 비트의 게임 내 이름은 여전히 미확인이다. |
| `0x0431` | 캐릭터와 현재 상태를 검사하고, 상태가 3일 때 4를 목표로 상태 전환 함수를 호출한다. | 조건부 3→4 전환이 대응한다. 이것만으로 실제 사망 순간이나 부활을 뜻한다고 확정하지 않는다. |

`0x041C` 수신 콜백은 payload의 0·4바이트에서 두 참조, 8바이트에서 값, 12·13·14바이트에서 번호·층·mode를 읽는다. `0x041D`는 0·4·8·9바이트에서 참조·값·번호·mode를 읽고 10·11바이트 플래그도 별도로 처리한다. 두 mode는 생성자를 부르기 전에 `!=0`으로 정규화하므로, 생성자에 있는 비트 마스킹을 다른 SET/ADD 규칙으로 오해하면 안 된다.

Android 수신 분기에서 실제 opcode를 따라간 연결은 다음과 같다. 주소는 Android ELF의 가상 주소이며 원래 심볼 이름이 없는 함수에는 역할로 이름을 붙였다.

| opcode | 수신 분기 진입 | 생성자 | 객체가 저장한 vtable 포인터 | 적용 함수 |
|---|---|---|---|---|
| 041C | `0x82bbd4` → 콜백 `0x829fac` | `0xc041e4` | `0x27116e0` | `0xc042ec` → `0xc042f0` |
| 041D | `0x82cc8c` → 콜백 `0x82a024` | `0xc043c0` | `0x2711718` | `0xc04498` → 핵심 `0xc04544` |
| 042B | `0x82cdb4` | `0xc0542c` | `0x27118d8` | `0xc054a0` |
| 0431 | `0x82cdd8` | `0xbfe30c` | `0x2710f38` | `0xbfe398` |

수신 함수 `0x82b85c`는 opcode를 읽고 `0x1a94bb0`의 분기표를 사용한다. 네 분기표 항목을 직접 계산해 위 진입점과 연결했다. 생성자가 저장하는 포인터는 각 vtable 헤더 주소에 16을 더한 값이다. 네 테이블의 다섯 함수 슬롯, 총 20개는 ELF `R_AARCH64_RELATIVE` 재배치 항목으로 확인했다. 큐 처리 함수 `0xbe2218`의 `0xbe2264..0xbe226c`가 실제로 vtable의 `+0x18` 슬롯을 호출한다.

각 테이블의 `+0x10` 송신 경로도 따라가 opcode 상수를 확인했다. 네 송신 함수가 만드는 첫 네 바이트는 양쪽에서 같다.

| opcode | Android와 VG:NA가 만드는 바이트 |
|---|---|
| 041C | `00 11 04 1c` |
| 041D | `00 0e 04 1d` |
| 042B | `00 0a 04 2b` |
| 0431 | `00 06 04 31` |

이 바이트는 네이티브 송신 함수의 헤더다. 리플레이 파일의 바깥쪽 timestamp·length 헤더와 혼동하지 않는다.

## KDA 이름을 실제 값까지 따라간 결과

| 출력 이름 | Android가 읽는 값 | VG:NA에서 읽는 값 |
|---|---|---|
| `myKills` | 계산된 능력치 41: component `+0xdc`, `+0x190`, `+0x244`, `+0x2f8` | 같은 번호와 네 위치 |
| `myDeaths` | 계산된 능력치 42: 위 쌍의 두 번째 float | 같은 번호와 네 위치 |
| `myAssists` | component `+0x334`, 자원 배열 `+0x308`의 11번 | 같은 번호와 위치 |

Android에서는 다음 연결을 확인했다.

1. `0x81b390`이 현재 캐릭터를 찾는 `0x81e360`을 호출한다. 해당 함수는 식별자를 비교한 뒤 이벤트 처리부와 같은 캐릭터 조회 함수 `0xc9e390`을 사용한다.
2. 반환 포인터는 X26 → stack `+0x20` → X20을 거쳐 `0x81cb34`에서 캐릭터의 `+0x40` 통계 컴포넌트로 이어진다.
3. `0x81cb44..0x81cb94`에서 킬·사망 두 float를 네 층과 경계값으로 계산하고, `0x81cb88`에서 어시스트 값을 읽는다.
4. `0x81cbc4`, `0x81cbfc`, `0x81cc88`이 각각 `myKills`, `myDeaths`, `myAssists` 문자열을 준비한다. 이어지는 출력 경로가 계산 결과와 S15의 어시스트 값을 각각 전달한다.
5. 값 저장 함수 `0xdc3ef0`은 float 타입을 지정하고 전달받은 S0를 저장한다. 다른 통계로 재계산하는 함수가 아니다.

킬·사망의 수학적 계산 구조는 양쪽 모두 다음과 대응한다.

```text
clamp((layer0 + layer1 × (layer3 + 1)) × (layer2 + 1), min[index], max[index])
```

따라서 능력치 41·42와 자원 11의 연결은 이번 Android APK에서도 뒷받침된다. 자원 9·10을 같은 이름으로 바꾸는 근거는 여전히 없다.

## 같다고 확정하지 않은 것

- **실행파일 전체 및 모든 버전:** Android와 iOS의 바이너리·주소·함수 배치는 다르다. 일부 코드 차이를 VG:NA의 변조 때문이라고 분리하려면 같은 플랫폼의 변조 전 파일이 필요하다.
- **부동소수점의 모든 비트 결과:** VG:NA의 K/D 계산은 FMLA와 FMINNM/FMAXNM을 사용하고 Android는 별도 덧셈·곱셈 및 비교·선택 명령을 사용한다. 자원 하한 처리도 FMAXNM과 FMAX가 다르다. 수학적 연산 구조와 필드 연결이 대응한다는 결과이며, 반올림·NaN·부호 있는 0까지 완전히 동일하다고 증명한 것은 아니다.
- **리플레이 생성 빌드:** 이 APK가 보유 56개 리플레이를 만든 정확한 빌드인지는 확인하지 않았다. 네이티브 수신부가 읽는 필드 뒤의 VGR 추가 바이트도 모두 해석하지 않았다.
- **최종 경기 점수와 사건 시각:** 초기값, 중간 누락, 경기 종료 기준, 기존 어시스트 추정 정책 문제는 별개다. 실제 죽는 순간·부활 시각·일부 상태 이름도 이번 정적 대조로 확정하지 않았다.

기존 판독기의 의미 필드를 바꿔야 한다는 근거는 이번 범위에서 나오지 않았다. 실행 코드 변경 없이 비교 증거를 추가했다. 앞서 ‘공식 VG:NA 엔진’이라고 쓴 출처 오류는 철회된 상태이며, 이번에는 별도 Android APK의 식별·서명·수신 경로를 명시적으로 남긴다.

## 검증 자료와 재현

- [APK·엔진·함수 식별 목록](/Users/gimhunhui/Documents/Codex/2026-09-05/ssh-winsrv-d-vg/outputs/vg-apk-comparison-manifest.json)
- [APK 서명 검증 원문](/Users/gimhunhui/Documents/Codex/2026-09-05/ssh-winsrv-d-vg/outputs/vg-apk-signature.txt)
- [대조 결과와 바이트 검증 기록](/Users/gimhunhui/Documents/Codex/2026-09-05/ssh-winsrv-d-vg/outputs/vg-apk-comparison-verification.json)
- [선택한 기계어·분기표·스크립트 묶음](/Users/gimhunhui/Documents/Codex/2026-09-05/ssh-winsrv-d-vg/outputs/vg-apk-comparison-evidence.zip)

묶음에는 APK·엔진 전체나 웹페이지의 추적 데이터가 들어 있지 않다. 각 바이너리의 해시, 선택한 함수 범위와 기계어, 재현용 스크립트를 담았다. 분석 도구는 기존 Android SDK의 apksigner/aapt2, Apple LLVM 도구 및 분석 폴더 안에 설치한 Capstone 5.0.9·pyelftools 0.33을 사용했다. KDA의 주요 명령은 Capstone과 LLVM 양쪽의 출력으로 확인했다.

실행 코드나 통계 정책을 수정하지 않았으므로 기존 263개 테스트를 새 APK 의미의 증거로 재사용하지 않았다. 이번 검증 대상은 APK 서명·파일 무결성·바이너리 안의 연결과 연산이다.
