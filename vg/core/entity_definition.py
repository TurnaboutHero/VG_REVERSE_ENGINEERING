"""Read an Actor definition's native kind from an explicitly paired resource.

The layout is established for the supported Windows build. Low-level callers
supplying another profile are responsible for establishing that same layout;
catalog enrichment accepts only the supported profile.
"""
from dataclasses import dataclass

from .cff_resource import CatalogError, _span, _u32, load_cff


ACTOR_SYMBOL_TYPE_ID = 0x2419fb6c
ACTOR_SERIALIZED_SIZE = 0x208


@dataclass(frozen=True)
class EntityKindEvidence:
    build_sha256: str
    resource_sha256: str
    serialized_name: str
    symbol_type_id: int
    root_offset: int
    native_kind: int
    kind: str


def load_entity_kind(resource: bytes, executable: bytes, *, build_sha256: str,
                     resource_sha256: str, key_table_va: int, version: int,
                     expected_name: str, architecture: int = 0) -> EntityKindEvidence:
    """Validate one Actor symbol and read its scalar enum without name guessing.

    Resource hashes are caller trust assertions; their pairing with the
    executable and manifest must be established independently.
    """
    decoded = load_cff(
        resource, executable, build_sha256=build_sha256,
        resource_sha256=resource_sha256, key_table_va=key_table_va,
        version=version, architecture=architecture,
    )
    root, symbol_type = _u32(decoded.symbol, 0), _u32(decoded.symbol, 4)
    if symbol_type != ACTOR_SYMBOL_TYPE_ID:
        raise CatalogError('unsupported entity symbol type')
    end = decoded.symbol.find(b'\0', 8, min(len(decoded.symbol), 8 + 1025))
    if end <= 8:
        raise CatalogError('unterminated, empty, or oversized entity symbol name')
    if any(decoded.symbol[end + 1:]):
        raise CatalogError('unsupported entity symbol trailing data')
    try:
        name = decoded.symbol[8:end].decode('ascii')
    except UnicodeDecodeError as exc:
        raise CatalogError('non-ASCII entity symbol name') from exc
    if any(ord(c) < 32 or ord(c) > 126 for c in name):
        raise CatalogError('invalid entity symbol name')
    if name != expected_name:
        raise CatalogError('entity symbol name does not match manifest serialized name')
    if root % 4:
        raise CatalogError('unaligned entity root')
    _span(decoded.inst, root, ACTOR_SERIALIZED_SIZE)
    if root in decoded.relocations:
        raise CatalogError('entity kind cannot be a relocated pointer')
    native_kind = _u32(decoded.inst, root)
    kind = {0: 'hero', 2: 'structure', 3: 'structure'}.get(native_kind, 'unknown')
    return EntityKindEvidence(
        build_sha256, resource_sha256, name, symbol_type, root, native_kind, kind,
    )
