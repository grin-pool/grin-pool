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


import os
import sys
import requests
import json
import atexit
from time import sleep
import traceback


from grinbase.dbaccess import database

from grinlib import lib
from grinlib import pool

from grinbase.model.blocks import Blocks
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_shares import Worker_shares

PROCESS = "paymentEstimator"
LOGGER = None
CONFIG = None

# XXX TODO - Get from config
check_interval = 60
cache_expire = 60*60*24*31   # 1 month
key_prefix = "payout-estimate-for-block-"

def main():
    global CONFIG
    global LOGGER
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    # Number of blocks of share data used to calculate rewards
    PPLNG_WINDOW_SIZE = 60
    try:
        PPLNG_WINDOW_SIZE = int(os.environ["PPLNG_WINDOW_SIZE"])
    except Exception as e:
        LOGGER.error("Failed to get PPLNG_WINDOW_SIZE from the environment: {}.  Using default size of {}".format(e, PPLNG_WINDOW_SIZE))

    POOL_FEE = 0.0075
    try:
        POOL_FEE = float(CONFIG[PROCESS]["pool_fee"])
    except Exception as e:
        LOGGER.error("Failed to get POOL_FEE from the config: {}.  Using default fee of {}".format(e, POOL_FEE))

    # Keep track of "next" block estimated
    next_height_estimated = 0

    # Connect to DB
    database = lib.get_db()

    while True:
        # Generate pool block reward estimates for all new and unlocked blocks
        try:
            database.db.initializeSession()
            next_height = Blocks.get_latest().height - 5 # A recent height which all worker shares are available
            unlocked_blocks = Pool_blocks.get_all_unlocked()
            new_blocks = Pool_blocks.get_all_new()
            unlocked_blocks_h = [blk.height for blk in unlocked_blocks]
            new_blocks_h = [blk.height for blk in new_blocks]

            need_estimates = unlocked_blocks_h + new_blocks_h
            LOGGER.warn("Will ensure estimate for blocks: {}".format(need_estimates))
            redisdb = lib.get_redis_db()

            # Generate Estimate
            for height in need_estimates:
                if height > next_height:
                    LOGGER.warn("Delay estimate until we have recent shares availalbe for block: {}".format(height))
                else:
                    LOGGER.warn("Ensure estimate for block: {}".format(height))
                    # Check if we already have an estimate cached
                    payout_estimate_map_key = key_prefix + str(height) 
                    cached_map = redisdb.get(payout_estimate_map_key)
                    if cached_map is None:
                        # We dont have it cached, we need to calcualte it and cache it now
                        payout_map = pool.calculate_block_payout_map(height, PPLNG_WINDOW_SIZE, POOL_FEE, LOGGER, True)
                        payout_map_json = json.dumps(payout_map)
                        redisdb.set(payout_estimate_map_key, payout_map_json, ex=cache_expire)
                        LOGGER.warn("Created estimate for block {} with key {}".format(height, payout_estimate_map_key))
                    else:
                        LOGGER.warn("There is an exiting estimate for block: {}".format(height))

            # Generate estimate for "next" block
            LOGGER.warn("Ensure estimate for next block: {}".format(next_height))
            if next_height_estimated != next_height:
                payout_map = pool.calculate_block_payout_map(next_height, PPLNG_WINDOW_SIZE, POOL_FEE, LOGGER, True)
                payout_map_json = json.dumps(payout_map)
                payout_estimate_map_key = key_prefix + "next"
                redisdb.set(payout_estimate_map_key, payout_map_json, ex=cache_expire)
                next_height_estimated = next_height
                LOGGER.warn("Created estimate for block {} with key {}".format(next_height, payout_estimate_map_key))
            else:
                LOGGER.warn("There is an exiting next block estimate for : {}".format(next_height))
                

            LOGGER.warn("Completed estimates")
            database.db.destroySession()
            # Flush debug print statements
            sys.stdout.flush()
        except Exception as e:  # AssertionError as e:
            LOGGER.error("Something went wrong: {} - {}".format(e, traceback.format_exc()))
            database.db.destroySession()
    
        LOGGER.warn("=== Completed {}".format(PROCESS))
        sleep(check_interval)

if __name__ == "__main__":
    main()
