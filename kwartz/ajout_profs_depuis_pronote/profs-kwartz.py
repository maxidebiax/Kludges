#!/bin/python
# -*- coding: utf8 -*-
import re, sys, codecs, unicodedata
"""
Ce script permet de mettre responsable de groupe kwartz les profs de chaque classe.
Il génère trois fichier qu'il faut importer depuis Kwartz~Control.

Comme il se base sur les informations de pronote, le script n'est pas parfait. La création et la modification de compte fonctionnent bien, mais il faut faire une vérification pour la suppression car il peut y avoir des variations dans
l'orthographe des noms.

== Paramètres d'entrée ==
* fichier d'export de Kwartz
* liste des profs par classes (export depuis pronote)
* nom du groupe kwartz des profs

=== Exportation depuis pronote ===
Depuis un client pronote en mode administrateur :
Fichier > Autres imports/exports > Exporter un fichier texte
* Type de données à exporter -> Services
* Format d'export > Charger > export_classe-profs.xml
* Puis Exporter...

=== Sorties ===
* 3 fichiers textes à importer dans kwartz
* Un quatrième fichier contient les doutes et un résumé des changements de classes

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
    print("Impossible de lire l'un des fichiers")
    exit(2)
groupe_profs = sys.argv[3]
# Fichiers de sortie
OUTmodif = codecs.open(u'Amodifier.txt', 'w', encoding='utf-8')
OUTajout = codecs.open(u'Aajouter.txt', 'w', encoding='utf-8')
OUTsuppr = codecs.open(u'Asupprimer.txt', 'w', encoding='utf-8')
OUTmess = codecs.open(u'Messages.txt', 'w', encoding='utf-8')

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

### Lecture des données ###
profsPronote = {} # profs connus dans Pronote
# format : 1S;M. DOE JOHN, Mme TARTELATIE FABIENNE
REprof = re.compile('M(\.|me)\s+(.+)', re.IGNORECASE|re.UNICODE)
for ligne in EXPpronote:
    a = ligne.split(';')
    classe = a[0].lower()
    if classe != 'CLASSES' and len(classe) > 0:
        for i in a[1].split(','): # Plusieurs profs avec la même matière dans la même classe
            n = REprof.search(i)
            if n:
                nom = unicode(n.group(2).strip().replace("'", '').upper())
                classe = classe.replace("-","").replace("bps", "bsp")
                if classe[0].isdigit():
                    classe = u"c"+classe
                if classe[:3] != "ufa":
                    if nom in profsPronote:
                        if classe not in profsPronote[nom]:
                            profsPronote[nom].append(classe)
                    else:
                        profsPronote[nom] = [ classe ]

profsKwartz={} # profs connus dans Kwartz
infos={} # donnée supplémentaire pour les profs
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
        if len(classes) > 0:
            profsKwartz[j] = classes
        a = ligne.split(';')
        a[0] = nom.upper()
        a[1] = prenom.capitalize()
        a[3] = login
        a[7] = u''
        a[8] = u' '.join(classes)
        infos[j] = a

### Traitement ###
# Format d'une ligne d'importation Kwartz
enr = u'{nom};{prenom};{groupe};{login};{login};;;;{classes};;;;;;<LOCAL>;Professeur;\r\n'
# À ajouter
Aajouter = list( set(profsPronote) - set(profsKwartz) )
Averif = {}
for a in sorted(Aajouter):
    b = a.split(' ')
    nom = b[0]
    prenom = b[1].capitalize()
    login = (prenom+'.'+nom).lower().replace(' ','')
    classes = les_classes(profsPronote[a])
    if len(b) > 2:
        #Nom composé !
        Averif[nom] = enr.format(nom=nom, prenom=prenom, groupe=groupe_profs, login=login, classes=classes)
    else:
        OUTajout.write(enr.format(nom=nom, prenom=prenom, groupe=groupe_profs, login=login, classes=classes))

# À supprimer ?
#Comptes Kwartz qui sont inconnus dans Pronote
#Nécessairement plein de faux positifs
Asuppr = list( set(profsKwartz) - set(profsPronote) )
for a in sorted(Asuppr):
    nom = infos[a][0]
    if nom in Averif.keys():
        # Nom déjà vérifier => proposition de correction
        Averif[nom] = Averif[nom]+"> "+enr.format(nom=nom, prenom=infos[a][1], groupe=u'anciens', login=infos[a][3], classes=u'')
    else:
        OUTsuppr.write(enr.format(nom=nom, prenom=infos[a][1], groupe=u'anciens', login=infos[a][3], classes=u''))
if len(Averif) > 1:
    OUTmess.write(u"### Comptes dont le nom est compose ###\n")
    OUTmess.write(u"=> Il faut vérifier l'orthographe du nom ou la correspondance kwartz/pronote, puis déplacer dans le bon fichier\n")
    for k, av in Averif.items():
        OUTmess.write("\n"+av)

# À modifier
Amodifier = list( set(profsKwartz) & set(profsPronote) )
OUTmess.write(u"\n### Résumé des changements d'affectation ###\n")
for a in sorted(Amodifier):
    # Comparaison des classes déclarées
    c = set(profsKwartz[a])^set(profsPronote[a])
    if len(c) > 0:
        ajout = ' +'.join(set(profsPronote[a])-set(profsKwartz[a]))
        retrait = ' -'.join(set(profsKwartz[a])-set(profsPronote[a]))
        OUTmess.write("{prof}: +{ajout} // -{retrait}\n".format(prof=a, ajout=ajout, retrait=retrait))
        nom = infos[a][0]
        prenom = infos[a][1]
        login = infos[a][3]
        classes = les_classes(profsPronote[a])
        OUTmodif.write(enr.format(nom=nom, prenom=prenom, groupe=groupe_profs, login=login, classes=classes))

OUTajout.close()
OUTsuppr.close()
OUTmodif.close()
