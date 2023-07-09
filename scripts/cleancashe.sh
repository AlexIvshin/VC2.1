#!/bin/bash

# check root
ROOT_UID=0
E_NOTROOT=67
if [ "$UID" != "$ROOT_UID" ]
    then echo "Нет прав на исполнение! Только root!"
         exit $E_NOTROOT
fi

sync; echo 1 > /proc/sys/vm/drop_caches
sync; echo 2 > /proc/sys/vm/drop_caches
sync; echo 3 > /proc/sys/vm/drop_caches
