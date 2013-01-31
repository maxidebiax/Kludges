#!/bin/python
# -*- coding: utf8 -*-
import re, sys, codecs, unicodedata
"""
Lit un export kwartz pour le transformer en import pour moodle
"""

# Fichiers d'entrée
EXPkwartz = codecs.open(sys.argv[1], 'r', encoding='ISO8859')
OUT = codecs.open(u'kwartz-vers-moodle.csv', 'w', encoding='utf-8')

OUT.write(u'username;password;firstname;lastname;email\r\n')

REkwartz = re.compile('^([^;]+);([^;]+);([a-z0-9]+);([^;]+?);.*', re.IGNORECASE|re.LOCALE|re.MULTILINE)
for ligne in EXPkwartz:
    m = REkwartz.search(ligne)
    if m and m.group(3) == "c2bam":
        nom = m.group(1).capitalize()
        prenom = m.group(2).capitalize()
        prenom = unicodedata.normalize('NFKD', prenom).encode('ASCII', 'ignore')
        login = m.group(4)
        passe = "{p1},{p2}".format(p1=nom[:4], p2=prenom[:4])
        #print(passe)
        OUT.write(u'{login};{passe};{prenom};{nom};a@a.com\r\n'.format(nom=nom, prenom=prenom, login=login, passe=passe))

EXPkwartz.close()
OUT.close()

