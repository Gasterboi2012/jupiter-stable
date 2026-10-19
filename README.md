# Jupiter Linux

Jupiter is a minimal, Arch Linux based distribution with a KDE Plasma desktop.
The live ISO boots straight into a guided TUI installer that:

1. Connects to the network (skipped automatically when a wired connection is online).
2. Lets you pick the install disk (it is erased).
3. Creates your user (hostname, username, password; the user gets sudo).
4. Lets you choose the graphics driver: **Mesa** or **NVIDIA Open** kernel modules.
5. Installs the system, paru (AUR helper) and **Zen Browser** (default browser).

## Repository layout

| Path | Purpose |
| --- | --- |
| `profile/` | archiso profile for the live installer ISO (UEFI, systemd-boot). |
| `installer/jupiter-setup` | Textual TUI installer that runs on tty1 of the live ISO. |
| `installer/jupiter-install` | Bash backend: partitioning, pacstrap, configuration, drivers, bootloader, paru, Zen. |
| `installer/system-packages.txt` | Packages of the installed system (minimal KDE Plasma set). |
| `branding/` | Files copied into the installed system: `os-release`, `lsb-release`, `issue`, KDE About page (`kcm-about-distrorc`), fastfetch config, default-browser config, placeholder logo. |
| `scripts/build-iso.sh` | Builds the ISO with `mkarchiso` (run on Arch as root). |
| `tests/tui_smoke.py` | Headless test of every TUI screen (demo mode, no hardware touched). |

## Branding

- Name: **Jupiter Linux** (`/usr/lib/os-release`, `ID=jupiter`).
- KDE Info Center "About this system": `/etc/xdg/kcm-about-distrorc` (icon `jupiter-logo`).
- fastfetch: `/etc/xdg/fastfetch/config.jsonc`, logo `/usr/share/jupiter/logo/jupiter-ascii.txt`.
- **Logos are placeholders.** Replace `branding/usr/share/icons/hicolor/scalable/apps/jupiter-logo.svg`
  and `branding/usr/share/jupiter/logo/jupiter-ascii.txt` with your artwork (keep the file names).

## Build the ISO

On an Arch Linux system with the `archiso` package:

```sh
sudo ./scripts/build-iso.sh            # output in ./out, work dir in ./work
```

The ISO is written to `out/jupiter-<date>-x86_64.iso`. Write it to a USB stick and boot in UEFI mode.

## Test

```sh
JUPITER_DEMO=1 python3 tests/tui_smoke.py           # walks the whole wizard, saves SVG screenshots
JUP_DRY_RUN=1 JUP_PACKAGE_LIST=installer/system-packages.txt \
  JUP_BRANDING_DIR=branding bash installer/jupiter-install --answers answers.env
shellcheck -x installer/jupiter-install scripts/build-iso.sh
```

`JUP_DRY_RUN=1` prints every destructive command instead of running it. A real run needs root,
a UEFI system and a disk that is not the live medium.

## Notes

- UEFI only. The installer refuses to run without UEFI.
- The installed system uses systemd-boot, NetworkManager, SDDM and Plasma (Wayland).
- Zen Browser is installed from the AUR (`zen-browser-bin`). If that fails during install, the
  installer warns and you can run `paru -S zen-browser-bin` after first boot.
- Timezone is set to UTC and the keymap to US by default.
