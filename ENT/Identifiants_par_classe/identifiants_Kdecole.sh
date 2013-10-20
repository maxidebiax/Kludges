#!/bin/bash
# Créer, à partir de l'export des identifiants ENT, un fichier csv par classe contenant
#les identifiants/mot de passe d'un type de compte en particulier
# Annuaire > Administration > Fichiers de identifiants > Valider

# Paramètres
# 1 : nom de l'export Kd'école
# 2 : type de profil voulu (Eleve, Tuteur, Enseignant, Personnel)
# 3 : csv avec la liste des profs (format: adresse, classe)

if [ $# -ne 3 ];then
    echo "Usage : $0 Export_ENT.csv Profil Liste_prof.csv"
    exit 1
fi

cat $1 | sort -t\; -k 6,6d -k 5,5d | awk -F';' -v profil=$2 '$4==profil {print $6","$5","$7","$8 > $3".csv"}'
if [ -f classe.csv ]; then
    rm -f classe.csv
fi

# Envoie par mail aux profs principaux
for line in $3
do
    addr=echo $line | cut -d';' -f1
    clas=echo $line | cut -d';' -f2
    echo $addr - $clas
done
