# Binary event candidate evidence

This snapshot accompanies [the 161-code catalog](../../vg-binary-event-candidates-2026-09-09.md) and [per-code validation requirements](../../vg-binary-event-candidates-2026-09-09-details.md).

The analysis targets Windows PE32 SHA-256 `659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`, image base `00400000`, dispatcher `004cfec0`. It combines 123 receiver handlers, 111 fixed-header formatters and 85 corpus-observed opcodes into 161 unique candidates. The catalog retains 147 related native vtables and 22 unclassified `htons` reference functions. It does not claim all versions, all server-side events or complete field semantics.

## Included evidence

- `branches/`: all 123 extracted receiver branch bodies. `source-branches.json` retains source line ranges, branch body hashes, calls, copies, shared-label references and links to these excerpts. Shared-label call metadata can refer to private source tails outside an excerpt; the excerpt alone does not prove those complete paths.
- `native/dispatcher-coverage.json`: raw PE jump-index and target table coverage, default ranges and source/machine comparison.
- `native/native-inventory.json`: selected vtable slots, references, constructor stores, packet labels and decompilation completion metadata. The 701 complete decompilations are private inputs and are not included.
- `native/htons-references.json`, `packet-emitters.json`, `outbound-candidates.json` and `htons-import-provenance.json`: all recovered references to the selected import, formatter constants, transport edges and request-class links. Instruction excerpts are bounded evidence, not the executable.
- `corpus/opcode-summary.json`: counts, every observed payload length and anonymized sample locators, without raw payload bytes.
- `corpus/provenance.json`: C01–C56, section hashes, record counts and original clock verdicts; no source filenames or player names. Totals are 56 recordings, 7,870 sections and 30,729,156 records.
- `corpus/validation.json` and `cli-checks.json`: results of the original corpus scan and independent exemplar checks. These were produced before publication, not rerun by packaging.
- `validation-plans.json`: unresolved questions, offline work, runtime scenarios, negative controls and pass criteria.

## Verification and reproduction boundaries

From the repository root, run:

```sh
python vg/docs/evidence/2026-09-09-binary-events/verify_bundle.py
```

The verifier checks distributed hashes, candidate-set arithmetic, CSV/JSON agreement, branch-body hashes, corpus totals and source hash links. It requires only the standard library and does not open a game or private data. Passing it establishes publication consistency, not native or gameplay truth.

To repeat the underlying native investigation, obtain the exact executable hash above, import PE32 at the recorded image base in Ghidra 12.1.3, recover dispatcher `004cfec0` and its index/target tables, and inspect all references to IAT `0120a648` (`WS2_32.dll`, ordinal 9). Check fixed u16 length/opcode constants, `[2, 2, length-2]` copies and edges to `004eb3f0` or `004cfea0`; retain unclassified functions. Follow recorded constructor stores and vtable slots for each proposed class link. Each JSON row provides addresses and conditions for targeted reproduction.

To repeat corpus observations, use the private C01–C56 source manifest and the section hashes in `corpus/provenance.json`, read all sections in numeric order with strict `vg.core.vgr_records.iter_records`, count opcodes and payload lengths, and independently read sample header locators. The decoder baseline was commit `018dfd227abc704ad3c281bacd9b203af2d2e108`. The original scan-script hashes are retained for provenance; those private-path orchestration scripts are not shipped as runnable tools here. The game and private corpus are required for their respective new experiments, not for bundle validation.

`manifest.json` distinguishes original artifact hashes from distributed hashes. The catalog's `source_hashes` uses distributed paths/hashes; `original_source_hashes` retains the source snapshot before path normalization. Original dispatcher source hashes and line numbers refer to the undistributed complete decompilation. Candidate semantics and observation numbers were not changed during publication. Existing runtime validation and the follow-up scenarios remain separate.
