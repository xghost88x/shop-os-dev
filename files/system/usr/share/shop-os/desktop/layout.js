// Applied once per account, after preserving the previous Plasma configuration.
var allDesktops = desktops();
if (!allDesktops.length) throw new Error("Desktop is not ready yet");
var required = ["org.kde.plasma.kickoff", "org.kde.plasma.icontasks", "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock"];
for (var i=0; i<required.length; i++) {
    if (knownWidgetTypes.indexOf(required[i]) < 0) throw new Error("Missing widget: " + required[i]);
}
theme = "breeze-dark";
for (var i=0; i<allDesktops.length; i++) {
    var desktop = allDesktops[i];
    desktop.wallpaperPlugin = "org.kde.image";
    desktop.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktop.writeConfig("Image", "file:///usr/share/shop-os/desktop/johns-garage-backyard-wallpaper.png");
    desktop.currentConfigGroup = ["General"];
    desktop.writeConfig("url", __SHORTCUT_URL__);
    desktop.writeConfig("iconSize", screenGeometry(desktop.screen).height < 900 ? 3 : 4);
    desktop.writeConfig("arrangement", 1);
    desktop.writeConfig("sortMode", 1);
    desktop.reloadConfig();
}
var existing = panels();
var panel = existing.length ? existing[0] : new Panel;
panel.location = "bottom";
panel.height = 60;
panel.hiding = "none";
panel.lengthMode = "fill";
var oldWidgets = panel.widgets();
for (var i=0; i<oldWidgets.length; i++) oldWidgets[i].remove();
var menu = panel.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "/usr/share/shop-os/assets/johns-garage.png");
menu.writeConfig("favorites", ["shop-os-dashboard.desktop", "johns-garage-02-videos.desktop", "johns-garage-03-parts.desktop", "johns-garage-04-files.desktop", "johns-garage-05-support.desktop"]);
var tasks = panel.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", ["applications:shop-os-dashboard.desktop", "applications:johns-garage-02-videos.desktop", "applications:johns-garage-03-parts.desktop", "applications:johns-garage-04-files.desktop", "applications:johns-garage-05-support.desktop"]);
panel.addWidget("org.kde.plasma.systemtray");
var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
if (knownWidgetTypes.indexOf("org.kde.plasma.showdesktop") >= 0) panel.addWidget("org.kde.plasma.showdesktop");
print("JOHNS_GARAGE_DESKTOP_READY");
