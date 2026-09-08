# VGR Record Framing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish byte-exact VGR records and reproducible structural auditing before changing gameplay semantics.

**Architecture:** A strict zero-copy iterator reads each file from offset0 using declared record lengths. An audit CLI consumes this iterator without legacy decoders, reports coverage and malformed inputs, and identifies AppleDouble metadata by its magic. Existing gameplay output stays untouched.

**Tech Stack:** Python3.13.2, standard library/unittest.

**Spec:** `docs/superpowers/plans/2026-09-06-vgr-record-framing-design.md`

## Global Constraints

- No new dependencies, no legacy parser/KDA imports in the new reader or auditor.
- No gameplay labels, inferred semantic corrections, clock caps, random resync, external requests, payload/player-name logging.
- New files only; preserve existing code and the six dirty user documents. Stage exact owned paths on the feature branch. No push/merge/game actions.
- VGNA and HackedGlory are fallible references; raw boundary coverage does not prove opcode semantics or statistic accuracy.

### Task 1: Strict record iterator and structural audit

**Files:** Create `vg/core/vgr_records.py`, `vg/analysis/record_framing_audit.py`, `tests/test_vgr_records.py`, `tests/test_record_framing_audit.py`, `vg/docs/RECORD_FRAMING_2026-09-06.md`.

**Interfaces:** `iter_records(data: bytes)` yields immutable `VGRRecord` values with `offset`, `timestamp`, `content_length`, `opcode`, `payload` (memoryview). `VGRRecordError(ValueError)` carries `offset`. `audit_path(path: Path) -> dict` returns JSON-serializable structural counts; `main(argv=None) -> int` accepts path and optional-o.

- [x] Step1: Red-first tests for true boundaries and timestamps. The fixture packer is independent:

```python
def packet(ts,opcode,payload=b''):
    body=struct.pack('>H',opcode)+payload
    return struct.pack('>fI',ts,len(body))+body

data=packet(2001.0,0x0431,bytes.fromhex('000005dc0000'))+packet(2002.0,0x041d,b'\x08\x04\x31')
records=list(iter_records(data))
self.assertEqual([r.timestamp for r in records],[2001.0,2002.0])
self.assertEqual([r.offset for r in records],[0,16])
self.assertEqual([r.content_length for r in records],[8,5])
self.assertEqual([r.opcode for r in records],[0x0431,0x041d])
self.assertEqual(bytes(records[1].payload),b'\x08\x04\x31')
```

Also test unknown opcode0xFFFF with payload300bytes, empty input, each partial header length1..7, body truncation, lengths0/1, NaN/±infinity timestamps, and correct error offset when a valid packet precedes a malformed one. Do not impose an1800-second cap or assign opcode names.

- [x] Step2: Implement the iterator's frame walk. Use memoryview and checked bounds; each iteration starts exactly at the preceding end.

```python
offset=0
while offset<len(data):
    # require remaining>=8; unpack >fI; require finite time and size>=2
    # require size<=len(data)-offset-8; opcode is >H at offset+8
    # yield record with payload memoryview(data)[offset+10:offset+8+size]
    offset += 8 + size
```

Actual production implementation must raise VGRRecordError with the failing record offset on invalid header/body, not silently stop. Zero-copy payload must not be converted into per-record bytes during iteration.

- [x] Step3: Implement structural CLI tests using TemporaryDirectory and small actual packet files. Include a valid file with2records, a second valid file, an AppleDouble file withmagic0x00051607 and .vgr extension, and a truncated .vgr. Assert counts, opcode/length histograms, excluded metadata count, valid consumption, malformed error offset and nonzero CLI exit. Check missing path/no .vgr files fail. Verify-o writes parseable JSON and--help returns0. Do not serialize payloads.

- [x] Step4: Implement audit_path/main. A single file or recursively found*.vgr directory files are accepted. Detect metadata by first4bytes, not filename alone. Suggested summary keys: `schema_version`, `files_seen`, `replay_files`, `replay_starts`, `apple_double_files`, `files_fully_consumed`, `records`, `bytes`, `consumed_bytes`, `opcode_counts`, `content_lengths`, `errors`. Key names may be adjusted consistently across tests/docs, and must be described in the report. Count real .0.vgr starts only after metadata exclusion. Errors include relative file path, record offset, reason; summaries never include payload/player names. Count records parsed before a framing failure but never mark that file fully consumed. Audit success requires at least1 real file and0 malformed files; metadata-only input fails. Existing real files are read-only; write output only when-o is requested.

- [x] Step5: Document observed framing, distinction from opcode semantics, full-byte coverage from controller's independent probe, metadata count correction, the next-record timestamp problem, and fallible source policy. Run targeted then full unittest. Commit only the5owned files with an Englishfeat: message and report red/green evidence plusSHA. Controller owns final real corpus run, final review and report; do not run30million-record corpus inside the worker.

## Controller acceptance

Run the delivered CLI over the real root on winsrv and require7,870 real files,56 starts,5 excluded AppleDouble files,30,729,156 records,1,044,589,605 consumedbytes and0 framingerrors. Verify actual old-signature bytes correspond to length+opcode, demonstrate an owning/next timestamp counterexample, and preserve old decoder outputs by absence of any changed existing source. Task and whole-branch reviews must pass. Save plan, report, auditJSON and patch in local Codex outputs. No unsupported assertion that gameplay semantics are now solved.

## Completed evidence

Implementation01273ee3f5a1bf3c83784fcf5e8f7dffee2897ec. Targeted14/full235 tests pass. Actual CLI consumed7,870files/30,729,156records/1,044,589,605bytes with0errors;5AppleDouble files excluded and56true starts. Task review approved with one low test-coverage observation; controller manually verified CLI missingargument/missingpath/emptydirectory exit2. Existing semanticdecoders untouched. Detailed findings and fallible-source policy:vg/docs/BINARY_REINVESTIGATION_2026-09-06.md.
