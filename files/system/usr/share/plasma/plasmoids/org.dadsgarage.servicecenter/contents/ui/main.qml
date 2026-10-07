import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

PlasmoidItem {
    id: root
    Plasmoid.onActivated: root.expanded = !root.expanded
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: compactRepresentation
    Layout.minimumWidth: 180
    Layout.preferredWidth: 190
    Layout.maximumWidth: 200
    property string launchError: ""
    property bool busy: false
    property string powerAction: ""
    function launch(action) {
        if (busy) return;
        busy = true;
        var request = new XMLHttpRequest();
        request.open("POST", "http://127.0.0.1:17381/launch");
        request.setRequestHeader("Content-Type", "application/json");
        request.onreadystatechange = function() {
            if (request.readyState !== XMLHttpRequest.DONE) return;
            busy = false;
            if (request.status === 200) {
                launchError = "";
                root.expanded = false;
            } else {
                launchError = "Service Center could not open that tool. Try again after login.";
            }
        };
        request.send(JSON.stringify({action: action}));
    }
    compactRepresentation: Item {
        implicitWidth: 190
        Layout.minimumWidth: 180
        Layout.preferredWidth: 190
        Layout.maximumWidth: 200
        implicitHeight: 44
        Image {
            anchors.fill: parent
            anchors.margins: 2
            source: "file:///usr/share/shop-os/desktop/dads-garage-start.png"
            sourceClipRect: Qt.rect(9, 104, 2163, 600)
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
        MouseArea {
            anchors.fill: parent
            onClicked: root.expanded = !root.expanded
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
        }
        ToolTip.visible: mouse.containsMouse
        ToolTip.text: "Service Center"
        MouseArea { id: mouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
    }
    fullRepresentation: Rectangle {
        implicitWidth: 390
        implicitHeight: 590
        Layout.minimumWidth: 370
        Layout.minimumHeight: 520
        color: "#171c22"
        radius: 16
        border.color: "#526172"
        border.width: 1
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 22
            spacing: 12
            Image {
                Layout.fillWidth: true
                Layout.preferredHeight: 84
                source: "file:///usr/share/shop-os/desktop/dads-garage-start.png"
                fillMode: Image.PreserveAspectFit
                smooth: true
            }
            Label {
                text: "OS  /  SERVICE CENTER"
                color: "#d9e2eb"
                font.pixelSize: 15
                font.bold: true
                font.letterSpacing: 2
                Layout.alignment: Qt.AlignHCenter
            }
            Rectangle { Layout.fillWidth: true; height: 1; color: "#465566" }
            TextField {
                id: search
                Layout.fillWidth: true
                placeholderText: "Find a service or tool…"
                placeholderTextColor: "#91a4b7"
                color: "#e5edf5"
                background: Rectangle { color: "#0e1319"; radius: 7; border.color: "#425163" }
            }
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                Column {
                    width: search.width
                    spacing: 5
                    Repeater {
                        model: [
                            {label:"Service Manuals", detail:"Your saved shop reference library", action:"manuals"},
                            {label:"Repair Videos", detail:"Tutorials and repair guidance", action:"videos"},
                            {label:"Parts Lookup", detail:"Find parts and suppliers", action:"parts"},
                            {label:"Files", detail:"Documents, downloads and drives", action:"files"},
                            {label:"Firefox", detail:"Browse the web", action:"firefox"},
                            {label:"Chromium", detail:"Alternative web browser", action:"chromium"},
                            {label:"Remote Support", detail:"Get help with the workstation", action:"support"},
                            {label:"Settings", detail:"Configure your workstation", action:"settings"},
                            {label:"All Applications", detail:"Search installed apps with KRunner", action:"apps"}
                        ]
                        delegate: ItemDelegate {
                            required property var modelData
                            width: search.width
                            height: visible ? 52 : 0
                            visible: modelData.label.toLowerCase().indexOf(search.text.toLowerCase()) >= 0
                            padding: 13
                            background: Rectangle {
                                radius: 7
                                color: parent.hovered || parent.activeFocus ? "#2d3b49" : "#202830"
                                border.color: parent.hovered || parent.activeFocus ? "#8ca7bd" : "#2c3844"
                            }
                            contentItem: Column {
                                spacing: 3
                                Label { text: modelData.label; color: "#edf2f7"; font.pixelSize: 14; font.bold: true }
                                Label { text: modelData.detail; color: "#a7b6c4"; font.pixelSize: 11 }
                            }
                            onClicked: root.launch(modelData.action)
                        }
                    }
                }
            }
            Label {
                visible: root.launchError.length > 0
                text: root.launchError; color: "#f0b899"; wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            Rectangle { Layout.fillWidth: true; height: 1; color: "#465566" }
            RowLayout {
                Layout.fillWidth: true
                Button { palette.button: "#2d3b49"; palette.buttonText: "#e5edf5"; text: "Lock"; Layout.fillWidth: true; onClicked: root.launch("lock") }
                Button { palette.button: "#2d3b49"; palette.buttonText: "#e5edf5"; text: "Restart"; Layout.fillWidth: true; onClicked: {root.powerAction="restart"; confirm.open();} }
                Button { palette.button: "#2d3b49"; palette.buttonText: "#e5edf5"; text: "Shut Down"; Layout.fillWidth: true; onClicked: {root.powerAction="shutdown"; confirm.open();} }
            }
        }
        Dialog {
            id: confirm
            anchors.centerIn: parent
            modal: true
            title: root.powerAction === "restart" ? "Restart this workstation?" : "Shut down this workstation?"
            standardButtons: Dialog.Ok | Dialog.Cancel
            onAccepted: root.launch(root.powerAction)
            Label { text: "Save your work before continuing."; color: "#e5edf5" }
        }
    }
}

