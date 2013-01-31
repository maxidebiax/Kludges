#!/bin/python
# -*- coding: utf8 -*-
import re, sys, codecs, unicodedata
"""
Ce script permet de mettre responsable de groupe kwartz les profs de chaque classe.
Il génère trois fichier qu'il faut importer depuis Kwartz~Control.

Comme il se base sur les informations de pronote, le script n'est pas parfait. La création et la modification de compte fonctionnent bien, mais il faut faire une vérification pour la suppression car il peut y avoir des variations dans
l'orthographe des noms.

== Paramètres ==
* fichier d'export de Kwartz
* liste des profs par classes (export depuis pronote)
* nom du groupe kwartz des profs

== Exportation depuis pronote ==
Depuis un client pronote en mode administrateur :
Fichier > Autres imports/exports > Exporter un fichier texte
* Type de données à exporter -> Services
* Format d'export > Charger > export_classe-profs.xml
* Puis Exporter...

Attention, Pronote exporte en encodage utf-16-le (aller savoir pourquoi) ; il faut le convertir en utf-8 avant usage. Sous linux, il suffit d'exécuter la commande :
> iconv -f UTF-16 -t UTF-8 MON_EXPORT_PRONOTE.txt > EXPORT_PRONOTE.txt
"""

if len(sys.argv) != 4:
    """
    print(u"!!! Ce programme nécessite trois paramètres : !!!\n" + \
    	  u"* le fichier d'export de kwartz\n" + \
          u"* l'export classes-profs issu de pronote\n" + \
          u"* le nom du groupe kwartz des profs\n" + \
          u"\nexemple: python profs-kwartz.py export EXP_PRONOTE.txt GroupeProf")
    """
    sys.exit(1)
# Fichiers d'entrée
EXPkwartz = codecs.open(sys.argv[1], 'r', encoding='ISO8859')
EXPpronote = open(sys.argv[2], 'r')
if not EXPkwartz or not EXPpronote:
    print('Impossible de lire l\'un des fichiers')
    exit(2)
groupe_profs = sys.argv[3]
# Fichiers de sortie
OUTmodif = codecs.open(u'Amodifier.txt', 'w', encoding='utf-8')
OUTajout = codecs.open(u'Aajouter.txt', 'w', encoding='utf-8')
OUTsuppr = codecs.open(u'Asupprimer.txt', 'w', encoding='utf-8')


def les_classes(table):
    # Génère la chaîne "groupe"
    c = []
    for b in table:
        suffixe = u''
        if b[0].isdigit():
            # on ajoute un c devant les classes dont le nom comme par un chiffre
            suffixe = u'c'
        c.append(suffixe + unicode(b).replace('-', ''))
    return u' '.join(c)

profs = {} # dico des profs
# format : 1S;M. DOE JOHN, Mme TARTELATIE FABIENNE
REprof = re.compile('M(\.|me)\s+(.+)', re.IGNORECASE|re.UNICODE)
for ligne in EXPpronote:
    a = ligne.split(';')
    classe = a[0].lower()
    if len(a) == 2 and classe != 'CLASSES' and len(classe) > 0:
        for i in a[1].split(','): # Plusieurs profs avec la même matière dans la même classe
            n = REprof.search(i)
            if n:
                nom = unicode(n.group(2).strip().replace("'", '').upper())
                # TODO: si le nom est composé
                if nom in profs:
                    if classe not in profs[nom]:
                        profs[nom].append(classe)
                else:
                    profs[nom] = [ classe ]

profsKwartz={}

ajouter = profs.keys() # liste des profs à créer
# Modification et suppression des comptes
# format : JOHN;Doe;profs;doe.john;doe.john;;;profs www;profs www;;;;;;<LOCAL>;Professeur;
REkwartz = re.compile('^(.+);(.+);%s;(.+?);[^;]*;[^;]*;[^;]*;[^;]*;(.*?);.*' % groupe_profs, re.IGNORECASE|re.LOCALE|re.MULTILINE)
for ligne in EXPkwartz:
    m = REkwartz.search(ligne)
    if m:
        nom = m.group(1)
        prenom = m.group(2).upper()
        prenom = unicodedata.normalize('NFKD', prenom).encode('ASCII', 'ignore')
        j = "{nom} {pre}".format(nom=nom, pre=prenom)
        login = m.group(3)
        classes = m.group(4).split(' ')
        profsKwartz[nom] = classes
        if j in profs:
            # Reprendre et modifier la ligne prof
            a = ligne.split(';')
            a[0] = nom.upper()
            a[1] = prenom.capitalize()
            a[7] = u''
            a[8] = les_classes(profs[j])
            OUTmodif.write(u';'.join(a))
            # Retirer ce prof de la liste des profs à ajouter
            ajouter.remove(j)
        else:
            # Déplacement dans le groupe "anciens"
            OUTsuppr.write(u'{nom};{prenom};anciens;{login};;;;;;;;;;;<LOCAL>;;\r\n'.format(nom=nom, prenom=prenom, login=login))
            # TODO: faire une recherche approfondie sur les variations classique d'orthographe

EXPkwartz.close()
EXPpronote.close()
OUTmodif.close()
OUTsuppr.close()

# Créer les profs manquants
for a in ajouter:
    b = a.split(' ')
    nom = b[0]
    if len(b) > 1:
        prenom = b[1]
    else:
        print(u'Pas de prénom pour : {c}'.format(c=a))
    login = u'{prenom}.{nom}'.format(nom=nom.lower(), prenom=prenom.lower())
    classe = les_classes(profs[a])
    OUTajout.write(u'{nom};{prenom};profs;{login};{login};;;;{classe};;;;;;<LOCAL>;Professeur;\r\n'.format(nom=nom, prenom=prenom, login=login, classe=classe))

OUTajout.close()

print(set(profsKwartz) - set(profs))

