#!/usr/bin/env python3
# asset-revision: exact-user-logo-v2
import shutil
import subprocess
import sys
from workshop_ui import WorkshopTile, WorkshopPanel, BrandTitle
from pathlib import Path

from PySide6.QtCore import QDateTime, QPointF, QRectF, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import (
    QColor,
    QCursor,
    QDesktopServices,
    QFont,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "John's Garage"
APP_ICON = "/usr/share/shop-os/assets/johns-garage.png"
CURSOR_ICON = "/usr/share/shop-os/assets/wrench-pointer.png"
MANUALS_DIR = Path.home() / "Documents" / "Shop Manuals"

PARTS_SITES = {
    "RockAuto": "https://www.rockauto.com/",
    "O'Reilly Auto Parts": "https://www.oreillyauto.com/",
    "Advance Auto Parts": "https://shop.advanceautoparts.com/",
    "AutoZone": "https://www.autozone.com/",
}


def load_engine_pixmap():
    """Load the exact user-supplied John's Garage engine artwork."""
    return QPixmap(APP_ICON)


def make_wrench_pointer():
    """Use the exact wrench artwork supplied for John's Garage."""
    pix = QPixmap(CURSOR_ICON)
    if pix.isNull():
        return QCursor(Qt.ArrowCursor)
    # The source wrench already points upper-left; the open jaw is the click point.
    return QCursor(pix, 4, 4)


def run_detached(program, args=None):
    args = args or []
    if shutil.which(program) is None:
        return False
    return subprocess.Popen([program, *args], start_new_session=True) is not None


class ShopOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pointer = make_wrench_pointer()
        self.setWindowTitle(APP_NAME)
        engine_icon_pixmap = load_engine_pixmap()
        if not engine_icon_pixmap.isNull():
            self.setWindowIcon(QIcon(engine_icon_pixmap))
        else:
            self.setWindowIcon(QIcon(APP_ICON))
        self.resize(1180, 760)
        self.setMinimumSize(940, 640)

        MANUALS_DIR.mkdir(parents=True, exist_ok=True)

        root = QWidget()
        root.setObjectName("root")
        root.setCursor(self.pointer)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self.build_header())
        self.subheader = self.build_subheader()
        self.subheader.hide()
        outer.addWidget(self.subheader)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.build_home())
        self.stack.addWidget(self.build_parts())
        self.stack.addWidget(self.build_remote())
        self.stack.addWidget(self.build_health())
        self.stack.addWidget(self.build_updates())
        self.stack.addWidget(self.build_settings())
        self.stack.addWidget(self.build_videos())
        outer.addWidget(self.stack, 1)

        outer.addWidget(self.build_footer())
        self.setCentralWidget(root)
        self.apply_style()

    def set_pointer(self, widget):
        widget.setCursor(self.pointer)
        return widget

    def action_button(self, text, callback, primary=False, icon=None):
        btn = QPushButton(text)
        self.set_pointer(btn)
        btn.setMinimumHeight(58)
        btn.setObjectName("primaryAction" if primary else "actionButton")
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
            btn.setIconSize(QSize(25, 25))
        btn.clicked.connect(callback)
        return btn

    def tile(self, title, icon_name, callback, number):
        btn = WorkshopTile(title, number)
        self.set_pointer(btn)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.clicked.connect(callback)
        return btn

    def build_header(self):
        frame = WorkshopPanel()
        self.set_pointer(frame)
        frame.setObjectName("header")
        frame.setMinimumHeight(144)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(22, 10, 22, 10)
        layout.setSpacing(16)

        logo = QLabel()
        logo.setObjectName("brandLogo")
        engine_pixmap = load_engine_pixmap()
        if not engine_pixmap.isNull():
            logo.setPixmap(
                engine_pixmap.scaled(
                    QSize(120, 120),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            logo.setText("JG")
        logo.setFixedSize(124, 124)
        logo.setAlignment(Qt.AlignCenter)

        brand = BrandTitle()
        self.set_pointer(brand)

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

        layout.addWidget(logo)
        layout.addWidget(brand, 2)
        layout.addStretch(1)
        self.clock.setMinimumSize(180, 80)
        layout.addWidget(self.clock)
        self.status_label.setText("●  Wi-Fi\n●  Updates OK\n●  Support Ready")
        self.status_label.setMinimumWidth(135)
        layout.addWidget(self.status_label)
        return frame

    def build_subheader(self):
        frame = QFrame()
        self.set_pointer(frame)
        frame.setObjectName("subheader")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(22, 8, 22, 8)

        self.back_btn = QPushButton("←  BACK")
        self.set_pointer(self.back_btn)
        self.back_btn.setObjectName("backButton")
        self.back_btn.clicked.connect(lambda: self.show_page(0))
        self.back_btn.hide()

        self.page_title = QLabel("HOME  /  WORKSTATION")
        self.page_title.setObjectName("pageTitle")

        ready = QLabel("● SYSTEM READY")
        ready.setObjectName("readyLabel")

        layout.addWidget(self.back_btn)
        layout.addWidget(self.page_title)
        layout.addStretch(1)
        layout.addWidget(ready)
        return frame

    def build_footer(self):
        frame = WorkshopPanel()
        self.set_pointer(frame)
        frame.setObjectName("footer")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(28, 14, 28, 14)
        storage = QLabel("●  Storage: available")
        network = QLabel("●  Network: checking…")
        ready = QLabel("●  Console: ready")
        for label in [storage, network, ready]:
            label.setObjectName("footerStatus")
            layout.addWidget(label)
            if label is not ready:
                layout.addStretch(1)
        self.network_label = network
        self.network_timer = QTimer(self)
        self.network_timer.timeout.connect(self.update_network_status)
        self.network_timer.start(15000)
        self.update_network_status()
        return frame

    def update_network_status(self):
        try:
            interfaces = Path("/sys/class/net").iterdir()
            connected = any(p.name != "lo" and (p / "operstate").read_text().strip() == "up"
                            for p in interfaces)
            self.network_label.setText("●  Network: connected" if connected else "○  Network: offline")
        except OSError:
            self.network_label.setText("○  Network: unknown")

    def build_home(self):
        page = QWidget()
        self.set_pointer(page)
        page.setObjectName("homePage")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(20, 12, 20, 16)
        outer.setSpacing(16)

        console = WorkshopPanel()
        self.set_pointer(console)
        console.setObjectName("consoleFrame")
        grid = QGridLayout(console)
        grid.setContentsMargins(14, 14, 14, 14)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        tiles = [
            ("REPAIR & MAINTENANCE VIDEOS", "video-x-generic", lambda: self.show_page(6, "REPAIR & MAINTENANCE VIDEOS")),
            ("PARTS LOOKUP", "applications-internet", lambda: self.show_page(1, "PARTS LOOKUP")),
            ("REMOTE SUPPORT", "preferences-desktop-remote-desktop", lambda: self.show_page(2, "REMOTE SUPPORT")),
            ("SYSTEM HEALTH", "utilities-system-monitor", lambda: self.show_page(3, "SYSTEM HEALTH")),
            ("UPDATES / RECOVERY", "system-software-update", lambda: self.show_page(4, "UPDATES / RECOVERY")),
            ("SETTINGS", "settings-configure", lambda: self.show_page(5, "SETTINGS")),
        ]

        for i, item in enumerate(tiles, start=1):
            grid.addWidget(self.tile(*item, i), (i - 1) // 3, (i - 1) % 3)

        outer.addWidget(console, 1)
        return page

    def subpage(self, intro):
        page = QWidget()
        self.set_pointer(page)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 26, 32, 26)
        layout.setSpacing(16)

        intro_box = QFrame()
        self.set_pointer(intro_box)
        intro_box.setObjectName("infoPanel")
        intro_layout = QVBoxLayout(intro_box)
        intro_layout.setContentsMargins(18, 14, 18, 14)

        label = QLabel(intro)
        label.setObjectName("intro")
        label.setWordWrap(True)
        intro_layout.addWidget(label)

        layout.addWidget(intro_box)
        return page, layout

    def build_videos(self):
        page, layout = self.subpage(
            "Choose a video source. Look up your vehicle's year, make, model and engine to find relevant repair and maintenance videos."
        )
        layout.addWidget(self.action_button(
            "CarCareKiosk — Repair & Maintenance Videos",
            lambda: QDesktopServices.openUrl(QUrl("https://www.carcarekiosk.com/")),
            True, "video-x-generic",
        ))
        layout.addWidget(self.action_button(
            "YouTube — Search Repair Videos",
            lambda: QDesktopServices.openUrl(QUrl("https://www.youtube.com/")),
            False, "video-x-generic",
        ))
        layout.addStretch(1)
        return page

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
        self.health_output.setCursor(Qt.IBeamCursor)

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
        self.update_output.setCursor(Qt.IBeamCursor)

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
        self.subheader.setVisible(index != 0)
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
        self.clock.setText(QDateTime.currentDateTime().toString("h:mm AP\nddd MMM d, yyyy"))

    def apply_style(self):
        self.setStyleSheet("""
            QWidget#root, QWidget#homePage {
                background: #0c0f12;
                color: #f5f6f7;
                font-family: "Noto Sans", "Segoe UI", sans-serif;
            }

            QFrame#unusedHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #161b1e, stop:0.5 #101416, stop:1 #202528);
                border-top: 1px solid #4b5359;
                border-bottom: 3px solid #ec491a;
            }

            QLabel#brandLogo {
                background: transparent;
                border: none;
                padding: 0px;
            }

            QLabel#headerTitle {
                color: white;
                font-size: 28px;
                font-weight: 900;
                letter-spacing: 1px;
            }

            QLabel#brandSubtitle {
                color: #ffd8bd;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 2px;
            }

            QLabel#clock {
                color: white;
                font-size: 20px;
                font-weight: 800;
                background: transparent;
                border: none;
                padding: 0px;
            }

            QLabel#statusLabel {
                color: #bff8c9;
                font-size: 12px;
                font-weight: 800;
            }

            QFrame#subheader {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252b30, stop:1 #171b1f);
                border-bottom: 1px solid #424b53;
            }

            QLabel#pageTitle {
                color: #eef1f3;
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 1px;
            }

            QLabel#readyLabel {
                color: #8fed9d;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 1px;
            }

            QPushButton#backButton {
                background: #2b3238;
                color: white;
                border: 1px solid #59636b;
                border-radius: 7px;
                padding: 7px 12px;
                font-size: 11px;
                font-weight: 900;
            }

            QPushButton#backButton:hover {
                border-color: #ee7a22;
            }

            QFrame#heroPanel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1b2025, stop:0.55 #252b30, stop:1 #15191d);
                border: 1px solid #475159;
                border-left: 6px solid #ee7a22;
                border-radius: 9px;
            }

            QLabel#heroBadge {
                background: #8f2026;
                color: white;
                border: 2px solid #d65359;
                border-radius: 21px;
                font-size: 13px;
                font-weight: 900;
            }

            QLabel#heroTitle {
                color: white;
                font-size: 16px;
                font-weight: 900;
                letter-spacing: 1px;
            }

            QLabel#heroText {
                color: #ee9a59;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 2px;
            }

            QFrame#unusedConsoleFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #151a1e, stop:1 #0d1013);
                border: 2px solid #424a51;
                border-top: 5px solid #686f75;
                border-radius: 16px;
            }

            QToolButton#scannerTile {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #30373d, stop:0.12 #262c31, stop:1 #171b1f);
                color: #ffffff;
                border-left: 2px solid #5b6369;
                border-right: 2px solid #15181b;
                border-bottom: 4px solid #0a0c0e;
                border-top: 8px solid #a7262d;
                border-radius: 15px;
                padding: 20px 14px;
                font-size: 16px;
                font-weight: 900;
                letter-spacing: 0.5px;
            }

            QToolButton#scannerTile:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d454c, stop:1 #20262b);
                border-left: 2px solid #ee7a22;
                border-right: 2px solid #ee7a22;
                border-bottom: 4px solid #7d3a0f;
                border-top: 8px solid #ee7a22;
            }

            QToolButton#scannerTile:pressed {
                background: #111417;
                border-color: #ff9d4f;
            }

            QFrame#infoPanel {
                background: #181d21;
                border: 1px solid #3d464e;
                border-left: 5px solid #f04b19;
                border-radius: 8px;
            }

            QLabel#intro {
                color: #d7dce0;
                font-size: 15px;
                font-weight: 650;
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
                background: #c33b13;
                border-color: #f76a2f;
            }

            QPushButton#primaryAction:hover {
                background: #e34c19;
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

            QFrame#unusedFooter {
                background: #080a0c;
                border-top: 1px solid #30373d;
            }

            QFrame#footer QLabel {
                color: #89939c;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QFrame#footer QLabel#footerStatus {
                color: #b9c4b5;
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0px;
            }
            QStackedWidget, QStackedWidget > QWidget {
                background: #101416;
                color: #f5f6f7;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("John's Garage")
    engine_icon_pixmap = load_engine_pixmap()
    if not engine_icon_pixmap.isNull():
        app.setWindowIcon(QIcon(engine_icon_pixmap))
    else:
        app.setWindowIcon(QIcon(APP_ICON))
    app.setFont(QFont("Noto Sans", 10))

    window = ShopOSWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

