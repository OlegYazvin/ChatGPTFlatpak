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
- The installed host bridge successfully runs `codex sandbox -- /usr/bin/true`.
- The desktop app initializes its local Codex app server over the host bridge.
- GitHub Actions builds, installs, checks the actual extra-data installer, signs,
  and publishes the package successfully. Packaging checks also pass in CI.
- The prerelease installer was downloaded from GitHub Releases; all release
  checksums and the embedded repository key match.
- A separate test installation used that downloaded installer to fetch the
  signed GitHub Pages repository and OpenAI payload. Its bundled CLI version
  and actual sandbox command both passed, without using the local build repo.
- The user confirmed phone pairing works in the new Flatpak profile.
- The packaged CLI reports an authenticated ChatGPT session. After restarting
  the Flatpak, it remains authenticated; credentials were not printed or copied.
- The normal user installation was reinstalled from the signed public repository
  with origin `chatgpt-flatpak`. Login and a sandbox command still pass afterward.
- `flatpak update --user io.github.OlegYazvin.ChatGPTFlatpak` successfully checks
  the public origin and reports no outstanding update. The temporary local test
  remote was removed; the original `chatgpt.desktop` login callback handler was
  restored.

## Interactive acceptance checklist

These require an account session and, for pairing, the user's phone. They must
not be reported as passed based solely on the host app working:

- Sign-in and persistence: passed, as recorded above.
- Phone pairing: user confirmed. Disconnect/reconnect behavior after a restart
  has not been independently exercised.
- Create/open a Work artifact; this has not yet been exercised explicitly.
- Choose a test project; let Codex read/edit a file and execute a command with
  its requested sandbox and approval policy intact. CLI sandbox execution is
  verified; a complete GUI-driven agent task is not yet recorded.
- Upload a file, download an artifact, and check desktop notifications.
- Run a task from the paired phone, disconnect, and reconnect.
- The local Flatpak update from packaging revision 1 to 2 preserved the profile.

The original installation, existing pairing identities, and launcher remain in
place. No kernel upgrade or account-data migration is part of this package.
