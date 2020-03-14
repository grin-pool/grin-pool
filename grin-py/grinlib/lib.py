#!/usr/bin/python

# Copyright 2018 Blade M. Doyle
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Common Routines for Grin-Pool Services
#

import os
import sys
import time
import configparser
import logging
import logging.handlers
import redis
import threading
import subprocess
from datetime import datetime


from grinbase.constants.MysqlConstants import MysqlConstants
from grinbase.dbaccess import database
from grinbase.dbaccess.database import database_details

from grinbase.model.blocks import Blocks


# XXX TODO: Get from config
REDIS_HOST = "redis-master"
MINIMUM_DIFFICULTY = 1
HF0_HEIGHT = 0

LOGGER = None
CONFIG = None
DATABASE = None
REDIS = None

def get_config():
    global CONFIG
    rlock = threading.RLock()
    with rlock:
        if CONFIG == None:
            print("Init new CONFIG")
            if not os.path.isfile('config.ini'):
                from shutil import copyfile
                copyfile('/usr/local/bin/config.ini', "config.ini")
            c = configparser.ConfigParser()
            c.read('config.ini')
            CONFIG = c
        return CONFIG

# Log to both stdout and the log file
def get_logger(program):
    global LOGGER
    rlock = threading.RLock()
    with rlock:
        if LOGGER == None:
            config = get_config()
            try:
                log_dir = config[program]["log_dir"]
                log_level = config[program]["log_level"]
            except:
                log_dir = "./"
                log_level = "WARNING"

            logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
            l = logging.getLogger()

            logfilename = "{0}/{1}.log".format(log_dir, program)

            fileHandler = logging.FileHandler(logfilename)
            fileHandler.setFormatter(logFormatter)
            fileHandler.setLevel(log_level)
            l.addHandler(fileHandler)

            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            consoleHandler.setLevel(log_level)
            l.addHandler(consoleHandler)

            rotationHandler = logging.handlers.RotatingFileHandler(
                    filename = logfilename,
                    mode = "a",
                    maxBytes = 100000000,
                    backupCount = 3,
                )
            l.addHandler(rotationHandler)

            LOGGER = l
        return LOGGER

def get_debug():
    try:
        debug = os.environ["DEBUG"]
        return True
    except:
        return False

def get_db_constraints():
    config = get_config()
    print("config: {}".format(config))
    db_host = config["db"]["address"] + ":" + config["db"]["port"]
    db_user = config["db"]["user"]
    try:
        db_password = os.environ['MYSQL_ROOT_PASSWORD']
    except KeyError as e:
        db_password = config["db"]["password"]
    db_name = config["db"]["db_name"]
    mysqlcontsraints = MysqlConstants(db_host, db_user, db_password, db_name)
    return mysqlcontsraints

def get_db():
    global DATABASE 
    rlock = threading.RLock()
    with rlock:
        if DATABASE is None:
            print("INIT DB")
            mysqlcontsraints = get_db_constraints()
            database.db = database_details(MYSQL_CONSTANTS=mysqlcontsraints)
            database.db.initialize()
            try:
                GRIN_POOL_ADMIN_USER = os.environ['GRIN_POOL_ADMIN_USER']
                GRIN_POOL_ADMIN_PASSWORD = os.environ['GRIN_POOL_ADMIN_PASSWORD']
                from grinbase.model.users import Users
                try:
                    user = Users.get_by_id(1)
                    if user is None:
                        user = Users(
                                id = 1,
                                username = GRIN_POOL_ADMIN_USER,
                                password = GRIN_POOL_ADMIN_PASSWORD,
                            )
                        database.db.createDataObj(user)
                except:
                    pass
            except KeyError:
                pass
            DATABASE = database
    DATABASE.db.initializeSession()
    return DATABASE

def teardown_db():
    global database
    database.db.destroySession()

def get_redis_db():
    global REDIS
    rlock = threading.RLock()
    with rlock:
        if REDIS == None:
            print("Init new REDIS")
            r = redis.Redis(
                    host='redis-master',
                    socket_timeout=10.0,
                    socket_connect_timeout=10.0,
            )
            REDIS = r
        return REDIS

def get_grin_api_url():
    config = get_config()
    grin_api_url = "http://" + config["grin_node"]["address"] + ":" + config["grin_node"]["api_port"]
    return grin_api_url


# Network chain height
def get_current_height():
    config = get_config()
    grin_api_url = "http://" + config["grin_node"]["address"] + ":" + config["grin_node"]["api_port"]
    status_url = grin_api_url + "/v1/status"
    response = requests.get(status_url)
    latest = response.json()["tip"]["height"]
    # XXX TODO:  Validate somehow?
    return latest

# Worker graph rate
# Calculate GPS from N shares submitted over time range
def calculate_graph_rate(ts1, ts2, n, sz, height):
    timedelta = (ts2 - ts1).total_seconds()
    print("Calculate gps: timedelta: {}, num_shares: {}, size: {}".format(timedelta, n, sz))
    if n == 0 or timedelta == 0:
      return 0
    factor = 42
    if sz == 29 and height > HF0_HEIGHT:
        factor = 21
    gps = (float(factor) * float(MINIMUM_DIFFICULTY) * float(n)) / float(timedelta)
    return gps

# Workers shares rate
# Calcualte Shares per Second from GPS
def calculate_shares_from_gps(gps, sz, height):
    factor = 42
    if sz == 29 and height > HF0_HEIGHT:
        factor = 21
    return gps/float(factor)

# API 'fields' string to python list
def fields_to_list(fields):
    if fields != None:
        # Split the fields elements into an array
        fields = fields.translate({ord(c): None for c in '[]'})
        fields = fields.split(',')
    return fields

# Python datetime.datetime into a unix epoch
def to_epoch(dt):
    return dt.timestamp()

# Itr for tailing a log file
class PopenItr:
    def __init__(self, command):
        self.cmd = command
        self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)

    def __iter__(self):
        return self

    def __next__(self):
        line = self.proc.stdout.readline().decode('utf-8')
        if line == '' and self.proc.poll() is not None:
            raise StopIteration
        return line

