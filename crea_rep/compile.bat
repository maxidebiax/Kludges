rem Compilation du programme crea_rep
C:\Python27\python.exe install\pyinstaller-2.0\pyinstaller.py --onefile -w -i logo.ico crea_rep.py
copy /Y *.yaml dist\
copy /Y config.cfg dist\
copy /Y logo.gif dist\
echo "Le programme crea_rep est disponible dans le sous-dossier dist"