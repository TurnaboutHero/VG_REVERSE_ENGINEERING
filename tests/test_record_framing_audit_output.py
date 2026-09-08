from pathlib import Path
import os
import tempfile
import unittest

from tests.test_record_framing_audit import packet
from vg.analysis.record_framing_audit import main


class RecordFramingAuditOutputTests(unittest.TestCase):
    def check_replay_is_preserved(self, alias_kind, directory_input=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            replay = root / 'match.0.vgr'
            data = packet(1.0, 0x1234)
            replay.write_bytes(data)
            output = root / 'audit.json'
            if alias_kind == 'direct':
                output = replay
            elif alias_kind == 'hardlink':
                os.link(replay, output)
            else:
                try:
                    output.symlink_to(replay)
                except OSError as error:
                    self.skipTest(f'Symlink creation unavailable: {error}')
            result = main([str(root if directory_input else replay), '-o', str(output)])
            self.assertEqual(result, 2)
            self.assertEqual(replay.read_bytes(), data)

    def test_direct_input_cannot_be_output(self):
        self.check_replay_is_preserved('direct')

    def test_hardlink_to_input_cannot_be_output(self):
        self.check_replay_is_preserved('hardlink')

    def test_symlink_to_input_cannot_be_output(self):
        self.check_replay_is_preserved('symlink')

    def test_selected_file_under_directory_cannot_be_output(self):
        self.check_replay_is_preserved('direct', directory_input=True)


if __name__ == '__main__':
    unittest.main()
