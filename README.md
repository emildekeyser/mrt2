This repo only contains the part of the program that I worked on (backend), the
frontend is redacted.

Installation
============

````
# git clone repo
# cd ./repo
# ./install.sh
````

(Re)setting test attempts
=========================

````
# echo "reset" | socat - /var/local/queueer/sbqueue.socket # => reset all
# echo "reset name.sb.be" | socat - /var/local/queueer/sbqueue.socket # => reset this student
# echo "reset name.sb.be 7000" | socat - /var/local/queueer/sbqueue.socket # => reset this student to 7000 attempts
````

Archiving
=========

In the crontab you can see run_tests_v2.py. By Default his script writes the
results of all test's for all students to a logfile, directories and an sqlite
db.

Configuration
=============

* Queue api server: /usr/local/mrt2/src/queue_config.py
    * To apply, run: systemctl restart queue_server
* Frontend: /var/www/html/mrt2/js/config.js
    * To apply: hard refresh your browser.
* Add tests: /usr/local/mrt2/src/test_list.py + /usr/local/mrt2/src/scripts/
    * To apply, run: /usr/local/mrt2/src/run_tests_v2.py
* Add students: /usr/local/mrt2/src/namen.csv
    * To apply, run: /usr/local/mrt2/src/convert_csv.sh + /usr/local/mrt2/src/run_tests_v2.py
