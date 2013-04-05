#!/bin/bash
# Test la présence d'une liste de machines sur le réseau
# Paramètre 1 : nom du fichier comptenant la liste des adresses

ADRESSES=$1
# Fichier contenant les adresses à tester, une IP par ligne

function tester()
{
    hote=`host $1|cut -d" " -f5`
    local a=`ping -c 1 -q $1|grep -G "[^0] received"`
    if [ ${#a} -gt 0 ];then
        #echo -e "$1\t($hote) ...\tOK"
        echo -e "$hote\t($1) ...\tOK"
        return 0
    fi
    echo "$1 : impossible de joindre $hote"
}

while read line
do
    b=""
    if [[ $line =~ ^[0-9]+\.[0-9]+\. ]];then
        b=`tester $line`
    fi
    if [ -n "$b" ];then
        echo $b
    fi
done < $ADRESSES
