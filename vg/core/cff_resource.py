"""Checked CFF decoding for explicitly configured PE32 resource profiles."""
from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import struct
from types import MappingProxyType


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
class CFFResource:
    inst: bytes
    relocations: Mapping[int, int]
    symbol: bytes


def load_cff(resource: bytes, executable: bytes, *, build_sha256: str,
             resource_sha256: str, key_table_va: int, version: int,
             architecture: int = 0) -> CFFResource:
    """Check hashes/envelopes, unmask INST, and validate/apply relocations.

    Every architecture's envelope is checked. Only the explicitly selected
    PE32 layout is decoded; no key or executable data is bundled.
    """
    _verify_hash(resource, resource_sha256, 'resource')
    _verify_hash(executable, build_sha256, 'build')
    if not 0 <= version <= 255:
        raise CatalogError('invalid version')
    if _span(resource, 0, 4) != b'CFF0' or _u32(resource, 4) != len(resource):
        raise CatalogError('invalid CFF0 signature or length')
    if _u32(resource, 12) != 0x0201 or _u32(resource, 16) != 0:
        raise CatalogError('unsupported CFF format version/flags')
    count = _u32(resource, 8)
    if not 1 <= count <= 11 or not 0 <= architecture < count:
        raise CatalogError('invalid architecture count/index')
    offsets = [_u32(resource, 20 + i * 4) for i in range(count)]
    if offsets[0] != 64 or offsets != sorted(set(offsets)):
        raise CatalogError('invalid architecture offsets')
    _span(resource, 0, 64)
    selected = None
    for arch, start in enumerate(offsets):
        end = offsets[arch + 1] if arch + 1 < count else len(resource)
        header = _span(resource, start, 16)
        if header[:4] != b'DEF0' or _u32(header, 4) != 16 or start + 16 >= end:
            raise CatalogError('invalid DEF0 header')
        chunks = {}
        at = start + 16
        while at < end:
            tag = bytes(_span(resource, at, 4))
            size = _u32(resource, at + 4)
            if size < 8 or at + size > end or tag not in (b'INST', b'PTCH', b'SYMB') or tag in chunks:
                raise CatalogError('invalid, duplicate, or unsupported chunk')
            chunks[tag] = _span(resource, at + 8, size - 8)
            at += size
        if at != end or set(chunks) != {b'INST', b'PTCH', b'SYMB'}:
            raise CatalogError('incomplete architecture')
        if arch == architecture:
            if header[8] != 1 or header[9] != version:
                raise CatalogError('unsupported architecture/version profile')
            selected = chunks
    blob = bytearray(selected[b'INST'])
    length = len(blob)
    key = _key_at_va(executable, key_table_va + version * 4)
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
    return CFFResource(bytes(blob), MappingProxyType(relocations), bytes(selected[b'SYMB']))
