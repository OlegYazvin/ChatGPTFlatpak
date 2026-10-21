#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python3 -m unittest discover -s tests -v
if command -v flatpak-builder >/dev/null 2>&1; then
    exec flatpak-builder --disable-rofiles-fuse --force-clean --repo=repo \
        --default-branch=beta build io.github.OlegYazvin.ChatGPTFlatpak.json "$@"
fi
exec ./scripts/flatpak.sh run --user \
    --env="XDG_DATA_HOME=${HOST_XDG_DATA_HOME:-$HOME/.local/share}" \
    --command=flatpak-builder org.flatpak.Builder \
    --disable-rofiles-fuse --force-clean --repo=repo --default-branch=beta \
    build io.github.OlegYazvin.ChatGPTFlatpak.json "$@"
