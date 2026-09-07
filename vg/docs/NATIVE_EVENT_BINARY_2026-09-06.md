# Native event binary verification

**Provenance correction (2026-09-07):** Per the user clarification, VG:NA is a community-modified redistribution, not the original official client. The inspected engine was extracted from a VG:NA iOS IPA; the separate original official Android APK was not inspected. Handler links and KDA mappings below are established for this specific VG:NA engine only. Their equivalence to the original official client and the replay-producing build remains unverified. Agreement with public decompiled material does not independently authenticate the original official implementation.

**Current status:** The later named-getter trace in `NATIVE_STAT_LABELS_2026-09-06.md` confirms attribute41/0x29=myKills, attribute42/0x2a=myDeaths, and resource11/0x0b=myAssists. References below to those names being unresolved describe the earlier investigation stage. Resource9/10, actor-state names, and whole-build identity remain unconfirmed.


2026-09-06. Final result; the initial whole-archive size stop was resolved by targeted HTTP Range extraction.

## Range continuation — final result: exact four vtable links verified

A subsequent separately authorized bounded attempt used ZIP HTTP Range access to the **same archive**, superseding the earlier whole-IPA size stop. Total response-body bytes downloaded were **15,777,593** (15.78 MB), far below250MB. Only the game-engine entry was decompressed; it is **26,503,168 bytes**. No downloaded code was executed or installed. Parsing scripts and Apple's existing `otool` / `llvm-objdump` inspected it as data.

### Archive ranges and extracted member

The server honored every request with HTTP206 and the exact Content-Range. Each request sent the previously observed ETag in `If-Range` and `Accept-Encoding: identity`; the code would close before reading a body on a200 response. Archive Content-Length and ETag remained1729814907 / `"6a9a99f6-671ae17b"`.

|Purpose|Inclusive archive range|Response bytes|
|---|---|---:|
|EOCD tail|1729749350–1729814906|65557|
|Central directory|1723684604–1729814884|6130281|
|Engine local ZIP header|202418066–202418095|30|
|Compressed engine data|202418191–211999915|9581725|

EOCD is at1729814885, contains50634 entries, and names central-directory offset1723684604 / size6130281. The directory contains no entry whose basename is exactly `GameKindred`. It contains the separate small `VGNAHost` application and the actual game engine at:

`Payload/VGNAClient.app/Frameworks/GameKindredEngine.framework/GameKindredEngine`

Only that one plausible game engine was fetched. ZIP metadata: method8(raw deflate), flags8(data descriptor, **not ZIP encryption**), local header offset202418066, compressed size9581725, decompressed size26503168, CRC32 `71488f0b`. Decompression length and CRC match the directory. The output was written to fixed filename `native-binary/GameKindredEngine`; there was no extract-all or use of archive paths as filesystem paths.

Extracted engine SHA256: **`c23b2e9eb201f47694c7e71ab39d2c8c96850beb4ddf489745def23927fcd891`**.

Evidence: `range-log.json`, `zip-tail.bin`, `zip-central-directory.bin`, `zip-entries.json`, `range_extract.py`, `range_entry.py`. The first script stopped after the exact GameKindred filename was absent; the second reused the same saved directory and cumulative download log to fetch the framework engine. No second archive or alternative build was requested.

### Mach-O identity and matching scope

- Thin64-bit ARM64 Mach-O, filetypeMH_DYLIB.
- UUID **B51EBB99-1532-32DC-9FB0-3C8CD08B505A**.
- LC_ID_DYLIB: `@rpath/GameKindredEngine.framework/GameKindredEngine`.
- `__TEXT` VM base0x100000000, filesize0x1444000; `__DATA` VM0x101444000, file offset0x1444000. Thus each target vtable and function maps directly to file offset(VM−0x100000000).
- LC_ENCRYPTION_INFO_64 cryptoff32768, cryptsize21217280, **cryptid0**. The code is statically readable without decryption.
- Classic LC_DYLD_INFO_ONLY rebase stream at file25640960, length9056; parser recovered294727 rebase entries. **Every slot shown below, including0x0/0x8, is registered as pointer rebase type1.** These are ordinary preferred-image pointers to which the loader applies its slide, not unresolved imports or guessed pointer encodings.

A bounded literal-string search did not find147219. Therefore this report does **not** assert that the complete modified VGNA engine has an independently verified original build147219 identifier, nor that all its bytes equal the original HackedGlory executable. Instead, the exact addresses, constructor layouts, serializer constants, handler branches and virtual queue code for the four target opcodes were independently verified in the current community-distribution engine. This closes the relevant structural links without claiming whole-build identity.

Evidence: `macho-load-commands.txt`, `macho-identity.json`, `build-string-probe.json`, `inspect_macho.py`.

### Actual vtable values

All addresses are preferred-image VM addresses in the extracted engine. Raw little-endian pointer reads were checked against the Mach-O segment mapping and pointer-rebase stream.

|Opcode|Vtable base|slot+0x10 serializer|slot+0x18 apply|slot+0x20 copy/enqueue|
|---|---|---|---|---|
|0431|0x101496a38|0x1003d4490|**0x1003d451c**|0x100496aa8|
|041c|0x1014971e0|0x1003db71c|**0x1003db808 → 0x1003db80c**|0x1004969f4|
|041d|0x101497218|0x1003db9a0|**0x1003dba48**|0x100496328|
|042b|0x1014973d8|0x1003dcbd0|**0x1003dcc0c**|0x100497acc|

The041c actual table value is1003db808, not1003db80c. Instruction at1003db808 is `b 0x1003db80c` (`14000001`), closing that one-instruction thunk explicitly. The original C export named the thunk but omitted this exact start address in its symbolic function label.

### Fingerprint checks against pinned C semantics

`function-fingerprints.json` stores exact address/span/file-offset/SHA256/bytes for18 selected spans; `fingerprints-disassembly.txt` contains their bounded disassemblies. This is evidence of inspected machine operations, not a claim that a C decompile has a comparable byte hash.

1. **All four constructors match at exact expected addresses:**1003c6194 loads vtable101496a38 and writes entity to+1c;1003c4f68 loads1014971e0, writes integer fields at+1c/+20/+24/+28, floatS0 at+2c, byte at+30;1003a34f4 loads101497218, stores floatS0 at+24, mode byte+28 and flags+29;1003dcba4 loads1014973d8 and stores four bytes at+20..+23. These independently confirm that the apparent C undefined4 values at the value fields are ARM float arguments.
2. **Opcode encoder constants match at exact expected addresses:**100347060 builds0x31040600;100347e30 builds0x1c041100;100347f30 builds0x1d040e00;100348964 builds0x2b040a00. Their send-opcode immediates are correspondingly0x3104,0x1c04,0x1d04,0x2b04, reflecting little-endian construction of network opcode bytes.
3. **Queue entry and drain match:**100345498 loads vtable+20 and branches through it;1003454b8 reads object byte+18 and calls vtable+18 on the received-event path. This links the dispatcher-created object to the actual apply slots above.
4. **0431 apply:**1003d451c checks entity/current numeric state3 and requests state4 through10046211c. It does not directly increment a death statistic.
5. **041c apply:**1003db808 branches to1003db80c; that function branches on object mode byte+30 to1003db860(SET) or1003d9ff0(ADD). The target arithmetic at100463154 and100465300 matches the prior assignment/add traces.
6. **041d apply:**1003dba48 reaches1003dbaec; byte+28 branches to1003dbb54(SET) or1003d7388(ADD). Independent disassembly of1003dbb54 and1004653d8 confirms clamped assignment versus clamped old+value arithmetic.
7. **042b apply:**1003dcc0c loads the four bytes+20..+23 and calls1003d932c at instruction1003dcc78, matching the indexed state/mask mutation trace.

**Final implication:** the earlier missing-vtable qualification in `native-trace.md` is resolved for these four opcode handlers in this statically inspected engine. The English enum meanings of resource9/10/11, attribute0x29/0x2a, actor states3/4, and042b bits remain unproven. The native SET/ADD behavior and0431 state transition now have a closed constructor→vtable→handler link. The separate question of the VGR outer payload's extra bytes/version framing is not resolved by these pointer checks.

A bounded `__cstring` inventory is saved as `cstring-label-candidates.json` for a subsequent registry lookup. It finds `resourceName` at0x1013dd55c, `totalKills` at0x1013dabd6, `myAssists` at0x1013db718, `hud_stats_assists` at0x1013d0c43, and `HeroKilled` / multikill notification strings at0x1013ce529 onward. The scanned section had no killStreak/deathStreak literal match. These string addresses are verified, but **no string-to-resource/attribute-index mapping was traced**, so none establishes the English enum labels requested above.
