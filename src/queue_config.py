#                            ___                   
#                          /'___\  __              
#    ___     ___     ___  /\ \__/ /\_\      __     
#   /'___\  / __`\ /' _ `\\ \ ,__\\/\ \   /'_ `\   
#  /\ \__/ /\ \L\ \/\ \/\ \\ \ \_/ \ \ \ /\ \L\ \  
#  \ \____\\ \____/\ \_\ \_\\ \_\   \ \_\\ \____ \ 
#   \/____/ \/___/  \/_/\/_/ \/_/    \/_/ \/___L\ \
#                                           /\____/
#                                           \_/__/ 

import datetime
import os
cpucount = lambda : len(os.sched_getaffinity(0))

# Where the http rest api listens
host_name = 'localhost'
port_number = 9000

tests_perday_perstudent = 50
# This can be set to any desired number. Default is assigned cpu cores.
# concurrent_workers = cpucount()
concurrent_workers = 2

# Used to construct the correct ip addresses in run_testsv2.py
# Gets pasted to the left of the octets extracted from the vmid's
ip_prefix = 'REDACTED'
# Use the last three digits from the vmid as ip octet.
extract_octet_from_vmid = lambda vmid : vmid[-3:]

script_path_prefix = '/usr/local/mrt2/src/scripts'
socketpath = '/var/local/queueer/sbqueue.socket'
front_page_template = '/usr/local/mrt2/src/mrt-template.html.j2'
webroot_index_dot_html = '/var/www/html/mrt2/index.html'

directory_archive = True
archive_prefix = '/var/local/queueer/sbarchivedir'
logfile_archive = True
archive_logfile = '/var/local/queueer/sbarchivefile.log'
sqlite_archive = True
dbfile = "/var/local/queueer/sbarchive.db"

# Average test durations are calculated from this date until present.
# (y, m, d)
start_avg_range = (2021, 2, 15)
