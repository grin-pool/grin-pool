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

# Watches both the pool and grin logs and adds the records from each to separate tables:
#   pool log -> pool_shares: height, nonce, *user_address*, *expected_difficulty*
#   grin log -> grin_shares: height, nonce, *share_difficulty*
# Adds shares to *grin_shares* and *pool_shares* tables
# Adds pool solved blocks to *pool_blocks* table

import sys
import subprocess
import threading
import re
import glob
import time
import lib
from grinbase.model.pool_shares import Pool_shares
from grinbase.model.grin_shares import Grin_shares
from grinbase.model.pool_blocks import Pool_blocks

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
        sql_timestamp = lib.to_sqltimestamp(s_timestamp)
        new_pool_share = Pool_shares(height=s_height, nonce=s_nonce, worker_difficulty=s_difficulty, timestamp=sql_timestamp, found_by=s_worker, validated=False, is_valid=False, invalid_reason="None" )
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
                    LOGGER.error("Failed to process log message: {}".format(e))
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
            LOGGER.error("Failed to process log message: {}".format(e))


# Looking for share messages
# Add them to the grin_shares table
def process_grin_logmessage(line, database):
    global LOGGER
    # Looking for: "Jun 07 02:07:48.470 INFO (Server ID: StratumServer) Got share for block: hash 1a4480ad, height 99845, nonce 14139347905838955360, difficulty 9/1, submitted by 192.168.2.100:13415"
    if "Got share for block:" in line:
        match = re.search(
            r'^(.+) INFO .+ Got share for block: hash (.+), height (\d+), nonce (\d+), difficulty (\d+)/(\d+), submitted by (.+)$',
            line)
        s_timestamp = match.group(1)
        s_hash = match.group(2)
        s_height = int(match.group(3))
        s_nonce = match.group(4)
        s_share_difficulty = int(match.group(5))
        s_network_difficulty = int(match.group(6))
        s_worker = match.group(7)

        sql_timestamp = lib.to_sqltimestamp(s_timestamp)
        if s_share_difficulty >= s_network_difficulty:
            share_is_solution = True
        else:
            share_is_solution = False

        # Create a new record
        new_grin_share = Grin_shares(hash=s_hash, height=s_height, nonce=s_nonce, actual_difficulty=s_share_difficulty, net_difficulty=s_network_difficulty, timestamp=sql_timestamp, found_by=s_worker, is_solution=share_is_solution)
        duplicate = database.db.createDataObj_ignore_duplicates(new_grin_share)
        database.db.getSession().commit()
        if duplicate:
            LOGGER.warn("Duplicate GrinShare: {}".format(new_grin_share))
        else:
            LOGGER.warn("Added GrinShare: {}".format(new_grin_share))

        # If this is a full solution found by us, also add it as a pool block
        if s_share_difficulty >= s_network_difficulty:
            new_pool_block = Pool_blocks(hash=s_hash, height=s_height, nonce=s_nonce, actual_difficulty=s_share_difficulty, net_difficulty=s_network_difficulty, timestamp=sql_timestamp, found_by=s_worker, state="new")
            duplicate = database.db.createDataObj_ignore_duplicates(new_pool_block)
            database.db.getSession().commit()
            if duplicate:
                LOGGER.warn("Duplicate Pool Block: {}".format(new_pool_block))
            else:
                LOGGER.warn("Added Pool Block: {}".format(new_pool_block))
        sys.stdout.flush()


def process_grin_log():
    global LOGGER
    global CONFIG
    # Connect to DB
    database = lib.get_db()

    GRIN_LOG = CONFIG["grin_node"]["log_dir"] + "/" + CONFIG["grin_node"]["log_filename"]

    # (re)Process all logs
    logfiles = glob.glob(GRIN_LOG + '*')
    LOGGER.warn("Processing existing logs: {}".format(logfiles))
    sys.stdout.flush()
    for logfile in logfiles:
        with open(logfile) as f:
            for line in f:
                process_grin_logmessage(line, database)
        f.close()

    # Read future log messages
    LOGGER.warn("Processing new logs: {}".format(GRIN_LOG))
    sys.stdout.flush()
    grinlog = subprocess.Popen(
        ['tail', '-F', GRIN_LOG],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    while True:
        line = grinlog.stdout.readline().decode('utf-8')
        try:
            process_grin_logmessage(line, database)
        except Exception as e:
            LOGGER.error("Failed to process log message: {}".format(e))



def main():
    global LOGGER
    global CONFIG
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    # XXX TODO:  Kubernetes does not always get the volume mounted before the processes start
    # maybe need a loop waiting on it
    # XXX TODO:  Need to handle the case where one thread dies but the other lives - probably
    # want to to exit with error status if both threads are not healthy
    t_pool = threading.Thread(name='PoolShareWatcher', target=process_pool_log)
    t_grin = threading.Thread(name='GrinShareWatcher', target=process_grin_log)
    t_pool.start()
    t_grin.start()
    t_pool.join()
    t_grin.join()


if __name__ == "__main__":
    main()

