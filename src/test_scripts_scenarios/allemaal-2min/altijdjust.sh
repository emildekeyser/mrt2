#!/bin/sh

sleep 2m
echo "$@" >> /var/local/queueer/testoutput.log
echo "10"
echo "$0: OK."
