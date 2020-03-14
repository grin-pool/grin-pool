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

#
# Routines for getting Grin Pool data
#

import os
import sys
import json
import time
import redis
import pprint
import requests
import traceback
import threading

from grinlib import lib
from grinlib import grin
from grinlib import grinstats
from grinbase.model.users import Users
from grinbase.model.blocks import Blocks
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_shares import Worker_shares


# Globals
NANOGRIN = 1000000000 # 1 and 9 zeros

# Verify / Update / Create Special Users
# (if we have the special users info in our environemnt)
def init_pool_users(CONFIG, LOGGER, database):
    ##
    # WebUI
    LOGGER.warn("Validate WebUI user account")
    try:
        webui_user = os.environ["GRIN_POOL_WEBUI_USER"]
        webui_pass = os.environ["GRIN_POOL_WEBUI_PASSWORD"]
    except KeyError:
        LOGGER.warn("We dont have WebUI account info, skipping...")
        return
    # Verify / create the account
    user = Users.get_by_id(1)
    if user is None:
        user = User(
                id = 1,
                username = webui_user,
                password = webui_pass,
            )
        database.db.getSession().add(user)
        database.db.getSession().commit()
    ##
    # Admin
    try:
        admin_user = os.environ["GRIN_POOL_ADMIN_USER"]
        admin_pass = os.environ["GRIN_POOL_ADMIN_PASSWORD"]
    except KeyError:
        LOGGER.warn("We dont have Admin account info, skipping...")
        return
    # Verify / create the account
    user = Users.get_by_id(2)
    if user is None:
        user = User(
                id = 2,
                username = admin_user,
                password = admin_pass,
            )
        database.db.getSession().add(user)
        database.db.getSession().commit()
    ##
    # Grin Developers Fund
    try:
        devfund_user = "devfund"
        devfund_pass = "IgnosLambo"
    except KeyError:
        LOGGER.warn("We dont have Admin account info, skipping...")
        return
    # Verify / create the account
    user = Users.get_by_id(3)
    if user is None:
        user = User(
                id = 3,
                username = admin_user,
                password = admin_pass,
            )
        database.db.getSession().add(user)
        database.db.getSession().commit()

def get_block_reward():
    BLOCK_REWARD = float(os.environ["BLOCK_REWARD"])
    return BLOCK_REWARD

def get_block_reward_nanogrin():
    BLOCK_REWARD_NANOGRIN = get_block_reward() * NANOGRIN
    return BLOCK_REWARD_NANOGRIN

def get_reward_by_block(height):
    # Get the block and determine how much its worth to the winner
    theblock = Blocks.get_by_height(height)
    #print("The block {}".format(theblock.to_json()))
    if theblock is None:
        return 0;
    return get_block_reward_nanogrin() + theblock.fee

def get_scale_by_block(height):
    # Get the block and determine its secondary_scale value
    theblock = Blocks.get_by_height(height)
    return theblock.secondary_scaling

# Calculate expected grin reward per day for 'gps' at 'height' using 'range' avg data
def estimated_daily_reward(gps=1, height=0, range=60):
    if height == 0:
        height=grin.blocking_get_current_height()
    # Get Avg Network GPS
    network_gps_avgs = grinstats.avg_network_gps(height, range)
    # Get POW Ratios
    C29Ratio = grin.secondary_pow_ratio(height)
    PrimaryRatio = 100 - C29Ratio
    # Calculate Expected Grin Reward per Day
    estReward = {}
    for powsize, gpsavg in network_gps_avgs.items():
        if powsize == grin.SECONDARY_SIZE:
            estReward[powsize] = float(gps) / network_gps_avgs[powsize] * C29Ratio/100.0 * grin.DAY_HEIGHT * get_block_reward()
        else:
            estReward[powsize] = float(gps) / network_gps_avgs[powsize] * PrimaryRatio/100.0 * grin.DAY_HEIGHT * get_block_reward()
    return estReward

# Create a dictionary of user_id -> share size and count
def get_share_counts(height, window_size):
    shares = Worker_shares.get_by_height(height, window_size)
    # Sum up the number of each size share submitted by each user
    shares_count_map = {}
    for worker_shares_rec in shares:
        if not worker_shares_rec.user_id in shares_count_map:
            shares_count_map[worker_shares_rec.user_id] = {}
        for pow_size in worker_shares_rec.sizes():
            #print("pow_size = {}".format(pow_size))
            if not pow_size in shares_count_map[worker_shares_rec.user_id]:
                shares_count_map[worker_shares_rec.user_id][pow_size] = 0
            num_valid = worker_shares_rec.num_valid(pow_size)
            shares_count_map[worker_shares_rec.user_id][pow_size] += num_valid
    return shares_count_map

# XXX TODO: Move to grin lib
def get_share_scale(size, secondary_scaling):
    if size == 29:
        return max(size, secondary_scaling)
    elif size >= 31:
        return 2**(1+size-24)*size

# Calculate total share value of all shares in a share_count_map
def calculate_total_share_value(shares_count_map, scale):
    total_value = 0
    for user_id, worker_shares_count in shares_count_map.items():
        #print("Add this up to total: {} - {}".format(user_id, worker_shares_count))
        #sys.stdout.flush()
        for size, count in worker_shares_count.items():
            #print("xxx: {} {}".format(size, count))
            #sys.stdout.flush()
            value = get_share_scale(size, scale)
            total_value += value * count
    return total_value

# Calculate share value for a single worker
def calculate_worker_shares_value(worker_shares_count, scale):
    worker_value = 0
    #print("Add this up: {}".format(worker_shares_count))
    #sys.stdout.flush()
    for size, count in worker_shares_count.items():
        #print("yyy: {} {}".format(size, count))
        #sys.stdout.flush()
        value = get_share_scale(size, scale)
        worker_value += value * count
    return worker_value

# Get a payout estimate map if it exists in redis cache
def get_block_payout_map_estimate(height, logger):
    payout_estimate_map_key = "payout-estimate-for-block-" + str(height)
    try:
        # Estimates are cached in redis, get it from there if we can
        redisdb = lib.get_redis_db()
        cached_map = redisdb.get(payout_estimate_map_key)
        sys.stdout.flush()
        if cached_map is None:
            return None
        #logger.warn("The Map: {}".format(cached_map.decode('utf-8')))
        return json.loads(cached_map.decode('utf-8'))
    except Exception as e:
        logger.warn("block_payout_map Lookup Error: {} - {}".format(payout_estimate_map_key, repr(e)))

# Calculate Payout due to each miner with shares in the shares_count_map
def calculate_block_payout_map(height, window_size, pool_fee, logger, estimate=False):
    block_payout_map = {}
    # Get the grinpool admin user ID for pool fee
    pool_admin_user_id = 1
    # Total the payments for sanity check
    total_payments_this_block = 0
    try:
        admin_user = os.environ["GRIN_POOL_ADMIN_USER"]
        pool_admin_user_id = Users.get_id_by_username(admin_user)
        logger.warn("Pool Fee goes to admin account with id={}".format(pool_admin_user_id))
    except Exception as e:
        logger.warn("We dont have Admin account info, using default id={}: {}".format(pool_admin_user_id, e))
    # Create the payout map
    # Get pool_block record and check block state
    #print("getting the pool block: {}".format(height))
    #sys.stdout.flush()
    if estimate == False:
        poolblock = Pool_blocks.get_by_height(height)
        if poolblock is None or poolblock.state != "unlocked":
            return {}
        #print("The pool block {}".format(poolblock.to_json()))
    #sys.stdout.flush()
    # Get total value of this block: reward + tx fees
    reward = get_reward_by_block(height)
    print("Reward for block {} = {}".format(height, reward))
    sys.stdout.flush()
    # The Pools Fee
    the_pools_fee = reward * pool_fee
    block_payout_map[pool_admin_user_id] = the_pools_fee
    reward = reward - the_pools_fee
    logger.warn("Pool Fee = {}".format(block_payout_map))
    # Get the "secondary_scaling" value for this block
    scale = get_scale_by_block(height)
    #print("Secondary Scaling value for block = {}".format(scale))
    #sys.stdout.flush()
    # build a map of total shares of each size for each user
    shares_count_map = get_share_counts(height, window_size)
    # DUMMY DATA
#    scale = 529
#    shares_count_map = {
#            1: {29: 50},
#            2: {29: 25, 31: 10},
#            3: {32: 5},
#        }

    #print("Shares Count Map:")
    #sys.stdout.flush()
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(shares_count_map)
    #sys.stdout.flush()
    # Calcualte total value of all shares
    total_value = calculate_total_share_value(shares_count_map, scale)
    print("total share value in payment window: {}".format(total_value))
    sys.stdout.flush()
    # For each user with shares in the window, calculate payout and add to block_payout_map
    for user_id, worker_shares_count in shares_count_map.items():
        #print("xxx: {} {}".format(user_id, worker_shares_count))
        #sys.stdout.flush()
        # Calcualte the total share value from this worker
        total_worker_value = calculate_total_share_value({user_id:worker_shares_count}, scale)
        if total_value * reward > 0:
            worker_payment = int(total_worker_value / total_value * reward)
        else:
            # For next block estimate, there may be no shares submitted to the pool
            worker_payment = 0
        total_payments_this_block += worker_payment
        print("worker_payment: {}".format(worker_payment/1000000000))
        sys.stdout.flush()
        if user_id in block_payout_map.keys():
            block_payout_map[user_id] += worker_payment
        else:
            block_payout_map[user_id] = worker_payment
    logger.warn("Total Grin Paid Out this block: {} + the_pools_fee: {} ".format(total_payments_this_block, the_pools_fee))
    print("block_payout_map = {}".format(block_payout_map))
    #sys.stdout.flush()
    #logger.warn("calculate_map: {}".format(block_payout_map))
    return block_payout_map

#def main():
#    database = lib.get_db()
#    logger = lib.get_logger("test")
#    calculate_block_payout_map(15472, 60, logger, True)
#
#if __name__ == "__main__":
#    main()

