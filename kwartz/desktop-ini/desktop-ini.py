#!/usr/bin/python
# -*- coding: utf-8  -*-
import fnmatch
import os, sys

# Trouve les fichiers desktop.ini et les supprime
# Pour winodws, installer vcredist_x86.exe ou copier le fichier msvcr100.dll

recherche = 'desktop.ini'
racine = 'C:\\'

matches = []
for root, dirnames, filenames in os.walk(racine):
    for filename in fnmatch.filter(filenames, recherche):
        matches.append(os.path.join(root, filename))
foo = 'o'
for pa in matches:
    #foo = input('Supprimer le fichier {0} ? [O/n] '.format(pa))
    if foo.lower() != 'n':
        print('Suppression de {0}'.format(pa))
        os.remove(pa)
#foo = input('fin ? ')
