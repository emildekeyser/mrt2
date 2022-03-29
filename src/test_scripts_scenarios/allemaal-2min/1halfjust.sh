#!/bin/sh

sleep 2m
echo "$@" >> /var/local/queueer/testoutput.log
echo "5"
echo "$0: HOK."
