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

from grinbase.dbaccess import database

from grinlib import lib
from grinlib import grin
from grinbase.model.blocks import Blocks
from grinbase.model.worker_stats import Worker_stats
from grinbase.model.pool_shares import Pool_shares
from grinbase.model.pool_blocks import Pool_blocks

PROCESS = "workerStats"
LOGGER = None
CONFIG = None
DIFFICULTY = 29

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
    last_height = 100
    latest_stat = Worker_stats.get_last()
    print("XXX: latest stat: ".format(latest_stat))
    
    if latest_stat != None:
        last_height = latest_stat.height
    LOGGER.warn("Starting at block height: {}".format(last_height))

    last_stat = None


    # Generate worker status records - one per grin block for each active worker
    while True:
        latest = grin.get_current_height()
        # LOGGER.warn("Latest Network Block Height = {}".format(latest))
        while latest > last_height:
            try:
                print("Current Height: {}".format(last_height))
                current_height = last_height+1
                while True:
                    current_grin_block = Blocks.get_by_height(current_height)
                    avg_over_first_grin_block = Blocks.get_by_height(current_height-avg_over_range)
                    if avg_over_first_grin_block is not None and current_grin_block is not None:
                        break;
                    sleep(1)
                    
                # Get the worker share data from which to generate the stats
                #   All shares for all workers for the current range of blocks
                latest_pool_shares = Pool_shares.get_by_height(current_height, avg_over_range)
                # Create a worker_stats for each user who submitted a share in this range
                workers = list(set([share.found_by for share in latest_pool_shares]))
                for worker in workers:
                    print("XXXX: worker:               {}".format(worker))
                    # Get this workers most recent worker_stats record (for running totals)
                    last_stat = Worker_stats.get_last_by_id(worker)
                    print("XXXX: Last Stat:            {}".format(last_stat))
                    if last_stat == None:
                        # Initialize stats for new worker
                        LOGGER.warn("Init new worker: {}".format(worker))
                        last_stat = Worker_stats(0, datetime.datetime.now(), last_height, worker,0,0,0,0,0,0)
                        database.db.createDataObj(last_stat)
                        last_stat = None
                        continue
                    print("XXXX: Final Last Stat:            {}".format(last_stat))
                    # Calculate workers gps over the past n blocks
                    this_worker_shares = [share for share in latest_pool_shares if share.found_by == worker]
                    this_worker_shares_this_block = [share for share in this_worker_shares if share.height == current_height]
                    # print("XXXX: {}".format(this_worker_shares))
                    gps = grin.calculate_graph_rate(DIFFICULTY, avg_over_first_grin_block.timestamp, current_grin_block.timestamp, len(this_worker_shares))
                    
                    shares_processed = len(this_worker_shares_this_block)
                    total_shares_processed = last_stat.total_shares_processed + shares_processed
                    print("XXXX: Shares Processed: {} - {}".format(shares_processed, total_shares_processed))
                    # Create a worker stats record
                    new_stats = Worker_stats(
                                        id = 0,
                                        timestamp = current_grin_block.timestamp,
                                        height = current_grin_block.height,
                                        worker = worker,
                                        gps = gps,
                                        shares_processed = shares_processed,
                                        total_shares_processed = total_shares_processed,
                                        grin_paid = 123,
                                        total_grin_paid = 456,
                                        balance = 1,
                    )
                    LOGGER.warn("Added Worker_stats for block: {}, Worker: {} - {} {} {} {} {} {}".format(new_stats.height, new_stats.worker, new_stats.gps, new_stats.shares_processed, new_stats.total_shares_processed, new_stats.grin_paid, new_stats.total_grin_paid, new_stats.balance))
                    last_stat = None
                    database.db.createDataObj(new_stats)
                    sleep(.01)
                last_height = last_height + 1
                last_stat = None
            except Exception as e:
                LOGGER.error("Something went wrong: {}".format(e))
                raise
        sys.stdout.flush()
        sleep(check_interval)
    LOGGER.warn("=== Completed {}".format(PROCESS))


if __name__ == "__main__":
    main()
