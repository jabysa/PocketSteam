import unittest
import re
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


if __name__ == "__main__":
    unittest.main()
