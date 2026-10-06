#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QDateTime, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "John's Garage"
MANUALS_DIR = Path.home() / "Documents" / "Shop Manuals"

PARTS_SITES = {
    "RockAuto": "https://www.rockauto.com/",
    "O'Reilly Auto Parts": "https://www.oreillyauto.com/",
    "Advance Auto Parts": "https://shop.advanceautoparts.com/",
    "AutoZone": "https://www.autozone.com/",
}


def run_detached(program, args=None):
    args = args or []
    if shutil.which(program) is None:
        return False
    return subprocess.Popen([program, *args], start_new_session=True) is not None


class ShopOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1180, 760)
        self.setMinimumSize(940, 640)

        MANUALS_DIR.mkdir(parents=True, exist_ok=True)

        root = QWidget()
        root.setObjectName("root")

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self.build_header())
        outer.addWidget(self.build_subheader())

        self.stack = QStackedWidget()
        self.stack.addWidget(self.build_home())
        self.stack.addWidget(self.build_parts())
        self.stack.addWidget(self.build_remote())
        self.stack.addWidget(self.build_health())
        self.stack.addWidget(self.build_updates())
        self.stack.addWidget(self.build_settings())
        outer.addWidget(self.stack, 1)

        outer.addWidget(self.build_footer())
        self.setCentralWidget(root)
        self.apply_style()

    def action_button(self, text, callback, primary=False, icon=None):
        btn = QPushButton(text)
        btn.setMinimumHeight(58)
        btn.setObjectName("primaryAction" if primary else "actionButton")
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
            btn.setIconSize(QSize(25, 25))
        btn.clicked.connect(callback)
        return btn

    def tile(self, title, subtitle, icon_name, callback):
        btn = QToolButton()
        btn.setObjectName("scannerTile")
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn.setText(f"{title}\n{subtitle}")
        btn.setIcon(QIcon.fromTheme(icon_name))
        btn.setIconSize(QSize(54, 54))
        btn.setMinimumHeight(188)
        btn.setSizePolicy(btn.sizePolicy().horizontalPolicy(), btn.sizePolicy().verticalPolicy())
        btn.clicked.connect(callback)
        return btn

    def build_header(self):
        frame = QFrame()
        frame.setObjectName("header")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(18)

        brand = QWidget()
        brand.setObjectName("brandBlock")
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(0)

        title = QLabel("JOHN'S GARAGE")
        title.setObjectName("headerTitle")
        subtitle = QLabel("AUTOMOTIVE SERVICE CONSOLE")
        subtitle.setObjectName("brandSubtitle")
        brand_layout.addWidget(title)
        brand_layout.addWidget(subtitle)

        self.clock = QLabel()
        self.clock.setObjectName("clock")
        self.clock.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("●  Wi-Fi   |   ●  Updates OK   |   ●  Support Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        layout.addWidget(brand, 2)
        layout.addWidget(self.clock, 1)
        layout.addWidget(self.status_label, 2)
        return frame

    def build_subheader(self):
        frame = QFrame()
        frame.setObjectName("subheader")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(22, 8, 22, 8)

        self.back_btn = QPushButton("←  BACK")
        self.back_btn.setObjectName("backButton")
        self.back_btn.clicked.connect(lambda: self.show_page(0))
        self.back_btn.hide()

        self.page_title = QLabel("HOME  /  WORKSTATION")
        self.page_title.setObjectName("pageTitle")

        ready = QLabel("SYSTEM READY")
        ready.setObjectName("readyLabel")

        layout.addWidget(self.back_btn)
        layout.addWidget(self.page_title)
        layout.addStretch(1)
        layout.addWidget(ready)
        return frame

    def build_footer(self):
        frame = QFrame()
        frame.setObjectName("footer")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(22, 8, 22, 8)
        layout.addWidget(QLabel("JOHN'S GARAGE  •  SERVICE CONSOLE"))
        layout.addStretch(1)
        layout.addWidget(QLabel("SIGNED ATOMIC IMAGE  •  READY"))
        return frame

    def build_home(self):
        page = QWidget()
        page.setObjectName("homePage")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(26, 22, 26, 24)
        outer.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("heroPanel")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(20, 13, 20, 13)

        hero_left = QLabel("SHOP COMMAND CENTER")
        hero_left.setObjectName("heroTitle")
        hero_desc = QLabel("Manuals  •  Parts  •  Support  •  Diagnostics  •  Recovery")
        hero_desc.setObjectName("heroText")
        hero_desc.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        hero_layout.addWidget(hero_left)
        hero_layout.addStretch(1)
        hero_layout.addWidget(hero_desc)
        outer.addWidget(hero)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        tiles = [
            ("SERVICE MANUALS", "Local manuals & PDFs", "x-office-document", self.open_manuals),
            ("PARTS LOOKUP", "Supplier quick access", "applications-internet", lambda: self.show_page(1, "PARTS LOOKUP")),
            ("REMOTE SUPPORT", "RustDesk & network", "preferences-desktop-remote-desktop", lambda: self.show_page(2, "REMOTE SUPPORT")),
            ("SYSTEM HEALTH", "Temps · drives · resources", "utilities-system-monitor", lambda: self.show_page(3, "SYSTEM HEALTH")),
            ("UPDATES / RECOVERY", "Atomic system control", "system-software-update", lambda: self.show_page(4, "UPDATES / RECOVERY")),
            ("SETTINGS", "Workstation configuration", "settings-configure", lambda: self.show_page(5, "SETTINGS")),
        ]

        for i, item in enumerate(tiles):
            grid.addWidget(self.tile(*item), i // 3, i % 3)

        outer.addLayout(grid, 1)
        return page

    def subpage(self, intro):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 26, 32, 26)
        layout.setSpacing(16)

        intro_box = QFrame()
        intro_box.setObjectName("infoPanel")
        intro_layout = QVBoxLayout(intro_box)
        intro_layout.setContentsMargins(18, 14, 18, 14)

        label = QLabel(intro)
        label.setObjectName("intro")
        label.setWordWrap(True)
        intro_layout.addWidget(label)

        layout.addWidget(intro_box)
        return page, layout

    def build_parts(self):
        page, layout = self.subpage(
            "Choose a supplier. The selected catalog opens in Firefox."
        )
        grid = QGridLayout()
        grid.setSpacing(14)

        for i, (name, url) in enumerate(PARTS_SITES.items()):
            btn = self.action_button(
                name,
                lambda checked=False, address=url: QDesktopServices.openUrl(QUrl(address)),
                primary=True,
                icon="applications-internet",
            )
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch(1)
        return page

    def build_remote(self):
        page, layout = self.subpage(
            "Remote assistance tools for quick support without digging through the desktop."
        )
        layout.addWidget(self.action_button("Open RustDesk", self.open_rustdesk, True, "preferences-desktop-remote-desktop"))
        layout.addWidget(self.action_button("Open KDE Network Settings", self.open_network_settings, False, "network-wired"))
        layout.addStretch(1)
        return page

    def build_health(self):
        page, layout = self.subpage(
            "Run a workstation health scan for deployment, storage, memory, temperatures and attached drives."
        )
        self.health_output = QPlainTextEdit()
        self.health_output.setObjectName("output")
        self.health_output.setReadOnly(True)

        layout.addWidget(self.action_button("RUN SYSTEM HEALTH SCAN", self.refresh_health, True, "utilities-system-monitor"))
        layout.addWidget(self.health_output, 1)
        return page

    def build_updates(self):
        page, layout = self.subpage(
            "John's Garage uses signed atomic deployments. The previous working deployment remains available as a rollback point."
        )
        self.update_output = QPlainTextEdit()
        self.update_output.setObjectName("output")
        self.update_output.setReadOnly(True)

        row = QHBoxLayout()
        row.addWidget(self.action_button("Show Deployment Status", self.refresh_update_status, False, "dialog-information"))
        row.addWidget(self.action_button("Check / Stage Update", self.stage_update, True, "system-software-update"))

        layout.addLayout(row)
        layout.addWidget(self.update_output, 1)
        return page

    def build_settings(self):
        page, layout = self.subpage(
            "Workstation settings and information for John's Garage."
        )
        layout.addWidget(self.action_button("KDE System Settings", self.open_system_settings, True, "settings-configure"))
        layout.addWidget(self.action_button("Network Settings", self.open_network_settings, False, "network-wired"))
        layout.addWidget(self.action_button("About John's Garage", self.show_about, False, "help-about"))
        layout.addStretch(1)
        return page

    def show_page(self, index, title="HOME  /  WORKSTATION"):
        self.stack.setCurrentIndex(index)
        self.back_btn.setVisible(index != 0)
        self.page_title.setText(title if index != 0 else "HOME  /  WORKSTATION")

    def open_manuals(self):
        MANUALS_DIR.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(MANUALS_DIR)))

    def open_rustdesk(self):
        if not run_detached("flatpak", ["run", "com.rustdesk.RustDesk"]):
            QMessageBox.warning(self, APP_NAME, "RustDesk could not be started.")

    def open_system_settings(self):
        if not run_detached("systemsettings"):
            QMessageBox.warning(self, APP_NAME, "KDE System Settings could not be started.")

    def open_network_settings(self):
        if not run_detached("systemsettings", ["kcm_networkmanagement"]):
            self.open_system_settings()

    def refresh_health(self):
        sections = []

        def capture(title, command):
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                data = (result.stdout or result.stderr).strip()
            except Exception as exc:
                data = f"Unavailable: {exc}"
            sections.append(f"=== {title} ===\n{data or 'No data returned.'}")

        capture("Deployment", ["rpm-ostree", "status"])
        capture("Storage", ["df", "-h", "/"])
        capture("Memory", ["free", "-h"])
        capture("Temperatures", ["sensors"])
        capture("Block Devices", ["lsblk", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL"])
        self.health_output.setPlainText("\n\n".join(sections))

    def refresh_update_status(self):
        try:
            result = subprocess.run(
                ["rpm-ostree", "status"], capture_output=True, text=True, timeout=15
            )
            self.update_output.setPlainText((result.stdout or result.stderr).strip())
        except Exception as exc:
            self.update_output.setPlainText(f"Unable to read deployment status:\n{exc}")

    def stage_update(self):
        answer = QMessageBox.question(
            self,
            "Check for update",
            "Check for and stage the latest John's Garage deployment?\n\nA reboot is only needed if a newer image is found.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if answer != QMessageBox.Yes:
            return

        self.update_output.setPlainText("Checking for updates…")
        QApplication.processEvents()
        try:
            result = subprocess.run(
                ["rpm-ostree", "upgrade"], capture_output=True, text=True, timeout=300
            )
            self.update_output.setPlainText(
                (result.stdout or result.stderr).strip() or "Update check finished."
            )
        except Exception as exc:
            self.update_output.setPlainText(f"Update failed:\n{exc}")

    def show_about(self):
        QMessageBox.information(
            self,
            APP_NAME,
            "John's Garage\n\nAutomotive Service Console\nDevelopment build\nFedora Atomic KDE / BlueBuild",
        )

    def update_clock(self):
        self.clock.setText(QDateTime.currentDateTime().toString("ddd MMM d   h:mm AP"))

    def apply_style(self):
        self.setStyleSheet("""
            QWidget#root, QWidget#homePage {
                background: #101316;
                color: #f5f6f7;
                font-family: "Noto Sans", "Segoe UI", sans-serif;
            }

            QFrame#header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #76191d, stop:0.48 #a92127, stop:1 #74181c);
                border-bottom: 3px solid #ee7a22;
            }

            QLabel#headerTitle {
                color: white;
                font-size: 27px;
                font-weight: 900;
                letter-spacing: 1px;
            }

            QLabel#brandSubtitle {
                color: #ffd9c1;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 2px;
            }

            QLabel#clock {
                color: white;
                font-size: 15px;
                font-weight: 800;
            }

            QLabel#statusLabel {
                color: #d9ffe0;
                font-size: 13px;
                font-weight: 750;
            }

            QFrame#subheader {
                background: #1c2227;
                border-bottom: 1px solid #3b444c;
            }

            QLabel#pageTitle {
                color: #f0f2f4;
                font-size: 12px;
                font-weight: 850;
                letter-spacing: 1px;
            }

            QLabel#readyLabel {
                color: #8fea9e;
                font-size: 11px;
                font-weight: 850;
                letter-spacing: 1px;
            }

            QPushButton#backButton {
                background: #2a3036;
                color: white;
                border: 1px solid #4a535c;
                border-radius: 7px;
                padding: 7px 12px;
                font-size: 11px;
                font-weight: 850;
            }

            QPushButton#backButton:hover {
                border-color: #ee7a22;
            }

            QFrame#heroPanel {
                background: #181d21;
                border: 1px solid #394149;
                border-left: 5px solid #ee7a22;
                border-radius: 8px;
            }

            QLabel#heroTitle {
                color: white;
                font-size: 15px;
                font-weight: 900;
                letter-spacing: 1px;
            }

            QLabel#heroText {
                color: #aeb7bf;
                font-size: 12px;
                font-weight: 650;
            }

            QToolButton#scannerTile {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #262c31, stop:1 #181c20);
                color: #f7f8f9;
                border: 2px solid #722126;
                border-top: 7px solid #be3037;
                border-radius: 14px;
                padding: 18px 14px;
                font-size: 15px;
                font-weight: 800;
            }

            QToolButton#scannerTile:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #343b41, stop:1 #20262b);
                border: 2px solid #ee7a22;
                border-top: 7px solid #ee7a22;
            }

            QToolButton#scannerTile:pressed {
                background: #0e1113;
                border-color: #ff9c4d;
            }

            QFrame#infoPanel {
                background: #181d21;
                border: 1px solid #3d464e;
                border-left: 5px solid #be3037;
                border-radius: 8px;
            }

            QLabel#intro {
                color: #d7dce0;
                font-size: 15px;
                font-weight: 600;
            }

            QPushButton#actionButton, QPushButton#primaryAction {
                background: #252b30;
                color: white;
                border: 2px solid #48525b;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 15px;
                font-weight: 800;
            }

            QPushButton#actionButton:hover {
                border-color: #ee7a22;
                background: #30373d;
            }

            QPushButton#primaryAction {
                background: #9c252b;
                border-color: #c43a40;
            }

            QPushButton#primaryAction:hover {
                background: #b92c33;
                border-color: #ee7a22;
            }

            QPlainTextEdit#output {
                background: #090b0d;
                color: #dfe5e9;
                border: 1px solid #3c454d;
                border-radius: 9px;
                padding: 11px;
                font-family: monospace;
                font-size: 13px;
            }

            QFrame#footer {
                background: #090b0d;
                border-top: 1px solid #30373d;
            }

            QFrame#footer QLabel {
                color: #89939c;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("John's Garage")
    app.setFont(QFont("Noto Sans", 10))

    window = ShopOSWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
