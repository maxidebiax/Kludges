#!/bin/bash
# Script sauvegardant des Virtualboxes
VBOXMANAGE="/usr/bin/VBoxManage -q"
ORIG="~/VirtualBox VMs"
DEST="~/SauvegardesVB"

contains()
{
    # $2 contient l'élément $1
    [[ $1 =~ $2 ]] && return 0 || return 1
}

sauvegarder_vm()
{
    echo "# Sauvegarde de '$1'"
    if [ -f $DEST/$1 ]; then
        mkdir $DEST/$1
    fi
    rsync -a --delete "$ORIG/$1/" "$DEST/$1/"
}

echo `date +%Y%m%d`
vms=`$VBOXMANAGE list vms|cut -d" " -f1|tr -d '"'`
running=`$VBOXMANAGE list runningvms|cut -d" " -f1|tr -d '"'`

for vm in $vms; do
    echo "-> $vm"
    if contains $running $vm; then
        echo "# Machine en cours de fonctionnement. Redémarrage en cours..."
        $VBOXMANAGE controlvm $vm savestate
        sauvegarder_vm $vm
        VBoxHeadless --startvm $vm&
    else
        sauvegarder_vm $vm
    fi
done
