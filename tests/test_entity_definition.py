from dataclasses import FrozenInstanceError, asdict
import hashlib
import struct
import unittest

from tests.test_definition_catalog import fixture
from vg.core.cff_resource import CatalogError, load_cff
from vg.core.entity_definition import ACTOR_SYMBOL_TYPE_ID, load_entity_kind
from vg.core.definition_catalog import _mask_constant


def entity_fixture(kind=0, root=0, name=b'*Test*\0', *, size=0x208,
                   symbol_type=ACTOR_SYMBOL_TYPE_ID, symbol=None, relocations=()):
    manifest, executable, profile = fixture()
    blob = bytearray(size)
    if 0 <= root <= size - 4:
        struct.pack_into('<I', blob, root, kind)
    constant = _mask_constant(b'abcd', len(blob))
    previous = len(blob)
    for at in range(0, len(blob) // 4 * 4, 4):
        value = struct.unpack_from('<I', blob, at)[0]
        encoded = value ^ constant ^ (((previous << 1) | (previous >> 31)) & 0xffffffff)
        struct.pack_into('<I', blob, at, encoded)
        previous = encoded
    patch = struct.pack('<II', len(relocations), 0)
    patch += b''.join(struct.pack('<II', *item) for item in relocations)
    if symbol is None:
        symbol = struct.pack('<II', root, symbol_type) + name
    resource = bytearray(manifest[:80])
    for tag, data in ((b'INST', blob), (b'PTCH', patch), (b'SYMB', symbol)):
        resource += tag + struct.pack('<I', len(data) + 8) + data
    struct.pack_into('<I', resource, 4, len(resource))
    options = dict(build_sha256=profile.build_sha256,
                   resource_sha256=hashlib.sha256(resource).hexdigest(),
                   key_table_va=profile.key_table_va, version=profile.version,
                   architecture=profile.architecture)
    return resource, executable, options


class EntityDefinitionTests(unittest.TestCase):
    def read(self, resource, executable, options, expected_name='*Test*'):
        return load_entity_kind(resource, executable, expected_name=expected_name, **options)

    def test_native_enum_drives_kind_and_keeps_provenance(self):
        for native, kind in ((0, 'hero'), (2, 'structure'), (3, 'structure'),
                             (1, 'unknown'), (4, 'unknown'), (0xffffffff, 'unknown')):
            with self.subTest(native=native):
                resource, executable, options = entity_fixture(native)
                before = bytes(resource), bytes(executable)
                evidence = self.read(resource, executable, options)
                self.assertEqual(evidence.native_kind, native)
                self.assertEqual(evidence.kind, kind)
                self.assertEqual(evidence.serialized_name, '*Test*')
                self.assertEqual(evidence.symbol_type_id, ACTOR_SYMBOL_TYPE_ID)
                self.assertEqual(evidence.build_sha256, options['build_sha256'])
                self.assertEqual(evidence.resource_sha256, options['resource_sha256'])
                self.assertEqual(asdict(evidence)['native_kind'], native)
                self.assertEqual(before, (bytes(resource), bytes(executable)))
                with self.assertRaises(FrozenInstanceError):
                    evidence.kind = 'hero'

    def test_name_is_identity_not_kind_hint(self):
        resource, executable, options = entity_fixture(4, name=b'*HeroTurretCrystal*\0')
        evidence = self.read(resource, executable, options, '*HeroTurretCrystal*')
        self.assertEqual(evidence.kind, 'unknown')

    def test_nonzero_aligned_root_and_zero_padding(self):
        resource, executable, options = entity_fixture(3, root=8, size=0x210,
                                                     name=b'*Test*\0' + bytes(16))
        evidence = self.read(resource, executable, options)
        self.assertEqual((evidence.root_offset, evidence.native_kind), (8, 3))

    def test_shared_decoder_is_immutable(self):
        resource, executable, options = entity_fixture(relocations=((8, 16),))
        decoded = load_cff(resource, executable, **options)
        self.assertIsInstance(decoded.inst, bytes)
        self.assertIsInstance(decoded.symbol, bytes)
        self.assertEqual(decoded.relocations[8], 16)
        self.assertEqual(struct.unpack_from('<I', decoded.inst, 8)[0], 16)
        with self.assertRaises(TypeError):
            decoded.relocations[8] = 20
        with self.assertRaises(FrozenInstanceError):
            decoded.inst = b''

    def test_wrong_hashes_profile_and_architecture(self):
        resource, executable, options = entity_fixture()
        for field, value in (('build_sha256', '0' * 64),
                             ('resource_sha256', '0' * 64), ('resource_sha256', 'BAD'),
                             ('version', 2), ('version', 256), ('version', -1),
                             ('architecture', 1), ('architecture', -1), ('key_table_va', 0)):
            with self.subTest(field=field, value=value), self.assertRaises(CatalogError):
                self.read(resource, executable, dict(options, **{field: value}))

    def test_wrong_symbol_type_rejects_non_actor(self):
        for symbol_type in (0, 0xffffffff):
            resource, executable, options = entity_fixture(symbol_type=symbol_type)
            with self.assertRaisesRegex(CatalogError, 'symbol type'):
                self.read(resource, executable, options)

    def test_exact_serialized_name_including_asterisks(self):
        resource, executable, options = entity_fixture()
        for expected_name in ('Test', '*Test', 'Test*', '*Other*', ''):
            with self.subTest(expected_name=expected_name), self.assertRaisesRegex(CatalogError, 'match manifest'):
                self.read(resource, executable, options, expected_name)

    def test_symbol_name_encoding_termination_and_padding(self):
        for name in (b'', b'\0', b'*Test*', b'\xff\0', b'a\x01\0',
                     b'x' * 1025 + b'\0', b'*Test*\0\0x'):
            resource, executable, options = entity_fixture(name=name)
            with self.subTest(name=name[:20]), self.assertRaises(CatalogError):
                self.read(resource, executable, options)
        for symbol in (b'', bytes(4), bytes(7)):
            resource, executable, options = entity_fixture(symbol=symbol)
            with self.assertRaises(CatalogError):
                self.read(resource, executable, options)

    def test_invalid_root_alignment_layout_size_and_relocated_kind(self):
        for changes in (dict(root=1), dict(root=4), dict(root=0xffffffff),
                        dict(size=0), dict(size=4), dict(size=0x207),
                        dict(root=4, size=0x20b), dict(relocations=((0, 4),))):
            resource, executable, options = entity_fixture(**changes)
            with self.subTest(changes=changes), self.assertRaises(CatalogError):
                self.read(resource, executable, options)

    def test_truncated_resource_after_rehash(self):
        resource, executable, options = entity_fixture()
        for size in (0, 4, 63, 80, len(resource) - 1):
            truncated = resource[:size]
            with self.subTest(size=size), self.assertRaises(CatalogError):
                self.read(truncated, executable,
                          dict(options, resource_sha256=hashlib.sha256(truncated).hexdigest()))


if __name__ == '__main__':
    unittest.main()
