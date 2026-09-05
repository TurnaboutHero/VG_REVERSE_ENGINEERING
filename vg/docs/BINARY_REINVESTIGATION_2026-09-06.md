# 바이너리 역공학 재조사: 먼저 경계와 의미를 분리한다

2026-09-06. 사용자 방향 수정에 따라 작성했다. **VGNA는 정답이 아닌, 틀릴 수 있는 비교 구현이다.** 이 원칙은 기존 `VGNA_REPLAY_SERVER_2026-07-30.md` 등의 ‘외부 정답 소스’ 표현보다 우선한다. HackedGlory와 VGNA 서버 파서도 동일한 구현으로 취급하지 않는다.

## 이번에 확인한 구조

원시 파일의0번 오프셋부터 다음 구조를 순서대로 읽었다. 바이트 패턴 검색, 오류 후 재동기화, 정답값 보정은 하지 않았다.

```
record_start +0  timestamp       float32 big-endian
             +4  content_length uint32 big-endian
             +8  opcode         uint16 big-endian
            +10  payload        content_length -2 bytes
next_record = record_start +8 +content_length
```

실제7,870개 파일/1,044,589,605바이트에서30,729,156개 레코드를 끝까지 소비했다. 파일 경계 오류0건이다. 이는 **프레이밍의 근거**이며 각opcode의 게임 의미가 맞다는 증거가 아니다.

`vg/core/vgr_records.py`는 이를 구현한 독립 파서다. 기존 VGRParser/KDADetector를 호출하지 않으며, 각 레코드에 오프셋·자기 시각·길이·opcode·payload view를 제공한다. `vg/analysis/record_framing_audit.py`로 같은 검증을 반복할 수 있다. 이번 단계에서는 기존 통계 디코더를 변경하지 않았다.

## 실제로 드러난 문제

### 1. ‘사망 헤더’의 구조와 시각 위치

기존 `08 04 31`은 독립적인3바이트 헤더가 아니다. 길이8의 마지막 바이트와 opcode0x0431이 이어진 것이다. 같은 방식으로 `18 04 1C`는 길이24+opcode0x041C, `10 04 1D`는 길이16+opcode0x041D다.

0x0431 본문은8바이트이며, opcode2바이트를 제외하면6바이트다. 기존 코드의 시각 오프셋(`signature+9`)은 이 레코드가 끝난 위치, 즉 **다음 레코드의timestamp**를 가리킨다. 자기 시각은`signature-7` 또는 새 파서의`record.timestamp`다.

현재 플레이어0x0431 레코드2,209건 중 대부분은 다음 메시지와 같은 시각이라 이 잘못된 읽기가 가려졌다. 실제1건에서는 자기 시각32.58894초와 다음 시각32.69308초가 달랐다. 따라서 구조적 오류는 확인됐지만, 이 차이가M6의65초 차이나KDA 오차를 설명한다고 주장하지 않는다. 0x0431이 언제나 게임상의 사망인지도 독립 검증 대상이다.

### 2. 30분 제한이 형식 검증에 섞여 있다

기존 `KDADetector`는시각을`0 < ts < 1800`으로 제한한다. 실제8개 리플레이에서30분 이후의 플레이어0x0431 레코드44건, 기존 킬 패턴에 맞는 레코드41건을 찾았다. 전부 섹션 번호의 시간대와30초 이내로 정합했다. 프레이밍으로도30분 이후의 정상 레코드가 존재함을 확인했다.

기존 코드는전자는버리고 후자의시각을None으로바꾼다. 이는 레코드 형식과 통계 해석을 함께 제한하는 코드상의 문제다. 다만 그44/41건 모두 실제 사망/킬인지 독립 경기 정답으로 확인한 것은 아니므로, **구조적으로 유효한 사건 후보의 소실**로 기록한다. 새 reader에는이 시간 상한이 없다. 기존KDA의상한은 별도 재구성 단계까지 유지했다.

### 3. 메타데이터를 리플레이로 세었다

앞선 검사에서시작 파일60개를 처리했다고 보고했지만,4개는`__MACOSX/._*.0.vgr`의AppleDouble 메타데이터였다. 같은형식의다른섹션1개를포함해총5파일/880바이트다. `00051607`magic과본문`Mac OS X`를확인했고,[RFC1740](https://www.rfc-editor.org/rfc/rfc1740#appendix-B)의AppleDoublemagic과일치한다.

**실제리플레이시작파일은56개다.** 이전숫자는경로기준후보개수였으며,플레이어514행에도이잘못된입력의영향이포함돼있다. 새audit는이메타데이터를긍정식별해제외한다. 이전‘모든파일이오류없이디코딩됐다’는사실만으로입력유효성이입증되지는않는다.

## 비교 참고 자료에서 얻은 것과 배제한 것

### HackedGlory는 VGNA 서버 파서의 정답이 아니다

조회한HackedGlory HEAD는`0fdc6ddd65a6c0c8657d238d41668baa86debdf0`(2026-04-21)로 기존비교문서의고정SHA와같다. 이번확인에서새서버파서소스를확보했다고주장하지않는다.

[프로토콜보고서](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/mitm/match_decryption/protocol_decryption_writeup.md)는네트워크패킷의2바이트길이와복호화된2바이트opcode를기록한다. 로컬VGR는그대로같은포맷이아니며4바이트시각+4바이트길이wrapper를쓴다. 본문opcode와필드의대응은개별적으로검증해야한다.

[디컴파일dispatcher의0x0431분기](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10012.c#L5645)는32비트값하나를읽어`FUN_1003c6194`로전달한다. [생성자](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003c.c#L5427)도그값하나를저장한다. 이자료는레코드본문에timestamp가없다는해석과맞지만,그동작을‘사망’으로확정하지는않는다.

### 직접 이식 전에 확인해야 할 불일치

[HackedGlory dashboard](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/mitm/match_decryption/vg_match_dashboard.py#L574)는opcode0x042B의index0/value3전이를사망후보로센다. 같은필드해석과연속중복제거를로컬세경기에적용했다.

| 대상 | index0→value3 전이 | 로컬0x0431후보 |
|---|---:|---:|
| M1 |600|16|
| M5 |755|17|
| M6 |1085|31|

0x0431후보총64건중이value3후보와±1초안에겹치는것도0건이다. 두 후보 규칙은 로컬 세 경기에서 수와 시각이 크게 불일치한다. 따라서 이 규칙을 검증 없이 채택할 근거는 없으며, 어느 신호가 실제 사망을 나타내는지는 독립 사건 증거로 확인해야 한다. VGNA서버가이규칙을사용한다거나,HackedGlory의자체네트워크캡처에서도동일한차이가관찰된다는주장은하지않는다.

반대로로컬`0x041C/subtype0x29/value1`후보와`0x041D/subtype0x09/value1`은M1/M5/M6에서각각15/16/31건이고,플레이어별발생시각이전부같았다. 별도의두신호가있는것은후속재구성의단서지만,같은원천을복제한메시지일수있어독립정답으로두번세지않는다.

### 최근 VGNA 자료에서 참고할 방향

공식[배포페이지](https://client.vgna.net/)와[변경기록JSON](https://client.vgna.net/changelog/releases.json)을직접조회했다. JSON에는2026-09-03의1.09.02가최신항목으로있었고,8월30일1.09에는terminal-scoreboard자동캡처와native respawn일정,stream READY/END기록을다루는내용이있었다. 이는다음실험의참고대상이며,그출력정확도를이번에검증했다는뜻은아니다. 특히스트림END와실제경기종료는같은의미인지검증해야한다.

최신VGNA서버의파서버전·소스와**우리와같은입력에대한중간레코드/결과쌍**은아직확보하지못했다. 사용자에게최근자료위치를질문해둔상태다. 기존7월문서의결과JSON을정답으로승격하지않는다.

## 이후의 역공학 순서

1. **이번에완료:** 원시프레이밍,오프셋,소유시각,opcode추출을검증하고재현도구로고정한다.
2. **다음실험:** `0x0431`, `0x041C/subtype0x29`, `0x041D`의subtype·flags·source/target을보존한타임라인을만든다. 현`CreditRecord`가버리는action정보와500바이트근접가정을재검토한다.
3. **의미판정:** 통제된단일사건(사망/부활/킬/미니언처치/아이템거래)의영상·게임화면또는native handler와대조한다. 상대파서와합계가같다는것만으로승격하지않는다.
4. **VGNA비교:** 입력파일hash·클라이언트빌드·모드·파서버전을맞춘다. 같은raw사건에서우리와VGNA의해석이갈리는사례를우선한다. 양쪽일치/양쪽불일치/한쪽만일치를분리한다.
5. **교체:** 입증된신호만기존통계파서로옮긴다. 지금발견한timestamp위치/30분상한도이기반에서회귀검증해수정하며,정답숫자에맞춰보정하지않는다.

## 구현과 검증

구현커밋:`01273ee3f5a1bf3c83784fcf5e8f7dffee2897ec`.

- 신규14개테스트통과,전체235개unittest통과.
- 실제CLI재실행:실파일7,870개,시작56개,메타데이터5개제외,레코드30,729,156개,소비바이트1,044,589,605,오류0.
- 인수누락/없는경로/빈디렉터리의실제CLI는모두exit2와진단문구를반환했다.
- 기존파서·통계코드는수정하지않았다. 소스확인과프레이밍성공을수치정확도개선으로보고하지않는다.

```sh
python -m vg.analysis.record_framing_audit "D:/Desktop/My Folder/Game/VG/vg replay"
python -m unittest tests.test_vgr_records tests.test_record_framing_audit
```
