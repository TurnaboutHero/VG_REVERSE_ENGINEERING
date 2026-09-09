# Recorded death-counter gap audit

`vg.analysis.terminal_counter_audit` compares player `0430` death actions with
recorded `041c` death-counter ADD 1 operations. It preserves unmatched and
ambiguous observations for investigation. It does not change scoreboard
extraction, completion policy, winner selection or final statistics.

## CLI and library

```text
python -m vg.analysis.terminal_counter_audit replay.0.vgr \
  --player 1500 --player 1501 --window-seconds 0.1
```

Repeat `--player ID` for all player IDs established independently for this
recording. These are caller assertions, not identity discovery. IDs accept
decimal or `0x` notation and exclude the `FFFFFFFF` sentinel. The CLI reads
matching numbered sections in numeric order, emits one JSON document to stdout
and does not open an output file. Invalid arguments, unreadable inputs and
malformed record framing exit with code 2 before emitting a report.

```python
from vg.analysis.terminal_counter_audit import audit_counter_gaps

report = audit_counter_gaps(
    frames=[(0, section_zero_bytes), (1, section_one_bytes)],
    player_ids=[1500, 1501],
    window_seconds=0.1,
)
```

Library frame numbers must be unique, nonnegative and already in numeric order.
The window must be finite and nonnegative. Strict `iter_records` validation is
applied to every section. `sections` records section numbers, byte counts,
record counts and SHA-256 hashes without publishing source paths.

The decoder reuses the currently established layouts in `native_event_fields`
for `041c`, `041d`, `0430`, `0431` and `03f1`. Layout evidence identifiers in
decoded rows do not authenticate the executable that originally wrote an input
recording. The audit neither supplies nor infers that build provenance.

## Matching rules

Only caller-selected player victims are considered. A candidate increment must
be `041c`, attribute index 42, layer 0, operation `add`, value exactly 1, and
refer to the same entity as the death action.

1. First construct edges for equal outer-record timestamps. This phase is
   order-independent: the increment can precede the action in record order.
2. Pair only edges whose action and increment each have exactly one candidate.
   Preserve all ambiguous endpoints and edges; do not consume them greedily.
3. For endpoints with no exact candidate, repeat the same uniqueness rule using
   an increment later in record order with a positive timestamp difference no
   greater than `window_seconds`. Exact-phase ambiguities are not reconsidered.
4. Residual actions with no candidate become `cases`. Residual increments and
   ambiguous observations remain separately available.

The window is an explicit matching heuristic, not proof that the action caused
the increment. Every locator has global zero-based `seq`, section `frame`, byte
`offset`, outer-record `timestamp` and `opcode`. Pairs report their method and
timestamp difference. Record order is never replaced by timestamp sorting.

`clock` preserves the complete result of `inspect_native_clock`. Missing anchors,
mixed segments and other invalid clock statuses remain invalid even when
records can be framed and compared. Producing a report or a window match does
not promote its clock status or establish a game-time equivalence.

## Reading a case

Each case includes the latest prior player KDA/CS operation, counts of later
player operations, later victim snapshots, all later victim stat-operation
counts, later victim `0431` observations, the next `048d` and `03f1`, and EOF.
All comparisons use `seq`, so later records at the same timestamp are retained.

Operation summaries include SET and ADD. The player KDA/CS group comprises
`041c` indices 41/42 in every observed layer and `041d` indices 11/14. Here
“CS” follows the existing API's resource-14/minion-kills label; this audit does
not independently establish that field's native display meaning. Victim stat
summaries cover every decoded `041c`/`041d` index, layer and operation. Resource
operations have no decoded layer and report `layer: null`.

Snapshots remain separate from operations. Supported `03f3` payload lengths
are 746 and 750 bytes; the actor ID is at payload offset 8, death value at 302
and layer at 326. `last_player_kda_cs_operation` and `last_player_snapshot` are
distinct recording-level anchors. A snapshot assignment is not an ADD event.

`pre_layer0_deaths` and `eof_layer0_deaths` describe only the observed layer-zero
death array. A valid layer-zero snapshot or SET supplies an assignment; ADD
requires a known value. Missing baselines are not invented as zero. Unsupported
values, uncertain stat payloads and unproved negative clamp behavior can make
the observation unknown. Nonzero attribute layers are retained and explicitly
flagged instead of being interpreted as final scoreboard state.

Malformed known layouts and unsupported semantic values appear in
`unsupported_semantics`. Case-level counts of later unsupported observations
make an apparent absence of decoded updates distinguishable from unsupported
data. Nonfinite values are represented as null with available raw bits; JSON
serialization rejects nonfinite numeric literals.

`048d` is an opaque positional anchor with payload length. Its position is not
a decoded final-KDA cutoff. `03f1` retains the existing end-match action fields;
the recorded request does not prove match completion or result-screen timing.
No field in this report upgrades a recorded counter observation to a final
score, a credited kill, or proof that an unmatched action should be counted.

## Fresh original-corpus audit on 2026-09-09

This run independently rediscovered candidate gaps from all 56 original
recordings, rather than selecting the old 39 actions as scanner input. It read
7,870 sections and 30,729,156 strict-framed records. Player IDs came from the
existing parser with `auto_truth=False`; they were converted to the native
big-endian ID convention and passed explicitly to this audit. C01..C56 preserve
the earlier corpus manifest's array order; they are not the truth-set M numbers.

| Observation | Count |
|---|---:|
| Selected-player ActorDie actions | 2,221 |
| Selected-player layer-0 death ADD 1 operations | 2,182 |
| Unique equal-timestamp pairs | 2,157 |
| Additional unique forward pairs within 100 ms | 25 |
| Unpaired actions | 39 in 28 recordings |
| Unpaired increments / ambiguous endpoints / unsupported tracked semantics | 0 / 0 / 0 |

The 39 action section/offset locations exactly match the previous independently
stored cohort. All 4,139 section hashes in its existing 28-recording provenance
also match. Every newly read section was hashed before analysis and re-read
afterward; all input hashes were unchanged. Clock status remains 53 accepted,
two unsupported clocks and one mixed recording. All 28 affected recordings have
accepted clock status; the audit does not promote the other three.

Every gap action precedes `048d` by 0.109497..5.803589 record-time seconds and
precedes `03f1` by 0.119019..5.812500 seconds. All have end-reason byte 0; this
does not independently prove a crystal-destruction ending. In all 55 recordings
with terminal messages, `048d` immediately precedes `03f1`: 37 pairs share a
timestamp and 18 differ by about 8..26 ms. The other recording has neither.
Moving a candidate cutoff from `03f1` to `048d` cannot remove these 39 actions:
they are already before both messages.

After each of the 39 actions, no further selected-player K/D/A/resource-14
operation appears, including SET or nonzero attribute layers. No subsequent
tracked semantic error hides an undecoded operation. All 39 victims retain the
same known layer-zero death value through EOF. Eleven later victim snapshots
explicitly repeat that value. Other victim stat operations continue in all
39 cases, and a later `0431` occurs in 27 cases. This is selective recorded
score stasis, not absence of all subsequent data or proof of its producer.

The last selected-player score operation is 6.000..38.180 seconds before `048d`
in the 28 affected recordings (median 10.594). Among 26 unaffected recordings
with such an operation it is 3.044..21.647 seconds earlier (median 11.161); one
additional unaffected recording with terminal messages has no such operation.
These overlapping distributions do not locate a universal freeze time:
ordinary periods without a score-changing action also separate a last update
from an end message.

The [anonymized evidence JSON](evidence/2026-09-09-terminal-counter-audit.json)
contains all 39 action locators, snapshot observations, per-recording counts,
clock statuses and report hashes. Original paths, names and replay bytes are
not included. Private reproducibility artifacts are the owned Windows
worktree's `work/terminal-gap-20260909/run_corpus.py`, `corpus-report.json`,
`C01.json` through `C56.json`, `corpus-run.log` and `cli-proof.json`.

The Windows full suite passed 388 tests in 46.977 seconds. The actual C01 CLI
report equaled its library report; `--help` succeeded, and negative-window and
malformed-framing inputs returned exit 2. Twelve new boundary tests cover the
matching rules, ambiguity, invalid clocks, unsupported values and later
same-time observations. The temporary private test-fixture copy was removed
afterward; original fixtures and tracked caches were preserved. LSP was not
available and was not installed.

The next discriminating offline work is to examine earlier native state/action
signals around the last score update and first unmatched death, with unaffected
recordings as controls. Server production, callback effects and independently
displayed final KDA remain unverified. No final-counter correction or completion
cutoff follows from this diagnostic.
