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

# Get the payment estimate records from REDIS and generate a report


import sys
import json
import pickle
import pprint
import traceback

from grinbase.dbaccess import database
from grinbase.model.pool_blocks import Pool_blocks

from grinlib import lib
from grinlib import pool

PROCESS = "paymentReport"
LOGGER = None
CONFIG = None

NUM_BLOCKS = 2500

def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    # Connect to DB
    database = lib.get_db()
    database.db.initializeSession()

    pp = pprint.PrettyPrinter(indent=4)

    # Fetch and print pool block reward estimates for latest N pool blocks
    try:
        pool_blocks = Pool_blocks.get_latest(NUM_BLOCKS)
        pool_blocks_h = [blk.height for blk in pool_blocks]
        LOGGER.warn("Will report estimates for pool blocks: {}".format(pool_blocks_h))

        # Print Estimate
        for height in pool_blocks_h:
            pp.pprint("Eestimate for block: {}".format(height))
            payout_map = pool.get_block_payout_map_estimate(height, LOGGER)
            pp.pprint(payout_map)
    except Exception as e:  # AssertionError as e:
        LOGGER.error("Something went wrong: {} - {}".format(e, traceback.print_stack()))
    
        LOGGER.warn("=== Completed {}".format(PROCESS))

if __name__ == "__main__":
    main()
