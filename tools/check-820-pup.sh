#!/bin/sh
# Verify that a downloaded PUP is one of the known 8.20 system updates.
# Usage: tools/check-820-pup.sh <file.PUP>
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 <file.PUP>" >&2
    exit 2
fi

f="$1"
if [ ! -f "$f" ]; then
    echo "not a file: $f" >&2
    exit 1
fi

if command -v md5 >/dev/null 2>&1; then
    h="$(md5 -q "$f")"
else
    h="$(md5sum "$f" | awk '{print $1}')"
fi

if stat -f%z "$f" >/dev/null 2>&1; then
    size="$(stat -f%z "$f")"
else
    size="$(stat -c%s "$f")"
fi

echo "file: $f"
echo "size: $size bytes"
echo "md5:  $h"
echo

case "$h" in
    140e49033e839967c4a446c741201984)
        echo "MATCH: 8.20.00 system update (1305 MB class)"
        ;;
    a3aad7f04e84230e72af02f7c458d05a)
        echo "MATCH: 8.20.02 system update (1274 MB class)"
        ;;
    555af0f384f054f95b5107fe63affd33)
        echo "MATCH: 8.20.02 sys_ex (811 MB class) - not the main system PUP"
        ;;
    *)
        echo "NO MATCH: this is not a known 8.20 system PUP."
        echo "Do not put it on the console until the version/hash is confirmed."
        exit 3
        ;;
esac
