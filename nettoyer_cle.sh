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
read -p "Continuer ?" yn

# Nettoyage
echo "# Nettoyage du virus sur la clé usb"
cmd="rm -f"
find $media -name "*.lnk" -exec $cmd {} \;
find $media -name "*.vbs" -exec $cmd {} \;
find $media -name "*.vbe" -exec $cmd {} \;

# Copie de sauvegarde
echo "## Copie de la clé"
tmp="/tmp/sauvegarde_cle"
if [ ! -d $tmp ];then
    mkdir $tmp
else
    read -p "$tmp plein ; procéder au nettoyage ? [O/n] " yn
    case $yn in
        [Nn]* )
            rm -rf $tmp.old
            mv $tmp $tmp.old ;;
        * )
            rm -rf $tmp ;;
    esac
fi
cp -R $media $tmp

# Formattage
echo "### Formattage de la clé usb"
read -p "Continuer ?" yn
umount $media
mkfs.vfat $dev

# Restauration
echo "#### Restoration du contenu de la clé usb"
mount $dev
mount=`mount | grep $dev`
media=`echo $mount|cut -d' ' -f3`
cp -R $tmp $media

echo "##### Opération réussie !! #####"
