#!/bin/sh
start(){
    celery -A widget_tasks worker -Q of_twitter_widget --loglevel=debug -n of_twitter_widget &
    ./TrainTwitterFilter.py &
}

stop(){
    pkill -9 -f of_twitter_widget
    pkill -9 -f TrainTwitterFilter.py
}

case "$1" in
    start)
        start
    ;;
    stop)
        stop
    ;;
    restart)
        stop
        start
    ;;
esac
