#!/bin/bash

cd `dirname $0`

while true; do
    ./dvdrip.py
    if [ $? -eq 0 ]; then
        eject
    fi
    sleep 5
done
