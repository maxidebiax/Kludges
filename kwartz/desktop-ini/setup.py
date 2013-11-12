# -*- coding: utf-8 -*-

# Run the build process by running the command 'python setup.py build'

from cx_Freeze import setup, Executable

executables = [
    Executable('desktop-ini.py')
]

setup(name='desktop-ini',
      version='0.1',
      description='Desktop-ini',
      executables=executables
      )