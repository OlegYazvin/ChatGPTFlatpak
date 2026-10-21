# ChatGPT Flatpak for Linux

Independent packaging of **OpenAI's native Linux desktop application**. This is
not a website wrapper and is not affiliated with or endorsed by OpenAI.

**Experimental prerelease:** the package targets the same app version as the
maintainer's working Linux Mint installation. See [VALIDATION.md](VALIDATION.md)
for checks performed on the Flatpak itself and outstanding interactive checks.

## Install

Download [ChatGPT.flatpakref](https://olegyazvin.github.io/ChatGPTFlatpak/ChatGPT.flatpakref)
and open it in your software manager, or run:

```sh
flatpak install --user https://olegyazvin.github.io/ChatGPTFlatpak/ChatGPT.flatpakref
flatpak run io.github.OlegYazvin.ChatGPTFlatpak
```

This is a GitHub-hosted, signed Flatpak repository. Flathub supplies the public
runtime dependencies; this application is not listed on Flathub. The installer
downloads the pinned proprietary application **directly from OpenAI** and checks
its SHA-256 and size. This repository and its release assets do not redistribute
OpenAI's application binaries.

Only x86_64 is currently packaged. A ChatGPT account and internet access are
required. Account features, limits, subscriptions, and service availability are
controlled by OpenAI. Sign in again in the Flatpak; existing credentials and
phone-pairing identities are not imported.

## What is packaged

- OpenAI ChatGPT Linux `26.930.31730`, downloaded from its immutable official RPM
  URL. [payload.json](packaging/payload.json) records the URL, size, and checksum.
- The same narrowly scoped compatibility correction used in the working Mint
  installation: remove the obsolete `apps_mcp_path_override` Codex feature flag.
  The installer checks the expected marker and rebuilds ASAR offsets/integrity.
- Freedesktop SDK `25.08` for developer tools and the Electron BaseApp/Zypak for
  desktop dependencies and Chromium process integration.
- An independent desktop launcher and icon, separate from any existing ChatGPT
  installation. The package does not register itself as the default `codex://`
  handler during installation.

The official RPM was compared against the original, unmodified files retained
on the Mint machine: the application binary, app archive, and native pairing
module matched. This establishes provenance, not feature parity under Flatpak;
see the validation results.

## Permissions and application data

The app can access local files, the network, graphics, audio, the desktop login
keyring, and desktop notifications. Host filesystem access is intentional for
ChatGPT Work and Codex projects. This is a broadly capable desktop development
application; treat its agent approval prompts accordingly. It does not receive
unrestricted D-Bus access.

Application state lives under `~/.var/app/io.github.OlegYazvin.ChatGPTFlatpak/`.
The launcher gives Codex its own data directory there. Existing host ChatGPT and
Codex configuration is not copied. Do not publish that directory, authentication
tokens, pairing codes, or logs containing private conversations.

## Updates and removal

```sh
flatpak update --user io.github.OlegYazvin.ChatGPTFlatpak
flatpak uninstall --user io.github.OlegYazvin.ChatGPTFlatpak
```

Uninstalling normally keeps your Flatpak app data. Add `--delete-data` only when
you also want to remove its local account state and history. Your original,
separately installed ChatGPT application is unaffected.

## Build

Install Flatpak Builder, Freedesktop SDK `25.08`, and
`org.electronjs.Electron2.BaseApp//25.08` from Flathub. Python 3.11+ is used for
the packaging tests. Then:

```sh
git clone https://github.com/OlegYazvin/ChatGPTFlatpak.git
cd ChatGPTFlatpak
./scripts/build.sh --user --install-deps-from=flathub
flatpak install --user ./repo io.github.OlegYazvin.ChatGPTFlatpak
```

The build produces packaging only. Installing from the repository downloads and
extracts OpenAI's application. To use dependencies already installed system-wide,
pass `--system` instead of `--user` to the build script.

The package is distributed using `.flatpakref` plus a signed OSTree repository.
It is not exported as a self-contained `.flatpak` that embeds OpenAI's binaries.

## Publishing

The GitHub Actions publishing workflow builds and tests the packaging, signs its
OSTree commit and repository summary, deploys the repository to GitHub Pages,
and attaches the installer, repository reference, public signing key, and
checksums to a prerelease.

Repository configuration:

- GitHub Pages source: GitHub Actions.
- Secret `FLATPAK_GPG_PRIVATE_KEY`: an armored export of the repository signing
  key, dedicated to this project. Never commit it.
- Variable `FLATPAK_GPG_KEY_ID`: that key's full fingerprint.

The public key is committed in `packaging/repo-public-key.gpg` and embedded in
the installation references. Preserve the signing key across releases so that
existing installations can verify updates. Publishing a release does not
promote it out of experimental status automatically.

## License

The packaging is MIT licensed. OpenAI's proprietary app is covered by its own
terms and third-party notices. OpenAI's code, account data, and signing private
keys are not included in this source repository.

This packaging was developed with AI assistance. It is intended for independent
distribution and has not been submitted to Flathub.
