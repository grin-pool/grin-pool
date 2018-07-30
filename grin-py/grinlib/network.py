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
# Routines for getting Grin Network data
#

import sys
import time
import requests
import json

from grinlib import lib
from grinbase.model.blocks import Blocks

def get_api_url():
    config = lib.get_config()
    grin_api_url = "http://" + config["grin_node"]["address"] + ":" + config["grin_node"]["api_port"]
    return grin_api_url

# Network chain height
def get_current_height():
    config = lib.get_config()
    grin_api_url = get_api_url()
    status_url = grin_api_url + "/v1/status"
    response = requests.get(status_url)
    latest = response.json()["tip"]["height"]
    # XXX TODO:  Validate somehow?
    return latest

def get_block_by_height(height):
    config = lib.get_config()
    grin_api_url = get_api_url()
    blocks_url = grin_api_url + "/v1/blocks/" + str(height)
    try:
        response = requests.get(blocks_url)
        block = response.json()
        return block
    except:
        return None
    

# Network graph rate
#  difficulty = block or share difficulty
#  ts1, ts2   = Time range for finding the blocks or shares
#  n          = Number of blocks or shares found in that range
def calculate_graph_rate(difficulty, ts1, ts2, n):
    # gps = 42 * (diff/scale) / 60
    # XXX TODO:  Assumes cuckoo 30 for all blocks
    scale = 29.0
    if n == 0:
      return 0
    avg_time_between_blocks = abs((ts2 - ts1).total_seconds()) / n
    if avg_time_between_blocks == 0:
      return 0
    gps = 42.0 * (difficulty/scale) / avg_time_between_blocks
    return gps

# Network Difficulty
def get_network_difficulty(height):
    latest_blocks = Blocks.get_range_by_height(height-1, height)
    return latest_blocks[1].total_difficulty - latest_blocks[0].total_difficulty

# get_stats() Response is:
# { 
#    network_stats:{
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
    last_n = 10 # Look at N blocks to calculate avg time between
    # Get the blocks from the DB
    latest_blocks = Blocks.get_last_n(last_n)
    # Latest block height
    stats_json["height"] = latest_blocks[-1].height
    # Latest block hash
    stats_json["latest_hash"] = latest_blocks[-1].hash
    # Latest block timestamp
    stats_json["latest_timestamp"] = latest_blocks[-1].timestamp.strftime('%s')
    # Latest block network difficulty
    latest_difficulty = latest_blocks[-1].total_difficulty - latest_blocks[-2].total_difficulty
    stats_json["latest_difficulty"] = latest_difficulty
    # Network graph rate
    stats_json["graph_rate"] = lib.calculate_graph_rate(latest_difficulty, latest_blocks[0].timestamp, latest_blocks[-1].timestamp, last_n)
    return stats_json

def get_blocks_found_data(num_blocks):
    ##
    # Returns data needed to create a *blocks found* chart over the past num_blocks history
    blocks_found_data = []
    latest_blocks = Blocks.get_last_n(num_blocks)
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
    latest_blocks = Blocks.get_last_n(num_blocks)
    for i in range(0, num_blocks-5):
      # rolling 5-block window
      ratedata = {}
      ts1 = latest_blocks[i].timestamp
      ts2 = latest_blocks[i+5].timestamp
      difficulty = latest_blocks[i+5].total_difficulty - latest_blocks[i+4].total_difficulty
      gps = calculate_graph_rate(difficulty, ts1, ts2, 5)
      ratedata["height"] = latest_blocks[i+5].height
      ratedata["gps"] = gps
      ratedata["timestamp"] = ts2.strftime('%s')
      graph_rate_data.append(ratedata)
    return graph_rate_data

def get_difficulty_data(num_blocks):
    ##
    # Returns data needed to create a *difficulty* chart over the past num_blocks history
    graph_difficulty_data = []
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
    PROCESS = "libNetworkTest"
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

