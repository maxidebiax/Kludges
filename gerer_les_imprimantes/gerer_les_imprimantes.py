#!c:/Python27/python.exe -u
# -*- coding: utf8 -*-
import win32print, subprocess, socket, re, os, sys, ConfigParser, logging, string, argparse
"""
                ****  Gerer les imprimantes  ****
    Ajoute et supprime les imprimantes nécessaires pour cet ordinateur
		
	Paramètre :
	* dossier réseau où se situe l'exe, les cfg et les vbs. Ex: \\kwartz-server\netlogon\wpkg\software\imprimantes

	TODO:
	choix ip/unc (globale et local)
	forcer purge par un paramètre ?
	
	Problèmes connus:
	L'imprimante doit etre démarrée avant! (sinon, la résolution pour trouver l'ip lors de la première installation n'aboutie pas) -> dns ?
"""
def nslook(ip):
	""" Retourne le nom et le groupe associé à une IP
		Spécifique à DOS (pas bien !)
	"""
	fqdn = ['', '']
	nslookup = str(subprocess.check_output('nslookup {ip}'.format(ip=ip)))
	REhost = re.compile('Nom\s+:\s+(.+)Address', re.LOCALE|re.DOTALL)
	n = REhost.search(nslookup)
	if n:
		fqdn = n.group(1).replace(r'\r\n', '').split('.')
	else:
		logging.error("Impossible de trouver le groupe pour {hote}".format(hote=ip))
	return (fqdn[0], fqdn[1]) # hote, groupe

"""
import dns.resolver
def requete_dns(nom):
	# Résolution DNS : fqdn => IP
	answers_IPv4 = dns.resolver.query(nom, 'A')
	return answers_IPv4.address.pop()
"""
	
def ajouter_ptr(nom, mode='ip'):
	""" Ajoute une imprimante, par son IP ou par son UNC (partage SMB)
	"""
	ptr = imprimantes[nom]
	logging.info("Ajout de '{nom}' par {mode}".format(nom=nom, mode=mode.upper()))
	if ptr['modele'] in modeles:
		mod = modeles[ptr['modele']]
	else:
		logging.error("Le modèle '{mdl}' n'existe pas.".format(mdl=ptr['modele']))
		return False

	if mode == 'ip':
		# Ajout du port IP
		try:
			ip = socket.gethostbyname(nom)
		except:
			logging.error("Impossible de retrouver l'IP de {nom}".format(nom=nom))
			return False
		inst = 'cscript {wd}prnport.vbs -a -r IP_{ip} -h {ip} -o raw -n 9100'.format(ip=ip, wd=wd)
		logging.debug("Installation IP : {chaine}".format(chaine=inst))
		try:
			subprocess.check_call(inst)
		except:
			logging.error("Impossible de créer le port IP : {inst}".format(inst=inst))
			return False

		# Installation du driver .inf
		path = os.path.dirname(chemin_inf+mod['inf'])
		inst = 'cscript {wd}prndrvr.vbs -a -i "{inf}" -h "{path}" -m "{drv}"'.format(wd=wd, inf=chemin_inf+mod['inf'], path=path, drv=mod['driver'])
		logging.debug("Installation DRV : {chaine}".format(chaine=inst))
		try:
			subprocess.check_call(inst)
		except:
			logging.error("Impossible d'installer le driver : {inst}".format(inst=inst))
			return False

		inst = 'cscript {wd}prnmngr.vbs -a -p "{nom}" -r "IP_{ip}" -m "{drv}"'.format(wd=wd, nom=nom, ip=ip, drv=mod['driver'])
	elif mode == 'unc':
		#win32print.AddPrinter(Name, Level , pPrinter )
		#inst = 'rundll32 printui.dll,PrintUIEntry /in /q /n "{unc}"'.format(unc=ptr['unc'])
		inst = 'rundll32 printui.dll,PrintUIEntry /if /u /b "{nom}" /f "{inf}" /r "{unc}" /m "{drv}"'.format(
			nom=nom, inf=chemin_inf+mod['inf'], unc=ptr['unc'], drv=mod['driver'])
	else:
		logging.error("Mode {mode} inconnu".format(mode=mode))
		return False

	logging.debug("Installation PTR : {chaine}".format(chaine=inst))
	try:
		subprocess.check_call(inst)
	except subprocess.CalledProcessError:
		logging.critical("Erreur "+returncode+" lors de l'installation de l'imprimante : "+cmd+"\r\n"+output)
	logging.debug("--- {nom} installé ---".format(nom=nom))

def supprimer_ptr(nom):
	""" Supprime une imprimante
	"""
	if nom not in ignorer_ptr:
		logging.info("Suppression de '{nom}'".format(nom=nom))
		try:
			subprocess.check_call('cscript {wd}prnmngr.vbs -d -p "{nom}"'.format(nom=nom, wd=wd))
		except:
			logging.error("Impossible de supprimer {nom}".format(nom=nom))
			
def default_ptr(nom):
	""" Définit l'imprimante par défaut
	"""
	logging.info("{nom} sera l'imprimante par défaut".format(nom=nom))
	#win32print.SetDefaultPrinter(nom)
	try:
		subprocess.check_call('cscript {wd}prnmngr.vbs -t -p "{nom}"'.format(nom=nom, wd=wd))
	except:
		logging.error("Impossible de définir {nom} comme imprimante par défaut".format(nom=nom))

def lister_ptr():
	""" Liste les imprimantes installées
	"""
	printers = []
	for a in win32print.EnumPrinters(2):
		# a(flags, description, name, comment)
		printers.append(a[2])
	return(printers)

#------------------------
#####  Préparation  #####
# Lecture des paramètres
parser = argparse.ArgumentParser(prog='gerer_les_imprimantes')
parser.add_argument('--defauts', action='store_true', help='Uniquement définir les imprimantes par défaut')
parser.add_argument('workingdir', nargs=1, help='Dossier contenant les .cfg et les .vbs')
args = parser.parse_args(sys.argv[1:])
wd = args.workingdir.pop() + os.sep

# Fichier de log
fichier_log=r'C:\imprimantes.log'
logging.basicConfig(
	filename=fichier_log,
	level=logging.DEBUG,
	format='%(asctime)s - %(levelname)s: %(message)s')
# Chargement de la liste des imprimantes
config = ConfigParser.ConfigParser()
logging.debug("wd: {g}".format(g=wd))
config.read(wd + 'config.cfg')
imprimantes = {}
for sec in config.sections():
	if sec != "General":
		imprimantes[sec] = {}
		for key, val in config.items(sec):
			imprimantes[sec][key] = val
# Options générales
chemin_inf=config.get('General', 'chemin_inf')
nettoyage=config.get('General', 'nettoyage')
ignorer_ptr=config.get('General', 'ignorer_ptr')
# Chargement de la liste des modèles et de leur fichier INF
mod = ConfigParser.ConfigParser()
mod.read(wd + 'modeles.cfg')
modeles = {}
for sec in mod.sections():
	modeles[sec] = {}
	for key, val in mod.items(sec):
		modeles[sec][key] = val
# Récupération des infos concernant la machine
ip = socket.gethostbyname(socket.gethostname())
(hote, groupe) = nslook(ip)
logging.debug("Infos sur la machine : {hote} / {groupe}".format(hote=hote, groupe=groupe))

#----------------------------------
#####  Supressions et ajouts  #####
printers = lister_ptr()
logging.debug("Liste des imprimantes : {ptr}".format(ptr=', '.join(printers)))
# On regarde les imprimantes installées et on retire celles qui sont déclarées mais non affectées
if not args.defauts:
	for ptr in printers:
		if nettoyage == "oui": # Purge !
			supprimer_ptr(ptr)
		elif ptr in imprimantes:
			aff = imprimantes[ptr]['affectations']
			if groupe not in aff and hote not in aff:
				supprimer_ptr(ptr)

printers = lister_ptr()
# On ajoute les imprimantes affectées non encore installées
for imp in imprimantes:
	if not 'affectations' in imprimantes[imp]:
		logging.debug("{nom} n'a pas d'affectations".format(nom=imp))
		continue
	affectations = imprimantes[imp]['affectations']
	index = -42
	if groupe in affectations:
		index = string.find(affectations, groupe)
	elif hote in affectations:
		index = string.find(affectations, hote)
	if index >= 0:
		if imp not in printers and not args.defauts:
			ajouter_ptr(imp, 'ip')
			#if utiliser_unc and "unc" in imprimantes[imp]:
			#ajouter_ptr(imp, 'unc')
		if affectations[index-1] == "*":
			default_ptr(imp)
logging.debug("------  Installation des imprimantes terminée  ------")