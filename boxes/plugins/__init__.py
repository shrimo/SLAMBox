"""Implementing a plugin architecture"""

import time
import os
import inspect
from importlib import util
from collections import defaultdict


class TimeProfiling:
    """Class for profiling time"""

    def __init__(self):
        self.t1 = float
        print('Loading plugins:')

    def get_start(self):
        """Start point"""
        self.t1 = time.process_time()

    def get_end(self, text: str = 'plugins'):
        """End point"""
        t2 = time.process_time()
        print(f"-> {text}: {t2 - self.t1:.5f} seconds")


class PluginRegistration:
    """Registering plugins in the dictionary"""

    def __init__(self):
        self.__dirpath = os.path.dirname(os.path.abspath(__file__))
        self.__plugins = defaultdict(lambda: {"name": None})
        self.tp = TimeProfiling()
        self.registration()

    def registration(self):
        for fname in os.listdir(self.__dirpath):
            if (
                not fname.startswith(".")
                and not fname.startswith("__")
                and fname.endswith(".py")
            ):
                self.tp.get_start()
                plugin = self.load_module(os.path.join(self.__dirpath, fname))
                self.tp.get_end(fname)
                for name, obj in inspect.getmembers(plugin, inspect.isclass):
                    self.__plugins[name] = obj

    def get_plugin(self, name):
        return self.__plugins[name]

    def load_module(self, path):
        name = os.path.split(path)[-1]
        spec = util.spec_from_file_location(name, path)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
