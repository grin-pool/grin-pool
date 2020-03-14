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

# Checks blocks found by the pool to see if they are ready to be unlocked and made available for payout.
#

#paymentMaker.py gets unlocked blocks from the pool_blocks table,
#    For each unlocked pool_block:
#        gets worker shares for the past X blocks,
#        Caclulate this workers share of the rewards
#        Add to the pool_utxo

import os
import sys
import time
import traceback

from grinlib import lib
from grinlib import pool
from grinlib import grin
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_shares import Worker_shares
from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.worker_stats import Worker_stats
from grinbase.model.pool_credits import Pool_credits

# NOTE:  All calculations are in nanogrin

PROCESS = "paymentMaker"
LOGGER = None
CONFIG = None

def main():
    global LOGGER
    global CONFIG
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    # Get Config settings
    pool_fee = float(CONFIG[PROCESS]["pool_fee"])
    # Number of blocks of share data used to calculate rewards
    PPLNG_WINDOW_SIZE = 60
    try:
        PPLNG_WINDOW_SIZE = int(os.environ["PPLNG_WINDOW_SIZE"])
    except Exception as e:
        LOGGER.error("Failed to get PPLNG_WINDOW_SIZE from the environment: {}  Using default size of {}".format(e, PPLNG_WINDOW_SIZE))

    # Connect to DB
    database = lib.get_db()

    # Get current blockchain height
    chain_height = grin.blocking_get_current_height()

    # Get unlocked blocks from the db
    unlocked_blocks = Pool_blocks.get_all_unlocked()
    unlocked_blocks = [blk.height for blk in unlocked_blocks]
    LOGGER.warn("Paying for {} pool blocks: {}".format(len(unlocked_blocks), unlocked_blocks))
    for height in unlocked_blocks:
        try:
            LOGGER.warn("Processing unlocked block: {}".format(height))
            # Call the library routine to get this blocks payout map
            payout_map = pool.calculate_block_payout_map(height, PPLNG_WINDOW_SIZE, pool_fee, LOGGER, False)
            #print("payout_map = {}".format(payout_map))
            # Store the payment map for this block
            credits_record = Pool_credits(chain_height, height, payout_map)
            database.db.getSession().add(credits_record)
            # Make payments based on the workers total share_value
            Pool_blocks.setState(height, "paid")
            for user_id, payment_amount in payout_map.items():
                    # Add worker rewards to pool account balance
                    LOGGER.warn("Credit to user: {} = {}".format(user_id, payment_amount))
                    worker_utxo = Pool_utxo.credit_worker(user_id, payment_amount)
                    # Worker_stats accounting and running totals
                    #latest_worker_stats = Worker_stats.get_latest_by_id(user_id)
                    #latest_worker_stats.dirty = True
            database.db.getSession().commit()
            
        except Exception as e:
            database.db.getSession().rollback()
            LOGGER.exception("Something went wrong: {}".format(repr(e)))

    LOGGER.warn("=== Completed {}".format(PROCESS))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
