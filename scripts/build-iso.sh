#!/usr/bin/env bash
# build-iso.sh - builds the Jupiter Linux installer ISO with archiso.
#
# Must run on Arch Linux (or an Arch chroot) as root, with the `archiso` package installed.
#
# Usage: sudo ./scripts/build-iso.sh [output_dir] [work_dir]
#   output_dir  default: ./out
#   work_dir    default: ./work (removed and recreated on each build)
set -Eeuo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$(realpath -m "${1:-$REPO_DIR/out}")"
WORK_DIR="$(realpath -m "${2:-$REPO_DIR/work}")"
PROFILE_SRC="$REPO_DIR/profile"
PROFILE_WORK="$WORK_DIR/profile"

die() { echo "ERROR: $*" >&2; exit 1; }

[[ $EUID -eq 0 ]] || die "run as root (mkarchiso needs it)"
command -v mkarchiso >/dev/null || die "mkarchiso not found: install the 'archiso' package"

echo "==> Preparing profile in $PROFILE_WORK"
rm -rf "$WORK_DIR"
mkdir -p "$PROFILE_WORK" "$OUT_DIR"
cp -a "$PROFILE_SRC/." "$PROFILE_WORK/"

AIROOTFS="$PROFILE_WORK/airootfs"

echo "==> Injecting Jupiter branding"
# Branding is shipped under /usr/share/jupiter/branding and copied into the installed
# system by jupiter-install. It is deliberately not overlaid onto the live root:
# files such as /usr/lib/os-release are owned by the 'filesystem' package, and
# overlaying them before pacstrap makes the package transaction fail.
mkdir -p "$AIROOTFS/usr/share/jupiter/branding"
cp -a "$REPO_DIR/branding/." "$AIROOTFS/usr/share/jupiter/branding/"

echo "==> Injecting installer"
install -Dm755 "$REPO_DIR/installer/jupiter-setup" "$AIROOTFS/usr/bin/jupiter-setup"
install -Dm755 "$REPO_DIR/installer/jupiter-install" "$AIROOTFS/usr/bin/jupiter-install"
install -Dm644 "$REPO_DIR/installer/system-packages.txt" "$AIROOTFS/usr/share/jupiter/system-packages.txt"

echo "==> Running mkarchiso"
mkarchiso -v -w "$WORK_DIR/archiso" -o "$OUT_DIR" "$PROFILE_WORK"

echo "==> Done. ISO written to $OUT_DIR"
ls -lh "$OUT_DIR"/*.iso
