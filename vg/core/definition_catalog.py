"""Read user-owned 32-bit CFF definition manifests, without modifying assets.

This is an explicitly configured build profile, not a universal CFF decoder.
No executable keys, resources, or guessed definition names are bundled.
"""
from dataclasses import dataclass
import hashlib
import struct


class CatalogError(ValueError):
    pass


def _span(data, offset, size):
    if offset < 0 or size < 0 or offset > len(data) - size:
        raise CatalogError(f"out-of-bounds range {offset}+{size}")
    return data[offset:offset + size]


def _u32(data, offset):
    return struct.unpack('<I', _span(data, offset, 4))[0]


def _verify_hash(data, expected, label):
    if len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        raise CatalogError(f"{label} requires a lowercase SHA-256")
    if hashlib.sha256(data).hexdigest() != expected:
        raise CatalogError(f"{label} SHA-256 mismatch")


def _key_at_va(executable, va):
    if _span(executable, 0, 2) != b'MZ':
        raise CatalogError('not a PE executable')
    pe = _u32(executable, 60)
    if _span(executable, pe, 4) != b'PE\0\0':
        raise CatalogError('invalid PE signature')
    count = struct.unpack('<H', _span(executable, pe + 6, 2))[0]
    optional_size = struct.unpack('<H', _span(executable, pe + 20, 2))[0]
    optional = _span(executable, pe + 24, optional_size)
    if len(optional) < 32 or optional[:2] != b'\x0b\x01':
        raise CatalogError('only PE32 profiles are supported')
    rva = va - _u32(optional, 28)
    sections = _span(executable, pe + 24 + optional_size, count * 40)
    matches = []
    for at in range(0, len(sections), 40):
        start = _u32(sections, at + 12)
        raw_size = _u32(sections, at + 16)
        if start <= rva and rva + 4 <= start + raw_size:
            matches.append(_span(executable, _u32(sections, at + 20) + rva - start, 4))
    if len(matches) != 1:
        raise CatalogError('key VA must map to exactly one file-backed section')
    return matches[0]


def _mask_constant(key, length):
    # Native lookup2 mixing for an exactly four-byte key, seeded by INST length.
    mask = 0xffffffff
    a = (0x9e3779b9 + int.from_bytes(key, 'little')) & mask
    b = 0x9e3779b9
    c = (length + 4) & mask
    for right, left, last in ((13, 8, 13), (12, 16, 5), (3, 10, 15)):
        a = ((a - b - c) & mask) ^ (c >> right)
        b = ((b - c - a) & mask) ^ ((a << left) & mask)
        c = ((c - a - b) & mask) ^ (b >> last)
    return c


@dataclass(frozen=True)
class BuildProfile:
    build_sha256: str
    manifest_sha256: str
    key_table_va: int
    version: int
    definition_count: int
    architecture: int = 0


@dataclass(frozen=True)
class Definition:
    index: int
    name: str
    kind: str = 'unknown'
    serialized_name: str = ''


@dataclass(frozen=True)
class DefinitionCatalog:
    profile: BuildProfile
    definitions: tuple

    def lookup(self, index):
        if not isinstance(index, int) or not 0 <= index < len(self.definitions):
            raise CatalogError(f'definition index out of range: {index}')
        return self.definitions[index]


def load_catalog(manifest: bytes, executable: bytes, profile: BuildProfile):
    """Validate hashes, container, selected INST and relocations; return names.

    definition_count is explicit profile evidence, never guessed from string IDs.
    Only the configured 32-bit DEF0 architecture is interpreted. Other chunk
    envelopes are checked but their native object layouts are not interpreted.
    """
    _verify_hash(manifest, profile.manifest_sha256, 'manifest')
    _verify_hash(executable, profile.build_sha256, 'build')
    if profile.definition_count <= 0 or not 0 <= profile.version <= 255:
        raise CatalogError('invalid count or version')
    if _span(manifest, 0, 4) != b'CFF0' or _u32(manifest, 4) != len(manifest):
        raise CatalogError('invalid CFF0 signature or length')
    if _u32(manifest, 12) != 0x0201 or _u32(manifest, 16) != 0:
        raise CatalogError('unsupported CFF format version/flags')
    count = _u32(manifest, 8)
    if not 1 <= count <= 11 or not 0 <= profile.architecture < count:
        raise CatalogError('invalid architecture count/index')
    offsets = [_u32(manifest, 20 + i * 4) for i in range(count)]
    if offsets[0] != 64 or offsets != sorted(set(offsets)):
        raise CatalogError('invalid architecture offsets')
    _span(manifest, 0, 64)
    selected = None
    for arch, start in enumerate(offsets):
        end = offsets[arch + 1] if arch + 1 < count else len(manifest)
        header = _span(manifest, start, 16)
        if header[:4] != b'DEF0' or _u32(header, 4) != 16 or start + 16 >= end:
            raise CatalogError('invalid DEF0 header')
        chunks = {}
        at = start + 16
        while at < end:
            tag = bytes(_span(manifest, at, 4))
            size = _u32(manifest, at + 4)
            if size < 8 or at + size > end or tag not in (b'INST', b'PTCH', b'SYMB') or tag in chunks:
                raise CatalogError('invalid, duplicate, or unsupported chunk')
            chunks[tag] = _span(manifest, at + 8, size - 8)
            at += size
        if at != end or set(chunks) != {b'INST', b'PTCH', b'SYMB'}:
            raise CatalogError('incomplete architecture')
        if arch == profile.architecture:
            if header[8] != 1 or header[9] != profile.version:
                raise CatalogError('unsupported architecture/version profile')
            selected = chunks
    blob = bytearray(selected[b'INST'])
    length = len(blob)
    key = _key_at_va(executable, profile.key_table_va + profile.version * 4)
    constant = _mask_constant(key, length)
    previous = length
    for at in range(0, length // 4 * 4, 4):
        value = _u32(blob, at)
        rotation = ((previous << 1) | (previous >> 31)) & 0xffffffff
        struct.pack_into('<I', blob, at, constant ^ rotation ^ value)
        previous = value
    patch = selected[b'PTCH']
    reloc_count = _u32(patch, 0)
    expected_patch = 8 + reloc_count * 8
    if (len(patch) < expected_patch or len(patch) - expected_patch >= 16
            or any(patch[expected_patch:]) or _u32(patch, 4) != 0):
        raise CatalogError('invalid PTCH length/header')
    relocations = {}
    for i in range(reloc_count):
        at, target = struct.unpack('<II', _span(patch, 8 + i * 8, 8))
        if at == target == 0:
            continue
        _span(blob, at, 4)
        _span(blob, target, 1)
        if at % 4 or at in relocations:
            raise CatalogError('unaligned or duplicate relocation')
        relocations[at] = target
        struct.pack_into('<I', blob, at, target)
    def pointer(at):
        if at not in relocations:
            raise CatalogError(f'missing relocation at {at}')
        return relocations[at]
    table = pointer(0)
    _span(blob, table, profile.definition_count * 4 + 4)
    if _u32(blob, table + profile.definition_count * 4) != 0:
        raise CatalogError('definition count does not end at null sentinel')
    definitions = []
    for index in range(profile.definition_count):
        entry = pointer(table + index * 4)
        name_at = pointer(entry)
        end = blob.find(0, name_at, min(len(blob), name_at + 1025))
        if end < 0:
            raise CatalogError('unterminated or oversized definition name')
        try:
            name = blob[name_at:end].decode('ascii')
        except UnicodeDecodeError as exc:
            raise CatalogError('non-ASCII definition name') from exc
        if not name or any(ord(c) < 32 or ord(c) > 126 for c in name):
            raise CatalogError('invalid definition name')
        definitions.append(Definition(index, name.strip('*'), serialized_name=name))
    return DefinitionCatalog(profile, tuple(definitions))


SUPPORTED_BUILD_SHA256 = '659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642'

def supported_build_profile(build_sha256: str, manifest_sha256: str):
    """Observed Windows PE32 profile. Manifest hash is a user trust assertion.

    Callers must establish that their manifest belongs to this executable;
    hashing two arbitrary files does not prove that pairing.
    """
    if build_sha256 != SUPPORTED_BUILD_SHA256:
        raise CatalogError('unsupported build SHA-256')
    return BuildProfile(build_sha256, manifest_sha256, 0x01e3f978, 12, 932)


def main(argv=None):
    """Inspect a local catalog as JSON; stdout only, never rewrite source files."""
    import argparse
    from dataclasses import asdict
    import json
    from pathlib import Path
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--executable', required=True, type=Path)
    parser.add_argument('--build-sha256', required=True)
    parser.add_argument('--manifest-sha256', required=True,
                        help='Expected hash of a manifest independently paired with this build')
    parser.add_argument('--index', type=int, action='append', help='Definition index; repeat to select multiple')
    args = parser.parse_args(argv)
    try:
        profile = supported_build_profile(args.build_sha256, args.manifest_sha256)
        catalog = load_catalog(args.manifest.read_bytes(), args.executable.read_bytes(), profile)
        definitions = [catalog.lookup(index) for index in args.index] if args.index else catalog.definitions
        print(json.dumps({'profile': asdict(profile), 'definition_count': len(catalog.definitions),
                          'definitions': [asdict(item) for item in definitions]}, indent=2))
    except (OSError, CatalogError) as exc:
        print(f'catalog: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
