"""Extract Valve's Linux bootstrap into a user folder; never run package installers."""
import hashlib
import io
import os
from pathlib import Path
import platform
import posixpath
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

URL = 'https://repo.steampowered.com/steam/archive/stable/steam_latest.deb'
SHA256 = '765aba9a0ed339a50226ceb614fcc9879a991ba184098bc8de920efb12c714a4'


def deb_payload(data):
    if not data.startswith(b'!<arch>\n'):
        raise ValueError('Invalid Debian archive')
    offset = 8
    while offset + 60 <= len(data):
        header = data[offset:offset + 60]
        if header[58:60] != b'`\n':
            raise ValueError('Invalid ar header')
        name = header[:16].decode('ascii').strip().rstrip('/')
        size = int(header[48:58])
        offset += 60
        if size < 0 or offset + size > len(data):
            raise ValueError('Truncated Debian archive')
        if name in ('data.tar.xz', 'data.tar.gz'):
            return data[offset:offset + size]
        offset += size + size % 2
    raise ValueError('Unsupported Debian package payload')


def unpack_safe(archive, dest):
    members = archive.getmembers()
    if sum(m.size for m in members) > 512_000_000:
        raise ValueError('Oversized bootstrap archive')
    for m in members:
        name = posixpath.normpath(m.name)
        if name.startswith('/') or name == '..' or name.startswith('../') or '\\' in name:
            raise ValueError('Unsafe archive path')
        if m.issym():
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), m.linkname))
            if m.linkname.startswith('/') or target == '..' or target.startswith('../'):
                raise ValueError('Unsafe symbolic link')
        elif not (m.isfile() or m.isdir()):
            raise ValueError('Unsupported archive entry')
    # Validation precedes extraction; data filter additionally hardens modern Python.
    kwargs = {'filter': 'data'} if hasattr(tarfile, 'data_filter') else {}
    archive.extractall(dest, members=members, **kwargs)


def prepare(folder, data=None):
    folder = Path(folder)
    if folder.is_symlink():
        raise ValueError('Refusing symbolic-link Steam directory')
    if (folder / 'steam.sh').is_file():
        return folder / 'steam.sh'
    if folder.exists():
        raise ValueError('Incomplete LinuxSteam folder: move it aside before retrying')
    if data is None:
        print('Downloading Valve Linux bootstrap (no installer)...', flush=True)
        with urllib.request.urlopen(URL, timeout=60) as response:
            if not response.geturl().startswith('https://'):
                raise ValueError('Refusing insecure download')
            data = response.read(32_000_001)
    if len(data) > 32_000_000 or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('Linux package checksum changed; update PocketSteam before retrying')
    with tarfile.open(fileobj=io.BytesIO(deb_payload(data))) as package:
        member = package.getmember('./usr/lib/steam/bootstraplinux_ubuntu12_32.tar.xz')
        if not member.isfile() or member.size > 64_000_000:
            raise ValueError('Invalid Linux bootstrap member')
        bootstrap = package.extractfile(member).read()
    folder.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder.parent) as staging:
        with tarfile.open(fileobj=io.BytesIO(bootstrap)) as archive:
            unpack_safe(archive, Path(staging))
        if not (Path(staging) / 'steam.sh').is_file():
            raise ValueError('Linux bootstrap lacks steam.sh')
        os.rename(staging, folder)
    return folder / 'steam.sh'


def run(root):
    if platform.machine().lower() not in ('x86_64', 'amd64'):
        raise ValueError('Linux requires x86_64; ARM Linux is unsupported')
    if os.geteuid() == 0:
        raise ValueError('Run PocketSteam as a normal user, not root')
    if not Path('/lib/ld-linux.so.2').exists() and not Path('/lib32/ld-linux.so.2').exists():
        raise ValueError('Missing 32-bit Linux loader. No packages were installed. '
                         'This computer cannot use this bootstrap without existing prerequisites.')
    for tool in ('bash', 'tar', 'xz'):
        if not shutil.which(tool):
            raise ValueError('Missing prerequisite: ' + tool + '. No installer was run.')
    script = prepare(Path(root) / 'LinuxSteam')
    # Run steam.sh directly, not the distro wrapper that invokes steamdeps/package managers.
    subprocess.run(['bash', str(script)], cwd=script.parent,
                   env=dict(os.environ, STEAM_RUNTIME='1'), check=True)
