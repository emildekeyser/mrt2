#!/usr/bin/python3

#                            __                     __              
#                           /\ \__                 /\ \__           
#   _ __   __  __    ___    \ \ ,_\     __     ____\ \ ,_\    ____  
#  /\`'__\/\ \/\ \ /' _ `\   \ \ \/   /'__`\  /',__\\ \ \/   /',__\ 
#  \ \ \/ \ \ \_\ \/\ \/\ \   \ \ \_ /\  __/ /\__, `\\ \ \_ /\__, `\
#   \ \_\  \ \____/\ \_\ \_\   \ \__\\ \____\\/\____/ \ \__\\/\____/
#    \/_/   \/___/  \/_/\/_/    \/__/ \/____/ \/___/   \/__/ \/___/ 
#                                                                   
#                                                                   

################################################################################

# This runs's all tests in the order given in testList.py for each student.
# Students are run in parallel by a configured amount of workers. The result of
# each test is immediatly written to the archive's. After all students are
# finished, all results are also written to the sqlite archive and index.html
# is regenerated.

################################################################################

import subprocess
import datetime
import os
import jinja2
import threading
import queue

import generated_names
import test_list
import queue_config
import sqlite_adapter

# Used for archival
def write_file_in_dir(timestamp, duration, host, vmid, testdir, testscript, test_output_lines):
    fulldir = os.path.join(queue_config.archive_prefix,
                           host + "-" + vmid)
    os.makedirs(fulldir, exist_ok=True)
    filename = testdir + "-" + testscript
    line = [str(timestamp.isoformat(timespec='seconds')), str(duration.total_seconds())]
    line += test_output_lines
    with open(os.path.join(fulldir, filename), 'w') as f:
        f.write(" ".join(line) + "\n")

# Used for archival
def write_log_line(isotimestamp, duration, host, vmid, testdir, testscript, test_output_lines):
    line = [isotimestamp.isoformat(timespec='seconds'),
            str(duration.total_seconds()),
            host, vmid, testdir, testscript, test_output_lines[0], test_output_lines[1]]
    with open(queue_config.archive_logfile, 'a') as f:
        f.write(" ".join(line) + "\n")

#def run_test_battery(host, vmid):

def queue_worker(wid):
    while True:
        (host, vmid) = Q.get()
        # This is inside a generic try/catch to make sure all task_done's are fired.
        try:
            ip = queue_config.ip_prefix + queue_config.extract_octet_from_vmid(vmid)
            student = [host, vmid, ip, []]
            for check in testList.checks:
                testdir = check[0]
                testscript = check[1]
                scriptpath = os.path.join(queue_config.script_path_prefix, testdir, testscript)
                cmd = [scriptpath, host, ip]

                print(f"Worker {wid}: {testdir}/{testscript} for {host} - {ip}.")
                timestamp = datetime.datetime.now()
                test_output = subprocess \
                    .run(cmd, text=True, capture_output=True) \
                    .stdout
                delta = datetime.datetime.now() - timestamp

                test_output_lines = test_output.splitlines()
                if len(test_output_lines) != 2 or not test_output_lines[0].replace('.', '', 1).isdigit():
                    print(f"Garbage output for test {cmd} for {host}:\n{test_output}")

                # Archival:
                if queue_config.directory_archive:
                    write_file_in_dir(timestamp,
                                      delta,
                                      host, vmid,
                                      testdir, testscript,
                                      test_output_lines)

                if queue_config.logfile_archive:
                    write_log_line(timestamp,
                                   delta,
                                   host, vmid,
                                   testdir, testscript,
                                   test_output_lines)

                if queue_config.sqlite_archive:
                    with TESTRESULTS_MUTEX:
                        TESTRESULTS.append([
                            str(timestamp.astimezone().isoformat(timespec='microseconds')),
                            str(delta.total_seconds()),
                            host, vmid,
                            testdir, testscript,
                            test_output
                        ])

                # Used for generation of index.html:
                enquable = check[2]
                punt = float(test_output_lines[0])
                if punt == 10:
                    imgname = 'ok'
                elif punt >= 5:
                    imgname = 'hok'
                else:
                    imgname = 'nok'
                student[3].append([testdir, testscript, test_output_lines[0], test_output_lines[1], imgname, enquable])

            with STUDENTS_MUTEX:
                STUDENTS.append(student)
        except Exception as e:
            print(e)
        Q.task_done()

Q = queue.Queue()
STUDENTS = []
STUDENTS_MUTEX = threading.Lock()
TESTRESULTS_MUTEX = threading.Lock()
TESTRESULTS = []

# Run all tests.
if __name__ == '__main__':
    for wid in range(queue_config.concurrent_workers):
        threading.Thread(target=queue_worker, args=(wid,), daemon=True).start()

    for host, vmid in namesOutput.vms:
        Q.put((host, vmid))

    Q.join()

    if queue_config.sqlite_archive:
        print("Writing sql")
        sqlite_adapter.write_all_sql(TESTRESULTS)

    print("Writing index.html")
    with open(queue_config.front_page_template) as f:
        template = jinja2.Template(f.read(), trim_blocks=True)
    with open(queue_config.webroot_index_dot_html, 'w') as f:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(template.render(studentlist=STUDENTS,
                                testnames=[(t[0] if len(t) == 3 else t[3]) for t in testList.checks],
                                timestamp=ts
                ))
