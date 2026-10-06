"""One dashboard per user; launcher returns to the existing fullscreen window."""
import os
from pathlib import Path
from PySide6.QtCore import QLockFile, QStandardPaths, QTimer
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QMessageBox


class DashboardSession:
    def __init__(self, app, requested_page="home"):
        self.window = None
        self.requested_page = requested_page if requested_page in ("home", "videos", "parts") else "home"
        runtime = QStandardPaths.writableLocation(QStandardPaths.RuntimeLocation)
        if not runtime:
            runtime = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
        self.name = str(Path(runtime) / f"johns-garage-{os.getuid()}")
        self.lock = QLockFile(self.name + ".lock")
        self.lock.setStaleLockTime(0)
        self.server = QLocalServer(app)
        self.server.setSocketOptions(QLocalServer.UserAccessOption)
        self.server.newConnection.connect(self.restore)

    def activate_existing(self):
        client = QLocalSocket()
        client.connectToServer(self.name)
        if not client.waitForConnected(500):
            return False
        client.write((self.requested_page + "\n").encode())
        client.waitForBytesWritten(500)
        client.disconnectFromServer()
        return True

    def start(self):
        if self.activate_existing():
            return False
        if not self.lock.tryLock(1000):
            if not self.activate_existing():
                QMessageBox.warning(None, "John's Garage", "The dashboard is already starting. Please try opening it again in a moment.")
            return False
        # Only the lock owner may clear a socket left behind after a crash.
        QLocalServer.removeServer(self.name)
        if not self.server.listen(self.name):
            self.lock.unlock()
            QMessageBox.warning(None, "John's Garage", "Unable to start the dashboard: " + self.server.errorString())
            return False
        return True

    def restore(self):
        while self.server.hasPendingConnections():
            client = self.server.nextPendingConnection()
            def receive(socket=client):
                if not socket.canReadLine():
                    return
                request = bytes(socket.readLine(64)).decode("utf-8", errors="replace").strip()
                if self.window is not None:
                    self.window.return_to_dashboard({"videos": 6, "parts": 1}.get(request, 0))
                socket.close()
                socket.deleteLater()
            client.readyRead.connect(receive)
            if client.bytesAvailable():
                receive()
            else:
                QTimer.singleShot(2000, client.deleteLater)

