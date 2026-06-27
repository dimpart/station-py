#!/usr/bin/env bash

exec=python3
logs=/tmp

time=$(date +%Y%m%d-%H%M)

function start() {
    res=$(pgrep -f "${exec} .*$2")
    #res=$(pgrep -f "$2")
    if [[ "${res}" == "" ]]
    then
        log=${logs}/$1-${time}.log
        # echo "starting $2 >> ${log}"
        # ${exec} "$2" >> "${log}" 2>&1 &
        echo "starting $2 >> ${log}"
        ${exec} "$2" --log-dir=${logs} >> /dev/null 2>&1 &
    else
        for pid in ${res}
        do
            echo "process exists: $2 ($((pid)))"
        done
    fi
}


# main
if [[ $# -eq 2 ]]
then
    start "$1" "$2"
else
    echo ""
    echo "Usage:"
    echo "    $0 <name> <path/to/script.py>"
    echo ""
fi
