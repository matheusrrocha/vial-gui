# -*- mode: python ; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# PyInstaller spec for the native macOS build. This replaces `fbs freeze`,
# which is tied to Python 3.6 (x86_64-only on macOS and dependent on the
# Rosetta 2 translation layer that Apple is removing after macOS 27).
# The produced Vial.app is built for the architecture of the running Python
# (arm64 on Apple Silicon). Usage: pyinstaller vial-mac.spec

import json
import os
import shutil
import subprocess

SRC = os.path.join(SPECPATH, "src", "main")


def load_build_settings():
    settings = {}
    for name in ("base.json", "mac.json"):
        path = os.path.join(SPECPATH, "src", "build", "settings", name)
        if os.path.isfile(path):
            with open(path, "r") as inf:
                settings.update(json.load(inf))
    return settings


def write_build_settings(settings):
    # The application reads app name/version through
    # application_context.ApplicationContext.build_settings, which in frozen
    # mode expects a build_settings.json resource (same contract as fbs).
    path = os.path.join(workpath, "build_settings.json")
    with open(path, "w") as outf:
        json.dump(settings, outf)
    return path


def make_icns():
    iconset = os.path.join(workpath, "Vial.iconset")
    os.makedirs(iconset, exist_ok=True)
    sizes = {
        "icon_16x16.png": ("base", "16.png"),
        "icon_16x16@2x.png": ("base", "32.png"),
        "icon_32x32.png": ("base", "32.png"),
        "icon_32x32@2x.png": ("base", "64.png"),
        "icon_128x128.png": ("mac", "128.png"),
        "icon_128x128@2x.png": ("mac", "256.png"),
        "icon_256x256.png": ("mac", "256.png"),
        "icon_256x256@2x.png": ("mac", "512.png"),
        "icon_512x512.png": ("mac", "512.png"),
        "icon_512x512@2x.png": ("mac", "1024.png"),
    }
    for dest, (subdir, src) in sizes.items():
        shutil.copyfile(os.path.join(SRC, "icons", subdir, src),
                        os.path.join(iconset, dest))
    icns = os.path.join(workpath, "Icon.icns")
    subprocess.run(["iconutil", "-c", "icns", "-o", icns, iconset], check=True)
    return icns


build_settings = load_build_settings()

a = Analysis(
    [os.path.join(SRC, "python", "main.py")],
    pathex=[os.path.join(SRC, "python")],
    datas=[
        (write_build_settings(build_settings), "."),
        (os.path.join(SRC, "resources", "base"), "."),
    ],
    excludes=["keyboard", "tkinter"],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=build_settings["app_name"],
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name=build_settings["app_name"],
)

app = BUNDLE(
    coll,
    name="{}.app".format(build_settings["app_name"]),
    icon=make_icns(),
    bundle_identifier=build_settings["mac_bundle_identifier"],
    info_plist={
        "CFBundleShortVersionString": build_settings["version"],
        "CFBundleVersion": build_settings["version"],
        "NSHighResolutionCapable": True,
        "NSPrincipalClass": "NSApplication",
        "LSMinimumSystemVersion": "11.0",
    },
)
