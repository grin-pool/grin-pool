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
import traceback

# so hard...
import pprint
pp = pprint.PrettyPrinter(indent=4)


from grinlib import lib
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_shares import Worker_shares
from grinbase.model.pool_utxo import Pool_utxo

REWARD = 60.0  # XXX TODO: use the actual reward + fees of each block
PPLNS_WINDOW = 60 # blocks

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
            # Get Worker_stats of this block + range to calculate reward for each worker
            worker_shares_window = Worker_shares.get_by_height(pb.height, PPLNS_WINDOW)
            print("worker_shares_window = {}".format(worker_shares_window))
            # Calculate Payment info:
            if len(worker_shares_window) > 0:
                # Calcualte reward/share:
                # XXX TODO: Enhance
                #  What algorithm to use?  Maybe: https://slushpool.com/help/manual/rewards
                # For now, some variation on pplns

                # Sum up the number of each size share submitted by each user
                shares_count_map = {}
                for worker_shares_rec in worker_shares_window:
                    if not worker_shares_rec.worker in shares_count_map:
                        shares_count_map[worker_shares_rec.worker] = {}
                    for pow_size in worker_shares_rec.sizes():
                        print("pow_size = {}".format(pow_size))
                        if not pow_size in shares_count_map[worker_shares_rec.worker]:
                            shares_count_map[worker_shares_rec.worker][pow_size] = 0
                        shares_count_map[worker_shares_rec.worker][pow_size] += worker_shares_rec.num_valid(pow_size)
                print("Shares Count Map:")
                pp.pprint(shares_count_map)

                # Normalize and sum each workers shares to create a "share value"
                total_value = 0
                for worker, worker_shares_count in shares_count_map.items():
                    print("worker: {}, worker_shares_count: {}".format(worker, worker_shares_count))
                    sizes = list(worker_shares_count.keys())
                    print("sizes: {}".format(sizes))
                    shares_count_map[worker]["value"] = 0
                    value = 0
                    for size, count in worker_shares_count.items():
                        if size == 29:
                            value += float(count) * .33
                        else:
                            value += float(count)
                        total_value += value
                    shares_count_map[worker]["value"] = value
                    print("Worker {} value: {}".format(worker, value))
                
                # Make payments based on the workers total share_value
                for worker, worker_shares_count in shares_count_map.items():
                    worker_rewards = REWARD * worker_shares_count["value"] / total_value
                    # Add or create worker rewards
                    worker_utxo = Pool_utxo.credit_worker(worker, worker_rewards)
                    LOGGER.warn("Credit to user: {} = {}".format(worker, worker_rewards))
            # Mark the pool_block state="paid" (maybe "processed" would be more accurate?)
            pb.state = "paid"
            database.db.getSession().commit()
        except Exception as e:
            database.db.getSession().rollback()
            LOGGER.error("Something went wrong: {} - {}".format(e, traceback.print_exc()))

    #database.db.getSession().commit()
    LOGGER.warn("=== Completed {}".format(PROCESS))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
