Experimental independent Flatpak packaging of OpenAI's native ChatGPT Linux app.

- Packages version 26.930.31730, matching the working Mint baseline.
- Downloads the proprietary payload directly from OpenAI at installation and
  verifies its pinned checksum.
- Reproduces the obsolete-feature-flag correction from that working setup.
- Installs alongside the existing application with separate account state.
- Runs the bundled Codex CLI through explicit host integration so its own
  sandbox can operate on Mint's existing kernel. No separate host daemon is
  installed. This grants host execution capability; see README permissions.

Download `ChatGPT.flatpakref` and open it in your software manager, or use the
installation command in the README. Updates come from the signed GitHub Pages
repository.

See VALIDATION.md in the source repository for completed checks, limitations,
and interactive checks still needed. This prerelease does not claim that every
feature has been verified inside Flatpak. Not affiliated with or endorsed by
OpenAI; not a Flathub release.

Verified on Mint 21.3/kernel 5.15: signed-repository installation from the actual
GitHub download, native desktop startup, bundled Codex version, sandboxed command
execution through the host bridge, and login persistence after restart. The user
also confirmed phone pairing in this Flatpak. Work artifacts, uploads/downloads,
and a complete phone-driven task remain on the interactive checklist.
