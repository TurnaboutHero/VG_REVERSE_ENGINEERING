import hashlib
import struct
import unittest
from dataclasses import replace
from vg.core.definition_catalog import (
    BuildProfile, CatalogError, load_catalog, supported_build_profile, _mask_constant,
)


def fixture(name=b'*Test*\0'):
    exe = bytearray(1024)
    exe[:2] = b'MZ'
    struct.pack_into('<I', exe, 60, 64)
    exe[64:68] = b'PE\0\0'
    struct.pack_into('<H', exe, 70, 1)
    struct.pack_into('<H', exe, 84, 32)
    exe[88:90] = b'\x0b\x01'
    struct.pack_into('<I', exe, 116, 0x400000)
    struct.pack_into('<III', exe, 132, 0x1000, 128, 512)
    exe[516:520] = b'abcd'
    blob = bytearray(64)
    blob[24:24 + len(name)] = name
    constant = _mask_constant(b'abcd', len(blob))
    previous = len(blob)
    for at in range(0, len(blob), 4):
        value = struct.unpack_from('<I', blob, at)[0]
        encoded = value ^ constant ^ (((previous << 1) | (previous >> 31)) & 0xffffffff)
        struct.pack_into('<I', blob, at, encoded)
        previous = encoded
    patch = struct.pack('<II6I', 3, 0, 0, 4, 4, 16, 16, 24)
    def chunk(tag, data):
        return tag + struct.pack('<I', len(data) + 8) + data
    manifest = bytearray(64)
    manifest[:4] = b'CFF0'
    struct.pack_into('<I', manifest, 8, 1)
    struct.pack_into('<I', manifest, 12, 0x0201)
    struct.pack_into('<I', manifest, 20, 64)
    manifest += b'DEF0' + struct.pack('<I', 16) + bytes([1, 1, 0, 0]) + bytes(4)
    manifest += chunk(b'INST', blob) + chunk(b'PTCH', patch) + chunk(b'SYMB', bytes(8))
    struct.pack_into('<I', manifest, 4, len(manifest))
    profile = BuildProfile(hashlib.sha256(exe).hexdigest(), hashlib.sha256(manifest).hexdigest(), 0x401000, 1, 1)
    return manifest, exe, profile


class CatalogTests(unittest.TestCase):
    def test_valid_and_no_mutation(self):
        m, e, p = fixture()
        before = bytes(m), bytes(e)
        catalog = load_catalog(m, e, p)
        self.assertEqual(catalog.lookup(0).name, 'Test')
        self.assertEqual(catalog.lookup(0).serialized_name, '*Test*')
        self.assertEqual(catalog.lookup(0).kind, 'unknown')
        self.assertEqual(before, (bytes(m), bytes(e)))
        for index in (-1, 1, 1000000):
            with self.assertRaises(CatalogError):
                catalog.lookup(index)

    def test_name_bounds_and_encoding(self):
        for name in (b'x' * 40, b'\xff\0', b'\0', b'a\x01\0'):
            m, e, p = fixture(name)
            with self.assertRaises(CatalogError):
                load_catalog(m, e, p)

    def test_cli_help_and_wrong_build(self):
        import contextlib
        import io
        from vg.core.definition_catalog import main
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                main(['--help'])
        self.assertEqual(caught.exception.code, 0)
        with contextlib.redirect_stderr(io.StringIO()):
            result = main(['--manifest', 'missing', '--executable', 'missing',
                           '--build-sha256', '0' * 64, '--manifest-sha256', '0' * 64])
        self.assertEqual(result, 2)

    def test_wrong_hashes(self):
        m, e, p = fixture()
        for bad in (replace(p, build_sha256='0' * 64), replace(p, manifest_sha256='0' * 64), replace(p, manifest_sha256='x')):
            with self.assertRaises(CatalogError):
                load_catalog(m, e, bad)
        with self.assertRaises(CatalogError):
            supported_build_profile('0' * 64, p.manifest_sha256)

    def test_malformed_container_and_relocations(self):
        # Hashes are recomputed so these exercise structural checks, not just SHA.
        mutations = [
            (4, 1), (8, 0), (8, 12), (12, 0), (16, 1), (20, 65), (68, 15),
            (84, 7), (84, 0xffffffff), (156, 0xffffffff),
            (160, 9), (164, 1), (172, 64), (176, 2),
            (180, 100000), (184, 4),
        ]
        for offset, value in mutations:
            with self.subTest(offset=offset, value=value):
                m, e, p = fixture()
                struct.pack_into('<I', m, offset, value)
                p = replace(p, manifest_sha256=hashlib.sha256(m).hexdigest())
                with self.assertRaises(CatalogError):
                    load_catalog(m, e, p)

    def test_versions_counts_and_key_bounds(self):
        m, e, p = fixture()
        for bad in (replace(p, version=2), replace(p, architecture=1), replace(p, definition_count=0), replace(p, definition_count=2), replace(p, key_table_va=0), replace(p, key_table_va=0x40107c)):
            with self.assertRaises(CatalogError):
                load_catalog(m, e, bad)

    def test_truncations(self):
        m, e, p = fixture()
        for length in (0, 4, 63, 70, 100, len(m)-1):
            truncated = m[:length]
            with self.assertRaises(CatalogError):
                load_catalog(truncated, e, replace(p, manifest_sha256=hashlib.sha256(truncated).hexdigest()))
        for length in (0, 63, 100, 140, 518):
            truncated = e[:length]
            with self.assertRaises(CatalogError):
                load_catalog(m, truncated, replace(p, build_sha256=hashlib.sha256(truncated).hexdigest()))


if __name__ == '__main__':
    unittest.main()
