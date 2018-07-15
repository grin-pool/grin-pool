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

LOGGER = None
CONFIG = None

def get_config():
    rlock = threading.RLock()
    with rlock:
        global CONFIG
        if CONFIG == None:
            c = configparser.ConfigParser()
            c.read('/services/config.ini')
            CONFIG = c
        return CONFIG

# Log to both stdout and the log file
def get_logger(program):
    rlock = threading.RLock()
    with rlock:
        global LOGGER
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
