#!/bin/bash

cd `dirname $0`

while true; do
    f=`ls *.iso | head -n 1`
    if [ -n "${f}" ]; then
        echo Transferring "${f}"
        rsync --inplace -v --progress "${f}" "severn:/mnt/severn_dvds/${f}"
        if [ $? -eq 0 ]; then
            echo OK - deleting "${f}"
            rm "${f}"
        else
            sleep 10
        fi
    else
        sleep 10
    fi
done
