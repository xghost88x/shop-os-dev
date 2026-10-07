#!/usr/bin/env python3
"""Enable workshop autologin once for the primary installed local account."""
import configparser
import pwd
from pathlib import Path


def configure(account, root=Path('/')):
    state = root / 'var/lib/dads-garage'
    marker = state / 'autologin-v2.applied'
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
    manager = root / 'etc/systemd/system/display-manager.service'
    # Read the link name, including absolute links inside a test root.
    import os
    manager_name = Path(os.readlink(manager)).name if manager.is_symlink() else ''
    if manager_name == 'plasmalogin.service':
        target = root / 'etc/plasmalogin.conf'
    elif manager_name == 'sddm.service':
        target = root / 'etc/sddm.conf.d/zz-dads-garage-autologin.conf'
    else:
        print("Dad's Garage: unknown login manager; automatic login unchanged")
        return False
    state.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.optionxform = str
    if target.exists():
        config.read(target)
        (state / ('original-' + target.name)).write_bytes(target.read_bytes())
    if not config.has_section('Autologin'):
        config.add_section('Autologin')
    config['Autologin'].update(User=account.pw_name, Session=session.name, Relogin='false')
    temporary = target.with_suffix('.tmp')
    with temporary.open('w') as stream:
        config.write(stream, space_around_delimiters=False)
    temporary.chmod(0o644)
    temporary.replace(target)
    marker.write_text('Automatic login configured for ' + account.pw_name +
                      ' using ' + manager_name + '\n')
    return True


def main():
    try:
        account = pwd.getpwuid(1000)
    except KeyError:
        return
    if configure(account):
        print("Dad's Garage: automatic login enabled for " + account.pw_name)


if __name__ == '__main__':
    main()
