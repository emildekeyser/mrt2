#!/bin/sh

sleep 0.$(shuf -i0-5000 -n1)
echo "$@" >> /var/local/queueer/testoutput.log
echo "10"
echo "$0: OK."
