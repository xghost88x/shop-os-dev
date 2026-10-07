#!/usr/bin/env bash
set -euo pipefail
plymouth-set-default-theme dads-garage
systemctl enable dads-garage-autologin.service
systemctl --global enable dads-garage-status.service
