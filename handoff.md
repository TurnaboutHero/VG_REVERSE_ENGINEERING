# Vainglory Replay Handoff

Date: 2026-03-29
Workspace: `D:\Documents\GitHub\VG_REVERSE_ENGINEERING`

## Environment

- Game window mode: windowed maximized, not fullscreen.
- Display basis: `DISPLAY1` primary, virtual region `(0,0)-(3072,1920)`.
- Temp replay path: `C:\Users\khh56\AppData\Local\Temp`
- Vainglory process:
  - exe: `D:\SteamLibrary\steamapps\common\Vainglory\Vainglory.exe`
  - pid seen during run: `50888`
  - start time seen: `2026-03-29 오전 1:23:06`

## Target Replay

- Source folder: `D:\Desktop\My Folder\Game\VG\vg replay\21.11.17\리플`
- Replay name for `vgrplay`:
  - `0f66f336-3e1c-11eb-ad3d-02ea73c392db-28c9273d-f413-4d68-898c-5388383873f5`

## Confirmed Findings

- Guest/practice flow works without account login.
- The bottom-right `Tb` button opens the scoreboard overlay without holding `Tab`.
- `Tab` key automation attempts did not reliably open/hold the scoreboard in this setup.
- `vgrplay.exe` was used, not manual file copy.
- `vgrplay` overwrite succeeded against the live temp replay session name.
- A too-low click on the surrender area can miss.
- User correction:
  - after surrender is accepted, if the mouse is not moved, the `다시보기` button should be the replay entry point.
- Replay load was confirmed end-to-end in a later attempt:
  - surrendered practice match
  - overwrote active temp replay with `vgrplay`
  - entered replay successfully and saw real target replay HUD/player panels
- Replay menu was confirmed from the bottom-center control area.

## Exact UI Coordinates

All coordinates below are in primary-display virtual desktop coordinates on the maximized window.

### Main Menu

- `플레이` button:
  - click worked at `2730,1668`

### Mode Select

- `연습` tile:
  - click worked at `2453,836`

### Hero Select

- Confirm hero:
  - `선택` button worked at `1535,1793`
- Note:
  - double-click on hero or using the confirm button should both be viable per user note

### Talent Select

- First talent card click that worked:
  - `238,927`
- Talent confirm button:
  - `2863,1269`
- Note:
  - double-clicking the desired choice may also be enough

### Build Select

- Build card click that worked:
  - `674,804`
- Build confirm button:
  - `2863,1269`
- Note:
  - double-clicking the desired build may also be enough

### In-Match

- Focus click used before UI actions:
  - `1560,980`

- Bottom-right scoreboard button (`Tb` icon):
  - click worked at `2848,1768`

### Scoreboard / Surrender Overlay

- First surrender button:
  - good click: `185,1092`
  - low/marginal clicks that were unreliable:
    - `189,1130`
    - `166,1130`

- When surrender progressed to the next overlay, the title area showed red `항복` and these buttons appeared:
  - left: `다시보기`
  - center-left: `평가`
  - right: `게임플레이`
  - far-right: `닫기`

- Important:
  - one click path returned to home after this overlay
  - based on user correction, the intended button here is `다시보기`
  - likely safest next attempt is:
    1. `Tb` at `2848,1768`
    2. `항복` at `185,1092`
    3. inject replay with `vgrplay`
    4. click the left `다시보기` button without extra mouse movement

### Replay-Loaded State

- Replay successfully loaded to target players/teams.
- One confirmed loaded frame showed:
  - blue side names like `8815_DIOR`, `8815_Sui`, `8815_nok`, `8815_mumu`, `8815_Bro`
  - orange side names like `8815_korea`, `8815_LeeJiEun`, `8815_zm`, `8815_rui`, `8815_lamy_KR`
- This confirms the overwrite target replay was actually being rendered, not the throwaway practice match.

### Replay Controls

- Bottom-center replay control/menu button:
  - click worked at `1536,1776`
- After opening that menu:
  - a replay timeline/control strip appears
  - visible play/pause button near lower center
  - visible `다시보기 종료` button at lower right
  - visible time readout such as `1:47 / 19:06`
- Clicking the same bottom-center area again resumed playback successfully.
- Attempts to drag or jump the time bar were inconclusive in this run.
- User guidance:
  - bottom-center button opens a menu
  - that menu contains a bar for moving time
  - game should automatically show the result screen when replay reaches the end

## vgrplay Usage

Help confirmed:

```powershell
& 'D:\Desktop\My Folder\Game\VG\vg replay\vaingloryreplay-master\windows_amd64\vgrplay.exe' -h
```

Actual overwrite flow used:

```powershell
$temp = $env:TEMP
$latest = Get-ChildItem -Path $temp -Filter '*.vgr' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$oname = ($latest.BaseName -replace '\.\d+$','')
& 'D:\Desktop\My Folder\Game\VG\vg replay\vaingloryreplay-master\windows_amd64\vgrplay.exe' `
  -source 'D:\Desktop\My Folder\Game\VG\vg replay\21.11.17\리플' `
  -sname '0f66f336-3e1c-11eb-ad3d-02ea73c392db-28c9273d-f413-4d68-898c-5388383873f5' `
  -overwrite $temp `
  -oname $oname
```

Resolved live temp replay base name during the successful overwrite attempt:

- `a8d06624-352e-4897-b920-2cdbafdb48ab-9c279291-89e0-45ff-a36c-bb5c509be2a9`

Resolved live temp replay base name during the later successful replay-load attempt:

- `a8d06624-352e-4897-b920-2cdbafdb48ab-34d568ca-0c58-458f-871e-44f53d374c14`

Observed result after overwrite:

- temp replay files for that live session were updated through `.114.vgr`
- top visible modified time after overwrite: `2026-03-29 오전 1:50:20`

Observed result after later overwrite:

- temp replay files for the later live session were updated through `.114.vgr`
- top visible modified time after overwrite: `2026-03-29 오전 2:08:21`

## Interpreting the Previous Failure

- This did not look like a long idle timeout.
- More likely sequence:
  - surrender overlay opened
  - replay files were overwritten successfully by `vgrplay`
  - wrong follow-up button/click path returned the client to home

## Recommended Next Attempt

1. Start from home.
2. `플레이` at `2730,1668`
3. `연습` at `2453,836`
4. Hero select: choose or double-click hero, otherwise `선택` at `1535,1793`
5. Talent select: choose tile, then `선택` at `2863,1269`
6. Build select: choose tile, then `선택` at `2863,1269`
7. Once in match, open scoreboard using `Tb` at `2848,1768`
8. Click `항복` at `185,1092`
9. Immediately run the `vgrplay` overwrite command above
10. Click the left `다시보기` button on the post-surrender overlay
11. Once replay loads, open replay controls with `1536,1776`
12. Prefer time-bar jump if it can be made reliable; otherwise let replay auto-run to result
13. Capture result/truth screenshots

## Open Question

- ~~Exact safe coordinate for the post-surrender `다시보기` button~~ RESOLVED 2026-07-17: `190,1075` (see below)
- Exact reliable timeline-jump coordinate/drag behavior is still unresolved — but 5x playback speed makes it unnecessary for most cases.
- Replay menu and replay playback itself are confirmed working.

## 2026-07-17 Automation Run (fully automated via vg/tools/desktop_auto.py)

End-to-end loop executed without manual input: launch → practice match → surrender →
vgrplay inject → 다시보기 → replay loaded → 5x playback. Tool: `python -m vg.tools.desktop_auto`
(ctypes SendInput + capture; declares DPI awareness so all coordinates below are physical
3072x1920 pixels, same basis as the rest of this file).

### Launch (changed from direct exe)

- Direct `Vainglory.exe` launch shows `연결할 수 없습니다` and a Steam login handoff — dead end.
- Working path: `Start-Process 'steam://rungameid/1025580'` (app id from appmanifest_1025580.acf).
- Steam launches a small VG launcher window; its red `플레이` button opens the mode-select
  overlay in the same window. Maximize the window first (title bar buttons, standard Win32).
- Game window starts SMALL — maximize before using any coordinates in this file.

### New step: skin picker

- After hero confirm (`선택` 1535,1793) a skin popup appears; `기본 스킨` card at `1535,200`.

### Post-surrender overlay button coordinates (maximized, physical px)

- `다시보기`: `190,1075`  ← the replay entry point
- `평가`: `558,1075`
- `게임플레이`: `2515,1075`
- `닫기`: `2880,1075`

### Replay controls (opened via bottom-center `1536,1776`)

- Speed `−` button: `108,1779`; speed `+` button: `292,1779`; each click ±1x, **max 5x**.
  19-minute replay finishes in under 4 minutes of wall time at 5x.
- Pause/play: `1535,1779`. `다시보기 종료` button: `2894,1779`.
- Timeline bar: y≈`1710`, x spans ≈`84`(0:00) to `2995`(end); white dot = current position.
  **DO NOT click/seek the timeline** — see crash findings below.

### Crash findings (injected replays) — 5 runs, 2026-07-17

The client SELF-TERMINATES at a RANDOM point while playing an injected replay
(clean exit, no WER crash event). Observed survival (game-time at death):

| run | speed | last alive observation | died before |
|-----|-------|------------------------|-------------|
| 1   | 5x    | 7:04                   | ~19:06 (assumed end-crash at the time) |
| 2   | 1x    | 0:03 (+seek click)     | ~1 min |
| 3   | 5x    | 0:41                   | 17:46 |
| 4   | 1x    | (load only)            | 0:15 |
| 5   | 5x    | 5:46                   | ~6:30 |

- Randomness ⇒ NOT an end-of-file trigger, NOT a specific frame/event.
- Race-condition hypothesis REJECTED: after surrender the live session stops writing
  temp .vgr files (verified — no mtime updates during replay playback).
- Likely root cause: replay version mismatch — all archived replays are 2021-2022
  Community-Edition era; the Steam client is 4.12/4.13 (Feb 2020). No same-era replay
  exists in the archive to A/B test this.
- Timeline seek (run 2) still looks instantly fatal — keep seek forbidden.
- The always-on bottom HUD (per-player KDA/CS/gold) IS readable in every capture, so
  periodic-capture monitoring (`while tasklist | grep Vainglory: shot every ~10s`)
  extracts partial data from every run even when it dies.
- The Steam library window grabs foreground when the client dies; minimize Steam before
  the run so stray clicks land on the desktop, not Steam UI.
- Full-length playback needs ~19:06/5x ≈ 230s of survival; with observed survival times
  a single-run completion is unlikely — treat completion as a retry lottery, or solve
  the crash root cause first.
- Controls persist while the strip is open; time readout format `M:SS / M:SS` centered at
  ≈`837,1779`.
