# Windows replay failure: normal injection and offline crash-dump analysis

## Result

A freshly recorded practice replay was copied with the existing `vgrplay.exe`
into a different practice slot. All 15 frame hashes matched and the client
played the substituted recording. The injection procedure works on this build.

The original 150-frame recording ending `172f190f-db00-4091-b138-585854372063`
reached replay initialization, applied its first snapshot and native game clock
`81.5726624`, then failed in a **background texture-spec preparation task**.
Two existing Crashpad dumps identify the same assertion: a Buffer input record
exists, but its payload pointer is null. This is a concrete client resource-task
failure; it does not establish that the replay file is corrupt or explain its
original clock discontinuities.

The particular texture and the reason its data was absent remain unknown.
`unsupported_clock` and all decoder acceptance rules remain unchanged. The
other original unsupported recording was not retested in this follow-up.

## Controlled playback and file checks

The source practice recording contained 15 frames. Its unmodified replay opened
successfully. It was then substituted into a different practice slot, whose 11
original frames had first been backed up. The replay HUD showed the source
recording, and after a user-interface seek near the end it reached the result
screen at `2:26`. This is a playback/seek control, not an uninterrupted end-to-end
timing benchmark. The destination's original 11 frames were restored and hashed.

All 150 target frames matched the source after substitution. A complete
read-only envelope scan found 596,332 records with no framing errors; largest
message size was 1,616 bytes. The normal source contained 24,604 records and
had the same largest message size. This checks framing, not every packet's
semantic validity.

Both first-frame `046f` snapshots have 71-byte messages, a NUL-terminated mode
identifier within the 64-byte field, a finite clock, and trailing flag 1.
First-frame outer timestamps are ordered. Modes differ (`5v5_Practice` versus
`5v5_Ranked`); that difference alone is not a rejection condition.

The observed upstream workflow is documented in
[vgrplay's README](https://github.com/rbxb/vaingloryreplay/blob/1cd1f62b194dd3335c810c2736944b8d3dee398a/vaingloryreplay/README.md):
practice, surrender, replace files on the result screen, then select Replay.
The upstream program copies frame contents under the active slot name; it does
not convert protocol versions or correct clocks.

## Runtime boundary and offline confirmation

The exact PE32 executable remains SHA-256
`659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`.
Preferred image base is `0x00400000`; RVAs are independent of ASLR.

An initial broad trace observed the target snapshot but ended before it could
classify process termination. A narrower trace omitted high-frequency reader
and dispatcher hooks. It recorded successful snapshot return, then an access
violation 3.0145 seconds later at RVA `0x572352`, followed by process termination
before the 180-second observation deadline. Its exception observer returned
false, preserving normal exception handling. Runtime instrumentation may affect
execution; no corresponding uninstrumented target crash stack was collected.

A later attempt returned to the menu with no replay initialization event. It
must not be conflated with the captured texture failure. The final prepared
attempt was not replayed after the user requested a different investigation
method. No further hooks or client runs were used for the offline analysis.

The default Crashpad location was recovered from the executable as
`%APPDATA%\SEMC\Vainglory\CrashpadDb`. Two existing dumps correlated with the
owned target runs by process ID, file modification time, exception RVA and PE
module timestamp. The exception context was read from the exception stream,
not the crash handler's later thread context. Both dumps independently show:

- exception `0xc0000005`, read address zero, EAX zero, PC RVA `0x572352`;
- first saved return RVA `0xd3bd98`, identifying the fatal call at VA `0x0113bd93`;
- a task input record keyed `0x815f1c7b`, with captured payload field `+0xc` equal
  to zero, and no second input record;
- the input's RTTI type `Nuo::Concurrency::TaskData<Nuo::Base::Buffer>`.

The caller prepares `TaskData<Nuo::Shading::TextureSpec>`. Its second assertion
checks that Buffer payload and passes static text `Inconsistency` to the common
fatal helper. The helper deliberately dereferences a global null pointer. Thus
this PC is the engine's failure boundary, not an accidental player-structure
read or the replay reader's EOF branch.

The task descriptor was not available in captured memory. No exact texture
filename can be recovered through this verified stack/record chain. Missing
resources, incompatible content and a failed earlier dependency remain possible
causes; none is established individually.

## Installed-file integrity

A read-only check compared the installed tree with its cached Steam depot
manifest `1025581_7750352696555066549`, associated with installed build `4774194`:

- 48,236 nonempty files matched both size and SHA-1;
- six empty files matched entries explicitly declared empty;
- 258 directories existed;
- 3,532,716,015 file bytes verified; no missing or mismatched entries;
- elapsed time: 71.13 seconds; no Steam repair, download or update performed.

The cached manifest's file mapping fields follow the
[ContentManifestPayload schema](https://github.com/SteamDatabase/Protobufs/blob/master/steam/content_manifest.proto).
This rules out differing installed bytes relative to that local manifest. It
neither proves that this is the latest build nor that its resources support
every object/cosmetic referenced by an external replay. An installation repair
is not supported as the remedy by the current comparison.

## Evidence and cleanup

[Machine-readable results](evidence/2026-09-08-windows-replay-failure/results.json)
include normalized dump findings, the narrow trace excerpt, framing results and
installed-file verification. [Native fault evidence](evidence/2026-09-08-windows-replay-failure/native-fault.txt)
records the instruction/RTTI chain. Raw dumps, player-containing screenshots,
replay files, executable, Steam manifest and full memory data remain private.

Every substituted slot was restored and hash-verified. The experiment game,
observers and interactive scheduled tasks are stopped or removed. The desktop
helper's 60-minute lifetime expired while leaving its game alive; cleanup then
explicitly stopped that owned game process. Steam was left open. Original
replay corpus, installed client bytes and unrelated repository edits were not
modified. Display/sleep settings from the separate user request were preserved.

This advances the [earlier Windows experiment](WINDOWS_CLOCK_RUNTIME_2026-09-08.md)
from an unexplained replay-entry failure to a specific texture-task assertion.
The remaining question is which resource/dependency produced the null Buffer,
separate from the original recording-clock investigation.
