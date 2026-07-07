# SPDX-License-Identifier: GPL-2.0-or-later

# Compatibility layer over fbs_runtime. fbs only supports Python 3.5/3.6, whose
# macOS builds are x86_64-only and depend on Rosetta 2; the native Apple Silicon
# build uses a modern Python where fbs is unavailable, so this module provides
# the small subset of fbs_runtime that the app actually uses. When fbs_runtime
# is importable (Windows/Linux builds), it is used as-is.

import json
import os
import sys

try:
    from fbs_runtime.application_context import cached_property, is_frozen
    from fbs_runtime.application_context.PyQt5 import ApplicationContext
except ImportError:
    try:
        from functools import cached_property
    except ImportError:
        # Python < 3.8
        class cached_property:
            def __init__(self, getter):
                self._getter = getter

            def __get__(self, obj, objtype=None):
                if obj is None:
                    return self
                value = self._getter(obj)
                obj.__dict__[self._getter.__name__] = value
                return value

    def is_frozen():
        return getattr(sys, "frozen", False)

    def _platform_name():
        if sys.platform == "darwin":
            return "mac"
        if sys.platform in ("win32", "cygwin"):
            return "windows"
        return "linux"

    class ApplicationContext:
        def __init__(self):
            # fbs instantiates the QApplication as soon as the context is
            # created; main.py relies on this by constructing widgets before
            # first accessing .app.
            self.app

        @cached_property
        def app(self):
            from PyQt5 import QtWidgets

            return QtWidgets.QApplication(sys.argv)

        @cached_property
        def build_settings(self):
            try:
                path = self.get_resource("build_settings.json")
            except FileNotFoundError:
                # Development mode: merge the fbs build settings files
                project_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))))
                settings_dir = os.path.join(project_dir, "src", "build", "settings")
                result = {}
                for name in ("base.json", "{}.json".format(_platform_name())):
                    path = os.path.join(settings_dir, name)
                    if os.path.isfile(path):
                        with open(path, "r") as inf:
                            result.update(json.load(inf))
                return result
            with open(path, "r") as inf:
                return json.load(inf)

        def get_resource(self, name):
            for dirpath in self._resource_dirs():
                path = os.path.join(dirpath, name)
                if os.path.exists(path):
                    return path
            raise FileNotFoundError("could not locate resource '{}'".format(name))

        def _resource_dirs(self):
            if is_frozen():
                exe_dir = os.path.dirname(sys.executable)
                return [
                    getattr(sys, "_MEIPASS", exe_dir),
                    exe_dir,
                    # macOS .app bundle: Contents/MacOS/../Resources
                    os.path.normpath(os.path.join(exe_dir, "..", "Resources")),
                ]
            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))
            resources = os.path.join(project_dir, "src", "main", "resources")
            return [
                os.path.join(resources, _platform_name()),
                os.path.join(resources, "base"),
            ]
