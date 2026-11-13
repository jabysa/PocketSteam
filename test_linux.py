import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import linux_portable as linux


class LinuxTests(unittest.TestCase):
    def test_wrong_checksum_creates_no_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'Steam'
            with self.assertRaises(ValueError):
                linux.prepare(folder, b'not a trusted package')
            self.assertFalse(folder.exists())

    def test_archive_escape_is_rejected_before_writing(self):
        for name, link in [('../escape', None), ('/escape', None), ('link', '../../escape')]:
            with self.subTest(name=name, link=link), tempfile.TemporaryDirectory() as tmp:
                data = io.BytesIO()
                with tarfile.open(fileobj=data, mode='w') as archive:
                    info = tarfile.TarInfo(name)
                    if link:
                        info.type = tarfile.SYMTYPE
                        info.linkname = link
                    archive.addfile(info)
                data.seek(0)
                with tarfile.open(fileobj=data) as archive, self.assertRaises(ValueError):
                    linux.unpack_safe(archive, Path(tmp))
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_arm_linux_cannot_launch(self):
        with patch.object(linux.platform, 'machine', return_value='aarch64'), \
                patch.object(linux.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                linux.run(Path('/tmp'))
            run.assert_not_called()

    def test_launch_bypasses_distro_installer(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(linux.platform, 'machine', return_value='x86_64'), \
                patch.object(linux.os, 'geteuid', return_value=1000), \
                patch.object(linux.Path, 'exists', return_value=True), \
                patch.object(linux.shutil, 'which', return_value='/usr/bin/tool'), \
                patch.object(linux, 'prepare', return_value=Path(tmp) / 'steam.sh'), \
                patch.object(linux.subprocess, 'run') as run:
            linux.run(Path(tmp))
            self.assertEqual(run.call_args.args[0], ['bash', str(Path(tmp) / 'steam.sh')])
            self.assertEqual(run.call_args.kwargs['env']['STEAM_RUNTIME'], '1')


if __name__ == '__main__':
    unittest.main()
