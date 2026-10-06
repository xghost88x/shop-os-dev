#!/usr/bin/env python3
import base64
import shutil
import subprocess
import sys
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
APP_ICON = "/usr/share/icons/hicolor/64x64/apps/johns-garage.png"
ENGINE_LOGO_B64 = """iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAXuElEQVR42u1be1hTZ5p/zzk53Ey4ScCUEMRLuNoKVFsCUWpva7uODjNCIlQ7FKiiVEtr+/hsZ3dn2tlOdbS6tKCGpopgAp1ltWxtp3YVCFAL9VKBCkEFQkLEICIJkHByTvaP8rGnx0CxdXZnn+33PDwm5uQ7532/3/u+v/cSgJ/X/++F/bVvYLXZ/H/qHgI+f/j/nGatNpt/eYVGeD/2yt1SEHQ/FPk/hoDcLQVBqpKiwfuNgPIKjTArU2n5m1WA1WbzRw+LXh8sr7L/1H0jIsKqZA8teYm799+UAtinc761fUPLN+3q+42sZQ/FZicuiT3ORdn/ugLQw1htNn9tdc1+GicUepPR9X14jLIwPccNfO7+XBoqxgAA9B2dLgAAaVQkRjC0VpG2ZoeAzx++HyaB3S/hPz1dm366TnfUYrnJAAAwNF3JUM4mAACel+eBZLmcQEqxXO9muPsIhcH4lGKsozBww6xhKGcTTvJkOEFksK9NlssJhIafigTsx9g3el+4cxdPVVI0qFKXZdd/1VKEPmNourKitDibbR42F9HH3q9Rp6PZwkujIqee5ZqpP3fP6zuOoffKTXk5PC/PA1yFZWakveBOCffiI3g/1rmx3//TH999HwAYLjLQ64vn7zgXJwTO4ObnuEUWem0bc9z1ucVyk2n5pl1ttdlOCfj8HyX8jApA4atw5y6evrv3KavNdgoA4OTJGlKlLsv29iRr1q5dQ033ffaJfIeA2cNSKgwkc1/fMfX9zJx8mbvrCIbWshW2MkWGAQB1vrV9gzQi/NRsiBQ2G+8+7qDW1DadS0ldIcfBSdU3t7R8vHzZsl94e5I1WZlKC9cEkBn4kMRrAAB2Bnp/0AcsiMCR49N3dLrMfX0FfB/PE7Yxxzou/JEfyFz3zDwBnz9stdn8T56sIT/5/OxanOTJUlfIceQo7xkBXOIi4PMtVputGnjkityNyucRu8vN3qhWqcuyVWWaFYq0NTu+241ccUV/NWMS1koAUAIACKyjUzYvFAbjwgUROPL6yGmi9406HS0UBuOimKgiACgSuIkQ0SJRpWLdMzsAAFTqsuyTJ2tqAABwkidjKGcTOCmGK8t0ysC4whfu3MXbt+dtp7aqOg145ApF2pod2qrqNG9Psuabb7ueUSoVuynKcerPf/732huDlmIAgBXJso+QEipOnLrxQ1rXm4wuLgpQFEChb6aVue6Zedqq6rQr13vft1huMiuSZR8lJiSuPn/h/Ke5G5XPW202f21VdVrCskT7hYuXn0JocBcxcC7lZF9QW69jtFXVac0tLR9nZSotD8UsPgUAcLH9ihIJDwBA44Si7kKbpe5C27QxOUQkItEJW653M067Y/uFO4PSY4eK5njhEG7u6yuwXO9mEFLQ9e5WV09/J+3hVYzQU9/YtL750iU/sUh0CsnR3NLy8b4D7z8BTqp+JuKEuYM/sittVXUasv2OO0O79hZsNe98Z/9zN65fO8i2RbFEQhgNBhoAQCyREO4e2mgw0I06He20O7Zrjh4uZXt635gocm/BVnPuloKgMYrejRNEBtqXoiicJEmGvQ9bQdVV/021nXbH9mefeuzkOA176hub1qP3AABr166hTp6sIbnECXMHe6S1jlHrp1F+gW8nJiSu5sKeLTxbQPaDAwCQJMlwhWcLOoUQYYj2zq2B1wEA0GcZmZke3H2QI5U/vMyDJEmGoihcd7Z2AqFBuCACz3r270eaL13y25yV7oUOEsmlSE+rRgcs4POHMe7pb97x2j4AAB+SeE1VUjRYXqERxjyU2NZ86ZIfm7xwBQUAGDCbKX1Hp0saFYmxT89oMNC62trjFaXF2blbCoLsDPQKF0TgU1TXZHSBdRQslpuMFw7h7MjBVjASXhoqxrgmovu6ZQL5FeGCCPx3W/NEyPEhIrXikWUFSAFTUaC8QiNcu3YNJeDzh8+3tm9IlT3aUNt0LmV5kuxPy5ctq8/KVKozc/I/YZ+WO+FZ8Kf1HZ0uvcnoBABosw9bQ/pvz0G0eIyid4fME+EDXVc10lDxhklBqMmIAH5zQ97501tvvJCZk1/ZqNNlCBdEuKaixKSTnLz390xsVZKMZwwV08jH5G0t/LVKXcbQHl7FjTod7YVDeHNLCwBAmtVmq0achjfuoNYI+Hy1qkxz5ELL+frc7I3q07oveXMD5r4JAKszc/JTZiM8G6KI1lZfaxuJ8/IXWOD2VFjKf2VXBgjmQKpUjl82GKquduipSOlCQt/ZdRYAigcsAwoAeIGhnE04QWSwowJKitwtiqJwsUQCyXI5NOp0NM/L88CV6714liLjTnxs9KlH4pcMAgCsTNHUaKuq01AoxxXpadWZOfnq2nodk5u9UQ0A8KQ86bDlzq2/NF+65HdPwnd0utiwjvPyF0z3wDROKAAAPjNfPXvZaMIXRkcdQmTIXdhE2WCjTkcbDQaa7Rg5SiCS5XICcYx3i4r4VccaC9E1n3x+du2ZugYcHQjv3MXW9FTZow1n6hrwg+VVdoKhtc1fNr1a9uExJ04QUzaflp7uhZzOtMJP2v5fGho0w729v5p6kOvdwPfxPFG4cxdPKAzGLde7mWhhUEGsRFL8oDiUAQAGvqO1GSHCEC2bGyAT0ZuMrlVJMl6yXI6QQIslEuA+DzJFhAQAgBsjl/eqyjR4YkLi6r3793/iQxKvIXPAe7q6nGfqGnDN0cOly5cuvZOYkLjazkAvOnnhgggcCW80GOgBs5lC2ucKHyISkZqysmODnfp6hqYrdbW1xwmG1goXROC2Mce6ptuDntKoSCxZLidoD69iAADR/IhMGicU9Y1N6wEATH2GL1NSnp6HkzyZNCoS44ZAsURCSKMiMX1Hp4uLBPQ86Dp0ADhBZCCGmpWR/pmqpGgQcQLieMWx7tHR0Sjpwqd7KGrAdObSpbSx28MuJLz84WUeAABmk8mpNxldt6wjQLpcroDAQIx78maTyWno6WnFCDwMJ4gMl8vV3tNrcPHnBi6xW61/Z3aMFU30DwjD589fgh565M4dFwCAnUdg0cKgrf/y+zc+SH7scQXhQb4qCQ/Hff38cG8fH56hv5+e6+uL+fr54b5+fjhJki59R6eLJElXQGAgxjAMZjaZnI06HY2+5+vnh/v7+0OfweAaGxt1nWtu9ujquLL9wtfNYyp1WTYAAC7g84e9PcmaqDifX9Y2nUthhxJpqBgbMJspBCtpqBgD6yjoTUYX9+TZ2Rm3gCENFWNCYTC+lB/wZkVpcbautvY4F7YDXVc1udkb1bEKZSjPy/MA8gfolNnOENk62ycMmM0Ul4cg0oSQgMKrclNejjhMYlOkp1Xj7LISG/bsGw6YzRT7psgjs4VnOzaGpisZmq78nhKiIjGcIDKee7Fg9BvX2JnNWeledae/2Ib+KkqLs5Wb8nIS/IL0QmEwzhV4Joen7+h06Ts6XWze4C57RK9FMVFFKUkPfy7g84eJuSEP+NTVnvGIi42+0nyxdWd8YgI+19f3roRk1GZjvH18eKM2GzNs6t88MmTZ8oAkvBDBj2EYLCAwEAsICIgz9PS0TjG8xYuUt6wjcMs6Aof++KYPLzUl70EnL2NJ/MOLXAzTx/fxPDFB0VHxj8p0OI+3GgAgPjHhewIHBAZiyFR8/fxwhmEwAAB0T5IkXbcGb8HcoCDM188PpygKR8hlL0l4OC4JD8eD+XMq46IjPxu8beVj7CqK1Wbz7+rp72y+dMlv2kyuo9NlvXUzTFVSNKgq0xxJTEhc3T80FMh2VOyC6L7XC73R67htL35XKR53nHkI81mFE0QGQ9OV6F+Gcja1CjBZ23uHsgvf2TeOCBAO2PFFUdLM6ZIkrjOeKZOMj43WxCyOeBnRf8xdZffbru53L7ZfUXK/fLVDX4H4OlpeYeH7SAJfP9NNP9dfzk3yEHw2m+JlrEIZ2q7VmJDCHrJ/h1ycIDKQU+aG4wGzmQoRiUi2H5iurI4qRYgOY9PV9r+62PohWwldty0RnzU24Ev5AW9O5dKTPuPYoaI5O9/Z/9zKpEfVZ75scqJkZcBsps436sRI8FiFMvRcqWqUy9HR6fdd6/2Phoa/3EDPodyUl4Oqwggp3OxzujoD24+JJRJiZUKc0F1hBHNXEULVXtTgqDv9xTa+j+cJOwO9TrtjO9/H84RvTBQ58m0HNUbRuwEAKkqLs1VlmiPIESKl7S3Yao5VKENlAUEOpAjlpryc0DBJEoI1u1LMzhhVJUWDcdteVMdTHhmopEbRzEexEkn6dMUVJDhCwvKlS+8snv9AJDJxrhKwmYqiJ0/WkOMOak1u9kZ1Zk6+2ockXvONiSJdA0PXLZabDEPTlQf37y7M21r4a5zkySpKi7ML33hzHDUwUAmtrqHJpSopGszdUhAkmB/Rh+qC3GgzldlNZo5xLzyf5eEf+Fby3AfqVz3ySKbu65YJlGDFefkLpk6bU1ZH5jCbJgo2XU2QnTAoN+XlAACsWpnCXLne+740KhLTm4wuVMDc99ZvvZGCli9b9gvaw6v4fKNOzN07MVlu1Hd0uiyWm3cJj/YLEYlI3dctE7U3jQMTjtEzMO44A96eq7Y9+vgGds2wdvz2QGqwOIS9R4hIRD4Q6F/G4+GnpRHhp9BJz9Q8wWdqfqDkCCd5MgAA2sOrWBoVibUbDFUDXVc1KL4rN+XlMJSzyTbmWIcIEZtuqkqKBv3mhryDhE+Wy4lVSTIeMWHPR4pCgrDDl2tw5LdtHxwpBwBoNxiqpiAeFYnlxT86DylOLJEQC8PDXnrikfi5j8Qv+U3iktjj6NStNpv/TM4Xn2kQQaUuy2Y3KNB6UBzKoPweAEAcE+Nwh6RXCg8GIOgzAp8NSHhiwp5vNBho2sOrODFZbgQAICbs+e0GQxUKoXnxj86TBQQ5UNgc7u39FVtRYomEeDol6SMAAJJwaZ6UJx3mPn9WptLyQ6VxfLp+fG72RrW3J1mzMkWGoR4dm/GtfPKJ9xAkh3uufcr+HJxUPfvG/oHCZ7/nra/10ARDa4kJe37d6S+2EQyt1VuGqLP9XVMRZLIjtA4AoO2DI+XtfNLCDmcrE+KETycnbcx85ukXurv70lVlmiPnW9s3WG02f6vN5v/VxdYPrTab/w8NV+A/FJfHHdQavo/nCQCAutNfbENkqFGno/Umo8tpd2xH12qOHi5FWR4AwMh4O+Gu+6tUKnYDANQ2nUvheXke0JsH/pMG5jCyc93XLRMEQ2vRfQEAJoaH3tCbjC42EVKpy7JbvmlXN+p0dH1j0/r97x1U5b+yy1Rx4tSNy61tmL679xlVSdHgyZM15D0rgO012SioO/3FNuutm2HBcVGLrD3dYSg8+pDEayjDQsvXO5Z2t/f55nO7AAAYytnktDu2f9p35bF9rxd6EwytBesoWK53M536azQyn+8lTWYz5XQyT1acOHWj/quWInadEkWEheFhLwEATPYO/bMylZbpUIBPFwJR30+RnlY97qDWPPvUYycZytnE8/I8MEbRu/u//ubZMYrePUbRu71wCF+ZIsNoD69idEK5WwqC4hP9eAAAw0OWT9j9vOaWlo9pnFCIYqKKNEcPl6KTv2w04ShCYC6mnv1Mq6VLp7z9xfYrSrbgKPliaLoyWrqosqe7R0bjhKJRp6O11TX72VR/1j4AdVIKd+7i5WZvVM8NFj22MWvDiNPu2I4YoA9JvFZRWpytKika/KrXtHfKi/PIFaqSosG9+zbfRi243C0FQfv2vO1UlRQNTgnPyi6RwnGCyGAzUfakyOXWNowkXBqCobWpK+T4TKM302aDmTn5anlq6oarHfoK841+LHWFHKdxQlF3+ottmqOHS6cbfmw3GKqGrl93olLYVMvKYKD5GB3GzsZQtok6t2zH9ErR+6Iov8C3RfMjMrl5P3KWTrtjO5o+E0skhLmnu0KycD5O0ZjSaDDQbKXQOKEgJuz5yKe5VcArRe+LouYIVqPsTxQWVhQtXVSJNkD9NZTVzWbWB3ECVMEZNBmPeROwE6XHbsdxaNgTFCp+DpW5uMUPdvx32h3bVz75xHvEhD0/KDxChRIpfUenK3pB+Fbaw6sYKeLBJXGumMURL7M7w99TAGojo7mfV9946wNG4LMBUVhzX1+B5ujh0p3v7H9uYegDqtkogNtGQ4pAuTq3VTZdRZc9F8BVwopk2Udsv8CeTUT/v21zXhU3Rb4LAew6AFJC7paCINuYY91lh/XTdq3GlLulIGi2p4+EcVfSRt2cBwIDhwAA2EVV7kDETEpIlsuJheFhL13r7ftXNgdh9yXQ+M6sZ4TYxRBvT7IGwVWlLstmJzqzOXm2IFwkcG17+dKld/qHhgJnUgC33I1QhNpq3MWeXUJV4BlrglzOrK2qTtNbhiipMJBk29hsYe9OASRJMkLBnPLLrW3YFbM5A/X9f7c1T9TV09/ZPzQUaDQY6BCRiETf56IIPcfmrHSvg+VVdtQ2t1huMqg8Fh8brXkkfslv7nlUdrpJS6vN5l93oc3irhrLdnrTPTRb+JjFES9rq2v2IwVIoyIxNM6ClMBWmLvXMx0Gqv1zHd6sskH2CCyKzYghrkyIE0ZEhFVNd/LcTi33PQBAzOKIl2cax3W5qJfddX3ZHenpTORehZ9xVJb9RVVJEbtx8pLhWg/DJijTnTjX5gmG1kJCHBTu3MVbnnT39OsrhQcDLrSc9wIPL9QKn3bfEJHorvbXvQo/62FpxBBZPmKHtroG2EqYDpIhIhFJURSu7+h0RksXTSnWnQL27tt8+3xru73lm/bvihuCOeXuOlQ/1PK6l4Hpe/69ANtRftvV/S4AwPCYjQAA8Pfh0/1DwxvdKQP17ZDnpnFCMTXzMzn+OvX/k5w/WiSq5CLNnQkG+fp+hmL8vU6L/6gfTMx0E6vN5o/GZdnJy2xGYNn9gbvmg0LF2MLwsJeelCcdnq6Ex6XUP2lcfqbFbjigig0AwMWhIZ6AzzdbbbZ52qrqtGhhEEwNXk7M7rdT0cIgYF+L9kh4KPZz1Njk/hxvUvD7+muyH73c9RH+lhf211TCyhQZdvH8HScqj69MkWF1DU1uZ/0Qki4ODfHiAwOddQ1NLnS9b0wUGR8Y6Lzfvxn8ef28fl7wX7IAudT0XUuVAAAAAElFTkSuQmCC"""
CURSOR_ICON = "/usr/share/shop-os/assets/wrench-pointer.png"
MANUALS_DIR = Path.home() / "Documents" / "Shop Manuals"

PARTS_SITES = {
    "RockAuto": "https://www.rockauto.com/",
    "O'Reilly Auto Parts": "https://www.oreillyauto.com/",
    "Advance Auto Parts": "https://shop.advanceautoparts.com/",
    "AutoZone": "https://www.autozone.com/",
}


def load_engine_pixmap():
    """Load the supplied John's Garage engine artwork from embedded PNG data."""
    pix = QPixmap()
    try:
        pix.loadFromData(base64.b64decode(ENGINE_LOGO_B64), "PNG")
    except Exception:
        pass
    return pix


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
        btn = QToolButton()
        self.set_pointer(btn)
        btn.setObjectName("scannerTile")
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn.setText(f"{number:02d}   {title}")
        btn.setIcon(QIcon.fromTheme(icon_name))
        btn.setIconSize(QSize(72, 72))
        btn.setMinimumHeight(190)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.clicked.connect(callback)

        shadow = QGraphicsDropShadowEffect(btn)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 145))
        btn.setGraphicsEffect(shadow)
        return btn

    def build_header(self):
        frame = QFrame()
        self.set_pointer(frame)
        frame.setObjectName("header")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(22, 10, 22, 10)
        layout.setSpacing(16)

        logo = QLabel()
        logo.setObjectName("brandLogo")
        engine_pixmap = load_engine_pixmap()
        if not engine_pixmap.isNull():
            logo.setPixmap(
                engine_pixmap.scaled(
                    QSize(64, 64),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            logo.setText("JG")
        logo.setFixedSize(68, 68)
        logo.setAlignment(Qt.AlignCenter)

        brand = QWidget()
        self.set_pointer(brand)
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

        layout.addWidget(logo)
        layout.addWidget(brand, 2)
        layout.addWidget(self.clock, 1)
        layout.addWidget(self.status_label, 2)
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
        frame = QFrame()
        self.set_pointer(frame)
        frame.setObjectName("footer")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(22, 8, 22, 8)
        layout.addWidget(QLabel("JOHN'S GARAGE  •  SERVICE CONSOLE"))
        layout.addStretch(1)
        layout.addWidget(QLabel("SIGNED ATOMIC IMAGE  •  READY"))
        return frame

    def build_home(self):
        page = QWidget()
        self.set_pointer(page)
        page.setObjectName("homePage")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(24, 20, 24, 22)
        outer.setSpacing(16)

        hero = QFrame()
        self.set_pointer(hero)
        hero.setObjectName("heroPanel")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(18, 11, 18, 11)

        badge = QLabel("JG")
        badge.setObjectName("heroBadge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(42, 42)

        hero_left = QLabel("DIAGNOSTIC CONTROL PANEL")
        hero_left.setObjectName("heroTitle")

        hero_desc = QLabel("SELECT MODULE")
        hero_desc.setObjectName("heroText")
        hero_desc.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        hero_layout.addWidget(badge)
        hero_layout.addSpacing(8)
        hero_layout.addWidget(hero_left)
        hero_layout.addStretch(1)
        hero_layout.addWidget(hero_desc)
        outer.addWidget(hero)

        console = QFrame()
        self.set_pointer(console)
        console.setObjectName("consoleFrame")
        grid = QGridLayout(console)
        grid.setContentsMargins(18, 18, 18, 18)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        tiles = [
            ("SERVICE MANUALS", "x-office-document", self.open_manuals),
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
                background: #0c0f12;
                color: #f5f6f7;
                font-family: "Noto Sans", "Segoe UI", sans-serif;
            }

            QFrame#header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #101419, stop:0.17 #151a1f, stop:0.5 #871d22, stop:0.72 #a5272d, stop:1 #14191e);
                border-top: 1px solid #4b5359;
                border-bottom: 4px solid #ee7a22;
            }

            QLabel#brandLogo {
                background: #0b0e10;
                border: 1px solid #596169;
                border-radius: 12px;
                padding: 3px;
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
                font-size: 15px;
                font-weight: 800;
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

            QFrame#consoleFrame {
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
                border-left: 5px solid #be3037;
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
                background: #080a0c;
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
