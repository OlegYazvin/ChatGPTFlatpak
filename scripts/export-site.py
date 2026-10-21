#!/usr/bin/env python3
"""Generate downloadable Flatpak references embedding the repository public key."""
import base64
import hashlib
from pathlib import Path
import shutil
import sys

APP = "io.github.OlegYazvin.ChatGPTFlatpak"
URL = "https://olegyazvin.github.io/ChatGPTFlatpak"
root = Path(__file__).resolve().parents[1]
site = root / "site"
site.mkdir(exist_ok=True)
public_key = (root / "packaging/repo-public-key.gpg").read_bytes()
key = base64.b64encode(public_key).decode("ascii")
reference = f"""[Flatpak Ref]
Name={APP}
Branch=beta
Title=ChatGPT (Unofficial Flatpak)
Comment=Independent packaging of OpenAI's native Linux desktop application
Url={URL}/repo
Homepage=https://github.com/OlegYazvin/ChatGPTFlatpak
IsRuntime=false
RuntimeRepo=https://dl.flathub.org/repo/flathub.flatpakrepo
GPGKey={key}
"""
(site / "ChatGPT.flatpakref").write_text(reference)
(site / "ChatGPT.flatpakrepo").write_text(f"""[Flatpak Repo]
Title=Oleg Yazvin's unofficial ChatGPT packaging
Url={URL}/repo
Homepage=https://github.com/OlegYazvin/ChatGPTFlatpak
Comment=Independent native ChatGPT Linux packaging
GPGKey={key}
""")
shutil.copyfile(root / "packaging/repo-public-key.gpg", site / "repo-public-key.gpg")
(site / ".nojekyll").touch()
(site / "index.html").write_text('''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>ChatGPT — Unofficial Flatpak</title>
<style>body{font:18px/1.6 system-ui;max-width:46rem;margin:4rem auto;padding:0 1.5rem;color:#17332e}a{color:#08695d}code{background:#eee;padding:.2em}</style>
<h1>ChatGPT — Unofficial Flatpak</h1>
<p>Independent packaging of OpenAI’s native Linux desktop application. Not affiliated with or endorsed by OpenAI.</p>
<p><strong>Experimental prerelease.</strong> Read the current tested features and limitations before installing.</p>
<p><a href="ChatGPT.flatpakref">Download the Flatpak installer</a> · <a href="https://github.com/OlegYazvin/ChatGPTFlatpak">Source, instructions, and test results</a></p>
<p>Open the downloaded file in your software manager, or run <code>flatpak install --user ./ChatGPT.flatpakref</code>.</p>
<p>The installer downloads the pinned proprietary application directly from OpenAI and verifies its checksum. A ChatGPT account and internet access are required. Flatpak installs dependencies from Flathub; this application is distributed through this repository.</p>
</html>''')
files = ["ChatGPT.flatpakref", "ChatGPT.flatpakrepo", "repo-public-key.gpg"]
(site / "SHA256SUMS").write_text("".join(
    f"{hashlib.sha256((site / name).read_bytes()).hexdigest()}  {name}\n" for name in files))
print("Generated signed-repository installation references")
