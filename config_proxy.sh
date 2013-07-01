#!/bin/bash
# Script de configuration automatisé de proxy pour linux
#TODO : mode persistant

# Récupération auto du proxy
ip=`ip route | grep "default via" | cut -d" " -f3`
if [ -z $ip ];then
    echo "Impossible de retrouver l'ip du serveur Kwartz"
    exit 1
else
    echo "L'adresse de votre proxy est $ip"
fi
# Proxy
echo ""
echo "##  Déclaration du proxy  ##"
proxy=~/.bashrc
touch $proxy # car il n'existe certainement pas
if [ `grep -c tp_proxy $proxy` -lt 1 ];then
    echo "# Configuration du proxy (console)" >> $proxy
    echo "export http_proxy=http://$ip:3128" >> $proxy
    echo "export ftp_proxy=ftp://$ip:3128" >> $proxy
fi
chmod +x $proxy
source $proxy

# TODO : détection OS
echo "## ... et dans les sessions X"
gnome=/etc/profile.d/gnome.sh
echo "# Configuration du proxy (mode graphique)" > $gnome
echo "gsettings set org.gnome.system.proxy mode 'manual'" >> $gnome
echo "for proto in http https ftp" >> $gnome
echo "do" >> $gnome
echo "  gsettings set org.gnome.system.proxy.\$proto host '$ip'" >> $gnome
echo "  gsettings set org.gnome.system.proxy.\$proto port 3128" >> $gnome
echo "done" >> $gnome

# TODO : détection apt
echo "## ... et pour apt"
aptproxy=/etc/apt/apt.conf.d/proxy
echo "Acquire::http::Proxy \"http://$ip:3128\";" > $aptproxy
echo "Acquire::ftp::Proxy \"ftp://$ip:3128\";" >> $aptproxy

