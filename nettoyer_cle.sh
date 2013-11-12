#!/bin/bash

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

# Nettoyage
echo "# Nettoyage du virus sur la clé usb"
#cmd="rm -f"
cmd="ls -l"
find $media -name "*.lnk" -exec $cmd {} \;
find $media -name "*.vbs" -exec $cmd {} \;
find $media -name "*.vbe" -exec $cmd {} \;

# Copie de sauvegarde
echo "## Copie de la clé usb"
tmp="/tmp/sauvegarde_cle"
if [ ! -d $tmp ];then
    mkdir "$tmp"
else
    read -p "$tmp plein ; procéder au nettoyage ? [O/n]" yn
    case $yn in
        [Oo]* )
            rm -rf "$tmp/*"
            break;;
        * ) exit 3 ;;
    esac
fi
cp -R "$media/*" $tmp/

# Formattage
echo "### Formattage de la clé usb"
mkfs.vfat $dev

# Restauration
echo "#### Restoration du contenu de la clé usb"
cp -R "$tmp/*" "$media/"

echo "##### Opération réussie !! #####"
