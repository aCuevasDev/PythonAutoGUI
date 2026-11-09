"""Build the app with PyInstaller, copy images/ next to the exe and zip it.

Usage:
    python build.py            # windowed build (no terminal)
    python build.py --console  # keep the terminal, useful to see errors
    python build.py --no-zip   # skip creating the zip
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "AFKRetry"
ENTRY = ROOT / "gui.py"
IMAGES = ROOT / "images"
CONFIG = ROOT / "settings.toml"
DIST = ROOT / "dist"
BUILD = ROOT / "build"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--console", action="store_true", help="keep the console window")
    parser.add_argument("--no-zip", action="store_true", help="don't create the zip")
    args = parser.parse_args()

    if not IMAGES.is_dir():
        sys.exit(f"images folder not found: {IMAGES}")
    if not CONFIG.is_file():
        sys.exit(f"settings file not found: {CONFIG}")

    # sys.executable makes sure the venv's PyInstaller is used
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--name", APP_NAME,
        "--distpath", str(DIST),
        "--workpath", str(BUILD),
        "--specpath", str(BUILD),
        "--uac-admin",  # request admin privileges on Windows
        str(ENTRY),
    ]
    if not args.console:
        cmd.insert(-1, "--noconsole")

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)

    app_dir = DIST / APP_NAME
    target = app_dir / "images"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(IMAGES, target)
    print(f"Copied images to {target}")

    shutil.copy(CONFIG, app_dir / CONFIG.name)
    print(f"Copied settings to {app_dir / CONFIG.name}")

    if not args.no_zip:
        archive = shutil.make_archive(str(DIST / APP_NAME), "zip", root_dir=DIST, base_dir=APP_NAME)
        print(f"Created {archive}")

    print(f"Done: {app_dir / (APP_NAME + '.exe')}")


if __name__ == "__main__":
    main()