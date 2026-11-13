# PocketSteam

**Language:** English · [فارسی](docs/README.fa.md) · [العربية](docs/README.ar.md)

One menu for Windows Steam, macOS CS2Kit, and Linux Steam setup.

## Choose your system

Run `python pocketsteam.py` (Windows) or `python3 pocketsteam.py` (macOS/Linux).
The menu asks **Windows / macOS / Linux**. Choose the computer you are currently using;
this is not a cross-platform emulator.

- **Windows:** double-click `Start Steam.cmd`, select **1**. Uses the existing folder-based launcher.
- **macOS:** open `Start PocketSteam.command`, select **2**. If execution permissions were lost in a ZIP, run `sh "Start PocketSteam.command"` in Terminal. Apple Silicon only. Choose `y` for setup/repair or `n` to launch an existing CS2Kit setup. Allow about 90 GB. Sign into Windows Steam and install CS2 after setup.
- **Linux:** run `sh start.sh`, select **3**. An installed `steam` command is launched. Otherwise Ubuntu/Debian x86_64 users can confirm installation of Valve's official `.deb` through `sudo apt install`. Your password is entered in the terminal, never saved by PocketSteam. Other distributions must install Steam through their own supported package manager first.

Linux setup is a **system installation**, not a portable folder. Older distributions, missing 32-bit libraries, or GPU drivers may prevent installation. See [Valve's Linux requirements](https://github.com/ValveSoftware/steam-for-linux/blob/master/README.md).
macOS uses the bundled **CS2Kit** source snapshot, not native Mac Steam. It writes `~/CS2`, `~/.cs2kit`, and `~/Applications/CS2Kit.app`; it may move an existing CS2 install into its own library. **Competitive/VAC play remains unvalidated.**

For direct selection: `python pocketsteam.py --os windows`, `python3 pocketsteam.py --os macos`, or `python3 pocketsteam.py --os linux`.

## Install Python

- **Windows:** [download Python](https://www.python.org/downloads/windows/). Run the official installer/install manager and follow its prompts. With a classic installer, enable **Add Python to PATH**. Reopen your terminal and check `py -3 --version` or `python --version`.
- **macOS:** [download Python](https://www.python.org/downloads/macos/), open the official `.pkg`, follow the installer, then check `python3 --version` in Terminal. For CS2Kit, use a Python build with `lzma` support; the python.org installer includes it. Rosetta 2 must be installed for CS2Kit.
- **Ubuntu/Debian:** run `sudo apt update`, then `sudo apt install python3`. Check `python3 --version`. On other distributions use their Python package.

Python 3.9+ is required. No `pip install` step is needed for the PocketSteam menu.

## Official downloads

- [Download PocketSteam ZIP](https://github.com/jabysa/PocketSteam/archive/refs/heads/main.zip)
- [Steam — choose Windows, macOS or Linux](https://store.steampowered.com/about/)
- [Steam Windows installer](https://cdn.cloudflare.steamstatic.com/client/installer/SteamSetup.exe) — optional alternative; PocketSteam's Windows path does not run it
- [Steam Linux .deb](https://repo.steampowered.com/steam/steam_latest.deb)
- [CS2Kit upstream](https://github.com/piwas-21/cs2-apple-silicon) and [snapshot attribution](vendor/UPSTREAM.md)

## Source and license

`vendor/cs2kit/` contains an unmodified GPL-3.0 source snapshot, including its original license and documentation. No Wine, Steam, or DXMT binaries are bundled. This integration is not a separate GitHub fork. PocketSteam is distributed under [GPL-3.0](LICENSE); upstream notices remain intact.

## Windows folder launcher details

The following details describe the Windows folder-based path.
Built with Python's standard library. No pip packages, Wine, or CrossOver needed.

## Quick start

1. Install **Python 3.9+** from [python.org](https://www.python.org/downloads/windows/). Enable **Add Python to PATH** if offered.
2. Download this repository using **Code → Download ZIP**, then extract it to a writable folder, such as your Desktop.
3. Close any Steam client already running using **Steam → Exit**.
4. Double-click **`Start Steam.cmd`**.
5. Wait for Steam to download its files, then sign in through Steam itself.

Next time, double-click **`Start Steam.cmd`** again. Keep the project folder together.
You need a 64-bit Windows version supported by Steam, an internet connection, and enough free space for the client and games.

Prefer a terminal? Open it in the project folder and run:

```powershell
python steam_portable.py
```

If Windows does not recognize `python`, try `py -3 steam_portable.py`.

## How it works

PocketSteam downloads the bootstrap package directly from Valve, checks its size and SHA-256 against Valve's update manifest, and extracts only `Steam.exe` into `Steam/`.
Before launching on Windows, it checks that the executable has a valid Valve Authenticode signature. Steam then downloads and updates the rest of its client.
An existing `Steam.exe` is reused and its signature is checked again before launch.

## What “without an installer” means

The launcher does not run `SteamSetup.exe`. It does **not** isolate Steam from Windows:

- Steam may write to AppData and the Registry, or ask for administrator permission for Steam Client Service or game prerequisites. PocketSteam does not automatically approve those requests.
- Online games and VAC are not guaranteed to work without required services.
- Exit Steam completely before moving the folder. Deleting `Steam/` also deletes games and data stored inside it, but may leave files elsewhere on the computer.

## Files

- `steam_portable.py` — downloader and launcher
- `Start Steam.cmd` — Windows double-click entry point
- `test_launcher.py` — manifest parser tests
- `Steam/` — downloaded client and local data; ignored by Git

## Troubleshooting

- **Python not found:** install Python, reopen the terminal, and check `python --version` or `py -3 --version`.
- **Signature or checksum error:** do not run the executable manually. Check your connection and whether a launcher update is available.
- **Manifest format error:** Valve's package format may have changed; the launcher needs updating.
- **Steam logs:** look in `Steam/logs`. Review logs for account information before sharing.

## Development and verification

The platform menu has mocked routing/consent tests. Native Windows and Linux
end-to-end execution has not been tested. The bundled upstream CS2Kit revision
was installed on an M2 Pro separately; this menu's full Mac setup has not been rerun.

Run tests:

```powershell
python -m unittest -v
```

Prepare the bootstrapper without launching it (also works on macOS):

```sh
python3 steam_portable.py --prepare-only
```

Prepare-only verifies the package download, not Windows Authenticode. Signature verification happens before a normal Windows launch.
Parser tests and a real package download with size/SHA-256 verification passed on macOS. Windows launch and Authenticode verification have not yet been tested on Windows.

## Disclaimer

Not affiliated with Valve. Steam binaries are not included in the source repository.
See Valve's [Steam relocation guide](https://help.steampowered.com/en/faqs/view/4BD4-4528-6B2E-8327).
