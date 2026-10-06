#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QDateTime, QPoint, QRect, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QCursor, QDesktopServices, QFont, QIcon, QPainter, QPen, QPixmap
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
    QVBoxLayout,
    QWidget,
)

APP_NAME = "Shop OS"
MANUALS_DIR = Path.home() / "Documents" / "Shop Manuals"

PARTS_SITES = {
    "RockAuto": "https://www.rockauto.com/",
    "O'Reilly Auto Parts": "https://www.oreillyauto.com/",
    "Advance Auto Parts": "https://shop.advanceautoparts.com/",
    "AutoZone": "https://www.autozone.com/",
}


def make_wrench_pointer():
    """Create the Shop OS wrench-shaped mouse pointer."""
    pix = QPixmap(44, 44)
    pix.fill(Qt.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)

    # Dark outline and silver shaft
    p.setPen(QPen(QColor("#111417"), 10, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPoint(9, 35), QPoint(30, 14))
    p.setPen(QPen(QColor("#d8dde2"), 6, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPoint(9, 35), QPoint(30, 14))

    # Ring handle
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(QColor("#111417"), 5))
    p.drawEllipse(QRect(3, 29, 13, 13))
    p.setPen(QPen(QColor("#d8dde2"), 3))
    p.drawEllipse(QRect(5, 31, 9, 9))

    # Open jaw / click end
    p.setPen(QPen(QColor("#111417"), 9, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPoint(29, 14), QPoint(36, 7))
    p.drawLine(QPoint(31, 16), QPoint(39, 16))
    p.setPen(QPen(QColor("#d8dde2"), 5, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPoint(29, 14), QPoint(36, 7))
    p.drawLine(QPoint(31, 16), QPoint(39, 16))

    # Orange Shop OS accent
    p.setPen(QPen(QColor("#e56b1f"), 2, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPoint(14, 30), QPoint(25, 19))
    p.end()

    # Click hotspot is at the open end of the wrench.
    return QCursor(pix, 37, 8)


def run_detached(program, args=None):
    args = args or []
    if shutil.which(program) is None:
        return False
    return subprocess.Popen([program, *args], start_new_session=True) is not None


class ShopOSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pointer = make_wrench_pointer()
        self.setCursor(self.pointer)
        self.setWindowTitle(APP_NAME)
        self.resize(1180, 760)
        self.setMinimumSize(900, 620)

        MANUALS_DIR.mkdir(parents=True, exist_ok=True)

        root = QWidget()
        root.setObjectName("root")
        root.setCursor(self.pointer)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self.build_header())

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

    def button(self, text, callback, primary=False, icon=None):
        btn = QPushButton(text)
        btn.setCursor(self.pointer)
        btn.setMinimumHeight(58)
        btn.setObjectName("primaryAction" if primary else "actionButton")
        if icon:
            btn.setIcon(QIcon.fromTheme(icon))
            btn.setIconSize(QSize(26, 26))
        btn.clicked.connect(callback)
        return btn

    def tile(self, title, subtitle, icon_name, callback):
        btn = QPushButton(f"{title}\n{subtitle}")
        btn.setCursor(self.pointer)
        btn.setObjectName("tileButton")
        btn.setMinimumHeight(175)
        btn.setIcon(QIcon.fromTheme(icon_name))
        btn.setIconSize(QSize(52, 52))
        btn.clicked.connect(callback)
        return btn

    def build_header(self):
        frame = QFrame()
        frame.setObjectName("header")
        frame.setCursor(self.pointer)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(24, 13, 24, 13)

        self.back_btn = QPushButton("←  Back")
        self.back_btn.setObjectName("backButton")
        self.back_btn.setCursor(self.pointer)
        self.back_btn.clicked.connect(lambda: self.show_page(0))
        self.back_btn.hide()

        title = QLabel(APP_NAME)
        title.setObjectName("headerTitle")

        self.page_title = QLabel("Automotive Workstation")
        self.page_title.setObjectName("pageTitle")

        self.clock = QLabel()
        self.clock.setObjectName("clock")
        self.clock.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        layout.addWidget(self.back_btn)
        layout.addWidget(title)
        layout.addSpacing(16)
        layout.addWidget(self.page_title)
        layout.addStretch(1)
        layout.addWidget(self.clock)
        return frame

    def build_footer(self):
        frame = QFrame()
        frame.setObjectName("footer")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(24, 8, 24, 8)
        layout.addWidget(QLabel("Shop OS · Development"))
        layout.addStretch(1)
        layout.addWidget(QLabel("Signed Atomic Image"))
        return frame

    def build_home(self):
        page = QWidget()
        page.setCursor(self.pointer)
        grid = QGridLayout(page)
        grid.setContentsMargins(28, 28, 28, 28)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)

        tiles = [
            ("Service Manuals", "Open local manuals and PDFs", "x-office-document", self.open_manuals),
            ("Parts Lookup", "RockAuto · O'Reilly · Advance · AutoZone", "applications-internet", lambda: self.show_page(1, "Parts Lookup")),
            ("Remote Support", "RustDesk and support tools", "preferences-desktop-remote-desktop", lambda: self.show_page(2, "Remote Support")),
            ("System Health", "Temps · drives · resources", "utilities-system-monitor", lambda: self.show_page(3, "System Health")),
            ("Updates / Recovery", "Atomic updates and deployment status", "system-software-update", lambda: self.show_page(4, "Updates / Recovery")),
            ("Settings", "System and Shop OS settings", "settings-configure", lambda: self.show_page(5, "Settings")),
        ]

        for i, item in enumerate(tiles):
            grid.addWidget(self.tile(*item), i // 3, i % 3)

        return page

    def subpage(self, intro):
        page = QWidget()
        page.setCursor(self.pointer)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(16)

        label = QLabel(intro)
        label.setObjectName("intro")
        label.setWordWrap(True)
        layout.addWidget(label)
        return page, layout

    def build_parts(self):
        page, layout = self.subpage(
            "Choose a supplier. Shop OS opens the selected site in Firefox."
        )
        grid = QGridLayout()
        grid.setSpacing(14)

        for i, (name, url) in enumerate(PARTS_SITES.items()):
            btn = self.button(
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
            "Remote support keeps troubleshooting simple when the shop needs help."
        )
        layout.addWidget(self.button("Open RustDesk", self.open_rustdesk, True, "preferences-desktop-remote-desktop"))
        layout.addWidget(self.button("Open KDE Network Settings", self.open_network_settings, False, "network-wired"))
        layout.addStretch(1)
        return page

    def build_health(self):
        page, layout = self.subpage(
            "Quick workstation diagnostics. Refresh to collect current Shop OS information."
        )
        self.health_output = QPlainTextEdit()
        self.health_output.setObjectName("output")
        self.health_output.setReadOnly(True)
        self.health_output.setCursor(Qt.IBeamCursor)

        layout.addWidget(self.button("Refresh System Health", self.refresh_health, True, "utilities-system-monitor"))
        layout.addWidget(self.health_output, 1)
        return page

    def build_updates(self):
        page, layout = self.subpage(
            "Shop OS uses signed atomic deployments. The previous working deployment remains available as a rollback point."
        )
        self.update_output = QPlainTextEdit()
        self.update_output.setObjectName("output")
        self.update_output.setReadOnly(True)
        self.update_output.setCursor(Qt.IBeamCursor)

        row = QHBoxLayout()
        row.addWidget(self.button("Show Deployment Status", self.refresh_update_status, False, "dialog-information"))
        row.addWidget(self.button("Check / Stage Update", self.stage_update, True, "system-software-update"))

        layout.addLayout(row)
        layout.addWidget(self.update_output, 1)
        return page

    def build_settings(self):
        page, layout = self.subpage(
            "Open standard KDE settings or view information about this Shop OS build."
        )
        layout.addWidget(self.button("KDE System Settings", self.open_system_settings, True, "settings-configure"))
        layout.addWidget(self.button("Network Settings", self.open_network_settings, False, "network-wired"))
        layout.addWidget(self.button("About Shop OS", self.show_about, False, "help-about"))
        layout.addStretch(1)
        return page

    def show_page(self, index, title="Automotive Workstation"):
        self.stack.setCurrentIndex(index)
        self.back_btn.setVisible(index != 0)
        self.page_title.setText(title)

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

        capture("Shop OS Deployment", ["rpm-ostree", "status"])
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
            "Check for Shop OS update",
            "Check for and stage the latest Shop OS deployment?\n\nA reboot is only needed if a newer image is found.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if answer != QMessageBox.Yes:
            return

        self.update_output.setPlainText("Checking for Shop OS updates…")
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
            "Shop OS\n\nNative automotive workstation interface\nDevelopment build\nFedora Atomic KDE / BlueBuild",
        )

    def update_clock(self):
        self.clock.setText(QDateTime.currentDateTime().toString("ddd MMM d   h:mm AP"))

    def apply_style(self):
        self.setStyleSheet("""
            QWidget#root {
                background: #111417;
                color: #f4f5f6;
                font-family: "Noto Sans", "Segoe UI", sans-serif;
            }
            QFrame#header {
                background: #991f24;
                border-bottom: 3px solid #e56b1f;
            }
            QLabel#headerTitle {
                color: white;
                font-size: 28px;
                font-weight: 800;
            }
            QLabel#pageTitle {
                color: #ffd8c0;
                font-size: 16px;
                font-weight: 650;
            }
            QLabel#clock {
                color: white;
                font-size: 15px;
                font-weight: 650;
            }
            QPushButton#backButton {
                background: #20252a;
                color: white;
                border: 1px solid #4a525a;
                border-radius: 9px;
                padding: 8px 13px;
                font-weight: 700;
            }
            QPushButton#tileButton {
                background: #f1f2f3;
                border: 4px solid #a52228;
                border-radius: 18px;
                color: #16191b;
                padding: 18px;
                font-size: 17px;
                font-weight: 750;
                text-align: center;
            }
            QPushButton#tileButton:hover {
                background: white;
                border-color: #e56b1f;
            }
            QPushButton#tileButton:pressed {
                background: #d9dde0;
            }
            QLabel#intro {
                color: #c8cdd2;
                font-size: 16px;
                padding-bottom: 4px;
            }
            QPushButton#actionButton, QPushButton#primaryAction {
                background: #23292e;
                color: white;
                border: 2px solid #475057;
                border-radius: 12px;
                padding: 12px 18px;
                font-size: 16px;
                font-weight: 750;
            }
            QPushButton#actionButton:hover {
                border-color: #e56b1f;
                background: #2c3339;
            }
            QPushButton#primaryAction {
                background: #a52228;
                border-color: #d64549;
            }
            QPushButton#primaryAction:hover {
                background: #bf292f;
                border-color: #e56b1f;
            }
            QPlainTextEdit#output {
                background: #0c0f11;
                color: #e7eaec;
                border: 1px solid #3b434a;
                border-radius: 10px;
                padding: 10px;
                font-family: monospace;
                font-size: 13px;
            }
            QFrame#footer {
                background: #0b0d0f;
                color: #9aa3aa;
                border-top: 1px solid #30363b;
            }
            QFrame#footer QLabel {
                color: #9aa3aa;
                font-size: 12px;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Shop OS Project")
    app.setFont(QFont("Noto Sans", 10))

    window = ShopOSWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
