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
from datetime import datetime

from grinlib import lib
from grinlib import grin

from grinbase.model.blocks import Blocks
from grinbase.model.grin_stats import Grin_stats
from grinbase.model.gps import Gps

# MOVE TO CONFIG - Tromps magic numbers
SECONDARY_SIZE = 29
DIFFICULTY_ADJUST_WINDOW = 60

HF0_HEIGHT = 0

# Calculate average network GPS at height over range
def avg_network_gps(height=0, range=60):
    if height == 0:
        height = Blocks.get_latest().height
    if range <= 0:
        range = 1
    grinstats = Grin_stats.get_by_height(height, range)
    gpslists = [stat.gps for stat in grinstats]
    gpslists_len = len(gpslists)
    if gpslists_len == 0:
        return 0
    gpstotals = {}
    for gpslist in gpslists:
        for gps in gpslist:
            if gps.edge_bits not in gpstotals:
                gpstotals[gps.edge_bits] = 0
            gpstotals[gps.edge_bits] += gps.gps
    gpsavgs = {}
    for sz, gpstotal in gpstotals.items():
        gpsavgs[sz] = gpstotal / gpslists_len
    return gpsavgs


# Calculate GPS for window[-1] for all graph sizes and return it as a list of tuples [(edge_bits, gps_estimate ,), ...]
def estimate_all_gps(window):
    gps = []
    # Calcualte the gps for each graph size in the recnt blocks list
    # Based on jaspervdm code - https://github.com/jaspervdm/grin_mining_sim

    height = window[-1].height
    # Get the difficulty of the most recent block
    difficulty = window[-1].total_difficulty - window[-2].total_difficulty
    # Time Delta (as float, in minutes) for this window
    time_delta = float((window[-1].timestamp - window[0].timestamp).total_seconds())
    # Get secondary_scaling value for the most recent block
    secondary_scaling = window[-1].secondary_scaling
    if secondary_scaling == 0:
        secondary_scaling = 1840
    # Count the total number of each solution size in the window
    counts = {}
    counts[SECONDARY_SIZE] = 0
    for block in window:
        if block.edge_bits not in counts:
            counts[block.edge_bits] = 1
        else:
            counts[block.edge_bits] += 1
    # Get total counts for primary and secondary POWs
    count_secondary = counts[SECONDARY_SIZE]
    count_primary = sum(counts.values()) - count_secondary
    # ratios
    srr = grin.secondary_pow_ratio(height)/100.0
    prr = 1.0 - srr
    # Calculate the GPS
    all_gps = []
    for edge_bits in counts.keys():
        bps = float(counts[edge_bits]) / float(time_delta)
        factor = 42
        if edge_bits == SECONDARY_SIZE and height > HF0_HEIGHT:
            factor = 21
        if edge_bits == SECONDARY_SIZE:
            weight = secondary_scaling
        else:
            weight = grin.graph_weight(edge_bits)
        # Caclulate GPS
        gps = (bps/(weight/difficulty))*factor
        all_gps.append((edge_bits, gps, ))
        print("All GPS: {}".format(all_gps))
    return all_gps


# Calculate the grin stats for the specified height
# Return a Grin_stats object
# Raises AssertionError
def calculate(height, avg_range=DIFFICULTY_ADJUST_WINDOW):
    # Get the most recent blocks from which to generate the stats
    recent_blocks = []
    previous_stats_record = Grin_stats.get_by_height(height-1)
    print("XXX: {}".format(previous_stats_record))
    assert previous_stats_record is not None, "No previous stats record found"
    print("height {}, avg_range {}".format(height, avg_range))
    recent_blocks = Blocks.get_by_height(height, avg_range)
    if len(recent_blocks) < min(avg_range, height):
        # We dont have all of these blocks in the DB
        raise AssertionError("Missing blocks in range: {}:{}".format(height-avg_range, height))
    print("{} vs {}".format(recent_blocks[-1].height, height))
    assert recent_blocks[-1].height == height, "Invalid height in recent_blocks[-1]"
    assert recent_blocks[-2].height == height - 1, "Invalid height in recent_blocks[-2]: {} vs {}".format(recent_blocks[-2].height, height - 1)
    # Calculate the stats data
    first_block = recent_blocks[0]
    last_block = recent_blocks[-1]
    timestamp = last_block.timestamp
    difficulty = recent_blocks[-1].total_difficulty - recent_blocks[-2].total_difficulty
    new_stats = Grin_stats(
        height = height,
        timestamp = timestamp,
        difficulty = difficulty,
    )
    # Caclulate estimated GPS for recent edge_bits sizes
    all_gps = estimate_all_gps(recent_blocks)
    for gps in all_gps:
        gps_rec = Gps(
            edge_bits = gps[0],
            gps = gps[1],
        )
        new_stats.gps.append(gps_rec)
    return new_stats


def initialize(avg_over_range, logger):
    database = lib.get_db()
    # Special case for new pool startup - Need 3 stats records to bootstrap
    block_zero = None
    while block_zero is None:
        logger.warn("Waiting for the first block record in the database")
        time.sleep(1)
        block_zero = Blocks.get_earliest()
    print("block_zero={}".format(block_zero))
    height = block_zero.height
    # Create avg_over_range dummy block records prior to block_zero
    print("Create block filtters: {} - {}".format(height-avg_over_range, height))
    for h in range(height-avg_over_range, height):
        print("Creating fillter at height {}".format(h))
        new_block = Blocks(hash = "x",
            version = 0,
            height = h,
            previous = "x",
            timestamp = datetime.utcnow(),
            output_root = "x",
            range_proof_root = "x",
            kernel_root = "x",
            nonce = 0,
            edge_bits = 29,
            total_difficulty = block_zero.total_difficulty,
            secondary_scaling = 0,
            num_inputs = 0,
            num_outputs = 0,
            num_kernels = 0,
            fee = 0,
            lock_height = 0,
            total_kernel_offset = "x",
            state = "filler")
        database.db.getSession().add(new_block)
    database.db.getSession().commit()
    seed_stat0 = Grin_stats(
        height=height-2,
        timestamp=block_zero.timestamp,
        difficulty=block_zero.total_difficulty)
    database.db.createDataObj(seed_stat0)
    seed_stat1 = Grin_stats(
        height=height-1,
        timestamp=block_zero.timestamp,
        difficulty=block_zero.total_difficulty)
    database.db.createDataObj(seed_stat1)
    seed_stat2 = Grin_stats(
        height=height,
        timestamp=block_zero.timestamp,
        difficulty=block_zero.total_difficulty)
    database.db.createDataObj(seed_stat2)
    return height
