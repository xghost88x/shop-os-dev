#!/usr/bin/env python3
"""Enable workshop autologin once for the primary installed local account."""
import pwd
from pathlib import Path


def configure(account, root=Path('/')):
    state = root / 'var/lib/dads-garage'
    marker = state / 'autologin-v1.applied'
    if marker.exists():
        return False
    if account.pw_uid != 1000 or account.pw_shell.endswith(('nologin', 'false')):
        return False
    if not (root / account.pw_dir.lstrip('/')).is_dir():
        return False
    sessions = root / 'usr/share/wayland-sessions'
    session = next((p for p in sorted(sessions.glob('*.desktop'))
                    if 'startplasma-wayland' in p.read_text()), None)
    if session is None:
        return False
    target = root / 'etc/sddm.conf.d/zz-dads-garage-autologin.conf'
    state.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        (state / 'original-autologin.conf').write_bytes(target.read_bytes())
    temporary = target.with_suffix('.tmp')
    temporary.write_text('[Autologin]\nUser=' + account.pw_name + '\nSession=' +
                         session.name + '\nRelogin=false\n')
    temporary.chmod(0o644)
    temporary.replace(target)
    marker.write_text('Automatic login configured for ' + account.pw_name + '\n')
    return True


def main():
    try:
        account = pwd.getpwuid(1000)
    except KeyError:
        return
    if configure(account):
        print('Dad\'s Garage: automatic login enabled for ' + account.pw_name)


if __name__ == '__main__':
    main()
