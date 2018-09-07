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
# Routines for working with grin_stats records
#

import sys
import time
import requests
import json

from grinlib import lib
from grinlib import grin

from grinbase.model.blocks import Blocks
from grinbase.model.grin_stats import Grin_stats
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.worker_stats import Worker_stats

# Calculate the grin stats for the specified height
# Return a Grin_stats object
# Raises AssertionError
def calculate(height, avg_range):
    # Get the most recent blocks from which to generate the stats
    recent_blocks = []
    previous_stats_record = Grin_stats.get_by_height(height-1)
    print("XXX: {}".format(previous_stats_record))
    assert previous_stats_record is not None, "No provious stats record found" 
    recent_blocks = Blocks.get_by_height(height, avg_range)
    if len(recent_blocks) < min(avg_range, height):
        # We dont have all of these blocks in the DB
        raise AssertionError("Missing blocks in range: {}:{}".format(height-avg_range, height))
    print(recent_blocks[-1])
    print(recent_blocks[-2])
    print(recent_blocks[-3])
    print(recent_blocks[-4])
    assert recent_blocks[-1].height == height, "Invalid height in recent_blocks[-1]" 
    assert recent_blocks[-2].height == height - 1, "Invalid height in recent_blocks[-2]: {} vs {}".format(recent_blocks[-2].height, height - 1) 
    # Calculate the stats data
    first_block = recent_blocks[0]
    last_block = recent_blocks[-1]
    timestamp = last_block.timestamp
    difficulty = recent_blocks[-1].total_difficulty - recent_blocks[-2].total_difficulty
    gps = lib.calculate_graph_rate(difficulty, first_block.timestamp, last_block.timestamp, len(recent_blocks))
    # utxo set size = sum outputs - sum inputs
    total_utxoset_size = previous_stats_record.total_utxoset_size + last_block.num_outputs - last_block.num_inputs
    return Grin_stats(
        height = height,
        timestamp = timestamp,
        gps = gps,
        difficulty = difficulty,
        total_utxoset_size = total_utxoset_size,
    )


# Re-Caclulate grin stats from the specified height and commits to DB
# Return height of the last stat recalculated
# Raises AssertionError
def recalculate(start_height, avg_range):
    database = lib.get_db()
    height = start_height
    while height <= grin.blocking_get_current_height():
        old_stats = Grin_stats.get_by_height(height)
        new_stats = calculate(height, avg_range)
        if old_stats is None:
            database.db.createDataObj(new_stats)
        else:
            old_stats.timestamp = new_stats.timestamp
            old_stats.difficulty = new_stats.difficulty
            old_stats.gps = new_stats.gps
            old_stats.difficulty = new_stats.difficulty
            old_stats.total_utxoset_size = new_stats.total_utxoset_size
            database.db.getSession().commit()
        height = height + 1


# Initialize Grin_stats
# No return value
def initialize():
    database = lib.get_db()
    # Special case for new pool startup - Need 3 stats records to bootstrap
    block_zero = Blocks.get_by_height(0)
    seed_stat0 = Grin_stats(
        height=0,
        timestamp=block_zero.timestamp,
        gps=0,
        difficulty=block_zero.total_difficulty,
        total_utxoset_size=block_zero.num_inputs)
    database.db.createDataObj(seed_stat0)
    block_one = Blocks.get_by_height(1)
    seed_stat1 = Grin_stats(
        height=1,
        timestamp=block_one.timestamp,
        gps=0,
        difficulty=block_one.total_difficulty - block_zero.total_difficulty,
        total_utxoset_size=seed_stat0.total_utxoset_size + block_one.num_outputs - block_one.num_inputs)
    database.db.createDataObj(seed_stat1)
    block_two = Blocks.get_by_height(2)
    seed_stat2 = Grin_stats(
        height=2,
        timestamp=block_two.timestamp,
        gps=0,
        difficulty=block_two.total_difficulty - block_one.total_difficulty,
        total_utxoset_size=seed_stat1.total_utxoset_size + block_two.num_outputs - block_two.num_inputs)
    database.db.createDataObj(seed_stat2)

