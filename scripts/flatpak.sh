#!/bin/sh
set -eu
if command -v flatpak >/dev/null 2>&1; then
    exec flatpak "$@"
fi
exec flatpak-spawn --host flatpak "$@"
