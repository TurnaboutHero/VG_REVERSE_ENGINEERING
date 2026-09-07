# Bounded native label trace: resourceName, totalKills, myAssists

**Android APK follow-up (2026-09-07):** The provenance correction below describes the earlier evidence state. A separately retrieved Android4.13.4(147219) archive APK has now passed hash/signature checks and its four opcode receive/apply paths and KDA field exports have been traced. The selected fields and core operations correspond to VG:NA; whole-client equivalence, all floating-point bit results, and replay-producer identity remain unverified. See [APK comparison](OFFICIAL_APK_COMPARISON_2026-09-07.md) and [binary identities](OFFICIAL_APK_COMPARISON_2026-09-07.json).

**Provenance correction (2026-09-07):** Per the user clarification, VG:NA is a community-modified redistribution, not the original official client. The inspected engine was extracted from a VG:NA iOS IPA; the separate original official Android APK was not inspected. Handler links and KDA mappings below are established for this specific VG:NA engine only. Their equivalence to the original official client and the replay-producing build remains unverified. Agreement with public decompiled material does not independently authenticate the original official implementation.

2026-09-06 KST. **Result: resource11 is the actor statistic exported as `myAssists`; attribute41/42 are exported as `myKills`/`myDeaths`. Resource9/10 English names remain unconfirmed.** `totalKills` is a match-actor aggregate of computed attribute41, not a direct resource9 read. `resourceName` is an icon/reward JSON field and supplies no resource-index registry here.

## Scope and evidence identity

This used only the previously extracted community-modified VGNA `GameKindredEngine` (SHA256 `c23b2e9eb201f47694c7e71ab39d2c8c96850beb4ddf489745def23927fcd891`, UUID B51EBB99-1532-32DC-9FB0-3C8CD08B505A) and two needed pinned decompile chunks. No additional IPA, executable installation, execution, subagents or implementation edits occurred.

The bounded scan found **five direct ADRP+ADD references** to the three target strings, below the fifteen-reference cap. It looked for exact64-bit pointers and same-register ADRP+ADD patterns within six instructions in the declared __text section. It is not a complete dataflow analyzer; absence of this pattern does not exclude every possible indirect reference. The five hits were then inspected in bounded disassembly and the corresponding source function. No exact64-bit pointer occurrences of the three string addresses were present in the binary.

`native-binary/10011.c` and `10014.c` were fetched at HackedGlory commit `0fdc6ddd65a6c0c8657d238d41668baa86debdf0`; Git blob hashes match the pinned tree. See `native-binary/label-source-manifest.json` and `label-xrefs.json`.

## Trace1 — resourceName: not the game resource enum registry

String address **0x1013dd55c**. Direct xrefs:

- ADRP0x100140d00 + ADD0x100140d04.
- ADRP0x100140e80 + ADD0x100140e84.

Both are in **FUN_1001406e0**, an object/JSON parsing routine. The relevant surrounding keys are `detailImage`, `level`, `freeTrack`, `iconRepresentations`, `resourceName`, `imageName`, `quantity`. It iterates the `iconRepresentations` JSON array, reads `resourceName` as a string and pairs it with image/quantity data. The other xref reloads the same key after calls within this parse path. No actor lookup, actor+0x40 access, or resource selector9/10/11 linkage is established by these references.

Thus this particular string's observed use is ruled out **as evidence for the requested actor resource-number mapping**. It does not prove that no other registry exists elsewhere.

Pinned proof: [parser entry](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10014.c#L167), [iconRepresentations/resourceName parsing](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10014.c#L434-L510). Binary evidence: `native-binary/resourceName-xrefs-disassembly.txt`.

## Trace2 — totalKills: aggregate computed actor attribute41

String address **0x1013dabd6**. Direct xrefs:

- ADRP0x100117874 + ADD0x100117878.
- ADRP0x100117ac8 + ADD0x100117acc.

Both occur in **FUN_100116f88**, which builds two keyed statistics objects. This is not inferred as a match statistic merely from the label. The source and machine-value path establish that it:

1. Obtains the selected actor through `FUN_100119128`, which matches an entity identifier in DAT_101dc7734 with `FUN_10034ee90`, then calls the same `FUN_100345d90(entity)` used by the packet handlers.
2. Enumerates actors into local_130 with `FUN_1003a6ce4` using an actor filter.
3. Reads each actor's `+0x40` component, calculates attribute41 from offsets+0xdc,+0x190,+0x244,+0x2f8, separates sums by `FUN_100345bbc(actor)` team selector versus the current actor's team, and adds the team sums.
4. Stores that sum under `totalKills` in both statistics objects. Neighboring exact string values are `myTeamKills` at0x1013db396 and `theirTeamKills` at0x1013db3b0.

Attribute arithmetic matches the existing attribute-layer layout:

`index=(0xdc−0x38)/4=41 (0x29)`; other layers are0xec+41*4=0x190,0x1a0+41*4=0x244,0x254+41*4=0x2f8.

The exact computed getter is `clamp((layer0 + layer1*(layer3+1))*(layer2+1), min[index], max[index])`. Machine instructions implement `fmla` twice, then `fminnm` with the per-index maximum and `fmaxnm` with the per-index minimum. Here layers0/1/2/3 are the arrays at component+0x38/+0xec/+0x1a0/+0x254. With zero other layers, the pre-clamp result equals layer0; that is a fixture assumption to verify rather than a universal simplification. It is not a read of resource9 at+0x32c or resource10 at+0x330. No English name for9/10 can be promoted from this label.

Pinned proof: [actor acquisition/filter](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10011.c#L7129-L7162), [actor loop and totalKills value](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10011.c#L7351-L7452), [second keyed output](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10011.c#L7508-L7517), [actor lookup](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10011.c#L8495-L8513).

Binary evidence: `native-binary/totalKills-xrefs-disassembly.txt`, `local-actor-lookup-disassembly.txt`. The C decompiler loses some NEON return assignments; the machine disassembly is authoritative for the arithmetic rather than treating its clamping globals as literal accumulated values.

## Trace3 — myAssists: resource11 confirmed

String address **0x1013db718**. Direct string-loading xref: ADRP0x100118084 + ADD0x100118088. The register is reused for two key insertions in **FUN_100116f88**.

The binary chain is explicit:

- **0x100117fa4:** `ldr x8,[x19,#0x40]` selects the actor's attributes/resources component.
- **0x100117ff0:** `ldr s15,[x8,#0x334]` reads the float statistic.
- **0x100118084–0x100118098:** prepares `myAssists`, calls keyed lookup/insertion `100101fac`.
- **0x10011809c:** moves v15 to v0; **0x1001180a0** calls float-value setter10052b18c.
- **0x1001180a4–0x1001180b8:** repeats the same named value into the second statistics object.
- The setter10052b18c marks value type3 then stores S0 at its value object's+0x20. It does not derive a different statistic.

The independently verified resource array begins at component+0x308; `(0x334−0x308)/4 = 11 (0x0b)`. This closes **actor resource11 → myAssists** without relying on Python names or fixture correlations. Source variables lVar11→lVar19→fVar41 follow the same exact read and keyed output. [component read and named output](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10011.c#L7771-L7812).

This actor-backed value is not shown here to be an account/profile lifetime-assists counter. Nor does the label alone guarantee that every fixture contains all updates or that all selectors use cumulative semantics. Resource11 retains the previously proven SET/ADD interpretation when reconstructed from041d.

### Additional direct labels in the same value block: kills/deaths attributes

No unrelated xref expansion was needed: immediately adjacent to the myAssists output, the same inspected block exports:

- **`myKills`** string0x1013d9ac6 from the low lane of the computed attribute pair starting at component+0xdc: **attribute41 (0x29)**.
- **`myDeaths`** string0x1013db70f from the high lane starting at component+0xe0: **attribute42 (0x2a)**.

Machine0x100117fac..0x100117fe8 loads/calculates those two lanes from all four attribute arrays.0x100117ff8 copies lane1 toS8;0x100118028..0x100118050 exports the low lane under myKills and S8 under myDeaths. The adjacent myKDApct expression also consumes kills, deaths and the resource11 float, but the exact value flow above is sufficient proof. These labels identify the exported **computed attributes**, not an unconditional interpretation of each raw041c delta as a fresh kill/death.

Binary evidence: `native-binary/myAssists-value-trace-disassembly.txt`, `myAssists-xrefs-disassembly.txt`; source [same value block](https://github.com/a1cnore/HackedGlory/blob/0fdc6ddd65a6c0c8657d238d41668baa86debdf0/ghidra_projects/GameKindred_decompile_output/structured/functions/10011.c#L7771-L7826).

## Final confidence and stopping boundary

|Requested/related mapping|Outcome|
|---|---|
|resourceName → numeric actor resource registry|No; observed reference is iconRepresentations JSON parsing|
|totalKills → resource9|Not established; observed value aggregates computed attribute41|
|myAssists → resource11|**Confirmed by direct actor component load and named value output**|
|myKills → attribute41/0x29|**Confirmed in the same inspected value block**|
|myDeaths → attribute42/0x2a|**Confirmed in the same inspected value block**|
|resource9 / resource10 English names|Unresolved; no names/streak mapping proved by these three label traces|

The bounded three-label task is complete. No broad all-opcode or all-string search followed. Source-only renderer/profile labels elsewhere were not used to fill the remaining9/10 gap. These verified mappings can inform KDA field selection together with correct event framing, SET/ADD mode, initial state and fixture coverage; they do not by themselves repair missing replay records.

The parent implementation can therefore decode041c attribute0x29/0x2a into **kills/deaths attribute updates**, preserving layer0..3 and SET/ADD mode, and041d resource0x0b into **assists resource updates**, preserving SET/ADD. Resource0x09/0x0a must remain separate resettable, empirically correlated candidates; the validated output labels do not read those slots.

For completeness, the selected-actor pointer was also followed in machine code:100116fc8 calls119128;100116fcc saves its return inX28;1001171f4 storesX28 atSP+0x20;100117da4 reloads that slot intoX19;100117fa4 dereferencesX19+0x40. This closes the actor-object origin of the myAssists/myKills/myDeaths component reads, rather than assuming an unrelated object with the same offsets. See `native-binary/stat-export-function-disassembly.txt` (one bounded function) and `stat-float-setter-disassembly.txt`.
