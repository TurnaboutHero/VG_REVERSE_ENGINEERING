# Terminal evidence for replay completeness

User request: plan and implement the next corrective step after auditing the current VG decoder. Scope is the false completion claim exposed by M6; do not invent missing CS/KDA events or tune thresholds to its identity.

## Evidence

At baseline 119322d1d3bdecb37fc5267b98d698a73fda194e, M6 has contiguous sections 0..148, 1490 recorded seconds, last player/generic death 1486.2308s, last item 1467.8193s, and only crystal-range candidate 1221.3105s. Truth duration1551s is for offline comparison only. Core declares complete from 1486/1490=.997; v2 declares complete from a long self-consistent activity tail. Neither proves recording reached match end. M4 has a stale crystal candidate and M7 none despite being truth-complete, so a conservative correction necessarily sacrifices acceptance coverage.

## Required behavior

- Activity tail alignment or recording length alone must not confirm match completion.
- Core retains numeric duration, KDA, items, gold, objectives and positions unchanged. A ratio below the existing 0.90 threshold still yields False. A ratio at/above threshold yields True only when an existing crystal candidate agrees with the last player death within 30s; otherwise None. Missing timing yields None. Add a human-readable completeness_reason with every result.
- v2 retains the existing direct crystal/player-death 30s corroboration and the existing late-crystal/generic-death/item corroboration for stale player-death tails. Remove positive decisions based only on activity tails or an inconsistent crystal. Preserve existing tiny-snippet and short-tail-gap incomplete rules. Other cases are completeness_unknown with an explicit terminal-evidence reason.
- M6 remains a 1486s max_death approximate estimate in v2, but completion is unknown and final KDA/winner/gold are withheld from index acceptance by the existing policy. Preserve safe/debug partial gold values with gold_status=partial_completeness_unknown; do not erase that existing research contract. Identity fields remain accepted. M9 remains incomplete.
- Do not encode truth, replay IDs, paths, team names, or tournament numbering in runtime decisions.
- Keep old test scenarios that described long/stale/no-crystal tails, but correct their expected completion semantics and names; do not delete coverage to get green. Add counterexample and public pipeline tests.
- Tests stay Python unittest, no new dependencies. Use synthetic inputs/temporary files or mock only external I/O; exercise the real policy and export aggregation. Current baseline is 212 tests passing.
- Work on winsrv in the existing folder and a feature branch to retain all local replay/data files. Preserve the pre-existing six uncommitted document changes. Stage only task-owned files. No push, merge, external services or game UI manipulation in this task.

## Acceptance

New regressions fail before the policy change, then pass. Full tests pass. Actual local 60 replay starts decode; M6 core None/v2 unknown, M9 incomplete, aligned terminal fixtures remain accepted. Record all demotions and coverage cost. Raw estimates are identical before/after except new/updated completeness fields. Reproduce the existing 49/60 item slot match count. No claim of increased KDA/CS numerical accuracy or complete detector perfection.
