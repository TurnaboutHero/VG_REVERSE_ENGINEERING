# Claim Ledger

## Confirmed

| claim | status | basis |
|---|---|---|
| player block `+0xA5` is player entity id | `CONFIRMED` | raw fixture scan |
| player block `+0xA9` is hero id | `CONFIRMED` | raw fixture scan + truth match |
| player block `+0xD5` groups binary teams | `CONFIRMED` | raw fixture scan |
| hero decoding from player block is production-ready | `CONFIRMED` | 109/109 truth validation |

## Strong

| claim | status | basis |
|---|---|---|
| complete fixture winner decoding is usable | `STRONG` | 10/10 complete fixtures |
| complete fixture kills decoding is usable | `STRONG` | 98/99 complete fixtures |
| complete fixture deaths decoding is usable | `STRONG` | 97/99 complete fixtures |
| complete fixture assists decoding is usable | `STRONG` | 97/99 complete fixtures |
| complete fixture gold estimate is index-usable | `STRONG` | `600 + [10 04 1D] action 0x06 positive no-sell`; 96/98 within 5%, 98/98 within 10%, corr 0.9993 |
| optional non-Finals minion policy is safe on current truth set | `STRONG` | `nonfinals-baseline-0e`: 40/40 accepted complete-fixture rows exact, 100% precision |
| kill/death/credit headers are semantically identified | `STRONG` | code + fixture behavior |
| binary team grouping is stable for index export | `STRONG` | 110 player blocks, team bytes `{1:55, 2:55}` on truth fixtures |
| current post-game K/D buffers are conservative enough to exclude known late kills without dropping short-tail real deaths | `STRONG` | fixture audit shows `death_buffer=0` is worse than `death_buffer=10` |

## Partial

| claim | status | counterexample |
|---|---|---|
| duration_seconds is a usable exact match end time | `PARTIAL` | exact 0/11, MAE 17.4s on complete fixtures |
| minion kill decoding is production-ready | `PARTIAL` | match 6, incomplete match 9 |
| complete replay detection rule is final | `PARTIAL` | current local replay pool is fully partitioned (`53 complete / 3 incomplete`), but external replay-family validation is still missing |
| match 6 minion residual has stable same-frame context candidate signals | `PARTIAL` | `28 04 3F`, `08 04 2C`, `18 04 1C`, and especially `0x02` family are enriched, but production-ready correction evidence is still missing |
| `[18 04 3E]` heartbeat may contain useful progression context | `PARTIAL` | timestamp/progression structure is visible, but no safe level field was found |
| action `0x02` is reward-pulse context | `PARTIAL` | `hackedglory_xp_level_validation_tournament`: 658 reward-like value buckets, but no monotonic XP total semantics |

## Rejected

| claim | status | basis |
|---|---|---|
| current `.vgr` tail focus burst is an independent HackedGlory-`1077` winner signal | `REJECTED` | `winner_signal_validation_tournament`: top focus matched truth winner side in only 5/11 matches and pointed to loser side in 6/11 |
| `[18 04 3E]` byte 15 directly encodes `level + 12` | `REJECTED` | `level_signal_probe_tournament`: rejected in 11/11 matches; byte values exceed valid `13..24` range |
| low-mixed-ratio minion gate is safe as a default export policy | `REJECTED` | `hackedglory_minion_validation_tournament`: 48/49 accepted rows exact, one accepted Finals error, failed CV folds |
| action `0x02` can be exported as total XP or level | `REJECTED` | reward-like buckets are pulses/subfamilies, while viable level candidates remain 0/11 |

## Open

| claim | status | note |
|---|---|---|
| exact end-of-match signal | `UNKNOWN` | current crystal/last-death heuristic insufficient |
| canonical minion kill signal for all matches | `UNKNOWN` | `0x0E` alone appears incomplete |
| XP / player level export | `UNKNOWN` | `[18 04 3E]` byte15=`level+12` rejected across 11 matches; no viable level candidate promoted |
| truth generation without result images | `UNKNOWN` | manifest alone is insufficient |
