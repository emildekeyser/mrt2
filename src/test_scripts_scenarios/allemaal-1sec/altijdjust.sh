#!/bin/sh

sleep 1s
echo "$@" >> /var/local/queueer/testoutput.log
echo "10"
echo "$0: OK."
