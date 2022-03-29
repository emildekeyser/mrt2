#!/bin/sh

sleep 1s
echo "$@" >> /var/local/queueer/testoutput.log
echo "0"
echo "$0: NOK."
