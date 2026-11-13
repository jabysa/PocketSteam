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

    def test_linux_uses_folder_runtime(self):
        with patch('linux_portable.run') as run, patch('builtins.print'):
            app.run_linux()
            run.assert_called_once_with(app.ROOT)

    def test_intel_mac_is_rejected_before_setup(self):
        with patch.object(app.platform, 'machine', return_value='x86_64'), \
                patch.object(app.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                app.run_macos()
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
