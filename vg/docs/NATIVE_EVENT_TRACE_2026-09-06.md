# Native opcode trace: 0431, 041c, 041d, 042b

**Provenance correction (2026-09-07):** Per the user clarification, VG:NA is a community-modified redistribution, not the original official client. The inspected engine was extracted from a VG:NA iOS IPA; the separate original official Android APK was not inspected. Handler links and KDA mappings below are established for this specific VG:NA engine only. Their equivalence to the original official client and the replay-producing build remains unverified. Agreement with public decompiled material does not independently authenticate the original official implementation.

**Current status:** The later named-getter trace in `NATIVE_STAT_LABELS_2026-09-06.md` confirms attribute41/0x29=myKills, attribute42/0x2a=myDeaths, and resource11/0x0b=myAssists. References below to those names being unresolved describe the earlier investigation stage. Resource9/10, actor-state names, and whole-build identity remain unconfirmed.


Date: 2026-09-06. Bounded static trace, independent of Python event names. No remote checkout changes.

**Final status:** This records the initial source-only trace. The missing vtable edge discussed below was subsequently resolved for all four opcodes in the inspected community-modified VGNA engine; see `NATIVE_EVENT_BINARY_2026-09-06.md`. Enum names and whole-build identity remain unconfirmed.


## Result

The native data model is materially more specific than generic event/action labels: **041c carries an attribute mutation with SET/ADD mode; 041d carries a resource mutation with SET/ADD mode; 042b carries an indexed state byte and two masks; 0431 corresponds to a guarded actor state-machine transition from numeric state 3 to 4.** The last statement is supported by the opcode's emitting function, not an English death/despawn enum. The exact resource index 9, attribute indices 41/42 (0x29/0x2a), state names, and the bit meanings in 042b remain unresolved.

These meanings are strong static inferences, not a completely closed execution proof. Constructors and opcode-specific serializers match the field layouts; the public export omits vtable values needed to prove the final virtual dispatch edges. A replay timeline should preserve native-neutral fields and confidence rather than equate every 0431 with death or every 041d/index9 record with an independent death.

## Source and verification

Pinned repository commit: `a1cnore/HackedGlory@0fdc6ddd65a6c0c8657d238d41668baa86debdf0`. Downloaded exports are under `native/`. Existing `../binary-reinvestigation/10012.c` and `1003c.c` were verified against the same Git tree. `NATIVE_EVENT_SOURCE_MANIFEST_2026-09-06.json` records blob SHA-1 values; all 12 consulted source/report files match the pinned tree. No annotations from `vg_match_schema.py` were used as semantic proof.

GitHub web browsing returned cache misses for the directory/raw source, so exact sources were retrieved from raw.githubusercontent.com and their Git object hashes checked against the GitHub tree API. Links below use stable commit/line anchors.

## Common dispatch and the exact missing link

The dispatcher decodes each opcode and creates an event object, sets its byte at offset `+0x18` to 1, and calls `FUN_100345498`. This function invokes **vtable+0x20**, passing the global queue `DAT_101e47d30`. The queue drain `FUN_1003454b8` invokes **vtable+0x18** for objects with `+0x18 != 0`; its other branch also uses **vtable+0x10**. Thus the missing data is precise: the function pointers at vtable addresses below plus offsets 0x10, 0x18, 0x20. [dispatcher](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10012.c#L6917-L6920), [virtual queue entry and drain](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10034.c#L4626-L4680).

| Opcode | Constructor / wrapper | Vtable address | Same-layout serializer | Candidate apply handler |
|---|---|---|---|---|
|0431|1003c6194|101496a38|1003d4490 → 100347060|1003d451c|
|041c|10012369c → 1003c4f68|1014971e0|1003db71c → 100347e30|1003db80c|
|041d|1001236ec → 1003a34f4|101497218|1003db9a0 → 100347f30|1003dba48 → 1003dbaec|
|042b|1003dcba4|1014973d8|1003dcbd0 → 100348964|1003dcc0c|

The public `globals.c` / header do not contain initialized values for these tables. The bounded checked `reports/generated/vtable_trace.md` also contains no matching table address. Repository tree includes Ghidra project metadata but no corresponding program database/binary from which these values can be read directly. Adjacent source functions alone would be weak evidence; matching serializers explicitly writing the target opcode provide the additional independent link.

## Payload layouts

Offsets below start **after the two-byte opcode**, not at the outer VGR record. Integers/floats are big-endian on the wire. The native structs are a different serialization layer from the VGR outer `f32 timestamp/u32 length/u16 opcode` envelope. Only fields consumed by this native version are identified. Any extra VGR bytes must remain raw until version/layout equivalence is proved; do not silently call them padding.

|Opcode|Payload fields consumed by dispatcher|Native payload size represented by serializer|
|---|---|---:|
|0431|0: u32 entity identifier|4|
|041c|0: u32 entity; 4: u32 auxiliary u32; 8: f32 value; 12: u8 attribute index; 13: u8 attribute layer; 14: boolean SET mode|15|
|041d|0: u32 entity; 4: f32 value; 8: u8 resource index; 9: boolean SET mode; 10: boolean flag; 11: boolean flag|12|
|042b|0: u32 entity; 4: u8 index; 5: u8 state bits; 6: u8 mask A; 7: u8 mask B|8|

In particular, the parent's observed VGR **content lengths** (including two-byte opcode) are 0431=8, 041c=24, 041d=16, 042b=16; their **payload lengths** are respectively 6,22,14,14. These are not the native payload sizes above. Their excess bytes are outside the fields consumed by this dispatcher version. These static layouts must be tested against the captured field offsets, not presumed to explain the complete VGR record.

Dispatcher proof: [041c and 041d](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10012.c#L5345-L5391), [042b](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10012.c#L5599-L5604), [0431](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10012.c#L5645-L5648).

### 041d: resource SET / ADD, not an action enum

`FUN_1001236ec` maps p[8] to object `+0x20`, f32 p[4] to `+0x24`, p[9] to `+0x28`; flags p[10], p[11] become object +0x29/+0x2a. Constructor defaults the two latter flags to 1 and 0, then wrapper conditionally changes them. [wrapper](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10012.c#L2949-L2968), [constructor](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003a.c#L1995-L2009).

Serializer `1003db9a0` interprets the value as float, reads the indexed resource at `actor->field40 + 0x308 + index*4` when SET mode is true, suppresses negligible changes, then emits opcode041d via `100347f30`. This is direct native evidence that p[8] is a numeric resource selector and p[4] is a value. [event serializer](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003d.c#L9919-L9958), [opcode serializer](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10034.c#L7069-L7102).

Candidate apply chain `1003dba48 → 1003dbaec`:

- SET p[9] != 0: `1003dbb54(value,actor,index)` assigns `resource[index] = max(value,0)`.
- ADD p[9] == 0: `1003d7388 → 1004653d8` assigns `resource[index] = max(old + value,0)`. Resource 0 has additional guard conditions; the call can be suppressed when already depleted. Other actor-state guards can suppress resource 0/2 changes.
- For index6 and positive ADD, `1004653d8` also increments resource7 at +0x324. This may eventually identify currency, but no English label is proven here.
- Both paths notify `onActorResourcesChangedName` and callbacks. Flags10/11 affect a special index6 controller path; name them raw flags until that path is decoded.

[SET/ADD branch and SET assignment](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003d.c#L9964-L10040), [ADD wrapper](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003d.c#L6364-L6393), [ADD arithmetic](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10046.c#L4533-L4548).

**Aggregation consequence:** raw sum(value), raw record count, and latest(value) are each wrong in some modes. Replay SET replaces the current resource; ADD changes it; raw occurrence counts are not final counters. Index9 correlates with kills and index10 with deaths in the parent corpus probe, but their enum labels and whether they are streak/current/lifetime counters remain unresolved. Native value semantics are supported even while the English selector name is unknown.

### 041c: attribute SET / ADD and layer

`10012369c → 1003c4f68` stores p0 at object+1c, p4 at+20, p12 at+24, p13 at+28, f32 p8 at+2c, p14 at+30. [wrapper](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10012.c#L2932-L2943), [constructor](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003c.c#L4429-L4445).

Serializer `1003db71c` reads the same value/index fields, evaluates current computed attribute when mode=true, and sends041c through `100347e30`. Candidate apply `1003db80c` branches on object+30. Mode=true calls `1003db860 → 100463154` (assignment); false calls `1003d9ff0 → 100465300 → 100463154` (old+value). Both notify `onActorAttributesChangedName`. [serializer and apply](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003d.c#L9737-L9845).

The attribute layer p13 selects arrays at object40+0x38 (0), +0xec (1), +0x1a0 (2), +0x254 (3), each with index*4. ADD obtains the old layer value and adds the payload float before calling the setter; the setter marks the attribute bit dirty. [ADD](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10046.c#L4498-L4528), [SET](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10046.c#L2558-L2579).

Index notation matters: the parent corpus's attribute `0x29` is decimal41 and `0x2a` is decimal42. Native calls found with index `0x1d` (decimal29) are a different attribute and do not establish or refute the meaning of 0x29/0x2a.

### 0431: guarded numeric actor-state transition 3 → 4

Constructor `1003c6194` copies just the entity field. Its copy/enqueue implementation `100496aa8` allocates a 0x20 object and copies that same vtable/entity. [constructor](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003c.c#L5427-L5436), [copy/enqueue](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10049.c#L6574-L6592).

The explicit0431 sender `1003d4490` looks up the entity, reads current state from `actor+0x88`'s low five bits and state descriptor at `actor + stateIndex*0x38 + 0x90`, requires state ID3, calls `10046211c(actor+0x88,4,0,0)`, then emits0431 through serializer constant `0x31040600`, whose little-endian bytes are `00 06 04 31`. Its paired candidate receiver `1003d451c` does the same guarded 3→4 transition in the opposite `DAT_101d23a38` branch. [sender/receiver](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003d.c#L3623-L3663), [explicit0431 serializer](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10034.c#L6372-L6403).

`10046211c` is an actual state-machine setter: finds target state descriptor, checks transition permission, invokes exit/entry callbacks, updates active-state bits. The actor constructor registers state3 and state4 and permits 3→4. State4 entry is `10046201c`; its visible behavior is a conditional local-actor callback, not a clear English death assertion. [state registration](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10046.c#L1600-L1674), [setter](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10046.c#L1976-L2041), [state4 entry](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10046.c#L1872-L1890).

**Supported:** entity-scoped completion/transition from native state3 to state4, conditionally applied. **Not independently proven:** death, exact death instant, despawn/removal, killer, final death count. Repeated messages may be ignored if the entity no longer occupies state3.

### 042b: indexed bit-state and masks, not four anonymous bytes

The constructor consumes all four p4..p7 bytes. `1003dcbd0` serializes all four unchanged and calls the explicit042b serializer `100348964`. Candidate handler `1003dcc0c` looks up entity, locates component type `DAT_10184dda8`, and passes all four bytes to `1003d932c`, then invokes descendant callbacks hash0x554207b0. [constructor/serializer/handler](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003d.c#L11056-L11123), [explicit042b encoder](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10034.c#L7573-L7594).

`1003d932c` indexes a bank with stride0x19 selected by component+0x5c and writes:

- base + bank*0x19 + p4 + 0x28 = p5 (state bits)
- base + bank*0x19 + p4 + 0x30 = p6 (mask A)
- base + bank*0x19 + p4 + 0x38 = p7 (mask B)

It checks bit1 of old/new state and can invoke distinct callbacks on changes. A reader `1003dcd70` evaluates `state & ~(maskA | maskB) == 0`. This is concrete bit-state/mask behavior; interpreting p4 as a team index or the operation as visibility/fog-of-war is plausible but not established by these unnamed fields alone. [writes and bit1 branch](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003d.c#L8020-L8068), [mask reader](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/1003d.c#L11164-L11173).

## Confidence and completion boundary

- High: constructor field offsets, endianness, explicit opcode encoder constants, SET/ADD arithmetic, state-machine setter, mask writes.
- Strong inference: connecting each constructor's unknown virtual slots to same-layout serializer/apply pair.
- Unresolved: actual vtable pointer values; resource/attribute enum names (especially resource9/10/11 and attribute41/42); actor state3/4 English names; auxiliary041c u32; resource flags10/11 full semantics;042b bit/index English meanings; excess VGR payload bytes and native-version compatibility.
- Next concrete proof would be 32 bytes per target vtable (slots0x10..0x28) from the matching Mach-O/Ghidra program or a live handler trace, then enum/callback registration evidence. No unbounded binary/tool install was attempted.


## Parent corpus observations kept separate from native proof

The parent-produced `mode-probe.json` (11 fixtures) supplies the independent timing/reset experiment. This report did not rerun it. Parent reports 301 player0431 records, none within0.25 seconds of a same-actor resource10 ADD1; M1 examples are resource10 ADD1 at151.9180145263672 followed by0431 at153.75604248046875 (1.8380279541015625 seconds), and336.5126037597656→338.349853515625 (1.837249755859375 seconds). Those example timestamps are present in the saved JSON. Parent also reports resource9/12/15 SET0 on the same actor/timestamp as resource10 ADD1.

This fits a later numeric-state transition and resettable counters; it is not proof that0431 is the statistical death instant. Native SET/ADD semantics independently explain why SET0 is a reset. Do not sum or fold a resettable resource and present it as a lifetime total without deriving the intended metric. In particular, retain resource9 as an unnamed resource/kills-correlated candidate, resource10 as a deaths-correlated candidate, and attribute0x29/0x2a (decimal41/42) as separate attribute candidates.

A final bounded registry search inspected10045.c and1003e.c, plus the earlier1003a/1003d/10034/10046 sources, globals and header for Resource/resource, streak, kills/deaths/assists symbols and resource-slot offsets. No registry mapping selectors9/10/11 to English names was recovered. Nearby identical offsets in other component structures were not treated as resource evidence. Resource names, cumulative/streak distinctions and cross-version compatibility remain explicit unresolved links.

## Binary follow-up

The one community-modified VGNA iOS candidate was checked against the bounded download condition; its1.73GB IPA exceeds250MB, so exact vtable slots remain unread. See [native-binary-followup.md](native-binary-followup.md) for current manifest/HEAD evidence and build/hash mismatch cautions.
