#!/bin/bash
# Script de nettoyage de clé pour le trojan iTunesHelper.vbe / .vbs
#####  Notes  #####
# Nécessite les mtools -> la clé doit être en fat
# Nécessite l'accès au devices -> être root

if [ ! $# -eq 1 ];then
    echo "ERREUR : Il faut préciser le point de montage de la clé !"
    exit 1
fi
mount=`mount | grep $1`
if [ ! `echo $mount|wc -l` -eq 1 ];then
    echo "ERREUR : Plusieurs points de montage possibles..."
    exit 2
fi
dev=`echo $mount|cut -d' ' -f1`
media=`echo $mount|cut -d' ' -f3`
echo MEDIA $media
echo DEVICE $dev
read -p "Continuer ?" yn

# Nettoyage de la merde
echo "# Nettoyage du virus sur la clé usb"
cmd1="ls -l {}"
#cmd2="echo {}"
cmd2="rm -f {}"
find $media \( -name "*.lnk" -o -name "*.vbs" -o -name "*.vbe" \) -exec $cmd1 \; -exec $cmd2 \;

# Retrait des attributs hidden et system
# mattrib : http://linlog.skepticats.com/entries/2007/10/26_1516/
echo "## Paramétrage des mtools"
mtoolsrc=~/.mtoolsrc
end="1"
echo "mtools_skip_check=1" > $mtoolsrc
for lettre in a b c d e f g h i j k
do
    device="/dev/sd$lettre$end"
    if [ -e $device ];then
        echo "drive $lettre: file=\"$device\"" >> $mtoolsrc
    fi
done
AA="${dev:7:1}:/"
echo "### Restauration des attributs de fichiers normaux sur $AA"
mattrib -s -h -/ $AA

echo "##### Opération réussie !! #####"
