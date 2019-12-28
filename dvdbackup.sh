#!/bin/bash

set -x

cd `dirname $0`

mkdir -p rip
while true; do
    echo Press ENTER to rip...
    read foo    
    rm -rf riptmp
    mkdir riptmp
    time dvdbackup -M -o riptmp -p
    if [ $? -ne 0 ]; then
        continue
    fi
    eject
    volid=$(ls riptmp/)
    volidfn=$(echo "${volid}"|tr ' /' '_-')
    mkisofs -udf -o "rip/${volidfn}.iso.tmp" -V "${volid}" "riptmp/${volid}"
    mv "rip/${volidfn}.iso.tmp" "rip/${volidfn}.iso"
    echo DONE
done
