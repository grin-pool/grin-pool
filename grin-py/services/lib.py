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

import sys
import time
import configparser
import logging
import threading
from datetime import datetime


from grinbase.constants.MysqlConstants import MysqlConstants
from grinbase.dbaccess import database
from grinbase.dbaccess.database import database_details

LOGGER = None
CONFIG = None

def get_config():
    global CONFIG
    rlock = threading.RLock()
    with rlock:
        if CONFIG == None:
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
            log_dir = config[program]["log_dir"]
            log_level = config[program]["log_level"]

            logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
            l = logging.getLogger()

            fileHandler = logging.FileHandler("{0}/{1}.log".format(log_dir, program))
            fileHandler.setFormatter(logFormatter)
            fileHandler.setLevel(log_level)
            l.addHandler(fileHandler)

            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            consoleHandler.setLevel(log_level)
            l.addHandler(consoleHandler)
            LOGGER = l
        return LOGGER


def get_db_constraints():
    config = get_config()
    db_host = config["db"]["address"] + ":" + config["db"]["port"]
    db_user = config["db"]["user"]
    db_password = config["db"]["password"]
    db_name = config["db"]["db_name"]
    mysqlcontsraints = MysqlConstants(db_host, db_user, db_password, db_name)
    return mysqlcontsraints

def get_db():
    rlock = threading.RLock()
    with rlock:
        if database.db is None:
            mysqlcontsraints = get_db_constraints()
            database.db = database_details(MYSQL_CONSTANTS=mysqlcontsraints)
            database.db.initialize()
    database.db.initializeSession()
    return database

def to_sqltimestamp(s_timestamp):
    year = str(datetime.today().year)
    tm = datetime.strptime(s_timestamp, '%b %d %H:%M:%S.%f')
    sql_timestamp = year + "-" + tm.strftime("%m-%d %H:%M:%S")
    return sql_timestamp

