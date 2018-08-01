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

# Watches the grin logs and adds records for grin shares and accepted pool blocks:
#   grin log -> grin_shares: height, nonce, *share_difficulty*
# Adds shares to *grin_shares*
# Adds pool solved blocks to *pool_blocks* table

import sys
import subprocess
import threading
import re
import glob
import datetime

from grinlib import lib
from grinbase.model.grin_shares import Grin_shares
from grinbase.model.pool_blocks import Pool_blocks

PROCESS = "shareWatcher"
LOGGER = None
CONFIG = None

# Looking for share messages
# Add them to the grin_shares table
def process_grin_logmessage(line, database):
    global LOGGER
    # Looking for: "Jun 07 02:07:48.470 INFO (Server ID: StratumServer) Got share for block: hash 1a4480ad, height 99845, nonce 14139347905838955360, difficulty 9/1, submitted by 192.168.2.100:13415"
    if "Got share for block:" in line:
        match = re.search(
            r'^(.+) INFO .+ Got share for block: hash (.+), height (\d+), nonce (\d+), difficulty (\d+)/(\d+), submitted by (.+)$',
            line)
        s_timestamp = datetime.datetime.strptime(str(datetime.datetime.now().year) + " " + match.group(1), "%Y %b %d %H:%M:%S.%f")
        s_hash = match.group(2)
        s_height = int(match.group(3))
        s_nonce = match.group(4)
        s_share_difficulty = int(match.group(5))
        s_network_difficulty = int(match.group(6))
        s_worker = match.group(7)

        #sql_timestamp = lib.to_sqltimestamp(s_timestamp)
        if s_share_difficulty >= s_network_difficulty:
            share_is_solution = True
        else:
            share_is_solution = False

        # Create a new record
        new_grin_share = Grin_shares(hash=s_hash, height=s_height, nonce=s_nonce, actual_difficulty=s_share_difficulty, net_difficulty=s_network_difficulty, timestamp=s_timestamp, found_by=s_worker, is_solution=share_is_solution)
        duplicate = database.db.createDataObj_ignore_duplicates(new_grin_share)
        database.db.getSession().commit()
        if duplicate:
            LOGGER.warn("Duplicate GrinShare: {}".format(new_grin_share))
        else:
            LOGGER.warn("Added GrinShare: {}".format(new_grin_share))

        # If this is a full solution found by us, also add it as a pool block
        if s_share_difficulty >= s_network_difficulty:
            new_pool_block = Pool_blocks(hash=s_hash, height=s_height, nonce=s_nonce, actual_difficulty=s_share_difficulty, net_difficulty=s_network_difficulty, timestamp=s_timestamp, found_by=s_worker, state="new")
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
                try:
                    process_grin_logmessage(line, database)
                except Exception as e:
                    LOGGER.error("Failed to process grin log message: {} {}".format(line, e))
                    database.db.getSession().rollback()
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
            LOGGER.error("Failed to process grin log message: {} {}".format(line, e))



def main():
    global LOGGER
    global CONFIG
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    # XXX TODO:  Kubernetes does not always get the volume mounted before the processes start
    # maybe need a loop waiting on it
    process_grin_log()


if __name__ == "__main__":
    main()

