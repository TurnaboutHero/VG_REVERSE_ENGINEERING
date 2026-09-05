# Terminal Completeness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop exporting uncertain full-match statistics as confirmed when only an activity tail supports completion.

**Architecture:** Keep the current core decoder and v2 output layers. Tighten their completion decisions using existing crystal corroboration; leave raw numerical decoding unchanged. Preserve the real replay corpus outside Git and add small repeatable policy and public output regressions.

**Tech Stack:** Windows Git Bash, Python 3.13.2, unittest; no new dependencies.

**Spec:** `docs/superpowers/plans/2026-09-06-terminal-completeness-design.md`

## Global Constraints

- Tests stay Python unittest, no new dependencies. Use synthetic inputs/temporary files or mock only external I/O; exercise the real policy and export aggregation. Current baseline is 212 tests passing.
- Do not encode truth, replay IDs, paths, team names, or tournament numbering in runtime decisions.
- Work on winsrv in the existing folder and a feature branch to retain all local replay/data files. Preserve the pre-existing six uncommitted document changes. Stage only task-owned files. No push, merge, external services or game UI manipulation in this task.
- Preserve raw duration, KDA, minion, item, gold, objective and position calculations. Coverage may decrease when evidence cannot confirm completion; do not represent that as improved numerical accuracy.

---

### Task 1: Enforce terminal evidence and pin the export boundary

**Files:**
- Modify: `vg/core/unified_decoder.py` (`DecodedMatch`, Step 7a, result assembly; extract a small pure policy helper if needed for direct unit tests)
- Modify: `vg/decoder_v2/completeness.py` (`assess_completeness`)
- Modify: `tests/test_decoder_v2_completeness.py` (retain old scenarios and change incorrect completion assertions)
- Create: `tests/test_unified_decoder_completeness.py`
- Modify: `tests/test_decoder_v2_decode_match.py` (uncertain match output boundary)
- Create: `vg/docs/COMPLETENESS_EVIDENCE_2026-09-06.md`

**Interfaces:**
- Consumes: core `UnifiedDecoder.decode(...) -> DecodedMatch` with `duration_seconds`, `recorded_seconds`, `completeness_ratio`, `data_complete`; v2 `assess_completeness(ReplaySignalSummary) -> CompletenessAssessment`; `decode_match(replay_file) -> DecoderV2MatchOutput`.
- Produces: same outputs with stricter completeness decisions, plus `DecodedMatch.completeness_reason: str` with a default compatible with existing construction. No new required caller arguments.

- [ ] Step 1: Add a regression for the misleading long tail before changing production. Reuse the existing signal construction and assert both uncertainty and retained approximate duration:

```python
signals = ReplaySignalSummary(
    replay_name="synthetic", replay_file="synthetic.0.vgr",
    frame_count=149, max_frame_index=148, crystal_ts=1221.3,
    max_kill_ts=1484.4, max_player_death_ts=1486.2,
    max_death_header_ts=1486.2, max_item_ts=1467.8,
)
assessment = assess_completeness(signals)
self.assertEqual(assessment.status, CompletenessStatus.COMPLETENESS_UNKNOWN)
self.assertIn("terminal", assessment.reason.lower())
estimate = estimate_duration_from_signals(signals)
self.assertEqual((estimate.estimate_seconds, estimate.source), (1486, "max_death"))
```

Run `python -m unittest tests.test_decoder_v2_completeness -v`; record the expected false-complete failure before implementation. Rename the existing long-tail regression to express its corrected uncertainty requirement, retaining all input fixtures.

- [ ] Step 2: Replace the unsupported positive v2 branches. Keep exactly the two existing corroborated positive conditions: crystal/player death within30s, and the existing late-crystal/generic-header/item condition for a stale player death. Preserve the two existing incomplete conditions. The final fallback uses `COMPLETENESS_UNKNOWN` with a reason explaining that aligned activity tails do not establish terminal completion. Preserve approximate duration behavior in `duration.py` without changing it.

```python
return CompletenessAssessment(
    status=CompletenessStatus.COMPLETENESS_UNKNOWN,
    reason="No corroborated terminal crystal evidence; aligned activity tails do not confirm match completion.",
    signals=signals,
)
```

All former no/stale-crystal acceptance scenarios remain as uncertainty tests. Aligned crystal, late corroborated crystal, short incomplete and tiny snippet tests remain positive controls with their existing expected outcomes.

- [ ] Step 3: Tighten core Step7a and add reason. For the current optional integer duration/recorded values and optional timestamp candidate/death tail, use the following decision order:

```python
# Keep ratio calculation identical to baseline.
if not duration or not recorded_seconds:
    data_complete = None
    reason = "Insufficient timing evidence to assess match completion."
elif duration / recorded_seconds < COMPLETENESS_THRESHOLD:
    data_complete = False
    reason = "Event duration falls short of the recorded span."
elif (crystal_ts is not None and duration_est is not None
      and abs(crystal_ts - duration_est) <= 30):
    data_complete = True
    reason = "Terminal crystal candidate agrees with the player-death tail."
else:
    data_complete = None
    reason = "Recording coverage alone does not confirm a terminal match end."
```

Pass this reason into `DecodedMatch.completeness_reason`. Document that None/False statistics remain estimates and are not guaranteed lower bounds; even the current M6 has overcounted fields. Core's positive criterion is deliberately narrower than v2's extra late-crystal corroboration path, because core does not collect those signals. Do not expand core scanning merely to equalize positive coverage.

Tests must cover: high ratio + stale crystal -> None; high ratio + no crystal -> None; aligned terminal candidate + high ratio -> True; missing timing -> None; low ratio -> False even if a crystal is present; exact 0.90 and30s boundaries; JSON contains the reason. A helper is allowed to isolate this real policy, but at least one `UnifiedDecoder.decode()` aggregation test must verify the new field flows through the public result. Patch only expensive I/O and event extraction for that aggregation test.

- [ ] Step 4: Exercise v2's existing public aggregation using the uncertain long-tail signal: unknown completeness must withhold K/D/A, winner and gold, retain identity, and keep duration only as a withheld estimate. Follow existing test construction; do not implement a parallel policy in tests. Run targeted tests, then `python -m unittest discover -s tests`.

- [ ] Step 5: Write `vg/docs/COMPLETENESS_EVIDENCE_2026-09-06.md` describing the counterexample, changed contract, sacrificed coverage, retained estimates and limitations. Link this new document from the core completeness comments if useful, leaving unrelated legacy docs untouched. Commit only task-owned files with an English `fix:` message; provide the full SHA and red/green evidence in the task report.

## Runtime verification after Task 1

The controller reuses `work/audit_remote.py` from the current local Codex task by piping it to remote `python -` (it reads all60 local starts and truth11). Compare with `outputs/vg-runtime-audit-2026-09-06.json`: all numeric fields, players, item slots, positions and objective totals must stay unchanged. M6 becomes coreNone/v2unknown; M9 stays coreFalse/v2incomplete. Record every changed classification. Also re-run `python -m vg.analysis.truth_comparison`; its old path-based denominator remains an explicitly named limitation, not a new accuracy claim.

For full raw-output invariance, save deterministic hashes per replay before editing, excluding only `data_complete` and the new `completeness_reason`; compare after. New regressions and an independent diff review must pass. Final deliverables are the feature-branch commit, this completed plan, the evidence document, a concise Korean run report and anonymized runtime JSON in the Codex outputs directory.
