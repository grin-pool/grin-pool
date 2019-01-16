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

import sys
import time
import traceback

# so hard...
import pprint
pp = pprint.PrettyPrinter(indent=4)


from grinlib import lib
from grinlib import pool
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_shares import Worker_shares
from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.worker_stats import Worker_stats

# NOTE:  All calculations are in nanogrin
# XXX TODO: Get from config
PPLNS_WINDOW = 60 # blocks

PROCESS = "paymentMaker"
LOGGER = None

def main():
    global LOGGER
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    # Connect to DB
    database = lib.get_db()

    # XXX All in one db transaction....
    # Get unlocked blocks from the db
    unlocked_blocks = Pool_blocks.get_all_unlocked()
    unlocked_blocks = [blk.height for blk in unlocked_blocks]
    for height in unlocked_blocks:
        try:
            LOGGER.warn("Processing unlocked block: {}".format(height))
            # Call the library routine to get this blocks payout map
            payout_map = pool.calculate_block_payout_map(height, PPLNS_WINDOW, LOGGER, False)
            #print("payout_map = {}".format(payout_map))
            # Make payments based on the workers total share_value
            Pool_blocks.setState(height, "paid")
            database.db.getSession().commit()
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
            LOGGER.error("Something went wrong: {} - {}".format(e, traceback.print_exc()))

    LOGGER.warn("=== Completed {}".format(PROCESS))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
