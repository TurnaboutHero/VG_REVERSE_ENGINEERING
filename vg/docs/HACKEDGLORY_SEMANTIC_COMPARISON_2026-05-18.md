# HackedGlory Semantic Comparison Matrix

Date: 2026-05-18

Source repo: `a1cnore/HackedGlory` at `0fdc6ddd65a6c0c8657d238d41668baa86debdf0`

Scope: use HackedGlory as a semantic comparison source for `.vgr` replay decoding. HackedGlory decodes captured in-match packets, not `.vgr` files, so its byte layouts are not direct `.vgr` offsets. The useful part is the meaning layer: entity mapping, scoreboard state, resource counters, death/kill heuristics, winner signals, and coverage metrics.

## Source Priority

Primary HackedGlory references:

- `mitm/match_decryption/autoresearch.md`
- `mitm/match_decryption/protocol_decryption_writeup.md`
- `mitm/match_decryption/scripts/vg_match_schema.py`
- `mitm/match_decryption/vg_match_dashboard.py`
- `mitm/match_decryption/decoded_matches/*.jsonl`

Secondary references:

- `mitm/match_decryption/scripts/decode_match_packets.py`
- `mitm/match_decryption/scripts/evaluate_decode_coverage.py`
- `mitm/match_decryption/vg_dashboard_server.py`

Low-priority / out of scope for `.vgr` parser work:

- `vg_unlock_android`
- iOS unlock work
- CE gate analysis
- UI unlock reports

## Comparison Matrix

| Semantic target | HackedGlory signal | Local `.vgr` signal | How to use it here |
|---|---|---|---|
| Player name | `1005`, `1006`, and `1113/1114` snapshot handle strings | Player block marker `DA 03 EE` / `E0 03 EE`, variable ASCII name | Keep `.vgr` player block as primary. Use HackedGlory to validate expected roster cardinality and slot ordering. |
| UUID | `1000`, `1006`, `1113/1114` snapshot UUID string | Player block / parser UUID extraction | Compare UUID presence, slot count, and name-UUID pair stability. |
| Team | Snapshot record byte 15: `1=Blue`, `2=Red`; `1011` team at bytes `12:16` | Player block `+0xD5`, currently grouped as left/right | Use as semantic side mapping check. Do not assume byte values match across formats. |
| Entity mapping | `1006` handle/UUID/entity mapping; `1113/1114` entity at record bytes `18:20`; hero entities often `1500-1505` in packet captures | Player block `+0xA5` entity id, local events reference player entity ids | Compare relationship shape: one active entity per player, stable through timeline. Do not copy packet entity ranges into `.vgr`; local ranges differ. |
| Game mode | `1108` game mode string at payload offset 5; `1135` mode display name | `GameMode_*` string extraction | Normalize ARAL/ranked/5v5 labels and use mode-specific invariants. |
| Hero | `1107` sends full hero catalog; `1011` has `hero_type_id` candidate but per-player assignment remains uncertain | Player block `+0xA9` hero id is confirmed | Treat local `.vgr` hero id as stronger than HackedGlory. Use HackedGlory catalog only for naming/cross-checking, not assignment truth. |
| Spawn/setup | `1011`: `0:4` hero type candidate, `10:12` entity, `12:16` team, `18:22`/`22:26` spawn X/Y, `138:146` spawn health values | Player block plus early frame state/action records | Search `.vgr` early frames for equivalent setup clusters: entity, team, spawn-like floats, initial health-like values. |
| Position | `1070`: entity at `2:4`, BE float X at `4:8`, BE float Y at `8:12`; ARAL range roughly X `-90..90`, Y `-10..20` | Movement/action payload candidates | Use coordinate ranges as float plausibility filters when scanning `.vgr` payloads. |
| Damage | `1053` stat type `6` is HP delta; large negative values mark heavy damage | KDA/event payload analysis, death/kill headers | Use damage spikes as context around local kill/death windows, not as standalone truth. |
| Death | `1067`: state index `0`, value `3` means death candidate | Header `08 04 31` death event | Local death header remains primary. HackedGlory suggests validating deaths as state transitions with dedupe windows. |
| Respawn | `1067`: state index `0`, value `1` after death means respawn candidate | Not a primary exported field yet | Use as a search target for `.vgr` lifecycle timelines and completeness checks. |
| Kill attribution | No confirmed single kill opcode. Current heuristic: latest opposing `1087` source-target interaction before death, then opponent-only `1086` reward fallback within about 1s | Header `18 04 1C` kill event plus credit records | Use HackedGlory to harden local attribution rules: never credit same-team killers; use reward windows only as fallback. |
| Assists | Recent `1087` attackers and reward-window participants around death | `10 04 1D` credit records after kill | Cross-check assist semantics: same-team non-killer participants near a kill event. |
| Gold total | `1086` type `0x4D`, monotonic plausible scoreboard counter | Credit/action families, gold earned/spent, item costs | Use monotonic counter expectations and plausible caps when separating earned/spent/total gold candidates. |
| XP total | `1086` type `0x3E`, monotonic plausible scoreboard counter | Credit/action families and level/skill events | Use XP monotonicity and level correlation to classify ambiguous credit payloads. |
| Level | `1086` type `0x3E` / `0x42` plus nearby `1053` stat changes; ARAL base level 4 and cap at level 12 | Action `0x3E` skill level-up is confirmed; level itself is not fully direct | Use ARAL invariants: start level 4, max 8 extra levels, ability upgrades capped by 12 total points. |
| Skills / ability upgrades | Ability-like interactions through `1087`; level milestones inferred from resource and stat follow-up | Action `0x3E` skill level-up event | Use level-skill correlation. A skill upgrade candidate should usually sit near a level/resource milestone. |
| Items | HackedGlory treats items as open/weak: likely `1087`, including later self-targeted family `0xBC` loadout-like changes | `FF FF FF FF [item_id LE]`, item acquisition header `10 04 3D`, action `0xBC` trigger | Keep local item parser primary. Use HackedGlory only as a reminder to separate loadout state from purchase event timing. |
| Creep score / minions | `1087` source hero targeting `2000-2100`, followed by `1086` reward pulses; CS target dedupe about 3s | Minion kill research is partial, baseline action/header families under evaluation | Use source-target-reward windows as a comparison model for minion research, especially outliers. |
| Winner | `1077` late seven-message burst, all targeting a winning-side focus player; payload team hint is secondary | Current v2 winner derives from complete-fixture K/D asymmetry; older logic also uses objective/turret/crystal signals | Search `.vgr` endgame tail for a burst/focus-card equivalent, but only promote it if it matches truth winner side. Current tail focus validation rejects the naive focus candidate. |
| Duration | Packet capture start/end timestamps and decoded event timeline | Frame count, death/objective tail, completeness gates | Compare as elapsed timeline shape, not direct timestamp format. |
| Timeline events | `decoded_matches/*.jsonl`: direction, message index, opcode, decrypted bytes, extracted strings | `.vgr` frame stream and event headers | Use HackedGlory JSONL as event vocabulary: roster setup, interactions, resource pulses, state transitions, end burst. |
| Coverage metrics | `scoreboard_score`, `gold_players`, `xp_players`, `death_players`, `kill_players`, `cs_players`, `level_players`, `replay_players`, `winner_matches` | `decoder_v2` validation matrix and safe export policy | Add matching metrics when evaluating new `.vgr` hypotheses, especially for replay-ready scoreboard state. |

## Practical Rules

1. Prefer local `.vgr` direct offsets and headers when they are fixture-backed.
2. Use HackedGlory as a candidate meaning map, not as direct byte layout evidence.
3. Promote a HackedGlory-inspired `.vgr` hypothesis only when temporal behavior matches: monotonic counters, team constraints, state transitions, and mode-specific invariants.
4. For KDA, keep local `18 04 1C` / `08 04 31` headers primary, but adopt HackedGlory's opponent-only kill attribution guard.
5. For resources, classify candidates by monotonicity and plausible total range before naming them gold or XP.
6. For ARAL, enforce gameplay constraints during validation: base level 4, level cap 12, six item slots, and normal ability upgrade caps.

## Immediate `.vgr` Research Uses

- Search for an endgame burst/focus-card structure analogous to packet opcode `1077`.
- Re-run minion research with a source-target-reward window model instead of isolated action counts.
- Add a scoreboard-readiness score mirroring HackedGlory's `replay_players`: gold + XP + death timeline plus one of kill, CS, or level.
- Use HackedGlory's `1086` resource-counter behavior as the reference shape for local gold/XP candidate validation.
- Treat hero assignment as solved locally; do not regress to HackedGlory's weaker `1011` hero candidate.

## Local Probe Tool

Run the local semantic readiness probe against any `.0.vgr`:

```bash
python -m vg.decoder_v2.hackedglory_semantic_probe <replay.0.vgr> -o vg/output/hackedglory_semantic_probe.json
```

This does not prove byte-level equivalence. It scores the current `.vgr` decoder output against HackedGlory's semantic anchors and highlights the next missing searches, especially `1077`-like endgame burst, `1086`-like total resource counters, and `1087`-style source-target-reward windows.

Focused follow-up probes:

```bash
python -m vg.decoder_v2.resource_counter_probe <replay.0.vgr> -o vg/output/resource_counter_probe.json
python -m vg.decoder_v2.resource_candidate_validation --truth vg/output/tournament_truth.json -o vg/output/resource_candidate_validation_tournament.json
python -m vg.decoder_v2.credit_resource_validation --truth vg/output/tournament_truth.json -o vg/output/credit_resource_validation_tournament.json
python -m vg.decoder_v2.level_signal_probe --truth vg/output/tournament_truth.json -o vg/output/level_signal_probe_tournament.json
python -m vg.decoder_v2.endgame_burst_probe <replay.0.vgr> -o vg/output/endgame_burst_probe.json
python -m vg.decoder_v2.winner_signal_validation --truth vg/output/tournament_truth.json -o vg/output/winner_signal_validation_tournament.json
python -m vg.decoder_v2.minion_window_research <replay.0.vgr> --truth vg/output/tournament_truth.json -o vg/output/minion_window_probe.json
python -m vg.decoder_v2.hackedglory_minion_validation --truth vg/output/tournament_truth.json -o vg/output/hackedglory_minion_validation_tournament.json
python -m vg.decoder_v2.hackedglory_xp_level_validation --truth vg/output/tournament_truth.json -o vg/output/hackedglory_xp_level_validation_tournament.json
```

Batch the follow-up probes across truth-covered local replays:

```bash
python -m vg.decoder_v2.hackedglory_followup_batch --truth vg/output/tournament_truth.json -o vg/output/hackedglory_followup_batch_tournament.json
```

Use the batch output as a triage table. Repeated resource families include truth-metric correlations but remain monotonic counter candidates until validated as gold/XP; repeated endgame focus candidates include truth-winner side checks and remain only candidates until they consistently match the actual winner side; repeated positive minion headers and credit patterns are the next source-target-reward families to validate.

## Current Follow-Up Result

`vg/output/resource_candidate_validation_tournament.json` validates the top `0x01` resource-counter candidates from the tournament truth set. Result: do not promote the current `0x01` candidates to gold/XP totals.

Across 11 truth-covered matches:

- `0x01:u32be@1` is rejected in 11/11 matches as target-entity-id-like. It often decodes values around `2000+`, which matches target/object/event ids better than player gold.
- `0x01:u32le@3` is rejected in 11/11 matches as an endian/offset alias of that target id context.
- `0x01:f32be@7` and `0x01:f32le@4` are rejected in 11/11 matches as timestamp-like; `f32be@7` has average frame correlation `1.0`.
- `0x01:u32be@5` is rejected in 11/11 matches as embedded event context.
- The same payload context includes known local headers such as `18 04 1C` kill and `10 04 3D` item-acquire, so the gold correlation is a progression artifact rather than a direct total-resource field.

Next resource search should move away from the `0x01` embedded-event family and focus on credit/resource families that are scale-compatible with truth gold, especially known `[10 04 1D]` action groups and any monotonic fields that are not target-id/timestamp/header aliases.

`vg/output/credit_resource_validation_tournament.json` validates credit-action gold formulas against local result-screen truth. Current best gold formula is:

```text
gold ~= 600 + sum([10 04 1D] action 0x06 positive values where sell_flag != 0x01)
```

On all truth rows this scores 96/107 players within 5% and 98/107 within 10%. The major misses come from one known incomplete fixture directory, `5 (Incomplete)`. On complete fixtures only, the same formula scores 96/98 within 5%, 98/98 within 10%, average absolute error `79.42` gold, and truth correlation `0.9993`.

This is strong enough to treat local credit-action gold as the primary `.vgr` gold estimate for complete replays. It does not solve XP, because the current truth set does not contain XP labels.

`vg/output/level_signal_probe_tournament.json` re-tests the historical local hypothesis that `[18 04 3E]` byte 15 encodes `level + 12`. Result: reject it.

Across 11 truth-covered matches:

- `[18 04 3E]` produced `152,917` player-scoped heartbeat records.
- The byte-15 `level + 12` hypothesis is rejected in 11/11 matches; values exceed the valid `13..24` level+12 range and can reach byte values such as `255`.
- The probe found `0` viable level candidates after excluding structural header/entity bytes.
- Offset `25` in the same heartbeat record behaves like a timestamp/progression value, not a level.
- Credit action `0x03` is not a universal level signal; when present, it appears only on subsets of players with hero/passive-like value distributions.

So the current state is: gold is accepted for complete replays, XP remains unsolved, and no level field is promoted to safe output yet.

`vg/output/winner_signal_validation_tournament.json` validates the current local tail-focus candidates against truth winner labels. Result: reject the naive `.vgr` endgame focus candidate as an independent HackedGlory-`1077` equivalent.

Across 11 truth-covered matches:

- Every match had at least one tail focus candidate.
- The top focus candidate matched the truth winner side in only 5/11 matches.
- The top focus candidate pointed to the loser side in 6/11 matches.
- Repeated top candidate families are dominated by noisy credit/kill/item or generic player-event activity, not a clean late seven-message winner burst.
- Tail-concentrated generic headers were sparse and did not repeat across the match set: `100440`, `280400`, and `080402` each appeared as a concentrated tail header in only one match.

So the current winner export should continue to rely on the conservative complete-fixture K/D asymmetry gate. The HackedGlory `1077` idea remains useful as a search shape, but the currently detected `.vgr` tail activity is not safe winner evidence.

The refreshed `vg/output/hackedglory_followup_batch_tournament.json` carries the same winner-side check in the batch summary:

- `matches_processed`: 11
- `endgame_top_focus_result_counts`: `{"loser_side": 6, "winner_side": 5}`
- `endgame_top_focus_winner_side_rate`: `0.4545`
- `scoreboard_readiness_totals`: `player_count=110`, `identity_players=110`, `kda_players=100`, `gold_players=100`, `local_export_ready_players=100`, `xp_players=0`, `level_players=0`, `strict_hackedglory_replay_ready_players=0`
- `scoreboard_blocking_field_frequency`: `{"xp_total": 11, "level": 11}`
- Semantic totals: `covered=95`, `partial=43`, `missing=16`

The missing semantic targets are now concentrated around unsolved level/XP plus incomplete-replay withholding, rather than gold.

The semantic probe also reports `scoreboard_readiness` to mirror HackedGlory-style replay-readiness metrics. On a complete 5v5 smoke replay:

- `identity_players`: 10
- `kda_players`: 10
- `gold_players`: 10
- `local_export_ready_players`: 10
- `xp_players`: 0
- `level_players`: 0
- `strict_hackedglory_replay_ready_players`: 0
- blocking fields: `xp_total`, `level`

This means local decoder v2 is strong enough for result-style roster/KDA/gold rows on complete replays, but not yet strong enough for strict replay-state reconstruction because XP/level remain unsolved.

`vg/output/hackedglory_minion_validation_tournament.json` consolidates the minion/CS side of the comparison. HackedGlory's useful model is source-target minion interaction followed by reward pulses; local `.vgr` evidence currently supports a narrower conclusion:

- Product-safe optional policy: `nonfinals-baseline-0e`
- Default policy should remain: `none`
- `nonfinals-baseline-0e`: 40/40 accepted rows exact, 100% precision, 51.28% complete-fixture coverage
- `nonfinals-or-low-mixed-ratio-experimental`: 48/49 accepted rows exact, one accepted error, so not default-safe
- Leave-one-series and leave-one-replay cross-validation both have one failed fold for metric-gated policies
- Source-target-reward context windows are enriched but concentrated in one match, so they remain context-only evidence rather than a direct general CS rule

In practical terms: local `0x0E` is safe for non-Finals optional export under the current truth set, but HackedGlory-style source-target-reward reconstruction is not solved globally yet.

`vg/output/hackedglory_xp_level_validation_tournament.json` separates local reward pulses from exportable XP/level state:

- `action 0x02` has 658 reward-like value buckets across the tournament truth set.
- Reward-like buckets are mostly `solo_reward_candidate` plus smaller shared/mixed families.
- These are event pulses/subfamilies, not monotonic total XP counters.
- `level_signal_probe` found viable level candidates in 0/11 matches.
- `[18 04 3E] byte15=level+12` is rejected in 11/11 matches.
- Current export status remains `xp_total=not_safe`, `level=not_safe`.

So local `action 0x02` is useful context for reward/minion/XP-like events, but it should not be treated as HackedGlory `1086`-style total XP or level.
