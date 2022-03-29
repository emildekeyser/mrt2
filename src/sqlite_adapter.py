#                  ___         __              
#                 /\_ \    __ /\ \__           
#    ____     __  \//\ \  /\_\\ \ ,_\     __   
#   /',__\  /'__`\  \ \ \ \/\ \\ \ \/   /'__`\ 
#  /\__, `\/\ \L\ \  \_\ \_\ \ \\ \ \_ /\  __/ 
#  \/\____/\ \___, \ /\____\\ \_\\ \__\\ \____\
#   \/___/  \/___/\ \\/____/ \/_/ \/__/ \/____/
#                \ \_\                         
#                 \/_/                         

################################################################################

# Provides write_all_sql(...) which is used by run_tests_v2.py to archive test
# attempts and avg_durations(...) which is used by queue_server.py to provide
# estimated durations in the /queue endpoint.

################################################################################

import sqlite3
from sqlite3 import Error
import os
import datetime

import queue_config

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def sql_ins(conn, task):
    c = conn.cursor()
    c.execute(task)
    conn.commit()

def sql_execute(conn, task):
    try:
        c = conn.cursor()
        c.execute(task)
    except Error as e:
        print(e)

def write_SQLLight(isotimestamp, duration, host, vmid, testdir, testscript, output):
    database = queue_config.dbfile
    duration = duration.total_seconds()
    isotimestamp =  isotimestamp.astimezone().isoformat(timespec='microseconds')

    sql_create_log_table = """ CREATE TABLE IF NOT EXISTS logs (
                                        timestamp text NOT NULL,
                                        duration text NOT NULL,
                                        host text NOT NULL,
                                        vmid text NOT NULL, 
                                        testdir text NOT NULL,
                                        testscript text NOT NULL,
                                        output text NOT NULL
                                    ); """

    sql_insert =  f""" INSERT INTO logs(timestamp, duration, host, vmid, testdir, testscript, output)
              VALUES("{isotimestamp}","{duration}","{host}","{vmid}","{testdir}","{testscript}","{output}") """

    conn = create_connection(database)
    if conn is not None:
        sql_execute(conn, sql_create_log_table)
        sql_ins(conn,sql_insert)
    else:
        print("Error! cannot create the database connection.")

def write_all_sql(testresults):
    database = queue_config.dbfile

    sql_create_log_table = """ CREATE TABLE IF NOT EXISTS logs (
                                        timestamp text NOT NULL,
                                        duration text NOT NULL,
                                        host text NOT NULL,
                                        vmid text NOT NULL, 
                                        testdir text NOT NULL,
                                        testscript text NOT NULL,
                                        output text NOT NULL
                                    ); """

    lines = ['("' + '", "'.join(result) + '")' for result in testresults]
    sql_insert = "INSERT INTO logs VALUES " \
        + ",".join(lines) \
        + ";"

    conn = create_connection(database)
    if conn is not None:
        sql_execute(conn, sql_create_log_table)
        sql_ins(conn,sql_insert)
    else:
        print("Error! cannot create the database connection.")

def avg_durations(tasks):
    if not os.path.exists(queue_config.dbfile) or tasks == []:
        return tasks

    hosts = ", ".join(['"' + t['hostname'] + '"' for t in tasks])
    dirs = ", ".join(['"' + t['testdir'] + '"' for t in tasks])
    scripts = ", ".join(['"' + t['testscript'] + '"' for t in tasks])

    (y, m, d) = queue_config.start_avg_range
    start = datetime.datetime(y, m, d).astimezone().isoformat()

    query = f"""select host, testdir, testscript, avg(duration)
                from logs
                where host in ({hosts}) and testdir in ({dirs}) and testscript in ({scripts})
                and timestamp > '{start}'
                group by host, testdir, testscript;
            """

    data = sqlite3 \
        .connect(queue_config.dbfile) \
        .execute(query) \
        .fetchall()

    data = {d[0]+d[1]+d[2] : d[3] for d in data}
    newtasks = []
    for task in tasks:
        concat = task['hostname']+task['testdir']+task['testscript']
        task['expected_duration'] = data.get(concat, 0)
    return tasks
