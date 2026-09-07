# Replay startup clock investigation — 2026-09-08

## Result

The two `unsupported_clock` inputs remain withheld. The investigation found a
native reason that a recording cannot be treated as a complete history of game
clock assignments: the writer deliberately drops clock-resynchronization
message `0451`. This establishes an observability limit, not proof that a
resynchronization caused either captured discontinuity. No timestamps or
production acceptance rules were changed.

This follows [native scoreboard integration](NATIVE_STATS_INTEGRATION_2026-09-07.md).

## Actual input evidence

The relevant recording identifiers are the second UUID in each filename.

| Recording | Section transition | Record delta | Game-clock delta | Excess game delta |
|---|---|---:|---:|---:|
| `172f190f-db00-4091-b138-585854372063` | 0 → 1 | 10.015263 | 16.730141 | 6.714878 |
| `d9cbb04f-85e7-4471-baff-88cfae0c03ae` | 0 → 1 | 10.006122 | 21.140392 | 11.134271 |
| `d9cbb04f-85e7-4471-baff-88cfae0c03ae` | 1 → 2 | 9.996022 | 11.840115 | 1.844092 |

Both first sections have their first nonzero record time at exactly 2 seconds.
That is compatible with the native delta cap described below; it does not tell
us the original wall-clock delay or locate any live correction. The second
input must not be modeled as just one constant startup offset: its next
interval also differs appreciably.

The reproducible [startup audit](evidence/2026-09-08-clock-startup/startup-audit.json)
read the first 3 sections of all 56 real replay starts, excluding 4 AppleDouble
metadata starts. Across 168 sections:

- No `0451` record was present.
- The individually decoded end-state of a section agreed with the next
  section's initial player snapshot for all 1,004 comparable actor checkpoints
  (four counters per actor). No changed checkpoint actor was found.
- This is internal state continuity, not screenshot accuracy, complete event
  coverage, or correct sub-section game-time mapping. In particular, checking
  only M9's first three sections does not detect its later mixed segments.

The [archive audit](evidence/2026-09-08-clock-startup/archive-evidence.json) searched
41 ZIPs under the known corpus root. For `172f…`, all 150 current sections match
the corresponding original ZIP members byte for byte by SHA-256. For `d9c…`,
117 loose sections were found, with no matching member in those ZIPs and no
alternate loose copy in that bounded search. Its archive integrity therefore
could not be checked. In both inputs the first three sections retain identical
actor-to-hero-signature/team mappings; names and raw player blocks are omitted
from the published [identity evidence](evidence/2026-09-08-clock-startup/identity-evidence.json).

## Native evidence

The analyzed signed-APK ARM64 engine has SHA-256
`cd1b8831f82c469274613fc30f1f1f6e78c788102cdad7db5db2c04b96580a47`.
Its identity is documented in the [APK comparison](OFFICIAL_APK_COMPARISON_2026-09-07.md).
The following paths are static observations of that binary; the exact client
build that produced each replay and live execution of these captures were not
established.

1. **Different stores and origins.** Snapshot builder `0x823528` calls game-clock
   getter `0x8bc268`, which reads object `+0x2bc`, then writes the float at
   `046f` payload offset 64. The record writer instead reads global `0x2b7bf10`.
   Recording startup resets that global to zero; writing `046f` enables its tick.
2. **An omitted game-clock setter.** `0451` dispatches through `0x82d490` and
   `0x82b300` to `0x8bd5c0`, assigning the same game-clock field. The writer's
   mask `0x1b140800070d` excludes `0451` (bit 0) but retains `046f` (bit 30).
   Consequently, absence of `0451` from a replay cannot rule out a live correction.
3. **A shared two-second cap, not a complete explanation.** At `0x18882ac`–
   `0x18882b8`, timer delta becomes `min(raw_delta, 2.0) * scale`. The traced
   caller passes the same capped delta to both the recording tick and the local
   game update. The latter has additional scale/pause behavior and can be
   independently assigned by messages. The hypothesis that only recording time
   is capped while local game time is uncapped is refuted for this path.

Selected disassembly and [exact byte ranges](evidence/2026-09-08-clock-startup/native-manifest.json)
accompany this document. The supplied byte verifier passed all 19 ranges against
the actual ELF. This checks artifact identity and bytes, not native runtime
execution or every semantic inference in the disassembly.

## Reproduction

From the repository root, with the same corpus available:

```bash
PYTHONPATH=. python vg/docs/evidence/2026-09-08-clock-startup/audit_startup.py \
  /path/to/replay-root --sections 3 > startup-audit.json
python vg/docs/evidence/2026-09-08-clock-startup/native-verify.py \
  /path/to/libGameKindred-arm64.so
```

The startup audit is read-only and prints diagnostic JSON. It neither repairs
files nor promotes single-section results into accepted whole-match values.
Its actual 56-replay execution reproduced the counts above. Help and invalid
root/section arguments were also checked. The native verifier additionally
rejects an unrelated input file.

## What remains necessary for a correction

A constant shift, stretching the first section, or ignoring the first clock
jump would select one unproved timeline. Stable later checkpoints do not
identify the clock values between earlier messages. Keep the existing
`unsupported_clock` result for both inputs; M9 remains `mixed_segments`.

The next decisive experiment is a controlled recording on an identified client
build that observes incoming `0451`, `046f` creation, both clock variables,
raw/capped delta, and scale/pause state around startup. This would distinguish
live resynchronization, activation order, and time scaling. The current stored
files alone have not established which mechanism occurred in these two games.
