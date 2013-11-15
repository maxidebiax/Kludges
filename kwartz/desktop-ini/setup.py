# -*- coding: utf-8 -*-

# Run the build process by running the command 'python setup.py build'

from cx_Freeze import setup, Executable

build_exe_options = { "optimize": 1 }

executables = [ Executable('desktop-ini.py') ]

setup(name='desktop-ini',
    version='0.2',
    description='Desktop-ini',
    options = {"build_exe": build_exe_options},
    executables=executables
    )
