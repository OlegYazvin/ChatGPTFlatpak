#!/usr/bin/python3
"""Run the bundled Codex CLI on the host, retaining Codex's own sandbox.

Flatpak blocks the user namespaces Codex needs. The original CLI works on the
target Mint kernel outside that outer sandbox. This explicit host integration
uses the exact installed commit and separate per-app state, without a daemon.
"""
import configparser
import os
from pathlib import Path

APP_ID = "io.github.OlegYazvin.ChatGPTFlatpak"


def host_path(value, files, profile):
    mappings = {
        "/app": files,
        "/var/data": profile / "data",
        "/var/config": profile / "config",
        "/var/cache": profile / "cache",
    }
    for prefix, target in mappings.items():
        if value == prefix or value.startswith(prefix + "/"):
            return str(target) + value[len(prefix):]
    return value


def command(arguments, info, home, cwd):
    if info["Application"]["name"] != APP_ID:
        raise ValueError("Unexpected Flatpak application identity")
    files = Path(info["Instance"]["app-path"])
    if not files.is_absolute():
        raise ValueError("Missing absolute installed application path")
    profile = Path(home) / ".var" / "app" / APP_ID
    executable = files / "extra/chatgpt/resources/codex.real"
    return ["/usr/bin/flatpak-spawn", "--host", "--watch-bus",
            "--directory=" + host_path(cwd, files, profile),
            "--env=CODEX_HOME=" + str(profile / "data/codex"),
            "--env=XDG_CONFIG_HOME=" + str(profile / "config"),
            "--env=XDG_DATA_HOME=" + str(profile / "data"),
            "--env=XDG_CACHE_HOME=" + str(profile / "cache"),
            "--env=TMPDIR=" + str(profile / "cache/tmp"),
            str(executable), *arguments]


if __name__ == "__main__":
    import sys
    info = configparser.ConfigParser(interpolation=None)
    info.read("/.flatpak-info")
    (Path(os.environ["XDG_CACHE_HOME"]) / "tmp").mkdir(parents=True, exist_ok=True)
    (Path(os.environ["XDG_DATA_HOME"]) / "codex").mkdir(parents=True, exist_ok=True)
    argv = command(sys.argv[1:], info, Path.home(), os.getcwd())
    os.execv(argv[0], argv)
