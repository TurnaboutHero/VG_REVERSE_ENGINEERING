# Replay completeness requires terminal evidence

## Counterexample

The audited M6 replay has contiguous sections 0 through 148, representing about 1490 recorded seconds. Its last player and generic death timestamp is 1486.2308 seconds, its last item timestamp is 1467.8193, and its only crystal-range candidate is stale at 1221.3105. The result screenshot independently shows 25:51 (1551 seconds). A 1486/1490 activity ratio and aligned activity tails therefore looked complete while the recording still lacked evidence of the actual terminal match event.

This is an evidence-boundary correction. The screenshot duration is offline validation only and is not used by runtime policy. Runtime code does not identify this replay by name, path, team, or tournament number.

## Changed contract

Core keeps the existing duration and recording ratio calculation. A ratio below 0.90 is still `False`. At or above 0.90, `data_complete` is `True` only when the existing crystal candidate agrees with the player-death tail within 30 seconds. Missing timing or missing/inconsistent terminal evidence yields `None`. Every `DecodedMatch` now carries `completeness_reason` explaining that decision.

Decoder v2 retains two positive paths: direct crystal/player-death agreement within 30 seconds, and a late crystal corroborated by generic death and item tails when the player-death tail is stale. Tiny snippets and the known short-tail-gap pattern remain confirmed incomplete. All other aligned activity-tail cases are `completeness_unknown` because activity does not prove a terminal match end.

## Export boundary and retained estimates

For unknown or incomplete v2 results, the existing safe export policy withholds K/D/A, winner, and gold from indexing. Player identity remains accepted. Partial gold may remain visible with a nonaccepted status, and approximate duration remains visible as a withheld estimate. For the counterexample, v2 retains 1486 seconds from `max_death`; it does not relabel that estimate as confirmed duration.

Core retains its numeric decoded fields so downstream research can inspect them. When `data_complete` is `None` or `False`, K/D/A, minion and jungle kills, gold, items, positions, and objectives are estimates. They are not guaranteed lower bounds: missing events can undercount, while known detector ambiguity can also overcount.

## Sacrificed coverage and limitations

This conservative rule demotes replays whose activity tails look internally consistent but lack corroborated terminal crystal evidence. Some truth-complete replays have stale or missing crystal candidates, so acceptance coverage decreases intentionally. Core is narrower than v2 because core does not collect the additional generic-header and item-tail evidence needed for v2's late-crystal path.

The rule does not prove detector perfection, improve K/D/A or CS numerical accuracy, or turn approximate duration into ground truth. It separates confirmed completion from plausible coverage so downstream consumers can make that uncertainty explicit.
