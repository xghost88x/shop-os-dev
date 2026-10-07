// Clean desktop: retain files in their original folders without displaying shortcuts.
theme = "default";
var allDesktops = desktops();
if (!allDesktops.length) throw new Error("Desktop is not ready yet");
for (var d = 0; d < allDesktops.length; d++) {
    var desktop = allDesktops[d];
    desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktop.writeConfig("FillMode", 1);
    desktop.writeConfig("Blur", true);
    desktop.writeConfig("Color", "#171b1f");
    desktop.currentConfigGroup = ["General"];
    desktop.writeConfig("url", __SHORTCUT_URL__);
    desktop.reloadConfig();
}
// Preserve the existing KDE panel and its widgets.
var list = panels();
if (!list.length) throw new Error("No panel available");
var panel = list[0];
panel.height = 42;
panel.hiding = "none";
var widgets = panel.widgets();
var menuFound = false;
var clockFound = false;
var trayFound = false;
var tasksFound = false;
for (var i = 0; i < widgets.length; i++) {
    var widget = widgets[i];
    if (widget.type === "org.kde.plasma.kickoff" || widget.type === "org.kde.plasma.kicker") {
        widget.currentConfigGroup = ["General"];
        widget.writeConfig("icon", "/usr/share/shop-os/desktop/dads-garage-start.png");
        widget.reloadConfig();
        menuFound = true;
    }
    if (widget.type === "org.kde.plasma.digitalclock") {
        widget.currentConfigGroup = ["Appearance"];
        widget.writeConfig("showDate", true);
        widget.reloadConfig();
        clockFound = true;
    }
    if (widget.type === "org.kde.plasma.systemtray") trayFound = true;
    if (widget.type === "org.kde.plasma.icontasks" || widget.type === "org.kde.plasma.taskmanager") {
        widget.currentConfigGroup = ["General"];
        widget.writeConfig("launchers", ["applications:org.mozilla.firefox.desktop", "applications:org.chromium.Chromium.desktop"]);
        widget.reloadConfig();
        tasksFound = true;
    }
}
if (!menuFound) {
    var menu = panel.addWidget("org.kde.plasma.kickoff");
    menu.currentConfigGroup = ["General"];
    menu.writeConfig("icon", "/usr/share/shop-os/desktop/dads-garage-start.png");
    menu.reloadConfig();
}
if (!tasksFound) {
    var tasks = panel.addWidget("org.kde.plasma.icontasks");
    tasks.currentConfigGroup = ["General"];
    tasks.writeConfig("launchers", ["applications:org.mozilla.firefox.desktop", "applications:org.chromium.Chromium.desktop"]);
    tasks.reloadConfig();
}
if (!trayFound) panel.addWidget("org.kde.plasma.systemtray");
if (!clockFound) {
    var clock = panel.addWidget("org.kde.plasma.digitalclock");
    clock.currentConfigGroup = ["Appearance"];
    clock.writeConfig("showDate", true);
    clock.reloadConfig();
}
print("JOHNS_GARAGE_DESKTOP_READY");
