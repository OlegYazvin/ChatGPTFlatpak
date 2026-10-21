# Validation

Target machine: Linux Mint 21.3, x86_64, kernel 5.15.0-191-generic,
Flatpak 1.12.7. Packaging version: 26.930.31730.2.

The existing unpacked host application is known to work, including phone
pairing. The Flatpak has a separate profile and must be tested independently.

## Completed

- Official versioned RPM downloaded directly from OpenAI; size and SHA-256
  recorded in `packaging/payload.json`.
- App binary, original ASAR, and native phone-pairing module compared with the
  original files retained on the working machine: identical.
- Seven packaging regression tests pass, covering extraction boundaries,
  hardlinks, path traversal, symlink escape, truncated input, ASAR offsets,
  integrity, refusal to patch an unexpected app archive, and host-bridge argument
  preservation and identity checks.
- Clean Flatpak build, signature creation, and local signed-repository install
  completed, including the actual `apply_extra` extraction and patch.
- Patched main JavaScript matches the working installation after trimming its
  extra trailing newline; no other main-code differences were introduced.
- Native app started through Zypak, initialized its local app server, and loaded
  the primary window with a fresh profile. Account-dependent connections request
  sign-in as expected.
- The installed bundled Codex CLI reports `codex-cli 0.160.0`.
- Direct nested Codex sandbox execution is blocked inside Flatpak; the same
  original CLI's sandbox command succeeds on the host with kernel 5.15. This is
  the reason for the explicit host integration, not a requirement to upgrade Mint.

## Pending package checks

- Codex sandbox command execution through the installed host bridge.
- Signed repository installation and the published GitHub installer.

## Interactive acceptance checklist

These require an account session and, for pairing, the user's phone. They must
not be reported as passed based solely on the host app working:

- Sign in, complete Google/2FA, quit, and relaunch; confirm login persists.
- Send a Chat message and create/open a Work artifact.
- Choose a test project; let Codex read/edit a file and execute a command with
  its requested sandbox and approval policy intact.
- Upload a file, download an artifact, and check desktop notifications.
- Pair an updated mobile app; run a remote task, disconnect, and reconnect.
- Update/reinstall the Flatpak and confirm its state persists.

The original installation, existing pairing identities, and launcher remain in
place. No kernel upgrade or account-data migration is part of this package.
