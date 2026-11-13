import unittest
from unittest.mock import patch
import pocketsteam as app


class PlatformTests(unittest.TestCase):
    def test_menu_retries_invalid_input(self):
        with patch('builtins.input', side_effect=['wrong', '2']), patch('builtins.print'):
            self.assertEqual(app.choose_os(), 'macos')

    def test_cancel_changes_nothing(self):
        with patch('sys.argv', ['pocketsteam.py']), patch('builtins.input', return_value='0'), \
                patch('builtins.print'), patch.object(app.subprocess, 'run') as run:
            app.main()
            run.assert_not_called()

    def test_wrong_platform_does_not_launch(self):
        with patch('sys.argv', ['pocketsteam.py', '--os', 'windows']), \
                patch.object(app, 'host_os', return_value='linux'), \
                patch.object(app.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                app.main()
            run.assert_not_called()

    def test_windows_delegates_to_existing_verified_launcher(self):
        with patch('sys.argv', ['pocketsteam.py', '--os', 'windows']), \
                patch.object(app, 'host_os', return_value='windows'), \
                patch.object(app.subprocess, 'run') as run:
            app.main()
            self.assertEqual(run.call_args.args[0][1], str(app.ROOT / 'steam_portable.py'))

    def test_linux_does_not_install_without_consent(self):
        with patch.object(app.shutil, 'which', return_value=None), \
                patch.object(app, 'linux_supported', return_value=True), \
                patch.object(app, 'confirm', return_value=False), \
                patch('builtins.print'), patch.object(app.urllib.request, 'urlopen') as fetch, \
                patch.object(app.subprocess, 'run') as run:
            app.run_linux()
            fetch.assert_not_called()
            run.assert_not_called()

    def test_installed_linux_steam_needs_no_download(self):
        with patch.object(app.shutil, 'which', return_value='/usr/bin/steam'), \
                patch.object(app.subprocess, 'run') as run, \
                patch.object(app.urllib.request, 'urlopen') as fetch:
            app.run_linux()
            run.assert_called_once_with(['/usr/bin/steam'], check=True)
            fetch.assert_not_called()

    def test_intel_mac_is_rejected_before_setup(self):
        with patch.object(app.platform, 'machine', return_value='x86_64'), \
                patch.object(app.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                app.run_macos()
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
