"""Implementing a plugin architecture"""

import time
import os
from typing import List
from importlib import util, import_module
from collections import defaultdict
import inspect

def print_profiling(text:str, t1:List[float], t2:List[float]) -> None:
    print(f"{text}\n Real time: {t2[0] - t1[0]:.2f} seconds")
    print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")

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
                # t1 = time.perf_counter(), time.process_time()
                plugin = self.load_module(os.path.join(self.__dirpath, fname))
                # t2 = time.perf_counter(), time.process_time()
                # print_profiling(fname, t1, t2)
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
