"""Folder-based Steam bootstrapper. Python 3.9+, no third-party packages."""
import argparse
import hashlib
import io
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
import zipfile

BASE = "https://client-update.steamstatic.com/"
VALVE_PUBLISHER_PATTERN = r"(?i)(^|,\s*)O=Valve Corp(oration|\.)?(,|$)"


def fetch(name, limit):
    with urllib.request.urlopen(BASE + name, timeout=60) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("Refusing an insecure download")
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Download exceeds expected size limit")
    return data


def package_info(manifest):
    # Select the worldwide Windows bootstrapper, not the entire Steam client.
    match = re.search(
        r'"file"\s+"(steam_win32_steamrow\.zip\.[a-f0-9]+)"'
        r'\s+"size"\s+"(\d+)"\s+"sha2"\s+"([a-f0-9]{64})"', manifest)
    if not match:
        raise ValueError("Valve changed the manifest format; launcher needs updating")
    return match[1], int(match[2]), match[3]


def bootstrap(folder):
    exe = folder / "Steam.exe"
    if exe.exists():
        if not exe.is_file() or exe.is_symlink():
            raise ValueError("Steam.exe must be a regular file")
        return exe
    print("Reading Valve's official update manifest...", flush=True)
    name, size, digest = package_info(fetch("steam_client_win32", 2_000_000).decode("utf-8"))
    if not 0 < size <= 32_000_000:
        raise ValueError("Unexpected bootstrap package size")
    package = fetch(name, size)
    if len(package) != size or hashlib.sha256(package).hexdigest() != digest:
        raise ValueError("Valve package size or SHA-256 verification failed")
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        entries = [item for item in archive.infolist()
                   if item.filename.replace("\\", "/").lower() == "steam.exe"]
        if len(entries) != 1 or not 0 < entries[0].file_size <= 32_000_000:
            raise ValueError("Package does not contain exactly one expected Steam.exe")
        executable = archive.read(entries[0])
    if not executable.startswith(b"MZ"):
        raise ValueError("Invalid Windows executable")
    folder.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: never overwrite an existing executable or symlink.
    with exe.open("xb") as output:
        output.write(executable)
    print("Verified bootstrapper saved to:", exe)
    return exe


def verify_signature(exe):
    # Pass the path via the environment rather than interpolate PowerShell code.
    script = (
        "$ErrorActionPreference='Stop'; "
        "$s=Get-AuthenticodeSignature -LiteralPath $env:STEAM_PORTABLE_EXE; "
        "if ($s.Status -ne 'Valid' -or "
        f"$s.SignerCertificate.Subject -notmatch '{VALVE_PUBLISHER_PATTERN}') "
        "{ throw ('Steam signature rejected. Status: {0}; Signer: {1}; Detail: {2}' "
        "-f $s.Status, $s.SignerCertificate.Subject, $s.StatusMessage) }"
    )
    env = dict(os.environ, STEAM_PORTABLE_EXE=str(exe))
    subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                   check=True, env=env, timeout=60)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true",
                        help="download and verify package only; do not run Steam")
    args = parser.parse_args()
    if sys.platform != "win32" and not args.prepare_only:
        parser.error("Run this launcher on Windows, or use --prepare-only to download")
    folder = Path(__file__).resolve().parent / "Steam"
    exe = bootstrap(folder)
    if args.prepare_only:
        print("Prepared only. Windows Authenticode verification occurs before launch.")
        return
    verify_signature(exe)
    subprocess.Popen([str(exe)], cwd=str(folder))
    print("Steam started. First launch downloads the rest of the client.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print("Error:", error, file=sys.stderr)
        sys.exit(1)
