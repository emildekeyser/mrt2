#!/bin/bash

#                                                 __                               
#                                                /\ \__                            
#    ___     ___     ___    __  __     __   _ __ \ \ ,_\    ___     ____   __  __  
#   /'___\  / __`\ /' _ `\ /\ \/\ \  /'__`\/\`'__\\ \ \/   /'___\  /',__\ /\ \/\ \ 
#  /\ \__/ /\ \L\ \/\ \/\ \\ \ \_/ |/\  __/\ \ \/  \ \ \_ /\ \__/ /\__, `\\ \ \_/ |
#  \ \____\\ \____/\ \_\ \_\\ \___/ \ \____\\ \_\   \ \__\\ \____\\/\____/ \ \___/ 
#   \/____/ \/___/  \/_/\/_/ \/__/   \/____/ \/_/    \/__/ \/____/ \/___/   \/__/  
#                                                                                  
#                                                                                  

################################################################################

# Input: namen.csv file with header and format: lastname,firstname,vmid
# Output: namesOutput.py, students in a python array.

################################################################################

DOMAIN_SUFFIX=${DOMAIN_SUFFIX:-.sb.uclllabs.be}
INPUTFILE=${1:-namen.csv}
OUTPUTFILE=${2:-namesOutput.py}

IFS=","
echo "vms = [" > $OUTPUTFILE
tail --lines=+2 $INPUTFILE | while read f1 f2 f3
do
    echo "    ['$f1-$f2$DOMAIN_SUFFIX','$f3']," >> $OUTPUTFILE
done
echo "]" >> $OUTPUTFILE
