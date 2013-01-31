#!c:/Python27/python.exe -u
# -*- coding: utf8 -*-
import _winreg, re, sys, codecs, os
"""
                ****  Reg_NSS 10  ****
    Ajoute les clés de registre nécessaires pour paramétrer automatiquement
    le Portable Tutor de Netsupport School 10
"""

# Paramètres obligatoires
salle = "0"
if len(sys.argv) > 3 or len(sys.argv) ==1:
    print(u"!!! Ce programme nécessite au moins un paramètre : !!!\n" + \
    	  u"* le fichier de base de registre pour configurer Portable Tutor\n" + \
          u"* le début du nom des ordis à surveiller (optionnel)\n" + \
          u"\nexemple: reg_nss10.exe c:\\config.reg s202")
    sys.exit(2)
elif len(sys.argv) == 3:
    salle = sys.argv[2]
        # Salle associée au prof
reg_file = sys.argv[1]
    # Fichier contenant les valeurs à ajouter au registre

utilisateur = os.environ.get( "USERNAME" )
# = Nom de l'utilisateur locale qui execute le programme
uid = ""
# Correspondance entre utilisateur et uid
try:
    base = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\hivelist")
except WindowsError:
    print(u"Impossible de faire la correspondance nom_utilisateur / uid")
    sys.exit(4)

dat = re.compile(r"\\([^\\]+)\\NTUSER\.DAT", re.IGNORECASE)
nom = re.compile(r"\\USER\\(S-1-[\d-]+)", re.IGNORECASE)
i = 0
try:
    while 1:
        name, obj, typ = _winreg.EnumValue(base, i)
        r = dat.search(obj)
        if r is not None:
            if r.group(1) == utilisateur:
                s = nom.search(name)
                if s is not None:
                    uid = s.group(1)
                    break
        i += 1
except WindowsError:
    pass
if uid == "":
    print(u"## Impossible de trouver l'utilisateur %s" % utilisateur)
    sys.exit(3)

# Ajoute la configuration au registre
try:
    key = _winreg.CreateKey(_winreg.HKEY_USERS, uid+r"\Software\NetSupport Ltd\PCICTL\ConfigList\NetSupport School")
except :
    print(u"Impossible de créer la clé de registre HK_USERS")
    sys.exit(5)
regDesc = codecs.open(reg_file, 'r', 'utf8', 'ignore')
data = re.compile(r'"(.+?)"="(.*?)"')
for line in regDesc:
    #print(codecs.encode(line, 'cp1252'))
    r = data.match(line.replace('\x00', ''))
    if r is not None:
        name  = r.group(1).replace(r'\\', '\\')
        value = r.group(2)
        if name == r"Startup\BrowsePrefix":
            _winreg.SetValueEx(key, name, 0, _winreg.REG_SZ, salle)
        elif name == r"Register\TeacherName":
            _winreg.SetValueEx(key, name, 0, _winreg.REG_SZ, utilisateur)
        else:
            _winreg.SetValueEx(key, name, 0, _winreg.REG_SZ, value)

