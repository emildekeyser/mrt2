#!/bin/sh

sleep 2m
echo "$@" >> /var/local/queueer/testoutput.log
echo "0"
echo "$0: NOK."
