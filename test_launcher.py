import unittest
import re
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import steam_portable
from steam_portable import VALVE_PUBLISHER_PATTERN, package_info


class SignaturePublisherTests(unittest.TestCase):
    def test_accepts_valve_certificate_subjects(self):
        for subject in (
            "CN=Valve Corp., O=Valve Corp., L=Bellevue, S=Washington, C=US",
            "O=Valve Corporation, C=US",
            "CN=Steam, O=Valve Corp",
        ):
            with self.subTest(subject=subject):
                self.assertIsNotNone(re.search(VALVE_PUBLISHER_PATTERN, subject))

    def test_rejects_other_publishers_and_embedded_names(self):
        for subject in (
            "CN=Other, O=Other Company, C=US",
            "O=Valve Corporation Fake, C=US",
            "CN=O=Valve Corp., O=Other Company, C=US",
            "O=Valve CorpX, C=US",
            "",
        ):
            with self.subTest(subject=subject):
                self.assertIsNone(re.search(VALVE_PUBLISHER_PATTERN, subject))


class ManifestTests(unittest.TestCase):
    def test_selects_bootstrapper_and_ignores_other_packages(self):
        manifest = ('"file" "other.zip" "size" "99" "sha2" "' + 'b' * 64 + '"\n'
                    '"file" "steam_win32_steamrow.zip.abc123" "size" "123" '
                    '"sha2" "' + 'a' * 64 + '"')
        self.assertEqual(package_info(manifest),
                         ("steam_win32_steamrow.zip.abc123", 123, "a" * 64))

    def test_rejects_missing_digest_or_path(self):
        for manifest in ('"file" "steam_win32_steamrow.zip.abc" "size" "1"',
                         '"file" "../Steam.exe" "size" "1" "sha2" "' + 'a' * 64 + '"'):
            with self.assertRaises(ValueError):
                package_info(manifest)


class WindowsUserSetupTests(unittest.TestCase):
    def test_network_folder_copies_games_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "network" / "Steam"
            source.mkdir(parents=True)
            (source / "game.dat").write_bytes(b"saved download")
            appdata = Path(root) / "local"
            kernel = SimpleNamespace(GetDriveTypeW=MagicMock(side_effect=[3, 4, 3, 4]))
            with patch.dict(os.environ, LOCALAPPDATA=str(appdata)), patch.object(
                    steam_portable.ctypes, "windll",
                    SimpleNamespace(kernel32=kernel), create=True):
                destination = steam_portable.windows_folder(source)
                self.assertEqual(destination, appdata / "PocketSteam" / "Steam")
                self.assertEqual((destination / "game.dat").read_bytes(), b"saved download")
                self.assertTrue((source / "game.dat").exists())
                self.assertEqual(steam_portable.windows_folder(source), destination)

    def test_local_writable_folder_is_reused(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "Steam"
            kernel = SimpleNamespace(GetDriveTypeW=MagicMock(return_value=3))
            with patch.dict(os.environ, LOCALAPPDATA=str(Path(root) / "local")), patch.object(
                    steam_portable.ctypes, "windll",
                    SimpleNamespace(kernel32=kernel), create=True):
                self.assertEqual(steam_portable.windows_folder(source), source)

    def test_failed_copy_is_not_published(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "Steam"
            source.mkdir()
            kernel = SimpleNamespace(GetDriveTypeW=MagicMock(side_effect=[3, 4, 3, 4]))
            appdata = Path(root) / "local"
            with patch.dict(os.environ, LOCALAPPDATA=str(appdata)), patch.object(
                    steam_portable.ctypes, "windll",
                    SimpleNamespace(kernel32=kernel), create=True), patch.object(
                    steam_portable.shutil, "copytree", side_effect=OSError("copy failed")):
                with self.assertRaises(OSError):
                    steam_portable.windows_folder(source)
            self.assertTrue(source.exists())
            self.assertFalse((appdata / "PocketSteam" / "Steam").exists())
            self.assertEqual(list((appdata / "PocketSteam").iterdir()), [])

    def test_insufficient_space_keeps_source(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "Steam"
            source.mkdir()
            kernel = SimpleNamespace(GetDriveTypeW=MagicMock(side_effect=[3, 4]))
            appdata = Path(root) / "local"
            with patch.dict(os.environ, LOCALAPPDATA=str(appdata)), patch.object(
                    steam_portable.ctypes, "windll",
                    SimpleNamespace(kernel32=kernel), create=True), patch.object(
                    steam_portable.shutil, "disk_usage", return_value=SimpleNamespace(free=0)):
                with self.assertRaisesRegex(ValueError, "Not enough local disk space"):
                    steam_portable.windows_folder(source)
            self.assertTrue(source.exists())
            self.assertFalse((appdata / "PocketSteam" / "Steam").exists())

    def test_network_appdata_is_rejected(self):
        kernel = SimpleNamespace(GetDriveTypeW=MagicMock(return_value=4))
        with patch.dict(os.environ, LOCALAPPDATA="redirected"), patch.object(
                steam_portable.ctypes, "windll", SimpleNamespace(kernel32=kernel), create=True):
            with self.assertRaisesRegex(ValueError, "LOCALAPPDATA points to a network"):
                steam_portable.windows_folder(Path("Steam"))

    def test_registry_writes_only_current_user(self):
        registry = MagicMock()
        exe = Path("Steam") / "Steam.exe"
        with patch.dict("sys.modules", winreg=registry):
            steam_portable.register_user_steam(exe)
        registry.CreateKeyEx.assert_called_once_with(
            registry.HKEY_CURRENT_USER, r"Software\Valve\Steam", 0, registry.KEY_SET_VALUE)
        self.assertEqual(registry.SetValueEx.call_count, 2)
        self.assertEqual([call.args[1] for call in registry.SetValueEx.call_args_list],
                         ["SteamPath", "SteamExe"])

    def test_running_steam_stops_setup(self):
        result = SimpleNamespace(stdout='"steam.exe","1234","Console","1","20 K"')
        with patch.object(steam_portable.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(ValueError, "Close Steam"):
                steam_portable.require_steam_closed()

    def test_no_steam_process_allows_setup(self):
        with patch.object(steam_portable.subprocess, "run", return_value=SimpleNamespace(
                stdout="INFO: No tasks are running which match the specified criteria.")):
            steam_portable.require_steam_closed()


if __name__ == "__main__":
    unittest.main()
