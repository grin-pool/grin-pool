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
# Routines for working with worker_stats records
#

import sys
import time
import requests
import json
import datetime

from grinlib import lib
from grinlib import grin

from grinbase.model.blocks import Blocks
from grinbase.model.grin_stats import Grin_stats
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.pool_shares import Pool_shares
from grinbase.model.worker_stats import Worker_stats

# XXX TODO: Move to config
POOL_MIN_DIFF = 29
BATCHSZ = 100

# Calculate worker stats for the specified height
# Return a list of Worker_stats object
# Raises AssertionError
def calculate(height, avg_range):
    avg_over_first_grin_block = Blocks.get_by_height( max(height-avg_range, 1) )
    assert(avg_over_first_grin_block is not None)
    current_grin_block = Blocks.get_by_height(height)
    assert(current_grin_block is not None)
    # Get all worker share data for the current range of blocks
    latest_pool_shares = Pool_shares.get_by_height(height, avg_range)
    # Create a worker_stats for each user who submitted a share in this range
    workers = list(set([share.found_by for share in latest_pool_shares]))
    new_stats = []
    for worker in workers:
        # Get this workers most recent worker_stats record (for running totals)
        last_stat = Worker_stats.get_latest_by_id(worker)
        if last_stat is None:
            # A new worker
            last_stat = Worker_stats(None, datetime.datetime.now(), height-1, worker, 0, 0, 0, 0, 0, 0)
            new_stats.append(last_stat)
        # Calculate the stats data
        latest_worker_shares = [share for share in latest_pool_shares if share.found_by == worker]
        worker_shares_this_block = [share for share in latest_worker_shares if share.height == height]
        difficulty = POOL_MIN_DIFF # latest_worker_shares[0].worker_difficulty # XXX TODO - enchance to support multiple difficulties
        gps = grin.calculate_graph_rate(difficulty, avg_over_first_grin_block.timestamp, current_grin_block.timestamp, len(latest_worker_shares))
        shares_processed = len(worker_shares_this_block)
        total_shares_processed = last_stat.total_shares_processed + shares_processed
        stats = Worker_stats(
                id = None,
                timestamp = current_grin_block.timestamp,
                height = current_grin_block.height,
                worker = worker,
                gps = gps,
                shares_processed = shares_processed,
                total_shares_processed = total_shares_processed,
                grin_paid = 123, # XXX TODO
                total_grin_paid = 456, # XXX TODO
                balance = 1) # XXX TODO
        new_stats.append(stats)
    return new_stats

# Re-Caclulate worker stats from the specified height and commits to DB
# Return height of the last stat recalculated
# Raises AssertionError
def recalculate(start_height, avg_range):
    database = lib.get_db()
    height = start_height
    while height <= grin.blocking_get_current_height():
        old_stats = Worker_stats.get_by_height(height)
        new_stats = calculate(height, avg_range)
        for old_stat in old_stats:
            database.db.deleteDataObj(old_stat)
        for stats in new_stats:
            print("new/updated stats: {} ".format(stats))
            worker = stats.worker
            database.db.getSession().add(stats)
            if(height % BATCHSZ == 0):
                database.db.getSession().commit()
        height = height + 1
    database.db.getSession().commit()
