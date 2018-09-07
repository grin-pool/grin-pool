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

# Add a worker stats record for each active user per block


import sys
import requests
import json
from time import sleep
import datetime
import traceback

from grinbase.dbaccess import database

from grinlib import lib
from grinlib import grin
from grinlib import workerstats

from grinbase.model.blocks import Blocks
from grinbase.model.worker_stats import Worker_stats
from grinbase.model.pool_shares import Pool_shares
from grinbase.model.pool_blocks import Pool_blocks

PROCESS = "workerStats"
LOGGER = None
CONFIG = None

# XXX TODO: Move to config
DIFFICULTY = 29
BATCHSZ = 100


def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    # Connect to DB
    database = lib.get_db()

    # Get config
    check_interval = float(CONFIG[PROCESS]["check_interval"])
    avg_over_range = int(CONFIG[PROCESS]["avg_over_range"])

    # Find the height of the latest stats record
    last_height = 0
    latest_stat = Worker_stats.get_latest()
    
    if latest_stat != None:
        last_height = latest_stat.height
    height = last_height + 1
    LOGGER.warn("Starting at block height: {}".format(height))

    # Generate worker stats records - one per grin block for each active worker
    while True:
        latest = grin.blocking_get_current_height()
        #LOGGER.debug("Latest Network Block Height = {}".format(latest))
        while latest >= height:
            try:
                new_stats = workerstats.calculate(height, avg_over_range)
                for stats in new_stats:
                    database.db.getSession().add(stats)
                    if( (height % BATCHSZ == 0) or (height >= (latest-3)) ):
                        database.db.getSession().commit()
                    LOGGER.warn("Added Worker_stats for block: {}, Worker: {} - {} {} {} {} {} {}".format(stats.height, stats.worker, stats.gps, stats.shares_processed, stats.total_shares_processed, stats.grin_paid, stats.total_grin_paid, stats.balance))
                height = height + 1
            except Exception as e:
                LOGGER.error("Something went wrong: {}".format(e))
                LOGGER.error("Traceback: {}".format(traceback.format_exc().splitlines()))
                sleep(check_interval)
        sys.stdout.flush()
        sleep(check_interval)
    LOGGER.warn("=== Completed {}".format(PROCESS))


if __name__ == "__main__":
    main()
