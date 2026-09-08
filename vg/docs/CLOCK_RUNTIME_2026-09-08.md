# Android startup clock runtime experiment — 2026-09-08

## Outcome

The exact analyzed Android APK was installed and instrumented in a dedicated
ARM64 Android 35 emulator. All seven guarded native hook entries matched and
hooks installed successfully. **No game-clock, recording, timer, or `0451` event
was captured.** The initially missing OBB was subsequently copied from the user's matching
147219 installation and installed in the emulator. Rendering then failed in
`EGLImpl._eglCreateContext`, including an uninstrumented launch. The startup clock anomaly in the original two replays remains
unexplained; their `unsupported_clock` status is unchanged.

This advances [the static clock investigation](CLOCK_STARTUP_2026-09-08.md) to
actual process attachment and guard/teardown testing. It does not establish
that the in-game callbacks produce correct measurements once gameplay begins.

## Identified environment

- Dedicated `VG_Clock_API35` emulator, Android API 35, ARM64 Google APIs image.
  Existing personal/project emulators were not used for this test.
- Installed package `com.superevilmegacorp.game`, version 4.13.4 (147219),
  target SDK 30. The APK's SHA-256 on the device matched the source archive:
  `e82a6beed517db32536cd0f85a703d84dda84e1d184c990728dfb7c87d561d2d`.
- Corresponding ELF SHA-256:
  `cd1b8831f82c469274613fc30f1f1f6e78c788102cdad7db5db2c04b96580a47`.
  Prior signature/provenance evidence is in the
  [APK comparison](OFFICIAL_APK_COMPARISON_2026-09-07.md).
- Frida host and ARM64 server version 17.17.0, installed in an isolated test
  environment. The server listened on device loopback through ADB transport.
- Windows also had a Vainglory executable, but it was PE32/x86 with SHA-256
  `659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`.
  No verified Windows clock offsets were available, so Android addresses were
  not applied to that build.

## Reusable probe

The [probe directory](../tools/clock_probe/README.md) contains a Python runner,
a Frida script, the seven entry-byte guards, and pinned dependencies. It:

- verifies the host ELF hash and all runtime entry bytes before hooking;
- refuses an already running package;
- observes scalar clock/timer values without changing arguments, return values,
  or game state; instrumentation itself uses transient interception patches;
- stops only the new test process it created, then detaches;
- distinguishes hook installation, sufficient clock events, and confirmed
  teardown. No summary automatically asserts the original cause is known.

The collector targets a controlled startup test, not an ongoing match. It must
be used with a compatible complete installation. The installed image identity
must be checked independently: matching seven code prefixes is not a whole-file
hash of the running module.

## Actual execution and a discovered cleanup defect

The first 45-second run installed seven hooks but stayed in initial setup. Its
summary correctly said `boot_only_or_insufficient_clock_evidence`.

After permission setup, the app entered `NuoActivityInstallAssets` and closed its
activities. Storage permissions were granted, but its OBB directory did not
exist. The known Windows VG data/repository search found no loose APK/XAPK/OBB;
42 archives contained no OBB. This is a bounded search, not proof that the user
has no copy elsewhere. A browser attempt to inspect APKPure was blocked by the
browser's site-safety policy and was not worked around.

The next attempt exposed a real collector bug: Android froze the background
process, and synchronous script cleanup waited indefinitely. A run requested
for 15 seconds returned only after the test controller stopped the process,
at 141.701 seconds. Android logged `freezing` for that same process. Replacing
RPC cleanup with a bounded detach limited the wait to 23.192 seconds but did
not confirm hook removal from the frozen process.

The final lifecycle stops the collector-owned process before detaching, with
bounded device operations. The same scenario then finished in **15.710 seconds**
with `cleanup_confirmed: true`, `spawn_terminated: true`, and no probe errors.
This verifies the cleanup correction; it does not verify gameplay timing.

Additional actual-device checks:

- Alter one expected entry byte: `rejected_bytes`, zero hooks, nonzero exit;
  the spawned test process is stopped during cleanup.
- Start the package before invoking the probe: nonzero exit, no hooks, and the
  pre-existing PID remains unchanged.
- CLI help works; nonfinite/out-of-range observation durations are rejected.

Machine-readable summaries are in
[evidence](evidence/2026-09-08-clock-runtime/runtime-results.json). Only scalar
probe logs and summarized environment facts are published; APK, emulator disk,
full device logs, and generated identifiers are not redistributed.

## OBB follow-up and remaining runtime blocker

The connected phone had version 4.13.4 (147219). Its matching
`main.147219.com.superevilmegacorp.game.obb` was copied read-only and installed
in the isolated emulator (1,394,159,471 bytes; SHA-256
`bcbe9aff2f161e59eb7f75ab57a124e35ee46ae708b5c933d74e912cba0478fb`).
The phone installation was not modified. OBB/APK data is retained locally and
is not included in the source package.

With OBB present, startup-05 reached asset installation but crashed in
`NuoView$b.createContext` (NuoView.java:279), through
`EGLImpl._eglCreateContext`, with `IllegalArgumentException`. Switching the
isolated emulator to SwiftShader did not resolve this: startup-06 spent its
observation interval in setup dialogs; startup-07 crashed after those dialogs.
All three runs installed seven hooks but captured no clock events.

A separate launch via Android's launcher, without attaching Frida, reproduced
the same GLThread exception. This establishes that the crash also occurs
without the collector; it does not prove the exact EGL configuration defect.
The APK's DEX shows a standard OpenGL ES 2 context attribute list and a custom
configuration selector that may return null when exact color/depth/stencil
criteria do not match. A null result is a hypothesis, not a measured result.

The remaining prerequisite is a compatible environment that reaches gameplay
and permits observation of the unmodified native module. No rendering or clock
return values were patched to bypass the failure. The replay clock jump and a
correction formula remain unconfirmed; `unsupported_clock` is unchanged.

The owned emulator and its instrumentation server were stopped after these
checks. The ADB daemon was left running; the final device list was empty (the phone
was no longer listed). SSH access to the Windows checkout was subsequently restored, allowing
the updated source package and summarized evidence to be synchronized.

Frida API references: [Android setup](https://frida.re/docs/android/) and
[JavaScript API](https://frida.re/docs/javascript-api/).
