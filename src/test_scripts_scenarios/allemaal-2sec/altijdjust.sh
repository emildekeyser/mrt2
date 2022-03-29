#!/bin/sh

sleep 2s
echo "$@" >> /var/local/queueer/testoutput.log
echo "10"
echo "$0: OK."
