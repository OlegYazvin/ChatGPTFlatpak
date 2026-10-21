Experimental independent Flatpak packaging of OpenAI's native ChatGPT Linux app.

- Packages version 26.930.31730, matching the working Mint baseline.
- Downloads the proprietary payload directly from OpenAI at installation and
  verifies its pinned checksum.
- Reproduces the obsolete-feature-flag correction from that working setup.
- Installs alongside the existing application with separate account state.

Download `ChatGPT.flatpakref` and open it in your software manager, or use the
installation command in the README. Updates come from the signed GitHub Pages
repository.

See VALIDATION.md in the source repository for completed checks, limitations,
and interactive checks still needed. This prerelease does not claim that every
feature has been verified inside Flatpak. Not affiliated with or endorsed by
OpenAI; not a Flathub release.
