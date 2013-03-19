rem Installation de python 2.7
cd install
python-2.7.3.amd64.msi
rem Installation de la bibliothèque Yaml
cd PyYAML-3.10
C:\Python27\python.exe setup.py install
rem Installation de pywin32 (python pour windows)
cd ..
pywin32-217.win-amd64-py2.7.exe
rem Compilation du programme
cd ..
call compile.bat