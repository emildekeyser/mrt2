#!/bin/bash
echo reset | socat - /var/local/queueer/sbqueue.socket
