#!/usr/bin/env python

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
# Routines for working with pool_stats records
#

import sys
import time
import requests
import json
from datetime import datetime

from grinlib import lib
from grinlib import grin

from grinbase.model.blocks import Blocks
from grinbase.model.grin_stats import Grin_stats
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_shares import Worker_shares

# XXX TODO: Move to config
POOL_MIN_DIFF = 29

# Calculate the pool stats for the specified height
# Return a Pool_stats object
# Raises AssertionError
def calculate(height, avg_range):
    # Get the most recent pool data from which to generate the stats
    previous_stats_record = Pool_stats.get_by_height(height-1)
    assert previous_stats_record is not None, "No previous stats record found"
    avg_over_first_grin_block = Blocks.get_by_height( max(height-avg_range, 1) )
    assert avg_over_first_grin_block is not None, "Missing grin block: {}".format(max(height-avg_range, 1))
    grin_block = Blocks.get_by_height(height)
    assert grin_block is not None, "Missing grin block: {}".format(height)
    latest_worker_shares = Worker_shares.get_by_height(height)
    # If no shares are found for this height, we have 2 options:
    # 1) Assume the share data is *delayed* so dont create the stats record now
    # assert len(latest_worker_shares) > 0, "No worker shares found"
    # 2) If we want we can create the record without share data and then when shares are added later this record will be recalculated
    avg_over_worker_shares = Worker_shares.get_by_height(height, avg_range)
    # Calculate the stats data
    timestamp = grin_block.timestamp
    difficulty = POOL_MIN_DIFF # XXX TODO - enchance to support multiple difficulties
    gps = 0
    active_miners = 0
    shares_processed = 0
    num_shares_in_range = 0
    if len(avg_over_worker_shares) > 0:
        num_shares_in_range = sum([shares.valid for shares in avg_over_worker_shares])
        gps = lib.calculate_graph_rate(difficulty, avg_over_first_grin_block.timestamp, grin_block.timestamp, num_shares_in_range)
        print("XXX: difficulty={}, {}-{}, len={}".format(difficulty, avg_over_first_grin_block.timestamp, grin_block.timestamp, num_shares_in_range))
    if latest_worker_shares is not None:
        active_miners = len(latest_worker_shares) # XXX NO, FIX THIS
        num_valid = sum([shares.valid for shares in latest_worker_shares])
        num_invalid = sum([shares.invalid for shares in latest_worker_shares])
        shares_processed = num_valid + num_invalid

    total_shares_processed = previous_stats_record.total_shares_processed + shares_processed
    total_grin_paid = previous_stats_record.total_grin_paid # XXX TODO
    total_blocks_found = previous_stats_record.total_blocks_found
    if Pool_blocks.get_by_height(height-1) is not None:
        total_blocks_found = total_blocks_found + 1
    return Pool_stats(
            height = height,
            timestamp = timestamp,
            gps = gps,
            active_miners = active_miners,
            shares_processed = shares_processed,
            total_shares_processed = total_shares_processed,
            total_grin_paid = total_grin_paid,
            total_blocks_found = total_blocks_found)



# Re-Caclulate pool stats from the specified height and commits to DB
# Return height of the last stat recalculated
# Raises AssertionError
def recalculate(start_height, avg_range):
    database = lib.get_db()
    height = start_height
    while height < grin.blocking_get_current_height():
        old_stats = Pool_stats.get_by_height(height)
        new_stats = calculate(height, avg_range)
        if old_stats is None:
            database.db.createDataObj(new_stats)
        else:
            old_stats.timestamp = new_stats.timestamp
            old_stats.gps = new_stats.gps
            old_stats.active_miners = new_stats.active_miners
            old_stats.shares_processed = new_stats.shares_processed
            old_stats.total_shares_processed = new_stats.total_shares_processed
            old_stats.total_grin_paid = new_stats.total_grin_paid
            old_stats.total_blocks_found = new_stats.total_blocks_found
            old_stats.dirty = False
            database.db.getSession().commit()
        height = height + 1


# Initialize Pool_stats
# No return value
def initialize():
    database = lib.get_db()
    # Special case for new pool startup
    seed_stat = Pool_stats(
            height=0,
            timestamp=datetime.utcnow(),
            gps=0,
            active_miners=0,
            shares_processed=0,
            total_shares_processed=0,
            total_grin_paid=0,
            total_blocks_found=0)
    database.db.createDataObj(seed_stat)

