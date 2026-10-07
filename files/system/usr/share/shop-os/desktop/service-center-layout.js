// Replace the stock launcher only when the new native applets are available.
if (knownWidgetTypes.indexOf("org.dadsgarage.servicecenter") < 0 ||
    knownWidgetTypes.indexOf("org.dadsgarage.workstation") < 0) {
    throw new Error("Dad's Garage applets are not registered yet");
}
var garagePanels = panels();
if (!garagePanels.length) throw new Error("Panel is not ready yet");
var garagePanel = garagePanels[0];
garagePanel.height = 48;
var garageWidgets = garagePanel.widgets();
var serviceMenu = null;
var serviceIndex = 0;
for (var garageI = 0; garageI < garageWidgets.length; garageI++) {
    var garageWidget = garageWidgets[garageI];
    if (garageWidget.type === "org.dadsgarage.servicecenter") serviceMenu = garageWidget;
    if (garageWidget.type === "org.kde.plasma.kickoff" || garageWidget.type === "org.kde.plasma.kicker") {
        serviceIndex = 0;
    }
}
if (!serviceMenu) serviceMenu = garagePanel.addWidget("org.dadsgarage.servicecenter");
serviceMenu.index = serviceIndex;
serviceMenu.globalShortcut = "Alt+F1";
// Add before removing, so an unavailable custom widget leaves the old launcher.
for (var garageI = 0; garageI < garageWidgets.length; garageI++) {
    var garageWidget = garageWidgets[garageI];
    if (garageWidget.type === "org.kde.plasma.kickoff" || garageWidget.type === "org.kde.plasma.kicker")
        garageWidget.remove();
}
var garageDesktops = desktops();
for (var garageD = 0; garageD < garageDesktops.length; garageD++) {
    var garageDesktop = garageDesktops[garageD];
    var garageDesktopWidgets = garageDesktop.widgets();
    var monitor = null;
    for (var garageJ = 0; garageJ < garageDesktopWidgets.length; garageJ++)
        if (garageDesktopWidgets[garageJ].type === "org.dadsgarage.workstation") monitor = garageDesktopWidgets[garageJ];
    if (!monitor) {
        monitor = garageDesktop.addWidget("org.dadsgarage.workstation");

    }
    var rectangle = screenGeometry(garageDesktop.screen);
    monitor.geometry = new QRectF(Math.max(12, rectangle.width - 326), Math.max(24, rectangle.height - 405 - garagePanel.height - 24), 302, 405);
}
print("DADS_GARAGE_SERVICE_CENTER_READY");

