"""Implementing a plugin architecture"""

import os
from importlib import util, import_module
from collections import defaultdict
import inspect


class PluginRegistration:
    def __init__(self):
        self.path = os.path.abspath(__file__)
        self.dirpath = os.path.dirname(self.path)
        self.plugins = defaultdict(lambda: {"name": None})
        self.registration()

    def registration(self):
        for fname in os.listdir(self.dirpath):
            if (
                not fname.startswith(".")
                and not fname.startswith("__")
                and fname.endswith(".py")
            ):
                clsx = self.load_module(os.path.join(self.dirpath, fname))
                for name, obj in inspect.getmembers(clsx, inspect.isclass):
                    self.plugins[name] = obj

    def load_module(self, path):
        name = os.path.split(path)[-1]
        spec = util.spec_from_file_location(name, path)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_plugin(self, name):
        return self.plugins[name]
