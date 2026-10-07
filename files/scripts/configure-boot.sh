#!/usr/bin/env bash
set -euo pipefail
plymouth-set-default-theme dads-garage
systemctl enable dads-garage-autologin.service
systemctl --global enable dads-garage-status.service

# OSTree uses PRETTY_NAME in /usr/lib/os-release for generated boot entries.
# Preserve Fedora IDs and version fields for package and update compatibility.
python3 - <<'PY'
from pathlib import Path
path = Path('/usr/lib/os-release')
lines = path.read_text().splitlines()
branding = {'NAME': '"Dad\'s Garage OS"', 'PRETTY_NAME': '"Dad\'s Garage OS"'}
seen = set()
for index, line in enumerate(lines):
    key = line.partition('=')[0]
    if key in branding:
        lines[index] = key + '=' + branding[key]
        seen.add(key)
lines.extend(key + '=' + value for key, value in branding.items() if key not in seen)
path.write_text('\n'.join(lines) + '\n')
PY
