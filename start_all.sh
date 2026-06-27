#!/usr/bin/env bash

root=$(cd "$(dirname "$0")" || exit;pwd)

start_shell=${root}/shell_start.sh
stop_shell=${root}/shell_stop.sh

# start "name" "path/to/script.py"
function start() {
    ${start_shell} "$1" "${root}/$2"
}

# stop "path/to/script.py"
function stop() {
    ${stop_shell} "${root}/$1"
}

# restart "name" "path/to/script.py"
function restart() {
    stop "$2"
    sleep 1
    start "$1" "$2"
}

function title() {
    echo ""
    echo "    >>> $1 <<<"
    echo ""
}


if [[ "$*" == "restart" ]]
then
    launch="restart"
    echo "========================"
    echo "    Restarting ..."
    echo "========================"
else
    launch="start"
    echo "========================"
    echo "    Starting ..."
    echo "========================"
fi


#
#   Station & Bridges
#

title "DIM Station"
${launch} "dims" "station/start.py"

sleep 2

title "DIM Station Bridge"
${launch} "bridge" "sbots/sbot_octopus.py"


#
#   Service Bots
#

#title "DIM Search Engine"
#${launch} "archivist" "sbots/sbot_archivist.py"
#
#title "DIM Push Center"
#${launch} "announcer" "sbots/sbot_announcer.py"
#
#title "DIM Monitor"
#${launch} "monitor" "sbots/sbot_monitor.py"

echo ""
echo "    >>> Done <<<"
echo ""
