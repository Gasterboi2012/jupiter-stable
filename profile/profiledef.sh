#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="jupiter"
iso_label="JUPITER_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="Jupiter Linux <https://github.com/Gasterboi2012/jupiter-stable>"
iso_application="Jupiter Linux Installer"
iso_version="$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="jupiter"
# The installer requires UEFI, so only UEFI boot is provided.
bootmodes=('uefi.systemd-boot')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15' '-b' '1M')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--auto-threads=logical' '--long' '-19')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/usr/bin/jupiter-setup"]="0:0:755"
  ["/usr/bin/jupiter-install"]="0:0:755"
)
