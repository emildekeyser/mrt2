#!/usr/bin/python3 -u
# the -u above is added to flush logs

#   _____                                      
#  /\  __`\                                    
#  \ \ \/\ \   __  __     __   __  __     __   
#   \ \ \ \ \ /\ \/\ \  /'__`\/\ \/\ \  /'__`\ 
#    \ \ \\'\\\ \ \_\ \/\  __/\ \ \_\ \/\  __/ 
#     \ \___\_\\ \____/\ \____\\ \____/\ \____\
#      \/__//_/ \/___/  \/____/ \/___/  \/____/
#                                              
#                                              

################################################################################

# The queue api server listens for enqueue requests for tasks en runs queue
# workers that run test scripts for students.

# Endpoints:
# /enqueue          = input: hostname&ipaddress&testdir&testscript,
#                     output: error message or succes confirmation
# /attempts         = input: nothing, output: the attempts register
# /queue            = input: nothing, output: the full Q
# /remove           = input: a specific task, output: error or success message
# /defaultattempts  = input: nothing, output: max amount of attempts

# Also provides a "control socket" where reset commands can be send when a
# student used all he's attempts.

################################################################################

import datetime
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import urllib.parse
import threading
import queue
import subprocess
from dataclasses import dataclass
import dataclasses
import os
import socket
import json
import sys
import argparse

# Handles wrting away results of the tests coming from the queue workers.
import isolatedRun_tests

# Provides the list of all student hostnames.
import namesOutput

# The server "config file".
import queue_config

# Interface to the sqlite archive, used to retrieve average durations.
import sqlite_adapter

# Needed to check is a test is allowed to be queued.
import testList

@dataclass()
class TestTask:
    hostname: str = ""
    ipaddress: str = ""
    testdir: str = ""
    testscript: str = ""
    expected_duration: int = 0

class RandomAccesQueue(queue.Queue):
  def try_remove(self, item):
    with self.mutex:
        try:
            self.queue.remove(item)
        except ValueError as e:
            return False
    return True

  def aslist(self):
    with self.mutex:
      return list(self.queue).copy()

Q = RandomAccesQueue()

def reset_register(amount):
    return {vm[0] : amount for vm in namesOutput.vms}

# REGISTER holds the remaining attempts for each student, 0 = student cant add
# task to the queue anymore.
REGISTER = reset_register(queue_config.tests_perday_perstudent)

# Lock above.
REGISTER_LOCK = threading.Lock()

# CURRENTTASKS represents the 'head' of the queue, needed for some functionality that
# is interested in the currenttly running task and all the upcoming tasks.
CURRENTTASKS = [None for _ in range(queue_config.concurrent_workers)]

# Lock above.
CURRENTTASKS_LOCK = threading.Lock()

# CURRENTTASKS + Q
def fullQ():
    with CURRENTTASKS_LOCK:
        global CURRENTTASKS
        tasks = [t for t in CURRENTTASKS if t is not None]
        return tasks + Q.aslist()

# Util to assemble the full path to a test script.
def script_path(task):
    return os.path.join(queue_config.script_path_prefix, task.testdir, task.testscript)

def missing_parameters(params, query_components):
    return [p for p in params if p not in query_components]

def queue_worker(wid):
    while True:
        current = Q.get()

        with CURRENTTASKS_LOCK:
            global CURRENTTASKS
            CURRENTTASKS[wid] = current

        print(f'Worker {wid} is working on {current}.')

        # We are not writing timing data and script output to the archive from here at the moment.
        # now = datetime.datetime.now()

        cmd = [script_path(current), current.hostname, current.ipaddress]
        test_output = subprocess \
            .run(cmd, text=True, capture_output=True) \
            .stdout

        # delta = datetime.datetime.now() - now

        test_output_lines = test_output.splitlines()
        if len(test_output_lines) != 2 or not test_output_lines[0].replace('.', '', 1).isdigit():
            print(f"Garbage output for test {cmd} for {host}:\n{test_output}")
        else:
            isolatedRun_tests.updateRow(current.hostname, current.testdir, current.testscript, test_output)

        print(f'Finished {current} with output: {test_output}.')

        with CURRENTTASKS_LOCK:
            CURRENTTASKS[wid] = None # When the queue is empty and this is not emptied the last task stays in the fullQ forever.

        Q.task_done()


# Handles reset commands for the REGISTER attempt counts.
# usage:
# echo "reset" | socat - ./sbqueue.socket # => reset all
# echo "reset name.sb.ukulele.be" | socat - ./sbqueue.socket # => reset this student
# echo "reset name.sb.ukulele.be 7000" | socat - ./sbqueue.socket # => reset this student to 7000 attempts
def control_socket():

    def try_update_attempts(msg):
        global REGISTER

        parser = argparse.ArgumentParser()
        parser.add_argument('command')
        parser.add_argument('student', default='*', nargs='?')
        parser.add_argument('amount', type=int, default=queue_config.tests_perday_perstudent, nargs='?')
        try:
            args = parser.parse_args(msg)
        except SystemExit:
            print(f"Invalid cmd: {msg}.")
            return

        if args.command == 'reset':
            with REGISTER_LOCK:
                if args.student == '*':
                    REGISTER = reset_register(args.amount)
                    print(f"Reset all students to {args.amount}.")
                elif args.student in REGISTER:
                    REGISTER[args.student] = args.amount
                    print(f"Set {args.student} attempt credits to {args.amount}.")
                else:
                    print(f"Student does not exist.")

    if os.path.exists(queue_config.socketpath):
        os.remove(queue_config.socketpath)

    print(f"Opening control socket: {queue_config.socketpath}.")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.bind(queue_config.socketpath)
        sock.listen()
        while True:
            conn, addr = sock.accept()
            with conn.makefile() as f:
                msg = f.readline().split()
                print(f"Control socket received cmd: {msg}.")
                try_update_attempts(msg)

# The web server that handles enqueue, queue and attmpts requests.
class NQServer(BaseHTTPRequestHandler):
    def default_respond(self, resp):
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(bytes(resp, "UTF-8"))

    # HTTP endpoint :: Input: hostname&ipaddress&testdir&testscript, output: error message or succes confirmation
    def enqueue(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        response_dict = {"success": False, "message": "", "name": "", "test": ""}

        missing = missing_parameters(["hostname", "ipaddress", "testdir", "testscript"], query_components)
        if len(missing) != 0:
            response_dict["message"] = f"missing parameter(s): {missing}"
            self.default_respond(json.dumps(response_dict))
            return

        task = TestTask(
            query_components["hostname"][0],
            query_components["ipaddress"][0],
            query_components["testdir"][0],
            query_components["testscript"][0]
        )

        response_dict["name"] = task.hostname
        response_dict["test"] = task.testscript

        sp = script_path(task)
        if not os.access(sp, os.X_OK):
            response_dict["message"] = f"{sp} does not exist or is not executable."
            self.default_respond(json.dumps(response_dict))
            return

        if not all([t[2] for t in testList.checks if t[0] == task.testdir and t[1] == task.testscript]):
            response_dict["message"] = f"{sp} is not allowed to be queued."
            self.default_respond(json.dumps(response_dict))
            return

        if task in fullQ():
            response_dict["message"] = f"{task.testscript} for {task.hostname} is already in the queue."
            self.default_respond(json.dumps(response_dict))
            return

        # If all else is well, enqueue the test script and subtract an attempts credit for this student.
        global REGISTER
        with REGISTER_LOCK:
            if task.hostname not in REGISTER:
                response_dict["message"] = f"Not adding {task.testscript} to Q, hostname invalid"
            elif REGISTER[task.hostname] <= 0:
                response_dict["message"]\
                    = f"No attempts remaining for today."
            else:
                response_dict["message"] = "Added to queue."
                response_dict["success"] = True
                Q.put(task)
                REGISTER[task.hostname] -= 1

        print(f"Web server done handling request, response: {response_dict}.")
        self.default_respond(json.dumps(response_dict))

    # HTTP endpoint :: Input: nothing, output: the attempts register
    def attempts(self):
        global REGISTER
        with REGISTER_LOCK:
            resp = json.dumps(REGISTER)
        self.default_respond(resp)

    # HTTP endpoint :: Input: nothing, output: the fullQ
    def queue(self):
        tasks = fullQ()
        q = [dataclasses.asdict(t) for t in tasks]
        q = sqlite_adapter.avg_durations(q)
        resp = json.dumps(q)
        self.default_respond(resp)

    # HTTP endpoint :: Input: nothing, output: max amount of attempts
    def defaultattempts(self):
        self.default_respond(str(queue_config.tests_perday_perstudent))

    # HTTP endpoint :: Input: a specific task, output: error or success message
    def remove(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        response_dict = {"success": False, "message": ""}

        missing = missing_parameters(["hostname", "ipaddress", "testdir", "testscript"], query_components)
        if len(missing) != 0:
            response_dict["message"] = f"missing parameter(s): {missing}"
            self.default_respond(json.dumps(response_dict))
            return

        task_toremove = TestTask(
            query_components["hostname"][0],
            query_components["ipaddress"][0],
            query_components["testdir"][0],
            query_components["testscript"][0]
        )

        if not Q.try_remove(task_toremove):
            response_dict["success"] = False
            response_dict["message"] = f"Task {task_toremove.testscript} for {task_toremove.hostname} is not waiting in the queue, it might be running under a worker right now."
            self.default_respond(json.dumps(response_dict))
            return

        response_dict["success"] = True
        response_dict["message"] = f"Task {task_toremove.testscript} for {task_toremove.hostname} will be removed from the queue."
        self.default_respond(json.dumps(response_dict))

    def do_GET(self):
        if self.path.startswith("/enqueue"):
            self.enqueue()
        elif self.path.startswith("/queue"):
            self.queue()
        elif self.path.startswith("/attempts"):
            self.attempts()
        elif self.path.startswith("/defaultattempts"):
            self.defaultattempts()
        elif self.path.startswith("/remove"):
            self.remove()
        else:
            r = json.dumps({"success": False, "message": f"endpoint {self.path} does not exist"})
            self.default_respond(r)

    def log_message(self, format, *args):
        # Fix wierd bug that occurs sometimes where the server thinks he doesn't have .path
        if hasattr(self, 'path') and self.path.startswith("/queue"):
            pass
        else:
            print(f"{self.address_string()} :: {args}")

if __name__ == '__main__':
    for wid in range(queue_config.concurrent_workers):
        threading.Thread(target=queue_worker, args=(wid,), daemon=True).start()

    threading.Thread(target=control_socket, daemon=True).start()

    httpd = HTTPServer((queue_config.host_name, queue_config.port_number), NQServer)
    print(f"Server UP at {queue_config.host_name}:{queue_config.port_number}.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(f"Server DOWN at {queue_config.host_name}:{queue_config.port_number}.")


