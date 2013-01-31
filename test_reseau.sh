#!/bin/bash
# Test la présence d'une liste de machines sur le réseau

ADRESSES="test_reseau.txt"
# Fichier contenant les adresses à tester, une IP par ligne

function tester()
{
    hote=`host $1|cut -d" " -f5`
    local a=`ping -c 1 -q $1|grep -G "[^0] received"`
    if [ ${#a} -gt 0 ];then
        echo -e "$1\t($hote) ...\tOK"
        return 0
    fi
    echo "Impossible de joindre $1 ($hote)"
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
