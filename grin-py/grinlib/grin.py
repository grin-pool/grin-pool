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
from grinbase.model.grin_stats import Grin_stats

def get_api_url():
    config = lib.get_config()
    grin_api_url = "http://" + config["grin_node"]["address"] + ":" + config["grin_node"]["api_port"]
    return grin_api_url

# Network chain height
def get_current_height():
    config = lib.get_config()
    grin_api_url = get_api_url()
    status_url = grin_api_url + "/v1/status"
    try:
        response = requests.get(status_url)
        latest = response.json()["tip"]["height"]
    except:
        return None
    return latest

def get_block_by_height(height):
    config = lib.get_config()
    grin_api_url = get_api_url()
    blocks_url = grin_api_url + "/v1/blocks/" + str(height)
    try:
        response = requests.get(blocks_url)
        block = response.json()
    except:
        return None
    return block
    
# Same as get_current_height except wait raither than returning None
def blocking_get_current_height():
    response = None
    while response is None:
        response = get_current_height()
        if response is None:
            time.sleep(1)
    return int(response)

# Same as get_block_by_height except wait raither than returning None
def blocking_get_block_by_height(i):
    response = None
    while response is None:
        response = get_block_by_height(i)
        if response is None:
            time.sleep(1)
    return response


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


def get_stats(height):
    ##
    # Get requested grin network stats as seen by our grin node
    return Grin_stats.get_by_height(height)

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

