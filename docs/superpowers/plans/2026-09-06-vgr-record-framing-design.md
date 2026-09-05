# VGR record framing before semantic reconstruction

User direction: redo questionable binary reverse engineering; treat VGNA as a fallible comparative implementation, never as ground truth. This step establishes the raw record boundaries and provenance needed to compare interpretations.

## Verified raw evidence

Sequential probing from offset0, with no signature search or resynchronization, consumes7,870 real .vgr files /1,044,589,605bytes as30,729,156 records. Each record is `[timestamp:f32BE][content_length:u32BE][opcode:u16BE][payload:content_length-2]`. Timestamp and length occupy8bytes; length includes the2-byte opcode. All bytes of every real file are consumed, no timestamp backsteps found by the probe.

5 files (880bytes), including4 apparent .0.vgr starts, are AppleDouble metadata: magic0x00051607, __MACOSX/._ paths. They are not replays. Thus60 start paths previously counted are56 real replay starts.

Existing `08 04 31` signature spans the low byte of content length8 plus opcode0x0431. Entity is a4-byteBE field at payload0 (current values fit16bits); the opcode's8-byte content has no timestamp. Its time is at record start. Old death timestamp at signature+9 reads the next record header's timestamp. Of2209 structurally matched player0x0431 records,1 shows a different next timestamp (32.58894vs32.69308). This is a framing observation, not proof that every0x0431 means death. Existing30-minute cap also drops44 matching late death candidates and erases41 kill-candidate timestamps across8 replays. No semantic counting changes in this step.

## Required output

A small reusable, strict record iterator and an independently runnable structural audit CLI, with no imports of VGRParser/KDADetector and no gameplay labels. Preserve every old decoder untouched. The new reader exposes record offset, owning timestamp, declared content length, opcode and payload view; it never reads the next record to derive current time. It supports finite times beyond1800s, content lengths beyond255, unknown opcodes, and payload bytes that resemble old signatures.

Malformed framing must fail with byte offset (partial8-byteheader, size<2, body beyondend, non-finite timestamp). No random resync, endian fallback, external requests or implied field repair. Empty bytes yields no records. Independent files are parsed separately.

Audit file/directory paths, count actual records/opcodes/lengths, exclude only positively identified AppleDouble magic, report complete-file consumption and errors, never print payload bytes/player names. Invalid/empty input set must return CLI error, framing errors nonzero; successJSON can be saved with-o. No new dependencies; unittest.

## Scope

New files only: vg/core/vgr_records.py, vg/analysis/record_framing_audit.py, tests/test_vgr_records.py, tests/test_record_framing_audit.py, vg/docs/RECORD_FRAMING_2026-09-06.md. Existing six dirty docs are not touched. Work in the existing remote folder on codex/vgr-record-framing-20260906. Parent runs real corpus and owns public-source comparison/report; worker tests small fixtures and self-reviews. No push/merge/game actions.
