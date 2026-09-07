# Read-only Windows clock observer

This standalone standard-library Python tool observes one identified PE32/x86
Vainglory build. It does not launch the game or change its memory, arguments,
files, or lifetime. Android/Frida dependencies are not needed.

On Windows, launch the existing client normally through Steam, enter a controlled
practice/replay session, then run from the repository root (PowerShell):

```powershell
python vg/tools/clock_probe/windows_read_clocks.py `
  --pid <Vainglory-process-id> `
  --exe 'C:\path\to\Vainglory.exe' `
  --seconds 60 `
  --output 'C:\path\to\new-clock-observation.jsonl'
```

The executable must have SHA-256
`659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`.
The loaded module path must match `--exe`; the tool also validates three runtime
function entry byte sequences, including the ASLR-adjusted singleton pointer.
Unsupported builds fail before collecting any samples. A new output path is
required; existing files are never overwritten.

Observation is sampled about every 100 ms for 0–600 seconds (exclusive zero).
A null `game_clock` means the game singleton is absent, such as at the menu.
`record_clock` is the recording accumulator: it may remain fixed during playback
and is not the currently displayed replay time. `clock_gate_bit` reports a native
field bit; it is not a verified UI-pause status. Pointer lifetime changes can cause
a read error and nonzero exit. The tool closes its own handles and leaves the
client running, including on error or Ctrl-C.

`native_cause_confirmed: false` is intentional. The observer supplies measurements,
not an automatic explanation or correction of the original replay clock anomaly.

For external recordings, use the existing `vg.tools.vgrplay_inject`/`vgrplay.exe`
workflow after backing up the particular temporary replay slot and identifying
its exact name. Verify copied frames. Copy success is not playback success.

[Actual execution and limitations](../../docs/WINDOWS_CLOCK_RUNTIME_2026-09-08.md).
