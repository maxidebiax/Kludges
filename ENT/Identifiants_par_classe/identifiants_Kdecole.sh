#!/bin/bash
# Créer, à partir de l'export des identifiants ENT, un fichier csv par classe contenant
#les identifiants/mot de passe d'un type de compte en particulier
# Annuaire > Administration > Fichiers de identifiants > Valider

# Paramètres
# 1 : nom de l'export Kd'école
# 2 : type de profil voulu (Eleve, Tuteur, Enseignant, Personnel)
cat $1 | sort -t\; -k 6,6d -k 5,5d | awk -F';' -v profil=Eleve '$4==profil {print $6","$5","$7","$8 > $3".csv"}'
if [ -f classe.csv ]; then
    rm -f classe.csv
fi
# On tri alphabétiquement les fichiers générés
#for cla in *.csv
#do
#	cat $cla | sort > tmp
#    mv tmp $cla
#done
