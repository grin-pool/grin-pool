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

# Watches the pool logs and adds the records for pool shares:
#   pool log -> pool_shares: height, nonce, *user_address*, *expected_difficulty*

import sys
import subprocess
import threading
import re
import glob
import time

from grinlib import lib
from grinbase.model.pool_shares import Pool_shares

PROCESS = "shareWatcher"
LOGGER = None
CONFIG = None

# Looking for share messages matching:  "Accepted share at height {} with nonce {} with difficulty {} from worker {}"
def process_pool_logmessage(line, database):
    global LOGGER
    # Looking for: "Jun 05 15:15:43.658 WARN Grin Pool - Got share at height 98029 with nonce 13100465979295287452 with difficulty 1 from worker http://192.168.1.102:13415"
    if line.find('Got share at height') >= 0:
        match = re.search(
            r'^(.+) WARN .+ Got share at height (\d+) with nonce (\d+) with difficulty (\d+) from worker (.+)$',
            line)
        s_timestamp = match.group(1)
        s_height = int(match.group(2))
        s_nonce = match.group(3)
        s_difficulty = int(match.group(4))
        s_worker = match.group(5)
        # Create a new record
        # sql_timestamp = lib.to_sqltimestamp(s_timestamp)
        new_pool_share = Pool_shares(height=s_height, nonce=s_nonce, worker_difficulty=s_difficulty, timestamp=s_timestamp, found_by=s_worker, validated=False, is_valid=False, invalid_reason="None" )
        duplicate = database.db.createDataObj_ignore_duplicates(new_pool_share)
        database.db.getSession().commit()
        if duplicate:
            LOGGER.warn("Duplicate PoolShare: {}".format(new_pool_share))
        else:
            LOGGER.warn("Added PoolShare: {}".format(new_pool_share))
        sys.stdout.flush()


def process_pool_log():
    global LOGGER
    global CONFIG
    # Connect to DB
    database = lib.get_db()

    POOL_LOG = CONFIG["stratum"]["log_dir"] + "/" + CONFIG["stratum"]["log_filename"]

    # (re)Process all logs
    logfiles = glob.glob(POOL_LOG + '*')
    LOGGER.warn("Processing existing logs: {}".format(logfiles))
    sys.stdout.flush()
    for logfile in logfiles:
        with open(logfile) as f:
            for line in f:
                try:
                    process_pool_logmessage(line, database)
                except Exception as e:
                    LOGGER.error("Failed to process pool log message: {} {}".format(line, e))
        f.close()

    # Read future log messages
    LOGGER.warn("Processing new logs: {}".format(POOL_LOG))
    sys.stdout.flush()
    poollog = subprocess.Popen(
        ['tail', '-F', POOL_LOG],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    while True:
        line = poollog.stdout.readline().decode('utf-8')
        try:
            process_pool_logmessage(line, database)
        except Exception as e:
            LOGGER.error("Failed to process pool log message: {} {}".format(line, e))


def main():
    global LOGGER
    global CONFIG
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    # XXX TODO:  Kubernetes does not always get the volume mounted before the processes start
    # maybe need a loop waiting on it
    process_pool_log()


if __name__ == "__main__":
    main()
