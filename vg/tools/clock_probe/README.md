# Exact-build Android startup clock probe

This probe observes the analyzed ARM64 Vainglory engine in a controlled test
instance. It starts a new process and terminates that process at the end; it
refuses an already running package. It is not intended for an ongoing match.

The local ELF must have SHA256
`cd1b8831f82c469274613fc30f1f1f6e78c788102cdad7db5db2c04b96580a47`.
All seven hook-entry byte signatures are checked in the loaded ARM64 module
before any hook is installed. Runtime entry checks do not prove the entire
installed binary; independently verify the installed APK/engine identity.

Use a test Android device with the matching Frida server, accessible through
ADB, and the corresponding game data installed. Use Frida 17.17.0 for the
recorded reproduction. Keep the server local to the device/ADB transport.

```bash
python -m venv .venv-clock
.venv-clock/bin/python -m pip install -r requirements.txt
.venv-clock/bin/python clock_probe.py --device emulator-5580 \
  --elf /path/to/libGameKindred-arm64.so --seconds 45 --output startup.jsonl
```

The script, manifest, and runner must remain in the same directory. Output is
new-file-only. The observation window is 1–60 seconds; connection/setup and
bounded process/session cleanup add time. This does not promise a hard total
wall-clock deadline for every device operation.

Observed fields: record-clock global, native game-clock getter/setters,
`0451`/`046f` writer entry, and raw/capped/scaled timer delta. High-frequency
samples are throttled to 500 ms; raw delta above one second is also recorded.
No argument, return value, or game-state field is modified. Frida's temporary
interception patches are instrumentation; lifecycle ownership includes stopping
the spawned test process. No chat, identity, credentials, or full packet payload
is logged.

The summary distinguishes hooks installed from actual clock events. Even
`clock_events_observed_needs_analysis` never means the original replay anomaly
has been explained. Read errors, rejected bytes, or cleanup failure return
nonzero. `cleanup_confirmed` and `spawn_terminated` describe teardown separately.

A 2026-09-08 experiment installed the exact signed APK on a fresh ARM64 Android
35 emulator. Seven hooks loaded, but no game-clock or recording events were
observed: the asset-install activity exited and compatible OBB data was absent.
The original two `unsupported_clock` inputs remain withheld. See the associated
runtime evidence report for the exact validation results and limitations.

Frida APIs: https://frida.re/docs/javascript-api/ and
https://frida.re/docs/android/ .
