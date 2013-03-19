#/bin/python2
# -*- coding: utf-8 -*-
#
# Copyleft - Romain Hennuyer - 2012
#
# crea_rep permet de générer une arborescence à partir d'un YAML
#
# Dépendances :
# * python 2.7 pour windows
# * pywin32 pour python 2.7
# * pyYAML (3.10)
# * pyinstaller (2.0)
# Doc pyinstaller : http://www.pyinstaller.org/export/v2.0/project/doc/Manual.html?format=raw
import os, re, shutil, yaml, Tkinter, tkFileDialog, ConfigParser, atexit
from datetime import datetime

################################## Attention ##################################
# Tout le paramétrage peut se faire dans les fichiers :                       #
#   * config.cfg pour les dossiers (depot et arrivee)                         #
#   * ou les fichiers yaml pour la structure des dossiers                     #
# Pour trouver les erreurs dans un fichier YAML : http://yamllint.com/        #
###############################################################################

# =================== Initialisation ===================
# === Système de logging ===
try:
    logfile = open('messages.log', 'a')
except IOError:
    print("CORE : Impossible d'ouvrir le fichier de log")
    os.exit(1)
    
def logger(mess):
    """ Enregistre une info dans le fichier de log
    """
    time = datetime.now().strftime('%x à %X')
    logfile.write(time+" > "+mess+'\n') #+os.linesep

# A la fermeture du programme
@atexit.register
def goodbye():
    logger('Fermeture du programme')
    logfile.close()

# === Variables globales : lecture du fichier de configuration ===
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
try:
    depot = config.get('dossiers', 'depot')
    arrivee = config.get('dossiers', 'arrivee')
except:
    erreur='CORE : Impossible de charger le fichier de configuration'
    logger(erreur)
    print(erreur)
    os.exit(2)

# =================== Traitement ===================
# === Fonction principale ===
annuler = False # Dit si une erreur s'est produite ; permet de tout annuler
def crea_rep(fils, peres):
    """ Créer récursivement les répertoires et appel les hooks
    """
    dossier = arrivee + os.sep.join(peres)
    global annuler
    for key,d in fils.items(): # Pour chaque élément d'un même dossier
        if key == 'RENOMMER' and not annuler: # Une copie/renommage doit être effectuée
            renommer(dossier, d)
        elif not annuler:
            nvdossier = dossier + os.sep + num + "_" + key
            try:
                os.mkdir(nvdossier)
            except OSError:
                logger("Impossible de créer le dossier {0}".format(nvdossier))
                annuler = True
                return
            if type(d) is dict:
                # ∃ 1 sous-dictionnaire => on traite le sous-dossier de la même manière
                crea_rep(d, peres + [num+"_"+key])

# === Définition des actions particulières (hooks) ===
num='' # Numéro do dossier
dpt='' # Département
nom='' # Nom du dossier
# Les variables disponibles dans le YAML : NUM, DPT, NOM, DEPOT, ARRIVEE
ERvariable = re.compile('\$([A-Z]+)\$') # expression rationnelle des variables à remplacer
def renommer(dossier, dico):
    """ Renommer un fichier du depot dans le dossier voulu
    """
    orig = dico['origine']
    nomDest = dico['destination']
    if orig is None or nomDest is None or len(orig)+len(nomDest) == 0:
        logger("Erreur d'origine ({0}) ou de destination ({1}).".format(orig, nomDest))
        return
    for a in re.finditer(ERvariable, nomDest): # On remplace les variables $VAR$
        var = a.group(1).lower()
        if globals().has_key(var):
            nomDest = nomDest.replace('$'+var.upper()+'$', globals()[var])
    try:
        shutil.copy(depot + orig, dossier) # Copie
    except IOError, e:
        logger('Impossible de copier {0}'.format(e))
    try:
        os.rename(dossier + os.sep + orig, dossier + os.sep + nomDest) # Renommage
    except:
        logger('Impossible de renommer le fichier {0} en {1}'.format(orig, nomDest))

# =================== Interface graphique ===================
# === Boutons ===
file_opt = {} # Options pour la boite de parcours de fichiers
file_opt['filetypes'] = [('Fichiers YAML', '.yaml'), ('Tous les fichiers', '.*')]
file_opt['defaultextension'] = '.yaml'
file_opt['title'] = 'Ouvrir YAML'
def ChargerFichier(): 
    """ Traitement pour la boite de dialogue permettant de choisir le YAML
    Bouton Parcourir
    """
    filename = tkFileDialog.askopenfilename(**file_opt)
    if filename: 
        global valYaml
        try: 
            valYaml.set(filename)
        except: 
            global valMess
            valMess.set("Impossible de lire le fichier\n'%s'"%filename)
            return

def Validation():
    """ Effectuer la création de l'arborescence lors d'un clic souris sur le bouton 'Créer'
    Bouton Créer répertoires
    """
    global valMess, num, dpt, nom
    num = valNum.get()
    dpt = valDpt.get()
    nom = valNom.get()
    fichier_yaml = valYaml.get() # Nom du dossier

    if len(num)==0 or len(dpt)==0 or len(nom)==0 or len(fichier_yaml)==0:
        # Si un champ champ n'est pas rempli, on stoptout
        valMess.set("Un des champs n'a pas été rempli...")
        return
    affaire = dpt + "_" + nom # Dossier père
    
    # === Chargement du fichier yaml ===
    try:
        file_handle = open(fichier_yaml)
    except IOError:
        valMess.set("Le fichier {0} n'existe pas.".format(fichier_yaml))
        return
    try:
        arbo = yaml.safe_load(file_handle) # dico contenant l'arborescence des répertoires
    except:
        valMess.set("Le fichier YAML n'est pas valide.")
        return
    file_handle.close()

    if not os.access(arrivee, os.W_OK): # accès en écriture ?
        message = "Le dossier affaire ({0}) n'est pas accessible en écritre.".format(affaire)
    else:
        # === Création des répertoires ===
        # On commence par tout mettre dans le dossier de l'affaire
        arbo = dict({affaire: arbo})
        # Puis on créer les répertoires
        crea_rep(arbo, [])
    
        grandpere=arrivee + os.sep + num + "_" + affaire
        global annuler
        if annuler: # Si une erreur s'est produite
            message = "Une erreur s'est produite pendant la creation des repertoires ; annulation en cours"
            os.remove(grandpere)
            annuler = False
        else:
            message = "L'affaire n°{0} a bien été initialisé.".format(num)
            # On réinitialisation les valeurs du formulaire pour recommencer
            valNum.set('')
            valDpt.set('')
            valNom.set('')
            # Renommage : le nom du dossier principal contient un '-' et non un '_' , comme les sous-dossiers
            try:
                os.rename(grandpere, arrivee+os.sep+num+"-"+affaire)
            except:
                message = 'Impossible de renommer le dossier principale {0} avec un -'.format(grandpere)
    valMess.set(message)
    logger(message)
    global saisie1
    saisie1.focus_set() # Re-sélection automatique du premier champ
    saisie1.selection_range(0, Tkinter.END)

# === La fenêtre ===
top = Tkinter.Tk() # Création de la fenêtre principale
top.grid()
# Logo
logo = Tkinter.PhotoImage(file="logo.gif")
w = Tkinter.Label(top, image=logo)
w.grid(row=0, column=0, rowspan=5, sticky='EW', padx=7, pady=7)
# Numéro du dossier
labNum = Tkinter.StringVar()
labNum.set("Numéro du dossier :")
label = Tkinter.Label(top,textvariable=labNum, anchor="w")
label.grid(column=1,row=0,sticky='EW')
valNum = Tkinter.StringVar()
saisie1 = Tkinter.Entry(top,textvariable=valNum, justify='right')
saisie1.grid(column=2,row=0,sticky='EW')
# Département
labDpt = Tkinter.StringVar()
labDpt.set("Département :")
label = Tkinter.Label(top,textvariable=labDpt, anchor="w")
label.grid(column=1,row=1,sticky='EW')
valDpt = Tkinter.StringVar()
saisie2 = Tkinter.Entry(top,textvariable=valDpt, justify='right')
saisie2.grid(column=2,row=1,sticky='EW')
# Nom du dossier
labNom = Tkinter.StringVar()
labNom.set("Nom du dossier :")
label = Tkinter.Label(top,textvariable=labNom, anchor="w")
label.grid(column=1,row=2,sticky='EW')
valNom = Tkinter.StringVar()
saisie3 = Tkinter.Entry(top,textvariable=valNom, justify='right')
saisie3.grid(column=2,row=2,sticky='EW')
# Choix du fichier yaml
labYaml = Tkinter.StringVar()
labYaml.set("Fichier YAML :")
label = Tkinter.Label(top,textvariable=labYaml, anchor="w")
label.grid(column=1,row=3,sticky='EW')
valYaml = Tkinter.StringVar()
valYaml.set("")
saisie4 = Tkinter.Entry(top,textvariable=valYaml, width=42)
saisie4.grid(column=2,row=3,columnspan=2,sticky='EW')
parcourir = Tkinter.Button(top, text = "Parcourir", command=ChargerFichier, width=6)
parcourir.grid(column=4,row=3,sticky='EW')
# Boite de messages
labMess = Tkinter.StringVar()
labMess.set("*** Messages ***")
label = Tkinter.Label(top,textvariable=labMess, justify='center', fg='blue')
label.grid(column=3,row=0,columnspan=2,sticky='EW')
valMess = Tkinter.StringVar()
valMess.set("Compléter les champs, SVP")
label = Tkinter.Label(top,textvariable=valMess,borderwidth=9, fg='red')
label.grid(column=3,row=1,columnspan=2,rowspan=2,sticky='EW')

# Bouton de Validation
button = Tkinter.Button(top, text=u"Créer l'arborescence", command=Validation)
button.grid(column=1,row=4,columnspan=4)

# Paramètres généraux
top.grid_columnconfigure(0,weight=1)
top.resizable(False,False) # Pas de redimentionnement horizontal ou vertical possible
top.update()
#top.geometry(top.geometry()) # Taille de fenêtre automatique et fixe
top.title('Création des répertoires - Copyleft - Hennuyer Romain') # Titre de la fenêtre
top.mainloop()
