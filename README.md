# PocketSteam

**Language:** English · [فارسی](docs/README.fa.md) · [العربية](docs/README.ar.md)

Run Steam on Windows from a local folder, without running the Steam installer.
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
