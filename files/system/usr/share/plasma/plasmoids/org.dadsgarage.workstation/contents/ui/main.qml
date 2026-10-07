import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation
    property var status: ({cpu:0,ram:0,ramUsed:0,ramTotal:0,diskFree:0,battery:null,charging:false,network:'Unknown',uptimeMinutes:0,weather:{available:false,stale:true,ageMinutes:0}})
    property bool online: false
    property bool pending: false
    function refresh() {
        if (pending) return;
        pending = true;
        var request = new XMLHttpRequest();
        request.open("GET", "http://127.0.0.1:17381/status");
        request.onreadystatechange = function() {
            if (request.readyState !== XMLHttpRequest.DONE) return;
            pending = false;
            if (request.status === 200) {
                try { status = JSON.parse(request.responseText); online = true; }
                catch (e) { online = false; }
            } else online = false;
        };
        request.send();
    }
    Timer { interval: 4000; repeat: true; running: true; triggeredOnStart: true; onTriggered: root.refresh() }
    fullRepresentation: Rectangle {
        implicitWidth: 302
        implicitHeight: 405
        Layout.minimumWidth: 270
        Layout.minimumHeight: 390
        color: "#ed171c22"
        radius: 15
        border.color: "#657688"
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 6
            Image {
                Layout.fillWidth: true
                Layout.preferredHeight: 45
                source: "file:///usr/share/shop-os/desktop/dads-garage-start.png"
                fillMode: Image.PreserveAspectFit
                smooth: true
            }
            Label { text: "OS  /  WORKSTATION STATUS"; color:"#c2cfda"; font.pixelSize:11; font.letterSpacing:1 }
            Rectangle { height:1; Layout.fillWidth:true; color:"#465566" }
            Label {
                text: !root.online ? "Monitor connecting…" :
                      root.status.battery === null ? "AC POWER  ·  No battery detected" :
                      "BATTERY  " + root.status.battery + "%  ·  " + (root.status.charging ? "Charging / plugged in" : "On battery")
                color:"#e5edf5"; font.pixelSize:12
            }
            Item {
                id: fuelGauge
                Layout.fillWidth: true
                Layout.preferredHeight: 26
                property bool available: root.online && root.status.battery !== null
                property real level: available ? Math.max(0, Math.min(100, Number(root.status.battery))) / 100 : 0
                Label { anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; text: "E"; color: "#ef6666"; font.bold: true; font.pixelSize: 11 }
                Label { anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: "F"; color: "#67d790"; font.bold: true; font.pixelSize: 11 }
                Rectangle {
                    id: fuelTrack
                    anchors.left: parent.left; anchors.right: parent.right
                    anchors.leftMargin: 18; anchors.rightMargin: 18
                    anchors.verticalCenter: parent.verticalCenter
                    height: 14; radius: 4
                    border.color: "#7d8a97"
                    opacity: fuelGauge.available ? 1 : 0.35
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0; color: "#df4b4b" }
                        GradientStop { position: 0.5; color: "#e4bf4f" }
                        GradientStop { position: 1; color: "#42bb78" }
                    }
                    Repeater {
                        model: 9
                        Rectangle {
                            required property int index
                            x: (index + 1) * fuelTrack.width / 10
                            width: 1; height: index === 4 ? 9 : 5
                            anchors.bottom: parent.bottom
                            color: "#c0171c22"
                        }
                    }
                    Rectangle {
                        visible: fuelGauge.available
                        x: Math.max(0, Math.min(parent.width - width, fuelGauge.level * parent.width - width / 2))
                        anchors.verticalCenter: parent.verticalCenter
                        width: 4; height: 24; radius: 2
                        color: "#f7fafc"; border.color: "#18202a"
                        Behavior on x { NumberAnimation { duration: 450; easing.type: Easing.InOutQuad } }
                    }
                }
                Label {
                    visible: !fuelGauge.available
                    anchors.centerIn: parent
                    text: root.online ? "AC POWER" : "—"
                    color: "#dae3ec"; font.pixelSize: 9; font.bold: true
                }
            }
            Repeater {
                model: [
                    {key:"cpu", label:"CPU"},
                    {key:"ram", label:"MEMORY"}
                ]
                delegate: ColumnLayout {
                    required property var modelData
                    Layout.fillWidth: true
                    spacing: 5
                    RowLayout {
                        Layout.fillWidth:true
                        Label { text:modelData.label; color:"#b8c6d4"; font.pixelSize:11; Layout.fillWidth:true }
                        Label {
                            text: !root.online ? "—" : modelData.key === "ram" ?
                                  root.status.ramUsed + " / " + root.status.ramTotal + " GB" : root.status.cpu + "%"
                            color:"#edf2f7"; font.pixelSize:12
                        }
                    }
                    ProgressBar {
                implicitHeight: 6
                background: Rectangle { implicitHeight:6; color:"#0d1218"; radius:3 }
                contentItem: Item {
                    implicitHeight:6
                    Rectangle { width:parent.width*parent.parent.visualPosition; height:parent.height; radius:3; color:"#94adc2" }
                } Layout.fillWidth:true; from:0; to:100; value: root.online ? root.status[modelData.key] : 0 }
                }
            }
            Label { text: root.online ? "STORAGE  ·  "+root.status.diskFree+" GB free" : "STORAGE  ·  —"; color:"#cad5df"; font.pixelSize:12 }
            Label { text: root.online ? "NETWORK  ·  "+root.status.network : "NETWORK  ·  —"; color:"#cad5df"; font.pixelSize:12 }
            Label {
                text: root.online ? "UPTIME  ·  "+Math.floor(root.status.uptimeMinutes/60)+"h "+root.status.uptimeMinutes%60+"m" : "UPTIME  ·  —"
                color:"#9daebf"; font.pixelSize:11
            }
            Rectangle { height:1; Layout.fillWidth:true; color:"#465566" }
            Label { text:"MACHESNEY PARK, IL 61115"; color:"#b7c7d7"; font.pixelSize:11; font.bold:true }
            RowLayout {
                Label {
                    text: root.online && root.status.weather.available ? root.status.weather.temperature+"°F" : "—°F"
                    color:"#f1f4f7"; font.pixelSize:30; font.bold:true
                }
                Label {
                    Layout.fillWidth:true
                    text: root.online && root.status.weather.available ? root.status.weather.label : "Weather unavailable"
                    color:"#c2cfda"; font.pixelSize:12; wrapMode:Text.WordWrap
                }
            }
            Label {
                text: !root.online || !root.status.weather.available ? "Weather requires an internet connection" :
                      (root.status.weather.stale ? "Last known · " : "Updated ") + root.status.weather.ageMinutes + " min ago"
                color:"#90a3b5"; font.pixelSize:10
            }
            Label {
                text:"Weather: Open-Meteo"
                color:"#90a3b5"; font.pixelSize:10
                MouseArea { anchors.fill:parent; cursorShape:Qt.PointingHandCursor; onClicked:Qt.openUrlExternally("https://open-meteo.com/") }
            }
            Item { Layout.fillHeight:true }
        }
    }
}
