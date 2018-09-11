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
#        gets worker stats for the past X blocks,
#        Caclulate this workers share of the rewards
#        Add to the pool_utxo

# XXX TODO: Single db transaction


import sys
import time

from grinlib import lib
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_stats import Worker_stats
from grinbase.model.pool_utxo import Pool_utxo

REWARD = 60.0  # XXX TODO: use the actual reward + fees of each block

PROCESS = "paymentMaker"
LOGGER = None

def main():
    global LOGGER
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    # Connect to DB
    database = lib.get_db()

    latest_block = 0

    # XXX All in one db transaction....
    # Get unlocked blocks from the db
    unlocked_blocks = Pool_blocks.get_all_unlocked()
    database.db.getSession().commit()
    for pb in unlocked_blocks:
        try:
            LOGGER.warn("Processing unlocked block: {}".format(pb))
            if pb.height > latest_block:
                latest_block = pb.height
            # Get Worker_stats of this block to calculate reward for each worker
            worker_stats = Worker_stats.get_by_height(pb.height)
            # Calculate Payment info:
            if len(worker_stats) > 0:
                # Calcualte reward/share:
                # XXX TODO: Enhance
                #  What algorithm to use?  Maybe: https://slushpool.com/help/manual/rewards
                r_per_g = REWARD / sum([st.gps for st in worker_stats])
                for stat in worker_stats:
                    # Calculate reward
                    worker_rewards = stat.gps * r_per_g
                    # Add or create worker rewards
                    worker_utxo = Pool_utxo.credit_worker(stat.worker, worker_rewards)
                    LOGGER.warn("Credit to user: {} = {}".format(stat.worker, worker_rewards))
            # Mark the pool_block state="paid" (maybe "processed" would be more accurate?)
            pb.state = "paid"
            database.db.getSession().commit()
        except Exception as e:
            database.db.getSession().rollback()
            LOGGER.error("Something went wrong: {}".format(e))

    #database.db.getSession().commit()
    LOGGER.warn("=== Completed {}".format(PROCESS))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
