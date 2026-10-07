# Dad's Garage OS: Dell Latitude 5420 Rugged test

The VM-tested image includes the animated boot screen, automatic login, garage desktop, Service Center, local weather, battery fuel gauge and LibreOffice. Hardware support still needs testing on the Dell.

## Prepare the USB
1. Open the repository's **Actions → Laptop test installer**. Wait for a successful run.
2. Download **Dads-Garage-OS-Laptop-Test** from the run's Artifacts section and extract it.
3. Check the ISO checksum. On Windows PowerShell use:
   `Get-FileHash .\Dads-Garage-OS-Laptop-Test.iso -Algorithm SHA256`
   Compare it with the included .sha256 file.
4. Use Fedora Media Writer's custom-image option to write the ISO to a spare USB drive. Writing the image erases that USB drive.

This ISO is an installation environment, not a live Dad's Garage OS desktop. Flatpak applications download on first login and need internet access.

## Boot and install
- Plug in AC power. Connect Ethernet if available.
- Tap **F12** at the Dell logo and select the USB's UEFI entry.
- To preserve Windows, use a separate spare or external SSD as the installation target. Identify the target by its model and capacity; do not erase the Windows disk.
- For internal-disk replacement, back up needed files and Windows recovery information before selecting that disk.
- Create the primary account during installation. **os_dev** matches the VM, but the setup supports the first normal user under another name.
- Complete installation, remove the USB, and reboot.
- If Secure Boot rejects the installed system, record the exact message before changing firmware settings. This image uses the Universal Blue base; kernel trust is separate from container-image signing.

## Test on the Dell
- Boot-menu branding, animated boot screen and automatic dashboard startup.
- Wi-Fi, Ethernet, sound, screen brightness and keyboard.
- Touchscreen taps, dragging and the passive stylus.
- Battery percentage and fuel-gauge movement, charging indication and unplugged operation.
- Suspend and resume, including touchscreen and network after waking.
- Service Center: Files, Firefox, Chromium, LibreOffice, Settings and All Applications.
- LibreOffice: create, save and reopen a document.
- Weather: Machesney Park, IL 61115; offline status after disconnecting.
- Desktop/widget placement at the laptop's native resolution.
- Restart and shutdown. Fingerprint support is not a requirement.

## Update and recovery
`rpm-ostree upgrade`, then `systemctl reboot`.

The older deployment remains a recovery option. OSTree can include version numbers and numbered deployment suffixes in branded boot-menu titles.

## References
- https://blue-build.org/how-to/generate-iso/
- https://github.com/JasonN3/build-container-installer
- https://www.fedoraproject.org/workstation/download/
