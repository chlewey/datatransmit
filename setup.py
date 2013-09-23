import sys
from cx_Freeze import setup, Executable

build_exe_options = {
#    "packages": ["os"],
    'include_files': ["config.mod","databases.mod","readers.mod"]
    }

setup ( name = "DB-Transmit",
        version = "0.1.5",
        description = "Database transmision program for Oruga Amarilla",
        options = {"build_exe": build_exe_options},
        executables = [Executable("transmit.py")] )
