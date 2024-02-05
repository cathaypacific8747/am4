import os
import shutil
import sys

import am4

if __name__ == "__main__":
    shutil.rmtree("stubs", ignore_errors=True)
    os.system(f'{sys.executable} -m pybind11_stubgen --print-safe-value-reprs=".*" -o _stubs am4.utils')
    shutil.move("_stubs/am4", "stubs")
    with open("stubs/__init__.py", "w") as f:
        f.write("from . import utils\n")
    shutil.copytree("stubs", am4.__path__[0], dirs_exist_ok=True)
