rem Compilation du programme crea_rep
C:\Python27\python.exe pyinstaller-2.0\pyinstaller.py --onefile -p "C:\Python27\Lib\site-packages\win32\lib" -c gerer_les_imprimantes.py
rem copy /Y *.cfg dist\
copy /Y *.vbs dist\