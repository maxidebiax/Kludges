#!/bin/bash
# Script de configuration automatisé de proxy pour linux
#TODO : mode persistant au choix
#TODO: voir par network manager

# Récupération auto de l'ip
ip=`ip route | grep "default via" | cut -d" " -f3`
if [ -z $ip ];then
    echo "Impossible de retrouver l'ip du serveur Kwartz"
    exit 1
else
    echo "L'adresse de votre proxy est $ip"
fi
# Test du port de connexion
trouve=non
for port in 3128 8080 80
do
    if [ `nc -z $ip 7864; echo $?` -eq 1 ]; then
        echo $port
        trouve=oui
done
if [ $trouve -eq "non" ]
    echo "Impossible de deviner le port de connexion"
    exit 2
fi

echo ""
echo "##  Déclaration du proxy  ##"
proxy=~/.bashrc
touch $proxy # car il n'existe certainement pas
if [ `grep -c tp_proxy $proxy` -lt 1 ];then
    echo "# Configuration du proxy (console)"
    echo "export http_proxy=http://$ip:$port"
    #echo "# Configuration du proxy (console)" >> $proxy
    #echo "export http_proxy=http://$ip:$port" >> $proxy
    #echo "export ftp_proxy=ftp://$ip:$port" >> $proxy
fi
source $proxy

# TODO : détection OS
#echo "## ... et dans les sessions X"
#gnome=/etc/profile.d/gnome.sh
#echo "# Configuration du proxy (mode graphique)" > $gnome
#echo "gsettings set org.gnome.system.proxy mode 'manual'" >> $gnome
#echo "for proto in http https ftp" >> $gnome
#echo "do" >> $gnome
#echo "  gsettings set org.gnome.system.proxy.\$proto host '$ip'" >> $gnome
#echo "  gsettings set org.gnome.system.proxy.\$proto port $port" >> $gnome
#echo "done" >> $gnome

aptd=/etc/apt/apt.conf.d
if [ -d "$aptd" ]; then
    aptd=$aptd/proxy
    echo "## ... et pour apt"
    #echo "Acquire::http::Proxy \"http://$ip:$port\";" > $aptd
    #echo "Acquire::ftp::Proxy \"ftp://$ip:$port\";" >> $aptd
fi
