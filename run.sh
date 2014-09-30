#!/bin/sh
start(){
    celery -A tasks worker --loglevel=info -n new &
    ./TwitterBayesFilter.py &
}

stop(){
    pkill -9 -f celery
    pkill -9 -f TwitterBayesFilter.py
}

case "$1" in
    start)
        start
    ;;
    stop)
        stop
    ;;
esac
