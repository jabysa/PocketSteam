"""PocketSteam: choose Windows, macOS CS2Kit, or native Linux Steam."""
import argparse
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parent


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


def run_linux():
    from linux_portable import run
    print("Linux folder mode: no sudo, apt, or package installer.\n"
          "Existing graphics drivers and 32-bit system libraries are required.")
    run(ROOT)


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
    except (OSError, ValueError, subprocess.SubprocessError, EOFError, tarfile.TarError) as error:
        print("Error:", error, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
