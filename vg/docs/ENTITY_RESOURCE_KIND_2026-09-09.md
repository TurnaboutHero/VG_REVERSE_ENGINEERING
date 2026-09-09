# Optional Actor-resource kind evidence

The timeline can enrich selected manifest definitions from user-owned Actor CFF
resources. The native type-to-factory proof and flag branches are documented in
[native kind evidence](ENTITY_KIND_NATIVE_2026-09-09.md). Resource kind evidence
supplements the existing prior-spawn identity; it does not establish current
life, owner, kill credit, screen timing, or final statistics.

## CLI and library

```text
python -m vg.analysis.event_timeline replay.0.vgr --opcode 0x0430 --entity 2007 \
  --manifest /path/to/owned/manifest --executable /path/to/owned/Vainglory.exe \
  --build-sha256 EXPECTED_EXECUTABLE_SHA256 \
  --manifest-sha256 EXPECTED_PAIRED_MANIFEST_SHA256 \
  --entity-resource 925 /path/to/owned/amael-resource EXPECTED_AMAEL_SHA256 \
  --entity-resource 296 /path/to/owned/crystal-resource EXPECTED_CRYSTAL_SHA256
```

`--entity-resource INDEX PATH SHA256` can be repeated for different definition
indices. All four catalog flags are required whenever it is used. The index is
parsed as an integer with Python base-0 notation, including decimal or `0x` hex;
duplicate indices are rejected. The index belongs to the supplied manifest and
is not a global entity-ID constant. Each hash is a lowercase SHA-256 of the
original resource. The caller must independently establish the recording,
executable, manifest and resource pairing; matching hashes cannot authenticate
that relationship.

In the library, load the catalog, then call
`enrich_definition(catalog, index, resource_bytes, executable_bytes, resource_sha256)`
from `vg.core.definition_catalog`. It returns a new immutable catalog and leaves
the original catalog and its manifest provenance intact. Pass the enriched
catalog to `iter_timeline` with its matching `build_sha256`.

Without catalog flags, timeline rows are unchanged. A catalog without additional
Actor resources retains `kind: "unknown"` and `kind_evidence: null` on resolved
spawn observations. An unobserved or sentinel reference has no kind evidence.
Resources enrich only their selected definitions, regardless of output filters.

## Supported profile and checked fields

Catalog enrichment requires the exact supported Windows PE32 profile:
executable SHA-256
`659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`,
key-table VA `01e3f978`, version 12, definition count 932 and architecture 0.
The manifest hash remains a caller assertion. Altering another field of this
profile is rejected even if the executable hash is supported. The low-level
`load_cff` and `load_entity_kind` readers accept explicit layout parameters for
research; using them directly with another profile does not establish support
for that build.

The shared CFF reader checks executable/resource hashes, file and architecture
envelopes, selected architecture code/version, chunks, decoded INST bounds and
PTCH relocation ranges, alignment and duplicates. The Actor reader requires:

- SYMB type `0x2419fb6c`, established as the native `Actor` descriptor key.
- A nonempty NUL-terminated printable ASCII symbol name of at most 1024 bytes,
  followed only by zero padding.
- Exact equality with the manifest's `serialized_name`, including any `*`.
- A four-byte-aligned root with room for the 520-byte serialized Actor layout.
- A root kind field that is a scalar uint32, not a relocated pointer.

The current reader accepts exactly one INST, PTCH and SYMB chunk per architecture.
Single-SYMB support and the stricter name/padding checks are reader limitations,
not claimed native rules. Native loader tracing permits up to 32 separate SYMB
chunks and uses `strlen`; it does not prove this reader's maximum name length or
zero-only trailing padding requirement.

The reader maps native value **0 to `hero`**, **2 or 3 to `structure`**, and every
other value to **`unknown`** while retaining the raw integer. No name substring,
filename hash, spelling correction, or guessed resource path determines kind.

Invalid resources, names, hashes, indices and profiles return CLI exit 2 before
opening the output file. An output that aliases any supplied resource, manifest,
executable or replay section is rejected, including an existing hard link.
Malformed replay records discovered while streaming can still leave a partial
JSONL file; consumers must check the exit code.

## Output evidence

Every resolved prior-spawn identity keeps its existing build/manifest hashes
and gains `kind_evidence` when its definition has a checked Actor resource. This
nested object contains `build_sha256`, `resource_sha256`, `serialized_name`,
`symbol_type_id`, `root_offset`, `native_kind` and `kind`. Numeric fields are JSON
integers; for example, `symbol_type_id` represents `0x2419fb6c` as an integer.
The parent identity's `kind` is the same classification. Raw kinds outside the
mapping still have non-null evidence and `kind: "unknown"`.

Historical spawn evidence remains available after a destroy action. The separate
`lifecycle` observation does not erase or promote its kind evidence into a claim
that the actor is currently alive. Resolver state remains recording-scoped.
`owner_entity_id` and `credited_player_id` remain null, and the raw ActorDie
source is not relabeled as a credited killer.

## Observed resources and validation

The installed-resource inventory matched manifest names exactly against CFF
symbols. It found 942 selected-architecture symbols, including 233 Actor symbols.
Of 932 manifest entries with 929 distinct names, 926 entries and 923 distinct
names had exact symbol matches. Six names had no match; the reader applies no
repair or fallback. This inventory is discovery evidence, not validation of all
Actor kinds or support for every installed resource.

Nine selected resources were checked against the paired executable and manifest:

| Definition index | Name | Native kind | Exposed kind |
|---|---|---:|---|
| 240 | Hero000 | 0 | hero |
| 250 | SAW | 0 | hero |
| 296 | VainCrystal_Away_5v5 | 2 | structure |
| 297 | VainNode | 3 | structure |
| 331 | 5v5_Ghostwing | 4 | unknown |
| 332 | 5v5_Blackclaw_Uncaptured | 4 | unknown |
| 339 | Turret5v5 | 3 | structure |
| 340 | OuterTurret5v5 | 3 | structure |
| 925 | Amael | 0 | hero |

All nine use architecture 0/code 1, version 12, Actor type `2419fb6c`, root offset
zero and a scalar root kind. Resource hashes are in the
[public evidence JSON](evidence/2026-09-09-entity-kind.json); original binaries,
resource bytes, and private inventory paths are not bundled.

The Windows CLI and library checks completed successfully. The CLI consumed
121 original recording sections; `--opcode 0x0430 --entity 2007` produced 20 rows.
At section 97, offset 100334, prior observations identify Amael as a hero and
VainCrystal_Away_5v5 as a structure with native kind 2. Credited-player fields
remain null. Removing identity additions yielded exact raw-row equality with
both the un-enriched run and the prior baseline. Name-only catalog output kept
unknown kinds, and library enrichment preserved the original catalog.

CLI `--help` succeeded. Wrong-name, wrong-hash, non-Actor and output-alias inputs
returned exit 2 while preserving existing output and source assets. Before/after
hashes confirmed that the executable, manifest, replay sections and all nine
resources were unchanged. The full Windows suite passed **376 tests in 46.180
seconds**. Its temporary 31,685-byte private truth-fixture copy was removed after
the run; the original fixture and tracked caches were unchanged. Private QA
artifacts are `work/offline-kind-20260909/actual-kind-proof.json` and
`full-suite.log` in the owned Windows worktree.

No new game launch or screen comparison was performed for this offline work.
Two-type screen acceptance and broader monster/minion semantics remain separate
work.
