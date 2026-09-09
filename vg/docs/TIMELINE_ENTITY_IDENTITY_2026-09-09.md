# Optional prior definition observations in the timeline

The native timeline accepts a user-owned, build-bound catalog. Without catalog
arguments, its row schema and decoding behavior are unchanged. Native decoding
now lives in `vg/analysis/native_event_fields.py`; existing imports of
`decode_fields`, `DecodedFields`, `KnownOpcode`, and decoder constants from
`vg.analysis.event_timeline` remain available.

## CLI and library

```text
python -m vg.analysis.event_timeline replay.0.vgr --opcode 0x0430 --entity 2007 \
  --manifest /path/to/owned/manifest --executable /path/to/owned/Vainglory.exe \
  --build-sha256 EXPECTED_EXECUTABLE_SHA256 \
  --manifest-sha256 EXPECTED_PAIRED_MANIFEST_SHA256
```

All four catalog flags are required together. Hashes are lowercase SHA-256.
The caller asserts that the recording came from this build and that the manifest
belongs to the executable; hashes alone cannot authenticate that pairing.
The supported profile is the observed Windows PE32 build
`659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`.
Assets are read-only and must not be redistributed. Unsupported profiles, wrong
hashes, missing assets and invalid catalog structures return exit 2 before the
output is opened. Output paths that alias an input section, manifest, executable or supplied
Actor resource are rejected. A malformed later replay record can still leave a partial JSONL stream;
consumers must check the exit code.

For the library, load and validate a `DefinitionCatalog`, then pass it as
`iter_timeline(path, catalog=catalog, build_sha256=expected_hash)`. Those two
keyword arguments must be supplied together and match. The resolver is created
fresh for each iterator and never shared across recordings. `recording_id` is a
resolved directory/prefix locator, not a content hash or authenticated identity.

## Evidence meaning

All strict records feed the resolver in section/offset order before opcode and
entity filtering. A decoded `ref0` or `ref1` gains a corresponding
`ref0_identity` or `ref1_identity` object. Its `evidence_scope` is always
`prior_spawn_observation`. Resolved observations preserve definition index/name,
raw spawn payload, source opcode, section, offset, timestamp, build/manifest
hashes and the previous observation link. They do not claim the actor remains
alive or that a repeated spawn establishes a new lifetime. Definition changes
and repeated observations remain explicit.

Unobserved IDs, out-of-range definition indices and the `0xffffffff` sentinel
remain unresolved. Sentinel references cannot acquire an identity even if a
spawn happens to contain that integer. Broad `kind` remains `unknown` unless a
checked Actor resource establishes a supported native kind. Optional resource
enrichment adds `kind_evidence` with the resource hash, exact serialized name,
type key, root offset and raw kind; see [Actor-resource kind evidence](ENTITY_RESOURCE_KIND_2026-09-09.md). Owner and credited-player fields remain null;
the raw death source is not renamed to a credited killer. Only observed spawn
payload lengths 122/126 for 03f2 and 746/750 for 03f3 are accepted in catalog
mode; unsupported layouts fail even if those opcodes were filtered out.

## Validation on 2026-09-09

The full suite passed once: 346 tests in 39.141 seconds, using a temporary
copy of the original private truth fixture (31,685 bytes). The owned copy was
removed after the run; its original was unchanged. Full output is
`work/entity-catalog-stage2/full-suite.log`.

45 focused unittest cases passed across timeline, native semantics, ActorDie,
end-match, catalog, resolver and the new timeline-identity suite. The eight new
cases cover re-export/output equivalence, filters and no future resolution,
numeric sections/repeated observations/recording isolation, sentinel/missing
definitions, unsupported spawn layouts, build argument contracts, CLI input
errors and preservation of source assets.

The real CLI consumed 121 original endgame-combat-backup sections. Filtering
ActorDie opcode **0430** and entity 2007 produced 20 rows in each
mode, with exit 0. The extracted decoder also produced byte-identical CLI
output to the pre-extraction HEAD. Removing the added identity objects gave
exact legacy row values. At recording timestamp 978.1154174804688, section 97, offset 100334,
`1500 <- 2007` links to prior observations of `Amael` (925) and
`VainCrystal_Away_5v5` (296). The source observation is section 97, offset 15603,
timestamp 970.00927734375. Its transition is
`repeated_spawn_lifetime_unknown`; this is not a lifetime or screen-time claim.

Reproducible local evidence is in `work/entity-catalog-stage2/`:
`timeline_cli_proof.py`, `timeline-cli-proof.json`, `timeline-legacy.jsonl`,
`timeline-enriched.jsonl`, `timeline-baseline-proof.json`, `timeline-tests.log`.
The two implementation modules contain 203 and 149 nonblank, noncomment,
non-docstring lines respectively. These paths are evidence artifacts, not bundled assets.
Screen comparison for two entity types and exact lifetime semantics remain
separate acceptance work. No native-stat or final-completeness policy changed.

## Subsequent lifecycle evidence

The resolver now also observes the exact six-byte payload of `040b`
`ActionEntityDestroy`. Historical spawn identity is retained, with separate
lifecycle evidence for a destruction action and a later spawn observation.
This does not prove that native removal completed at the record timestamp.
The optional explicit `--opcode 0x040b` selection decodes the entity ID and
preserves the opaque two-byte tail; the default opcode set stays unchanged.
See [native lifecycle evidence](ENTITY_LIFECYCLE_2026-09-09.md) and
[native kind provenance](ENTITY_KIND_NATIVE_2026-09-09.md).

## Subsequent Actor-resource evidence

Repeatable `--entity-resource INDEX PATH SHA256` arguments enrich selected
definitions after the four catalog flags validate the paired manifest and build.
The native Actor type key and factory/root relationship are now established
statically. Native kind 0 maps to `hero`, 2/3 to `structure`, and all other values
remain `unknown` with the raw integer preserved. Definitions without a supplied
resource remain unknown. See [resource contract and validation](ENTITY_RESOURCE_KIND_2026-09-09.md).

The Windows CLI read the same 121-section recording with nine checked resources.
The 20 selected ActorDie rows preserved their raw values exactly against both
the un-enriched run and the prior baseline. At section 97, offset 100334, the
prior Amael observation has `kind: "hero"`; the crystal source observation has
`kind: "structure"` and native kind 2. Credited-player fields remain null. This
follow-up passed 376 full-suite tests and the CLI/library checks documented in
the resource contract. It did not add a screen or live-state assertion.
