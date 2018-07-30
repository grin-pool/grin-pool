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

# Add a pool stats record ~per block


import sys
import requests
import json
from time import sleep

from grinbase.dbaccess import database

from grinlib import lib
from grinlib import network
from grinbase.model.blocks import Blocks
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.pool_shares import Pool_shares
from grinbase.model.pool_blocks import Pool_blocks

PROCESS = "poolStats"
LOGGER = None
CONFIG = None

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
    latest_stat = Pool_stats.get_latest()
    
    if latest_stat == None:
        # Special case for new pool startup
        seed_stat = Pool_stats(height=0, timestamp=0, gps=0, active_miners=0, shares_processed=0, total_shares_processed=0, total_grin_paid=0, total_blocks_found=0)
        database.db.createDataObj(seed_stat)
    else:
        last_height = latest_stat.height
    LOGGER.warn("Starting at block height: {}".format(last_height))


    # Generate status records - one per grin block
    while True:
        latest = network.get_current_height()
        # LOGGER.warn("Latest Network Block Height = {}".format(latest))
        while latest > last_height:
            try:
                # Get the most recent pool data from which to generate the stats
                current_height = last_height+1
                avg_over_first_grin_block = Blocks.get_by_height(current_height-avg_over_range)
                grin_block = Blocks.get_by_height(current_height)
                # LOGGER.warn("Working on block: {}".format(grin_block))
                latest_pool_shares = Pool_shares.get_range_by_height(current_height-avg_over_range, current_height)
                if avg_over_first_grin_block == None or grin_block == None:
                    # We dont have enough data in the DB.  If we are filling in historical data
                    # then just move on, otherwise wait and try again
                    if last_height < latest:
                        LOGGER.warn("Skipped stats for height {}".format(last_height))
                        last_height = last_height + 1
                    continue
                latest_stat = Pool_stats.get_latest()
                # Fill in the stats
                height = grin_block.height
                timestamp = grin_block.timestamp
                difficulty = 29 # Pools Difficulty
                gps = 0
                if len(latest_pool_shares) > 0:
                    # LOGGER.warn("Working with shares: height={} - height={}, count={}".format(latest_pool_shares[0].height, latest_pool_shares[-1].height, len(latest_pool_shares)))
                    gps = network.calculate_graph_rate(difficulty, avg_over_first_grin_block.timestamp, grin_block.timestamp, len(latest_pool_shares))
                active_miners = 1 # XXX TODO
                shares_processed = Pool_shares.get_count_by_height(current_height)
                total_shares_processed = Pool_shares.count() # XXX TODO - only count up to last_height
                total_grin_paid = latest_stat.total_grin_paid # XXX TODO
                total_blocks_found = Pool_blocks.count() # XXX TODO - only count up to last_height
                new_stats = Pool_stats(
                                   height = height,
                                   timestamp = timestamp,
                                   gps = gps,
                                   active_miners = active_miners,
                                   shares_processed = shares_processed,
                                   total_shares_processed = total_shares_processed,
                                   total_grin_paid = total_grin_paid,
                                   total_blocks_found = total_blocks_found,
                )
                LOGGER.warn("Added Pool_stats for block: {} - {} {} {} {} {} {}".format(new_stats.height, new_stats.gps, new_stats.active_miners, new_stats.shares_processed, new_stats.total_shares_processed, new_stats.total_grin_paid, new_stats.total_blocks_found))
                database.db.createDataObj(new_stats)
                last_height = last_height + 1
            except Exception as e:
                LOGGER.error("Something went wrong: {}".format(e))
        sys.stdout.flush()
        sleep(check_interval)
    LOGGER.warn("=== Completed {}".format(PROCESS))


if __name__ == "__main__":
    main()
