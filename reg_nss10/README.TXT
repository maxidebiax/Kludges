***  Reg_NSS10  ***

reg_nss10 permet d'ajouter automatiquement une configuration pour la version portable de Netsupport School 10, la version professeur (nommée "Portable Tutor").


== Besoin ==
Le soucis avec nss10 est que la clé de registre qui contient la configuration de "Portable Tutor" n'est pas portable (contrairement au logiciel) et dépend du nom de l'utilisateur qui l'execute.
D'où l'idée de développer ce programme permettant de rendre l'application tout à fait portable.


== Utilisation ==
L'application est compilée pour être autonome (pas besoin d'installer l'interpréteur python, entre autre). Il n'y a pas d'interface graphique il faut l'appeler depuis un terminal en précisant deux paramètres : un chemin d'accès vers un fichier .reg de référence (voir le § suivant) et une chaine de caractère permettant d'identifiant les membres d'une salle (optionnel). Voici la syntaxe :
 reg_nss10.exe c:\config.reg s203

Testé sous Windows Xp et 7.


== Fichiers ==
* config.reg : exemple de configuration
* library.zip : librairies nécessaires à reg_nss10.py
* python27.dll : dll python 2.7 pour windows
* reg_nss10.exe : l'executable à appeler
* reg_nss10.py : le code source du programme (utilisé par reg_nss10.exe)


== Créer le fichier reg de configuration ==
* Lancer Portable Tutor puis le paramétrer
* Dans une console > wmic useraccount get name,sid
* Noter l'uid correspondant à l'utilisateur en cours : S-1-5...
* Ouvrir la base de registre (Win+R > regedit)
* Aller à la clé HKEY_USERS\S-1-5-...\Software\NetSupport Ltd\PCICTL\ConfigList\NetSupport School
* Clic droit > Exporter


== Déploiement ==
Un exemple de script de déploiement à ajouter au logon.bat :
\\kwartz\netlogon\reg_nss10.exe \\kwartz\netlogon\config.reg %clientgroup:Salle=%

Explications pour le "s%clientgroup:Salle=%" :
* %clientgroup% est le nom du groupe où l'ordinateur se trouve
* l'ajout de ":Salle=" permet de remplacer le mot "Salle" par "" (rien).
Voir aussi ce site expliquant la manipulation de chaine de caractères sous dos : http://www.dostips.com/DtTipsStringManipulation.php


== Liens utiles ==
* python sous windows : http://docs.python.org/using/windows.html
* winreg : http://docs.python.org/library/_winreg.html
* py2exe : http://www.py2exe.org/index.cgi/Tutorial
* lien user/sid : http://stackoverflow.com/questions/2919286/getting-the-username-from-the-hkey-users-values
* autre solution pour le lien user/sid (dépendant de WMI) : http://timgolden.me.uk/python/wmi/index.html

