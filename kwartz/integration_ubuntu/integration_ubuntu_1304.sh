#!/bin/bash
# Script d'intégration d'Ubuntu 13.04 à un réseau Kwartz
# - Nécessite une connexion internet et d'être en root
# - Dans Kwartz~Control, mettre l'ordi en "Authorisé non filtré" pour la première màj

echo "-----------------------------------"
# Récupération auto du proxy
ip=`ip route | grep "default via" | cut -d" " -f3`
if [ -z $ip ];then
    echo "Impossible de retrouver l'ip du serveur Kwartz"
    read -p "Veuiller la saisir : " ip
else
    echo "L'adresse de votre proxy kwartz est $ip"
fi
echo "-----------------------------------"
# Disclaimer
echo "NB: Si vous voulez pouvoir construire une image sur kwartz, il faut que Linux soit installé sur une unique partition ext3 dont les inodes font 128 bits (Rembo5/Tivoli)."
echo "Voir http://www.kwartz.com/Installation-d-un-poste-Ubuntu-11.html pour l'utilisation manuelle de mkfs.ext3"
echo "De plus, il est indispensable d'utiliser lilo comme bootloader, et non grub"
read -n 1 -s -p '... Appuyez sur une touche pour continuer ...'
# Proxy
echo ""
echo "##  Déclaration du proxy  ##"
proxy=/etc/profile.d/proxy.sh
touch $proxy # car il n'existe certainement pas
if [ `grep -c tp_proxy $proxy` -lt 1 ];then
    echo "# Configuration du proxy (console)" >> $proxy
    echo "export http_proxy=http://$ip:3128" >> $proxy
    echo "export ftp_proxy=ftp://$ip:3128" >> $proxy
fi
chmod +x $proxy
source $proxy
echo "## ... et dans les sessions X"
gnome=/etc/profile.d/gnome.sh
echo "# Configuration du proxy (mode graphique)" > $gnome
echo "gsettings set org.gnome.system.proxy mode 'manual'" >> $gnome
echo "for proto in http https ftp" >> $gnome
echo "do" >> $gnome
echo "  gsettings set org.gnome.system.proxy.\$proto host '$ip'" >> $gnome
echo "  gsettings set org.gnome.system.proxy.\$proto port 3128" >> $gnome
echo "done" >> $gnome
echo "## ... et pour apt"
aptproxy=/etc/apt/apt.conf.d/proxy
echo "Acquire::http::Proxy \"http://$ip:3128\";" > $aptproxy
echo "Acquire::ftp::Proxy \"ftp://$ip:3128\";" >> $aptproxy

# Mises à jour
echo "##  Mises à jour  ##"
apt-get update
apt-get -y dist-upgrade
echo "## Installation des paquets localisés en français"
apt-get -y install language-pack-fr language-pack-fr-base firefox-locale-fr libreoffice-l10n-fr libreoffice-help-fr thunderbird-locale-fr hunspell-fr hyphen-fr mythes-fr wfrench
# Paquets requis pour un support complet des langues (évite un message d'alerte)
apt-get -y install myspell-en-au openoffice.org-hyphenation myspell-en-gb libreoffice-l10n-en-gb hyphen-en-us thunderbird-locale-en-us language-pack-gnome-fr hunspell-en-ca thunderbird-locale-en thunderbird-locale-en-gb mythes-en-us libreoffice-l10n-en-za mythes-en-au libreoffice-help-en-gb wbritish myspell-en-za

echo "## Installation de lilo"
read -p "Procéder à l'installation de lilo ? [O/n] : " choix
case $choix in
    [nN])
    ;;
    *)
    apt-get -y install lilo
    liloconfig -f
    # Retrait de l'écran de sélection du kernel
    sed -i -e 's/^prompt/#&/' /etc/lilo.conf
    # Définition du disque de démarrage
    #sed -i -e 's/^boot = \/dev\/disk/#&' /etc/lilo.conf
    #sed -i -e 's/^#boot = \/dev\/sda/boot = \/dev\/sda/' /etc/lilo.conf
    #sed -i -e 's/root = "UUID/#&/' /etc/lilo.conf
    #sed -i -e 's/#root = \/dev/root = \/dev/' /etc/lilo.conf
    lilo;;
esac

# Paramétrages
echo "" >> $gnome
echo "# Nettoyage de la barre de favoris (Unity launcher)" >> $gnome
echo "dconf write '/com/canonical/unity/launcher/favorites' \"['application://ubiquity-gtkui.desktop', 'application://nautilus.desktop', 'application://firefox.desktop', 'application://libreoffice-writer.desktop', 'application://libreoffice-calc.desktop', 'application://libreoffice-impress.desktop', 'application://gnome-control-center.desktop', 'unity://running-apps', 'unity://expo-icon', 'unity://devices']\"" >> $gnome
echo "# Désactivation du verouillage écran" >> $gnome
echo "dconf write '/com/gnome/desktop/lockdown/disable-lock-screen' 'true'" >> $gnome
echo "dconf write '/com/gnome/desktop/screensaver/lock-enabled' 'false'" >> $gnome
chmod +x $gnome
$gnome

echo "# Programmation de la retouche du fstab"
rclocal=/etc/rc.local
if [ `grep -c ext2 $rclocal` -lt 1 ];then
    sed -i -e '/exit 0/d' $rclocal
    echo "# Retouche du fstab (mal) réécrit par Tivoli" >> $rclocal
    echo "sed -i -e 's/ext2\tdefaults/ext3\terrors=remount-ro/' /etc/fstab" >> $rclocal
    echo "exit 0" >> $rclocal
fi

echo "## Coupure des màj auto"
sed -i -e 's/APT::Periodic::Update-Package-Lists "1"/APT::Periodic::Update-Package-Lists "0"/' /etc/apt/apt.conf.d/10periodic
echo "## Coupure du crash report (apport)"
# Bug connu de la 13.04 où on a un crash report de telepathy à chaque démarrage de l'ordi
sed -i -e "s/enabled=1/enabled=0/" /etc/default/apport
echo "## Configuration de l'horloge (NTP)" # Kwartz peut faire office de serveur de temps
sed -i -e 's/NTPDATE_USE_NTP_CONF=yes/NTPDATE_USE_NTP_CONF=no/' /etc/default/ntpdate
sed -i -e "s/NTPSERVERS=\"ntp.ubuntu.com\"/NTPSERVERS=\"$ip\"/" /etc/default/ntpdate
ntpdate-debian
#echo "## Suppression de /etc/hostname"
# Ainsi, dhcpd va récupérer le host-name par dhcp (/etc/dhcp/dhclient.conf) lors du démarrage
#rm -f /etc/hostname
# Par contre, le dhcp kwartz répond avec un suffixe _2 si on utilise la seconde interface réseau définit

# Authentification LDAP
echo "## Authentification des utilisateurs sur le réseau et 'liaison au domaine' ##"
echo "Les réponses à donner, dans l'ordre : "
echo "* ldap://$ip"
echo "* dc=monlycee,dc=fr (remplacer par votre nom de domaine)"
echo "* 3, non, non"
read -n 1 -s -p '... Appuyez sur une touche pour continuer ...'
apt-get -y install openbsd-inetd pidentd libpam-ldap
sed -i -e 's/^pam_password md5/#&/' /etc/ldap.conf
sed -i -e 's/#pam_password crypt/pam_password crypt/' /etc/ldap.conf
echo "## Modification de la configuration pam pour ldap"
auth-client-config -t nss -p lac_ldap

echo "## Ajout des lecteurs réseaux"
apt-get -y install libpam-mount cifs-utils
pammount=/etc/security/pam_mount.conf.xml
for lecteur in homes commun public
do
  nomm=( $lecteur )
  nom="${nomm[@]^}" # <=> Capitalize
  if [ "$nom" = "Homes" ];then
      nom="LecteurH"
  fi
  if [ `grep -c mountpoint=\"~/$lecteur $pammount` -lt 1 ];then
      sed -i -e "/<\/pam_mount>/i\<volume uid=\"1000-65532\" fstype=\"cifs\" server=\"$ip\" path=\"$lecteur\" mountpoint=\"~/$nom\" options=\"iocharset=utf8\" />" $pammount
  fi
done
echo "## Modification de /etc/pam.d/common-session"
pamcommon=/etc/pam.d/common-session
if [ `grep -c "pam_mkhomedir.so umask=077 silent skel=/etc/skel/" $pamcommon` -lt 1 ];then
    sed -i -e '/session.*optional.*mount/i\session required\tpam_mkhomedir.so umask=077 silent skel=/etc/skel/' $pamcommon
fi
echo "## Modification de lightdm.conf"
lightdm=/etc/lightdm/lightdm.conf
if [ `grep -c greeter-show-manual-login $lightdm` -lt 1 ];then
    # Focer l'écran de connexion
    echo "greeter-show-manual-login=true" >> $lightdm
fi
if [ `grep -c allow-guest $lightdm` -lt 1 ];then
    # Pas de compte invité, ni de connexion distante
    echo "allow-guest=false" >> $lightdm
    echo "greeter-show-remote-login=false" >> $lightdm
fi

echo "## Modification des répertoires par défaut du home"
sed -i -e 's/^MUSIC/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^DOWNLOAD/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^TEMPLATES/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^PUBLIC/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^DOCUMENTS/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^PICTURES/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^VIDEO/#&/' /etc/xdg/user-dirs.defaults

echo "## Création des liens symboliques"
ln -s /bin/bash /bin/kwartz-sh
ln -s /bin/umount /bin/smbumount

#echo "## Installation de LTSP"
#read -p "Procéder à l'installation de LTSP (partage de bureau ; nécessite un ordi serveur) ? [o/N] : " choix
#case $choix in
#    [oO])
#    apt-get -y install ltsp-client
#    *)
#    ;;
#esac

# Paquets supplémentaires
apt-get -y install vim numlockx synaptic 
# Paquets pédagogiques
apt-get -y install geogebra geogebra-gnome 
#... gromit, java + java-plugin

echo "###################################"
echo "#  Bravo ! Installation terminée  #"
echo "###################################"
