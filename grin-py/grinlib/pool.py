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

import sys
import time
import requests
import json

from grinlib import lib
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.grin_shares import Grin_shares
from grinbase.model.pool_shares import Pool_shares

# Share graph rate
def calculate_graph_rate(difficulty, ts1, ts2, n):
    # gps = 42 * (diff/scale) / 60
    # XXX TODO:  Assumes cuckoo 30 for all blocks - Fixes for cuckatoos?
    scale = 29.0
    timedelta = (ts2 - ts1).total_seconds()
    if n == 0 or timedelta == 0:
      return 0
    gps = (42.0 * float(n)) / float(timedelta)
    return gps

    

# get_stats() Response is:
# { 
#    pool_stats:{
#        height: Integer,
#        latest_hash: String,
#        latest_timestamp: String
#        latest_difficulty: Integer,
#        graph_rate: Integer,
#    }
# }
def get_stats():
    ##
    # Get current Network Info as seen by our grin node
    stats_json = {}
    last_n = 10 # Look at shares from the last N blocks to calculate avg time between
    # Get the poolblocks from the DB
    latest_blocks = Pool_blocks.get_last_n(last_n)
    # Latest poolblock height
    stats_json["height"] = latest_blocks[-1].height
    # Latest poolblock hash
    stats_json["latest_hash"] = latest_blocks[-1].hash
    # Latest poolblock timestamp
    stats_json["latest_timestamp"] = latest_blocks[-1].timestamp.strftime('%s')
    # Avg time between poolblocks
    found_every = (latest_blocks[-1].timestamp - latest_blocks[0].timestamp).strftime('%s')
    stats_json["found_every"] = found_every
# XXX TODO:
#    # Pool graph rate
#    stats_json["graph_rate"] = calculate_graph_rate(latest_difficulty, latest_blocks[0].timestamp, latest_blocks[-1].timestamp, last_n)
    return stats_json

def get_blocks_found_data(num_blocks):
    ##
    # Returns data needed to create a *blocks found* chart over the past num_blocks history
    blocks_found_data = []
    latest_blocks = Pool_blocks.get_last_n(num_blocks)
    for block in iter(latest_blocks):
      blockdata = {}
      blockdata["time"] = block.timestamp.strftime('%s')
      blockdata["height"] =  block.height
      blocks_found_data.append(blockdata)
    return blocks_found_data

def get_graph_rate_data(num_blocks):
    ##
    # Returns data needed to create a *graph rate* chart over the past num_blocks history
    graph_rate_data = []
    latest_blocks = Pool_blocks.get_last_n(num_blocks)
    for i in range(0, num_blocks-5):
      # rolling 5-block window
      ratedata = {}
      ts1 = latest_blocks[i].timestamp
      ts2 = latest_blocks[i+5].timestamp
      difficulty = latest_blocks[i+5].total_difficulty - latest_blocks[i+4].total_difficulty # XXX TODO: This isnt right
      gps = calculate_graph_rate(difficulty, ts1, ts2, 5)
      ratedata["height"] = latest_blocks[i+5].height
      ratedata["gps"] = gps
      ratedata["timestamp"] = ts2.strftime('%s')
      graph_rate_data.append(ratedata)
    return graph_rate_data

def get_active_miners_data(num_blocks):
    ##
    # Returns data needed to create an *active_miners* chart over the past num_blocks history
    graph_active_miners_data = []
    latest_blocks = Blocks.get_last_n(num_blocks)
    for i in range(0, num_blocks-1):
      difficultydata = {}
      difficulty = latest_blocks[i+1].total_difficulty - latest_blocks[i].total_difficulty
      difficultydata["height"] = latest_blocks[i].height
      difficultydata["difficulty"] = difficulty
      difficultydata["time"] = latest_blocks[i].timestamp.strftime('%s')
      graph_difficulty_data.append(difficultydata)
    return graph_difficulty_data



def main():
    config = lib.get_config()
    PROCESS = "libPoolTest"
    LOGGER = lib.get_logger(PROCESS)

    database = lib.get_db()
    
    # Get stats
    stats = get_stats()
    LOGGER.warn("stats = {}".format(stats))
    LOGGER.warn("")

    # Get blocks found
    bf = get_blocks_found_data(5)
    LOGGER.warn("blocks found = {}".format(bf))
    LOGGER.warn("")

    # Get graph rate
    gr = get_graph_rate_data(20)
    LOGGER.warn("graph rate = {}".format(gr))
    LOGGER.warn("")

    # Get difficulty data
    diff = get_difficulty_data(200)
    LOGGER.warn("difficulty = {}".format(diff))

    sys.exit(1)


if __name__ == "__main__":
    main()

