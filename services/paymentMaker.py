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
#        gets valid worker shares for that block,
#        generates a payment record for each worker
#        deletes share records ?

# XXX TODO: Single db transaction

import sys
import db_api
import time

PROCESS = "paymentMaker"
REWARD = 60.0  # XXX TODO: use the actual reward of each block


def main():
    db = db_api.db_api()
    latest_block = 0

    # XXX All in one db transaction....
    # Get unlocked blocks from the db
    unlocked_blocks = db.get_poolblocks_by_state("unlocked")
    for pb in unlocked_blocks:
        print("unlocked block: {}".format(pb))
        (pb_hash, pb_height, pb_nonce, pb_actual_difficulty, pb_net_difficulty,
         pb_timestamp, pb_found_by, pb_state) = pb
        if pb_height > latest_block:
            latest_block = pb_height
    # Get valid pool_shares for that block from the db
        pool_shares = db.get_valid_poolshares_by_height(pb_height)
        # Calculate Payment info:
        worker_shares = {}
        for ps in pool_shares:
            print("pool_shares: ", format(ps))
            (ps_height, ps_nonce, ps_difficulty, ps_timestamp, ps_found_by,
             ps_validated, ps_is_valid, ps_invalid_reason) = ps
            gs = db.get_grin_share_by_nonce(ps_nonce)
            if gs == None:
                # XXX NOTE: no payout for shares not accepted by grin node
                continue
            (gs_hash, gs_height, gs_nonce, gs_actual_difficulty,
             gs_net_difficulty, gs_timestamp, gs_found_by, gs_state) = gs
            if ps_found_by in worker_shares:
                worker_shares[ps_found_by] += gs_actual_difficulty
            else:
                worker_shares[ps_found_by] = gs_actual_difficulty
        print(worker_shares)
        if len(worker_shares) > 0:
            # Calcualte reward/difficulty: XXX TODO: Enhance
            #  What algorithm to use?  Maybe: https://slushpool.com/help/manual/rewards
            r_per_d = REWARD / sum(worker_shares.values())
            for worker in worker_shares.keys():
                # Calculate reward per share
                worker_rewards = worker_shares[worker] * r_per_d
                # Add or create worker rewards
                # XXX TODO: Batch these
                db.create_or_add_utxo(worker, worker_rewards)
                print("Credit to user: ", worker, worker_rewards)
    # Mark the pool_block state="paid" (maybe "processed" would be more accurate?)
        db.set_poolblock_state("paid", int(pb_height))
    sys.stdout.flush()
    db.set_last_run(PROCESS, str(time.time()))
    db.close()


if __name__ == "__main__":
    main()
