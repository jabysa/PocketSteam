"""PocketSteam: choose Windows, macOS CS2Kit, or native Linux Steam."""
import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent
DEB_URL = "https://repo.steampowered.com/steam/steam_latest.deb"


def host_os():
    return {"win32": "windows", "darwin": "macos"}.get(sys.platform,
            "linux" if sys.platform.startswith("linux") else "unsupported")


def choose_os():
    print("PocketSteam\n1. Windows — folder-based Steam\n"
          "2. macOS — CS2Kit (Apple Silicon)\n3. Linux — native Steam\n0. Exit")
    choices = {"1": "windows", "2": "macos", "3": "linux", "0": None}
    while True:
        choice = input("Choose [0-3]: ").strip()
        if choice in choices:
            return choices[choice]
        print("Please enter 0, 1, 2 or 3.")


def confirm(message):
    return input(message + " [y/N]: ").strip().lower() == "y"


def run_macos():
    if platform.machine() != "arm64":
        raise ValueError("CS2Kit requires an Apple Silicon Mac (M1 or newer).")
    repo = ROOT / "vendor" / "cs2kit"
    print("CS2Kit runs Windows Steam for CS2. Competitive/VAC play is not validated.\n"
          "Setup downloads Wine/DXMT/Steam, writes ~/CS2 and ~/.cs2kit, and may\n"
          "move an existing CS2 install to its separate library. Allow about 90 GB.")
    if not confirm("Set up or repair CS2Kit now? Choose N to launch an existing setup"):
        subprocess.run([str(repo / "bin/cs2kit"), "play", "--profile", "balanced-1080p",
                        "--detach"], cwd=repo, check=True)
        return
    subprocess.run([str(repo / "bin/cs2kit"), "setup", "--app-dest",
                    str(Path.home() / "Applications/CS2Kit.app")], cwd=repo, check=True)
    print("Setup complete. Open ~/Applications/CS2Kit.app, sign in, then install CS2.")


def linux_supported():
    if platform.machine().lower() not in ("x86_64", "amd64"):
        return False
    release = Path("/etc/os-release").read_text()
    return any(line in ('ID=ubuntu', 'ID="ubuntu"', 'ID=debian', 'ID="debian"')
               for line in release.splitlines()) and bool(shutil.which("apt"))


def run_linux():
    steam = shutil.which("steam")
    if steam:
        subprocess.run([steam], check=True)
        return
    if not linux_supported():
        raise ValueError("Automatic Linux setup supports Ubuntu/Debian x86_64 only. "
                         "Install Steam using your distribution, then run this again. "
                         "See https://store.steampowered.com/about/")
    print("Linux setup installs Valve's official .deb using apt (administrator\n"
          "permission required). This route is NOT a portable folder installation.\n"
          "Graphics drivers and 32-bit dependencies may need distribution setup.")
    if not confirm("Download and install Steam using apt?"):
        return
    downloads = ROOT / "downloads"
    downloads.mkdir(exist_ok=True)
    dest = downloads / "steam_latest.deb"
    if dest.is_symlink():
        raise ValueError("Refusing a symbolic-link package destination")
    with urllib.request.urlopen(DEB_URL, timeout=60) as response:
        if not response.geturl().startswith("https://"):
            raise ValueError("Refusing insecure download")
        data = response.read(32_000_001)
    if len(data) > 32_000_000 or not data.startswith(b"!<arch>\n"):
        raise ValueError("Invalid or oversized Debian package")
    dest.write_bytes(data)
    # apt resolves dependencies; package source is Valve over HTTPS, not a signed repository.
    command = ["apt", "install", str(dest)]
    if os.geteuid() != 0:
        command.insert(0, "sudo")
    subprocess.run(command, check=True)
    print("Steam installed. Run 'steam' as your normal user (not sudo).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--os", choices=("windows", "macos", "linux"))
    args = parser.parse_args()
    target = args.os or choose_os()
    if target is None:
        return
    if target != host_os():
        raise ValueError("Selected " + target + ", but this computer runs " + host_os()
                         + ". Copy this project to the target computer and run it there.")
    if target == "windows":
        subprocess.run([sys.executable, str(ROOT / "steam_portable.py")], check=True)
    elif target == "macos":
        run_macos()
    else:
        run_linux()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError, EOFError) as error:
        print("Error:", error, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
