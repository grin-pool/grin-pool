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

# GLOBALS - Tromps magic numbers
SECONDARY_SIZE = 29
BASE_EDGE_BITS = 24 # HARD FORK TO CHANGE



def get_secondary_size():
    return SECONDARY_SIZE

def get_api_auth():
    config = lib.get_config()
    auth = (config["grin_node"]["api_user"], config["grin_node"]["api_secret"])
    return auth

def get_api_url():
    config = lib.get_config()
    grin_api_url = "http://" + config["grin_node"]["address"] + ":" + config["grin_node"]["api_port"]
    return grin_api_url

def get_owner_api_url():
    config = lib.get_config()
    grin_owner_api_url = "http://" + config["wallet"]["owner_api_address"] + ":" + config["wallet"]["owner_api_port"] + "/v2/owner"
    return grin_owner_api_url

# Network chain height
def get_current_height():
    config = lib.get_config()
    auth = get_api_auth()
    grin_api_url = get_api_url()
    status_url = grin_api_url + "/v1/status"
    try:
        response = requests.get(status_url, auth=auth)
        latest = response.json()["tip"]["height"]
    except:
        return None
    return latest

def get_block_by_height(height):
    config = lib.get_config()
    auth = get_api_auth()
    grin_api_url = get_api_url()
    blocks_url = grin_api_url + "/v1/blocks/" + str(height)
    try:
        response = requests.get(blocks_url, auth=auth)
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


# MOVED TO lib.py
# Network graph rate
#  difficulty = block or share difficulty
#  ts1, ts2   = Time range for finding the blocks or shares
#  n          = Number of blocks or shares found in that range
#def calculate_graph_rate(difficulty, edge_bits=29):
#    print("in: calculate_graph_rate difficulty = {}".format(difficulty))
#    g_weight = graph_weight(edge_bits)
#    print("Graph Weight = {}".format(g_weight))
#    if edge_bits == 29:
#        gps = 21.0 * (difficulty / g_weight) / 60.0
#    else:
#        gps = 42.0 * (difficulty / g_weight) / 60.0
#    print("G/s  = {}".format(gps))
#    return gps

# Network Difficulty
def get_network_difficulty(height):
    latest_blocks = Blocks.get_by_height(height, 2)
    return latest_blocks[1].total_difficulty - latest_blocks[0].total_difficulty

# Compute weight of a graph as number of siphash bits defining the graph
# Must be made dependent on height to phase out smaller size over the years
# This can wait until end of 2019 at latest
# https://github.com/mimblewimble/grin/blob/6980278b95d266f6a420b64052ab6231a6e1c466/core/src/consensus.rs#L157
def graph_weight(edge_bits):
    return (2 << (edge_bits - BASE_EDGE_BITS)) * edge_bits

# The following is from
# https://github.com/mimblewimble/grin-explorer/blob/01b5fc1ebecdb7ec842be241b725675497419ccc/grinexplorer/blockchain/models.py
def scaled_difficulty(hash, graph_weight):
    # Difficulty achieved by this proof with given scaling factor
    diff = ((graph_weight) << 64) / int(hash[:16], 16)
    return min(diff, 0xffffffffffffffff)

def from_proof_adjusted(hash, edge_bits):
    # Computes the difficulty from a hash. Divides the maximum target by the
    # provided hash and applies the Cuck(at)oo size adjustment factor
    # scale with natural scaling factor
    return scaled_difficulty(hash, graph_weight(edge_bits))

def from_proof_scaled(hash, secondary_scaling):
    # Same as `from_proof_adjusted` but instead of an adjustment based on
    # cycle size, scales based on a provided factor. Used by dual PoW system
    # to scale one PoW against the other.
    # Scaling between 2 proof of work algos
    return scaled_difficulty(hash, secondary_scaling)

def difficulty(hash, edge_bits, secondary_scaling):
    # Maximum difficulty this proof of work can achieve
    # 2 proof of works, Cuckoo29 (for now) and Cuckoo30+, which are scaled
    # differently (scaling not controlled for now)
    if (edge_bits == SECONDARY_SIZE):
        return int(from_proof_scaled(hash, secondary_scaling))
    else:
        return int(from_proof_adjusted(hash, edge_bits))

## Secondary Target Ratio
# Block interval, in seconds
BLOCK_TIME_SEC = 60
# Nominal height for standard time intervals, hour is 60 blocks
HOUR_HEIGHT = 3600 / BLOCK_TIME_SEC
# A day is 1440 blocks
DAY_HEIGHT = 24 * HOUR_HEIGHT
# A week is 10_080 blocks
WEEK_HEIGHT = 7 * DAY_HEIGHT
# A year is 524_160 blocks
YEAR_HEIGHT = 52 * WEEK_HEIGHT

# Target ratio of secondary proof of work to primary proof of work,
# as a function of block height (time). Starts at 90% losing a percent
# approximately every week. Represented as an integer between 0 and 100.
def secondary_pow_ratio(height):
    ratio = 90 - (height / (2 * YEAR_HEIGHT / 90))
    return max(0, ratio)




def main():
    config = lib.get_config()
    PROCESS = "libNetworkTest"
    LOGGER = lib.get_logger(PROCESS)
    database = lib.get_db()
    

if __name__ == "__main__":
    main()

