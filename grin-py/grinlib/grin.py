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

def get_owner_api_url():
    config = lib.get_config()
    grin_owner_api_url = "http://" + config["wallet"]["address"] + ":" + config["wallet"]["owner_api_port"]
    return grin_owner_api_url

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
def calculate_graph_rate(difficulty, edge_bits=29):
    print("in: calculate_graph_rate difficulty = {}".format(difficulty))
    g_weight = graph_weight(edge_bits)
    print("Graph Weight = {}".format(g_weight))
    gps = 42.0 * (difficulty / g_weight) / 60.0
    print("G/s  = {}".format(gps))
    return gps

# Compute weight of a graph as number of siphash bits defining the graph
# Must be made dependent on height to phase out smaller size over the years
# This can wait until end of 2019 at latest
# https://github.com/mimblewimble/grin/blob/6980278b95d266f6a420b64052ab6231a6e1c466/core/src/consensus.rs#L157
def graph_weight(edge_bits):
    BASE_EDGE_BITS = 24 # HARD FORK TO CHANGE
    return (2 << (edge_bits - BASE_EDGE_BITS)) * edge_bits


# Network Difficulty
def get_network_difficulty(height):
    latest_blocks = Blocks.get_range_by_height(height-1, height)
    return latest_blocks[1].total_difficulty - latest_blocks[0].total_difficulty





def main():
    config = lib.get_config()
    PROCESS = "libNetworkTest"
    LOGGER = lib.get_logger(PROCESS)
    database = lib.get_db()
    

if __name__ == "__main__":
    main()

