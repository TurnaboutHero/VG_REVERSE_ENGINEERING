#!/usr/bin/env python3
"""Verify selected clock evidence bytes against a supplied ARM64 ELF; stdlib only."""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def verify(binary, manifest):
    data = binary.read_bytes()
    if data[:6] != b'\x7fELF\x02\x01':
        raise ValueError('Expected ELF64 little-endian input')
    shoff = struct.unpack_from('<Q', data, 40)[0]
    entsize, count = struct.unpack_from('<HH', data, 58)
    sections = [struct.unpack_from('<IIQQQQIIQQ', data, shoff + i * entsize) for i in range(count)]
    evidence = json.loads(manifest.read_text())
    if hashlib.sha256(data).hexdigest() != evidence['binary_sha256']:
        raise ValueError('Binary SHA256 differs from analyzed artifact')
    for row in evidence['evidence']:
        address = int(row['address'], 16)
        expected = bytes.fromhex(row['hex'])
        matching = [s for s in sections if s[1] != 8 and s[3] <= address and address + len(expected) <= s[3] + s[5]]
        if len(matching) != 1:
            raise ValueError('Unmapped/ambiguous address: ' + row['address'])
        section = matching[0]
        offset = section[4] + address - section[3]
        if data[offset:offset + len(expected)] != expected:
            raise ValueError('Evidence byte mismatch: ' + row['name'])
    return len(evidence['evidence'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('elf', type=Path)
    parser.add_argument('--manifest', type=Path, default=Path(__file__).with_name('native-manifest.json'))
    args = parser.parse_args()
    try:
        count = verify(args.elf, args.manifest)
    except (ValueError, OSError, KeyError, struct.error) as exc:
        parser.exit(1, str(exc) + '\n')
    print(json.dumps({'result': 'PASS', 'checked_ranges': count, 'scope': 'static bytes only; no native execution'}))


if __name__ == '__main__':
    main()
