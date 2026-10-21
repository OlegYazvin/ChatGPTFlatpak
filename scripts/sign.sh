#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
: "${FLATPAK_GPG_KEY_ID:?Set FLATPAK_GPG_KEY_ID to the repository signing fingerprint}"
GNUPGHOME=${GNUPGHOME:-$HOME/.gnupg}
./scripts/flatpak.sh build-sign --gpg-sign="$FLATPAK_GPG_KEY_ID" \
    "--gpg-homedir=$GNUPGHOME" repo io.github.OlegYazvin.ChatGPTFlatpak beta
./scripts/flatpak.sh build-update-repo --generate-static-deltas \
    --gpg-sign="$FLATPAK_GPG_KEY_ID" "--gpg-homedir=$GNUPGHOME" repo
mkdir -p site
python3 -c 'from pathlib import Path; import shutil; p=Path("site/repo"); shutil.rmtree(p) if p.exists() else None; shutil.copytree("repo",p)'
python3 scripts/export-site.py
