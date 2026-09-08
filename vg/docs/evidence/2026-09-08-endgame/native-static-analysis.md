# Windows native endgame opcode analysis — 2026-09-08

Scope: only 0x03f1 and 0x048d paths, offline Ghidra 12.1.3 read-only project. Exact Windows PE32/x86 SHA-256 `659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`; preferred image base `0x00400000`. Every address is recovered from this Windows build. No runtime/game/Frida/memory interaction, remote changes or networking.

## 0x03f1: native ActionEndMatch, including winner and surrender reason

High-confidence build-specific chain:

1. Dispatcher `0x004cfec0` (RVA `0x000cfec0`), case 0x03f1, reads **five payload bytes**: a network-order uint32 from +0, then byte +4. The trailing byte in the supplied six-byte payload is not consumed by this handler.
2. At `0x004d1682`, calls constructor `0x0081a680` (RVA `0x0041a680`). Assembly proves low byte of decoded uint32 is stored in action+0x10; payload byte +4 is widened and stored in action+0x14.
3. Constructor installs native RTTI-backed `Nuo::Kindred::ActionEndMatch::vftable` at `0x0127c834` (RVA `0x00e7c834`). This class name is native evidence, not a guessed rename.
4. Dispatcher invokes `0x0092c240` (RVA `0x0052c240`), which calls action vtable+0x0c. That entry is `0x0092df00` (RVA `0x0052df00`): allocates/copies the 0x18-byte action and queues it via `0x0092f720`. Therefore receipt and apply are distinct operations.
5. Vtable+8 is `0x0094d450` (RVA `0x0054d450`): invokes `0x004c0e10(action.byte10, action.word14)`.
6. `0x004c0e10` treats reason values 5/6/7 through startup-validation dialog branches, 8 as no-op, and other reasons through guarded `0x00549620` (RVA `0x00149620`). Reason 2 follows the latter path.
7. `0x00549620` stores the first field into game object+0x19c and reason into game object+0x190, then requests state 3 via `0x0054a030(3)`. Do not infer a universal absolute terminal timestamp or that this request guarantees the callback runs in all states.
8. Result path `0x00548c90` (RVA `0x00148c90`) compares object+0x19c against the local team getter and passes the equality result plus reason to `0x004c1370` (RVA `0x000c1370`). That stores `win` at global `0x01e6fa68`, reason at `0x01e6fa6c`.
9. Analytics `0x004c13b0` (RVA `0x000c13b0`) emits literal key `win` from the first global and literal key `surrender` from **reason == 2**. This supports winner-team identity and reason-2 surrender semantics beyond the action's name alone.

For parent's supplied bytes `000000020200`, this build interprets winning-team value **2**, end reason **2 (surrender)**, and ignores final `00` in this handler. Team 2's mapping to screen side/color is not established here. No float clock/timestamp is read from 0x03f1. The parent's outer timestamp 149.430206 is a recorded envelope time, not a native terminal-time field demonstrated by this opcode.

The parent observed another 32 same-time updates after this record. This is consistent with an action queue and record envelopes, but this static analysis does not establish the dynamic ordering of those updates relative to final result display. Do not truncate every replay at its first 0x03f1 on this evidence alone.

## 0x048d: structured post-match analytics/statistics snapshot

Dispatcher case 0x048d copies **0x64c = 1612 payload bytes**, then calls `0x004c3a70` (RVA `0x000c3a70`) at callsite `0x004d4f92`. It does not construct an ActionEndMatch or assign the game clock. Parent reported a 1616-byte content record; exact framing vocabulary must be preserved: this handler uses 1612 bytes after the opcode. Any remaining bytes in the supplied record are not interpreted by the recovered copy. No assumption that surplus bytes indicate corruption is warranted.

`0x004c3a70` endian-decodes a structure-of-arrays into:

- sixteen player slots, 0x70 bytes each, beginning at global `0x01e6eee8`; input player IDs at payload+4*i; skips entries matching sentinel `DAT_01265f20`;
- two team records, 0x48 bytes each, beginning at `0x01e6f5e8`; input team identifier bytes at payload+0x62c+i; skips identifier sentinel `DAT_01265f1a`;
- further match aggregates and a 19-word block.

Decoded slots are subsequently selected by player ID in analytics `0x004c13b0`, where literal keys provide field semantics. Verified examples (i=0..15):

| Payload offset | Native destination offset in 0x70-byte player slot | Supported meaning/type |
|---|---|---|
| 0x000+4*i | +0x00 | Player ID, BE32 |
| 0x040+i | +0x04 | Team identifier byte (subsequently team-matched) |
| 0x060+4*i | +0x34 | `myDamageToHeroes`, BE float32 bits |
| 0x0a0+4*i | +0x38 | `myDamageToHeroesWP`, BE float32 bits |
| 0x0e0+4*i | +0x3c | `myDamageToHeroesCP`, BE float32 bits |
| 0x120+4*i | +0x40 | `myDamageToHeroesTrue`, BE float32 bits |
| 0x160+4*i | +0x44 | `myDamageToStructures`, BE float32 bits |
| 0x1a0+4*i | +0x48 | Ambient gold input to `myAmbientGoldPct`, BE float32 bits |
| 0x1e0+2*i | +0x4c | `myLaneFarmAt5mins`, BE16 widened |
| 0x200+2*i | +0x50 | `myJungleFarmAt5mins`, BE16 widened |
| 0x220+2*i | +0x54 | `myNetworthAt5mins`, BE16 widened |
| 0x300+40*i+4*j (j=0..9) | +0x0c+4*j | Item ID slots, BE32; consumed as item-name list |

Team fields feed literal keys including `myTeamStructureKills`, blackclaw/ghostwing captures and several at-5min/at-10min aggregates. Additional tail floats support `minionToStructureDamagePct` and `minionToVainCrystalDamagePct`: payload0x63c/0x640 -> globals0x01e6fa7c/0x01e6fa78, payload0x644/0x648 ->0x01e6fa84/0x01e6fa80. These labels identify derived ratios, not every numerator/denominator's unambiguous original name.

Important limit: analytics `myKills`, `myDeaths`, and `myAssists` are read/derived from a live actor state path in `0x004c13b0`, not shown to come from these 0x048d decoded slots. Do not relabel 0x048d as a verified direct final-K/D/A packet. Analytics `minutes` likewise comes from clock getter `0x00548880`, not a newly discovered 0x048d total-duration field. Some team fields are timing statistics (e.g. turret kill times), which are not match-end time.

No native symbolic packet class name for 0x048d was recovered. “Post-match analytics/statistics snapshot” is an interpretation supported by the consumer and named fields, not an RTTI name. A bounded immediate-opcode search did not locate an originating network serializer for these two tags; writer provenance beyond the client recording wrapper remains unresolved.

## Evidence and boundaries

- `addresses.md`: VA/RVA and first24 entry bytes for all followed functions.
- `dispatcher-excerpts.c`: selected original dispatcher decompile with source line references.
- `end-evidence.txt`: ActionEndMatch vtable, constructor assembly, dispatcher argument pushes, 0x048d copy-size/call evidence.
- `native-consumer-excerpts.txt`: complete small consumer functions and selected original numbered lines from the larger result/analytics functions.
- Full decompilations, extraction scripts and headless logs remain private working artifacts and are not included in this published evidence subset.

The observed 03f1 bytes/time/order are parent-provided corpus observations, not independently reparsed here. No universal end-of-file rule, winning-side UI mapping, exact video-time alignment, target anomaly explanation, or decoder policy change is established. The existing Ghidra project was used read-only and released; this document accompanies a selected publication subset.

### Follow-up clarification: reason 0 and same-time trailing records

Reason 0 reaches the same generic end-match handler as reason 2. The recovered consumer sets analytics `surrender` to false for 0; no native string/enum mapping specifically naming reason 0 “crystal destruction” was found. Use “end reason 0 / non-surrender under this consumer” until an independently observed crystal-ending control supports a narrower label.

Parent subsequently reports 55/56 original recordings contain exactly one 048d/03f1 pair, with all trailing records sharing the 03f1 outer timestamp and counts 0..65. This strengthens a corpus-specific end-marker candidate, but is not static proof of a universal format invariant. Queue ordering matters: 048d updates decoded stats directly while 03f1 builds and queues ActionEndMatch; actual vtable+8 apply occurs when the action queue is processed. The exact callback ordering relative to every trailing same-time update was not established in this bounded pass. Preserve those records when calculating final state; do not truncate solely at the marker byte offset.
