#!/bin/bash

sleep 0.$(shuf -i0-5000 -n1)
echo "$@" >> /var/local/queueer/testoutput.log
echo "5"
echo "$0: HOK."
