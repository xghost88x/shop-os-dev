#!/usr/bin/env bash
set -euo pipefail

# Build Epson's GPL ESC/P-R driver for this Fedora image from Debian's
# checksum-pinned upstream source, with Debian's compiler compatibility fixes.
dnf -y install gcc make cups cups-devel cups-filters patch curl tar gzip
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cd "$work"
base="https://deb.debian.org/debian/pool/main/e/epson-inkjet-printer-escpr"
curl --fail --location --retry 3 "$base/epson-inkjet-printer-escpr_1.8.8.orig.tar.gz" -o source.tar.gz
curl --fail --location --retry 3 "$base/epson-inkjet-printer-escpr_1.8.8-1.debian.tar.xz" -o fixes.tar.xz
printf '%s  %s\n' \
  8a0430d9d596fd8efa5dda6467ffa0ac06fd88be16544e486ac68eeb3d74defb source.tar.gz \
  cceb84db56ef6314ec48fc8dade0ac2c45f932a1e7a8a1384259fc1ffc38891c fixes.tar.xz | sha256sum --check
tar --no-same-owner -xf source.tar.gz
tar --no-same-owner -xf fixes.tar.xz
cd epson-inkjet-printer-escpr-1.8.8
patch -p1 < ../debian/patches/0002-Include-xfifo.h-to-avoid-implicit-pointer-conversion.patch
patch -p1 < ../debian/patches/0004-fix-implicit-function-compile-error.patch
filterdir="$(cups-config --serverbin)/filter"
./configure --prefix=/usr --libdir=/usr/lib64 --disable-lsb --disable-static \
  --with-cupsfilterdir="$filterdir" --with-cupsppddir=/usr/share/ppd \
  CFLAGS="-O2 -std=gnu17 -fPIC -fstack-protector-strong"
make -j"$(nproc)"
make install
ldconfig
test -x "$filterdir/epson-escpr"
test -x "$filterdir/epson-escpr-wrapper"
ppd="$(find /usr/share/ppd -name 'Epson-ET-2400_Series-epson-escpr-en.ppd' -print -quit)"
test -n "$ppd"
grep -q 'epson-escpr-wrapper' "$ppd"
cupsTest="$(command -v cupstestppd)"
"$cupsTest" "$ppd"
if ldd "$filterdir/epson-escpr" "$filterdir/epson-escpr-wrapper" | grep -q 'not found'; then
  echo "Epson driver has an unresolved library dependency" >&2
  exit 1
fi
systemctl enable cups.socket
