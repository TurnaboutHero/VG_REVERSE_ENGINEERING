# Windows replay and clock runtime experiment — 2026-09-08

## Outcome

The installed Windows client successfully played its own unmodified practice
recording through the final result screen. A read-only process-memory observer
captured separate game and recording clocks. This supplies a working runtime
measurement path after the Android emulator's EGL failure.

The two original `unsupported_clock` recordings were copied into controlled
practice slots with the existing `vgrplay.exe`, with every copied frame verified
by SHA-256. Neither injection attempt produced an observed target replay HUD;
the client was at the main menu afterward. Their original clock discontinuities
remain unexplained, and decoder acceptance rules are unchanged. This experiment
does not establish that a client-version mismatch caused the menu transitions.

## Identified client and observation method

- Windows PE32/x86 executable, preferred image base `0x00400000`.
- SHA-256 `659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`,
  checked on the installed executable and the analysis copy.
- Steam launch through app ID 1025580 in the logged-in interactive session.
  SSH itself ran in session 0 and could not operate the user's desktop.
- Ghidra 12.1.3 independently recovered Windows functions; no Android address
  was applied to this binary. The runtime observer found actual base `0xaa0000`.
- [windows_read_clocks.py](../tools/clock_probe/windows_read_clocks.py) uses
  `ReadProcessMemory`, with query/read access only. It never launches, stops,
  injects into, or writes memory in the target process.
- Before collecting, it checks the supplied executable's SHA, the loaded module
  path, and three function entry guards. The singleton getter's absolute address
  operand is adjusted for ASLR. These checks are not a full hash of loaded memory.

## Independently recovered clock paths

All VAs below refer to the preferred image base; use RVA plus loaded base.

| Role | Preferred VA / field | Evidence |
|---|---|---|
| Game singleton pointer slot | `0x02091c24` | Getter `0x00549e20` reads this 32-bit pointer |
| Game clock | dereferenced singleton `+0x194` | `0x00548870`: `FLD float [ECX+0x194]; RET` |
| Direct clock setter | `0x00549d20` | Dispatcher case `0x0451` calls this field assignment |
| Snapshot writer | `0x004cb030` | `0x046f` payload+64 contains that float in network order |
| Snapshot initialization | `0x00549470` | `0x046f` dispatch assigns the same game-clock field |
| Recording elapsed float | `0x01ef0b30` | Reset in `0x004cd980`, advanced in `0x004ce050` |
| Timer cap | `0x0112b9c8` | `MINSD` against binary64 2.0 before timer scale |

The record writer `0x004cb590` excludes `0x0451`. Therefore replaying an old file
cannot recover clock-setting packets omitted during its original recording.
The game clock advances through `0x005497a0` unless object byte `+0x19d` bit 0
is set. The published observer calls that value `clock_gate_bit`: correspondence
with the UI pause button has **not** been established by this experiment.

The HUD formatter uses the same clock getter. Selected byte/assembly evidence
is included in [native evidence](evidence/2026-09-08-windows-clock/native-evidence.txt).
The full local Ghidra project and decompilation outputs are retained privately.

## Controlled runtime results

1. The normal menu, practice selection, gameplay, and surrender/result UI worked.
   In the observed practice run, 2,984 samples included 2,105 non-null game-clock
   values. The recording clock ended at `115.0041809`; the game clock ended at
   `113.8756638`.
2. Without substituting any files in that control run, the Replay button opened
   the actual recorded practice scene. It reached its final result screen at
   displayed `1:53`. The replay observation collected 1,194 non-null samples;
   game clock progressed from `38.2182770` to `113.8811188`, while the recording
   accumulator remained at `115.0041809`. Sampling began after replay start,
   so this control does not establish exact startup callback ordering.
3. Recording `172f190f-db00-4091-b138-585854372063`: all 150 substituted frames
   matched their source hashes. The instrumented-read attempt transitioned from
   the old practice clock `113.0533905` to a null game singleton at elapsed
   `9.9546249` seconds, and the UI was at the menu. No target game clock was
   captured. An earlier uninstrumented attempt also ended at the menu.
4. Recording `d9cbb04f-85e7-4471-baff-88cfae0c03ae`: all 117 substituted frames
   matched. The UI was at the menu after the replay-entry attempt. All 1,194
   samples had a null game singleton, including the first sample before the
   intended click. Therefore this case does not isolate the exact transition
   trigger and must not be presented as a proven format/version rejection.

Machine-readable results are in [runtime-results.json](evidence/2026-09-08-windows-clock/runtime-results.json).
Screenshots and full scalar logs remain in the local experiment directory;
player names, original replay data, and executable binaries are not published.

## What the failed attempts do and do not show

The native file reader accepts the same timestamp/length envelope used by the
provided target frame 0. Both a fresh control frame 0 and target `172f…` frame 0
parse completely; neither contains trailing bytes or a truncated record. The
largest message is 752 bytes in both. No header magic/version rejection was
found in the bounded static follow-up. Mode, player state, assets, and later
packet semantics remain possible differences, without a confirmed rejecting edge.

Two early desktop-automation runs are excluded from client stability evidence:
the temporary helper terminated its owned game on exit. One helper was limited
to 20 minutes; another exited with task result 1. Its old error path could close
the game, so the original termination cause was not reliably logged. The helper
was revised to publish commands atomically, log failures, and leave the game
alive on helper failure. These closures are not evidence of a replay crash.

A final separate Frida diagnostic attempt was rejected by its snapshot entry
byte guard **before any of its eight hooks were installed**. That experimental
check did not handle relocations crossing the end of its 24-byte guard range.
The process later exited, but the cause was not captured. This attempt supplies
no callback/teardown evidence and is excluded from replay timing conclusions.
The Frida script is not part of the published read-only observer.

## Reproduction and cleanup

See [Windows observer usage](../tools/clock_probe/WINDOWS_README.md). Use a normal
practice replay as a control before substituting a corpus recording. Locate the
current Windows temporary directory instead of assuming the old handoff path;
it was `D:\DevCache\Temp` during this run.

Each replaced slot was backed up first. Earlier test slots were subsequently
removed by normal client cleanup. The final remaining slot was restored to its
17 original practice frames and hash-verified. Original corpus files were only
read. The game, observers, and temporary interactive scheduled tasks are stopped
or removed. Steam is left open. Existing unrelated repository changes are preserved.

A future decisive run needs a successfully initialized target replay and,
separately, controlled live clock-assignment observation if explaining original
recording behavior. The current runtime path is useful, but it does not justify
repairing either unsupported recording or assuming a constant clock offset.

## Follow-up: normal injection and offline crash dumps

The [subsequent controlled investigation](WINDOWS_REPLAY_FAILURE_2026-09-08.md)
verified playback after injecting a normal recording into a different slot.
For the 150-frame target, existing crash dumps identify a null Buffer input in
a background texture-spec task after snapshot initialization. Installed files
match their cached Steam depot manifest. The exact resource and the original
recording-clock anomaly remain unexplained.
