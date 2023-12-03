"""Implementing a plugin architecture"""

import time
import os
from typing import List
from importlib import util, import_module
from collections import defaultdict
import inspect


class PluginRegistration:
    """Registering plugins in the dictionary"""

    def __init__(self):
        self.__dirpath = os.path.dirname(os.path.abspath(__file__))
        self.__plugins = defaultdict(lambda: {"name": None})
        self.registration()

    def registration(self):
        for fname in os.listdir(self.__dirpath):
            if (
                not fname.startswith(".")
                and not fname.startswith("__")
                and fname.endswith(".py")
            ):
                plugin = self.load_module(os.path.join(self.__dirpath, fname))
                for name, obj in inspect.getmembers(plugin, inspect.isclass):
                    if hasattr(obj, "__identifier__"):
                        self.__plugins[name] = obj

    def get_plugin(self, name):
        return self.__plugins[name]

    def get_list_plugin(self):
        return list(self.__plugins.values())

    def load_module(self, path):
        name = os.path.split(path)[-1]
        spec = util.spec_from_file_location(name, path)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
