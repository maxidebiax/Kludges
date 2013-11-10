#!/usr/bin/python
# -*- coding: utf-8  -*-
import fnmatch
import os, sys

# Trouve les fichiers suivant un pattern et propose de la supprimer

recherche = '*.vbe'
racine, x = os.path.splitdrive(sys.executable)
if racine == '':
    racine = '/'

matches = []
for root, dirnames, filenames in os.walk(racine):
    for filename in fnmatch.filter(filenames, recherche):
        matches.append(os.path.join(root, filename))
for pa in matches:
    foo = input('Supprimer le fichier {0} ? [O/n] '.format(pa))
    if foo.lower() != 'n':
        print('Suppression de {0}'.format(pa))
        os.remove(pa)
