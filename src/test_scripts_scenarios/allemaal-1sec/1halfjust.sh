#!/bin/sh

sleep 1s
echo "$@" >> /var/local/queueer/testoutput.log
echo "5"
echo "$0: HOK."
