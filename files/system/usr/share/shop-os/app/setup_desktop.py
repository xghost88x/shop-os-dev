#!/usr/bin/env python3
"""Install the simple workshop desktop once, preserving the user's old layout."""
import json
import shutil
import sys
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QStandardPaths, QTimer
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage

ASSETS = Path("/usr/share/shop-os/desktop")
STATE = Path(QStandardPaths.writableLocation(QStandardPaths.GenericDataLocation)) / "johns-garage-desktop"
PREVIOUS_MARKER = STATE / "simple-desktop-v1.applied"
MARKER = STATE / "simple-desktop-v2.applied"
CONFIG = Path(QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation))


class Setup:
    def __init__(self, app):
        self.app = app
        self.attempts = 0
        self.timer = QTimer(app)
        self.timer.timeout.connect(self.apply)

    def apply(self):
        if MARKER.exists():
            self.app.quit()
            return
        self.attempts += 1
        if self.attempts > 30:
            print("John's Garage desktop setup: Plasma was unavailable; will retry next login.", file=sys.stderr)
            self.app.quit()
            return
        interface = QDBusInterface("org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell", QDBusConnection.sessionBus())
        if not interface.isValid():
            return
        STATE.mkdir(parents=True, exist_ok=True)
        backup = STATE / "original-layout"
        if not backup.exists():
            backup.mkdir()
            for filename in ["plasma-org.kde.plasma.desktop-appletsrc", "plasmarc", "kdeglobals"]:
                source = CONFIG / filename
                if source.exists():
                    shutil.copy2(source, backup / filename)
        shortcuts = STATE / "shortcuts"
        shortcuts.mkdir(exist_ok=True)
        apps = Path("/usr/share/applications")
        for source in sorted(apps.glob("johns-garage-0*.desktop")):
            target = shortcuts / source.name
            if not target.exists():
                target.symlink_to(source)
        layout = "panel-tweaks.js" if PREVIOUS_MARKER.exists() else "layout.js"
        script = (ASSETS / layout).read_text().replace("__SHORTCUT_URL__", json.dumps(shortcuts.as_uri()))
        interface.setTimeout(15000)
        result = interface.call("evaluateScript", script)
        if result.type() == QDBusMessage.ErrorMessage:
            print("John's Garage desktop setup:", result.errorMessage(), file=sys.stderr)
            return
        output = "\n".join(str(value) for value in result.arguments())
        if "JOHNS_GARAGE_DESKTOP_READY" not in output:
            print("John's Garage desktop setup did not complete:", output, file=sys.stderr)
            return
        MARKER.write_text("Applied slim KDE panel v2.\n")
        self.app.quit()


def main():
    app = QCoreApplication(sys.argv)
    setup = Setup(app)
    setup.timer.start(2000)
    QTimer.singleShot(0, setup.apply)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
