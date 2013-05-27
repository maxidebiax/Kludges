#!/bin/bash
# Script d'intégration d'un Ubuntu à un réseau Kwartz
# !!! Nécessite une connexion internet !!!
# Dans Kwartz~Control, mettre l'ordi en "Authorisé non filtré" pour la première màj
#TODO: mointages réseau pour root ; créer un compte root ?
if [ $# -eq 1 ];then
    ip=$1
else
    echo "Erreur de syntaxe : veuiller préciser l'ip du serveur Kwartz"
    exit 1
fi
echo "Si vous voulez pouvoir construire une image sur kwartz, il faut que Linux soit installé sur une unique partition :"
echo "* En ext2, pour Rembo2"
echo "* En ext3 dont les inodes font 128 bits, pour Rembo5/Tivoli"
echo "Voir http://www.kwartz.com/Installation-d-un-poste-Ubuntu-11.html pour l'utilisation manuelle de mkfs.ext3"
echo "De même, il est indispensable d'utiliser lilo comme bootloader, et non grub"
read -n 1 -s -p 'Appuyez sur une touche pour continuer...'

echo "\n##  Declaration du proxy  ##"
bashrc=/etc/profile.d/proxy.sh
touch $bashrc # car il n'existe certainement pas
if [ `grep -c _proxy $bashrc` -lt 1 ];then
    echo "export http_proxy=http://$ip:3128" >> $bashrc
    echo "export ftp_proxy=ftp://$ip:3128" >> $bashrc
fi
source $bashrc
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
apt-get -y install language-pack-fr language-pack-fr-base language-pack-gnome-fr language-pack-gnome-fr-base firefox-locale-fr
echo "# Sélectionner vos paramétres : #"
gnome-language-selector

echo "## Coupure des màj auto"
sed -i -e 's/APT::Periodic::Update-Package-Lists "1"/APT::Periodic::Update-Package-Lists "0"/' /etc/apt/apt.conf.d/10periodic

echo "##  Authentification des utilisateurs sur le réseau et 'liaison au domaine'  ##"
# réponses : ldap://ip_du_serveur ; dc=monlycee,dc=fr ; 3 ; non ; non
apt-get -y install openbsd-inetd pidentd libpam-ldap
sed -i -e 's/^pam_password md5/#&/' /etc/ldap.conf
sed -i -e 's/#pam_password crypt/pam_password crypt/' /etc/ldap.conf

echo "## Modification de la configuration pam pour ldap"
auth-client-config -t nss -p lac_ldap
#la commande suivante est facultative
#pam-auth-update

echo "## Modification des repertoires par défaut du home"
sed -i -e 's/^MUSIC/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^DOWNLOAD/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^TEMPLATES/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^PUBLIC/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^DOCUMENTS/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^PICTURES/#&/' /etc/xdg/user-dirs.defaults
sed -i -e 's/^VIDEO/#&/' /etc/xdg/user-dirs.defaults

echo "## Ajout des lecteurs réseaux"
apt-get -y install libpam-mount smbfs
pammount=/etc/security/pam_mount.conf.xml
for lecteur in homes commun public
do
  nomm=( $lecteur )
  nom="${nomm[@]^}" # <=> Capitalize
  if [ "$nom" = "Homes" ];then
      nom="LecteurH"
  fi
  if [ `grep -c mountpoint=\"~/$lecteur $pammount` -lt 1 ];then
      sed -i -e "/<\/pam_mount>/i\<volume fstype=\"cifs\" server=\"$ip\" path=\"$lecteur\" mountpoint=\"~/$nom\" options=\"iocharset=utf8\" />" $pammount
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

echo "## Création des liens symboliques"
ln -s /bin/bash /bin/kwartz-sh
ln -s /bin/umount /bin/smbumount

read -p "Installer lilo ? [O/n] : " choix
case $choix in
    [nN])
    ;;
    *)
    echo "## Installation de lilo"
    apt-get -y install lilo
    sed -i -e 's/vmlinuz-2\* 2/vmlinuz-[23]\* 2/' /usr/sbin/liloconfig
    liloconfig -f
    lilo;;
esac

# Paquets supplémentaires
apt-get -y install numlockx
# Redemarrage final
read -p "Redémarrer maintenant ? [o/N] : " choix
case $choix in
    [oO])
    `reboot`;;
esac
