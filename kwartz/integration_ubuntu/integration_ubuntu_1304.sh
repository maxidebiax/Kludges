#!/bin/bash
# Script d'intégration d'Ubuntu 13.04 à un réseau Kwartz
# - Nécessite une connexion internet
# - Dans Kwartz~Control, mettre l'ordi en "Authorisé non filtré" pour la première màj

# Récupération auto du proxy
ip=`ip route | grep "default via" | cut -d" " -f3`
if [ -z $ip ];then
    echo "Impossible de retrouver l'ip du serveur Kwartz"
    read -p "Veuiller la saisir : " ip
else
    echo "L'adresse du proxy kwartz est $ip"
fi
echo "-------------------------------"
echo "Si vous voulez pouvoir construire une image sur kwartz, il faut que Linux soit installé sur une unique partition en ext3 dont les inodes font 128 bits (Rembo5/Tivoli)."
echo "Voir http://www.kwartz.com/Installation-d-un-poste-Ubuntu-11.html pour l'utilisation manuelle de mkfs.ext3"
echo "De plus, il est indispensable d'utiliser lilo comme bootloader, et non grub"
read -n 1 -s -p '> Appuyez sur une touche pour continuer...'

echo "\n##  Declaration du proxy  ##"
bashrc=/etc/profile.d/proxy.sh
touch $bashrc # car il n'existe certainement pas
if [ `grep -c tp_proxy $bashrc` -lt 1 ];then
    echo "export http_proxy=http://$ip:3128" >> $bashrc
    echo "export ftp_proxy=ftp://$ip:3128" >> $bashrc
fi
source $bashrc
# skel
bashrc=/etc/skel/.bashrc
if [ `grep -c tp_proxy $bashrc` -lt 1 ];then
    echo "export http_proxy=http://$ip:3128" >> $bashrc
    echo "export ftp_proxy=ftp://$ip:3128" >> $bashrc
fi
echo "## ... et dans la session X"
gsettings set org.gnome.system.proxy mode 'manual'
for proto in http https
do
    gsettings set org.gnome.system.proxy.$proto host "$ip"
    gsettings set org.gnome.system.proxy.$proto port 3128
done
echo "## ... et pour apt"
aptproxy=/etc/apt/apt.conf.d/proxy
echo "Acquire::http::Proxy \"http://$ip:3128\";" > $aptproxy
echo "Acquire::ftp::Proxy \"ftp://$ip:3128\";" >> $aptproxy

echo "##  Mises à jour  ##"
apt-get update
apt-get -y dist-upgrade
echo "## Installation des paquets localisés en français"
apt-get -y install language-pack-fr language-pack-fr-base firefox-locale-fr libreoffice-l10n-fr libreoffice-help-fr thunderbird-locale-fr hunspell-fr hyphen-fr mythes-fr wfrench
# Paquets requis pour un support complet des langues (évite un message d'alerte)
apt-get -y install myspell-en-au openoffice.org-hyphenation myspell-en-gb libreoffice-l10n-en-gb hyphen-en-us thunderbird-locale-en-us language-pack-gnome-fr hunspell-en-ca thunderbird-locale-en thunderbird-locale-en-gb mythes-en-us libreoffice-l10n-en-za mythes-en-au libreoffice-help-en-gb wbritish myspell-en-za
#echo "# Sélectionner vos paramétres de langue : #"
#gnome-language-selector

echo "## Installation de lilo"
read -p "Procéder à l'installation de lilo ? [O/n] : " choix
case $choix in
    [nN])
    ;;
    *)
    apt-get -y install lilo
    liloconfig -f
    # Retrait de l'écran de sélection du kernel
    sed -i -e 's/prompt/#prompt/' /etc/lilo.conf
    lilo;;
esac

echo "## Coupure des màj auto"
sed -i -e 's/APT::Periodic::Update-Package-Lists "1"/APT::Periodic::Update-Package-Lists "0"/' /etc/apt/apt.conf.d/10periodic
echo "## Coupure du crash report (apport)"
# Bug connu de la 13.04 où on a un crash report de telepathy à chaque démarrage de l'ordi
sed -i -e "s/enabled=1/enabled=0/" /etc/default/apport
echo "## Configuration de l'horloge (NTP)"
# Kwartz peut faire office de serveur de temps
sed -i -e 's/NTPDATE_USE_NTP_CONF=yes/NTPDATE_USE_NTP_CONF=no/' /etc/default/ntpdate
sed -i -e "s/NTPSERVERS=\"ntp.ubuntu.com\"/NTPSERVERS=\"$ip\"/" /etc/default/ntpdate
ntpdate-debian
#echo "## Suppression de /etc/hostname"
# Ainsi, dhcpd va récupérer le host-name (/etc/dhcp/dhclient.conf) lors du démarrage
#rm -f /etc/hostname
# Par contre, le dhcp répond parfois avec un suffixe _x

echo "## Authentification des utilisateurs sur le réseau et 'liaison au domaine' ##"
echo "Les réponses à donner, dans l'ordre : "
echo "* ldap://$ip"
echo "* dc=monlycee,dc=fr (remplacer par votre nom de domaine)"
echo "* 3, non, non"
read -n 1 -s -p '... Pause ... (appuyez sur une touche pour continuer)'
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
echo "## Activation de l'écran de login"
lightdm=/etc/lightdm/lightdm.conf
if [ `grep -c greeter-show-manual-login $lightdm` -lt 1 ];then
    echo "greeter-show-manual-login=true" >> $lightdm
fi

echo "## Modification des répertoires par défaut du home"
sed -i -e 's/^MUSIC/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^DOWNLOAD/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^TEMPLATES/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^PUBLIC/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^DOCUMENTS/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^PICTURES/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^VIDEO/#&/' /etc/xdg/user-dirs.defaults
echo "## Nettoyage de la barre de favoris (Unity launcher)" # Fonctionnement erratique
dconf write "/com/canonical/unity/launcher/favorites" "['application://ubiquity-gtkui.desktop', 'application://nautilus.desktop', 'application://firefox.desktop', 'application://libreoffice-writer.desktop', 'application://libreoffice-calc.desktop', 'application://libreoffice-impress.desktop', 'application://gnome-control-center.desktop', 'unity://running-apps', 'unity://expo-icon', 'unity://devices']"

echo "## Création des liens symboliques"
ln -s /bin/bash /bin/kwartz-sh
ln -s /bin/umount /bin/smbumount

# Paquets supplémentaires
apt-get -y install vim numlockx synaptic 
echo "## Installation de LTSP"
read -p "Procéder à l'installation de LTSP (partage de bureau ; nécessite un ordi serveur) ? [o/N] : " choix
case $choix in
    [oO])
    apt-get -y install ltsp-client
    *)
    ;;
esac
