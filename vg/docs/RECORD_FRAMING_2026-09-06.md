# Raw VGR record framing

## Scope

This document describes structural record boundaries only. It does not assign gameplay meanings or names to opcodes. Comparative decoders, including VGNA, remain fallible sources and are not imported by the raw reader or audit.

## Observed frame

Records are walked sequentially from byte offset zero:

```
[timestamp:f32 BE][content_length:u32 BE][opcode:u16 BE][payload]
```

The eight-byte header contains the owning record timestamp and the declared content length. `content_length` includes the two-byte opcode, so the payload has `content_length - 2` bytes. The next record begins exactly `8 + content_length` bytes after the current record begins. Timestamps must be finite, but they are not capped at 1,800 seconds. Opcodes and content lengths are not restricted to a known semantic catalog.

The reader rejects a partial header, a content length below two, a body extending past the file, or a non-finite timestamp. It reports the byte offset where the failing record began and does not search for a later resynchronization point. Empty bytes produce an empty iterator.

## Independent corpus evidence

The controller's independent sequential probe consumed all 1,044,589,605 bytes of 7,870 real files as 30,729,156 records. Five additional `.vgr` paths (880 bytes) begin with AppleDouble magic `00 05 16 07` and are excluded as metadata. Four of those metadata paths appeared to be `.0.vgr` starts, correcting the real start count from 60 paths to 56.

The older byte signature `08 04 31` crosses fields: `08` is the low byte of content length eight and `04 31` is opcode `0x0431`. The record's timestamp is in its own header. Reading a float after that record instead can read the next record's timestamp; the controller observed one such counterexample, 32.58894 versus 32.69308. This establishes timestamp ownership and framing, not the gameplay meaning of opcode `0x0431`.

## Structural audit

Run `python -m vg.analysis.record_framing_audit PATH`, optionally with `-o FILE`. A directory is searched recursively for `*.vgr`; a single `.vgr` file is also accepted. AppleDouble files are recognized by their first four bytes rather than their names.

The JSON summary reports schema version, paths seen, real replay files and `.0.vgr` starts, excluded AppleDouble files, completely consumed files, record and byte totals, consumed bytes, opcode and content-length histograms, and framing errors. Each error contains only a relative path, failing record offset, and reason. Payloads and player data are never serialized. An audit exits nonzero for missing or empty input sets, metadata-only inputs, or any malformed real file.
