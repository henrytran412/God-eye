#!/bin/bash
# Build a stub libnvdla_compiler.so.
#
# Why this exists: the host is JetPack 7 (L4T r39.2) and Orin Nano has NO DLA
# hardware, so JetPack 7 does not ship libnvdla_compiler.so. The host's stale
# /etc/nvidia-container-runtime/host-files-for-container.d/drivers.csv still
# lists it, so nvidia-container-runtime truncates the container's copy to 0
# bytes, and libnvinfer.so.10 (which DT_NEEDEDs it) then fails to load.
# Nothing here is ever called: there is no DLA to compile for.
set -e
SRC=/usr/lib/aarch64-linux-gnu/libnvinfer.so.10
OUT=/work/lib/libnvdla_compiler.so
mkdir -p /work/lib

nm -D --undefined-only "$SRC" | awk '{print $NF}' | grep '^_ZN*.*nvdla\|nvdla' | sort -u > /work/lib/nvdla_syms.txt
N=$(wc -l < /work/lib/nvdla_syms.txt)
echo "undefined nvdla symbols needed: $N"

{
  echo '/* auto-generated stub: no DLA hardware on Orin Nano */'
  while read -r s; do
    [ -z "$s" ] && continue
    echo "void ${s}(void) {}"
  done < /work/lib/nvdla_syms.txt
} > /work/lib/nvdla_stub.c

gcc -shared -fPIC -Wl,-soname,libnvdla_compiler.so -o "$OUT" /work/lib/nvdla_stub.c
echo "built $OUT"
ls -l "$OUT"
