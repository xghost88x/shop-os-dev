#!/usr/bin/env python3
"""Show immediate shutdown feedback before handing off to system shutdown."""
import sys
from PySide6.QtCore import QProcess, QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QProgressBar, QMessageBox

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action not in ("shutdown", "restart"):
        return 2
    preview = "--preview" in sys.argv[2:]
    app = QApplication(sys.argv)
    windows = []
    for screen in app.screens():
        window = QWidget()
        window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        window.setStyleSheet("QWidget { background: #171c22; color: #edf2f7; }")
        layout = QVBoxLayout(window)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        logo = QLabel()
        pixmap = QPixmap("/usr/share/shop-os/desktop/dads-garage-start.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(440, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo.setText("Dad's Garage OS")
            logo.setStyleSheet("font-size: 32px; font-weight: bold;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        label = QLabel("Shutting down…" if action == "shutdown" else "Restarting…")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 26px;")
        layout.addWidget(label)
        progress = QProgressBar()
        progress.setRange(0, 0)
        progress.setTextVisible(False)
        progress.setFixedSize(260, 8)
        progress.setStyleSheet("QProgressBar { border: none; background: #283541; border-radius: 4px; } QProgressBar::chunk { background: #94adc2; border-radius: 4px; }")
        layout.addWidget(progress, 0, Qt.AlignHCenter)
        window.setGeometry(screen.geometry())
        window.show()
        window.windowHandle().setScreen(screen)
        window.showFullScreen()
        windows.append(window)
    process = QProcess(app)
    def failure(message):
        for window in windows:
            window.close()
        QMessageBox.warning(None, "Dad's Garage OS", message)
        app.quit()
    def finished(exit_code, exit_status):
        if exit_status != QProcess.NormalExit or exit_code != 0:
            failure("Could not " + ("shut down" if action == "shutdown" else "restart") +
                    ".\n\n" + bytes(process.readAllStandardError()).decode(errors="replace").strip())
    process.finished.connect(finished)
    process.errorOccurred.connect(lambda error: failure("Could not start the system power command.") if error == QProcess.FailedToStart else None)
    def begin():
        process.start("systemctl", ["poweroff" if action == "shutdown" else "reboot"])
    if preview:
        QTimer.singleShot(2000, app.quit)
    else:
        # Allow the compositor to paint the feedback before requesting shutdown.
        QTimer.singleShot(400, begin)
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
