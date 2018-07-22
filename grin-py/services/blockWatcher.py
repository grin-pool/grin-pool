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

# Watches the blockchain for new blocks
#  Request chain height from grin core every x seconds.
#  If the height increased request each block from grin core.
#  Adds them to the database.
# This keeps a record of each block *as we see it* (before any chain reorgs).

import sys
import requests
import json
from time import sleep

from grinlib import lib
from grinbase.model.blocks import Blocks

PROCESS = "blockWatcher"
LOGGER = None
CONFIG = None

def get_current_height(url):
    response = requests.get(url)
    latest = response.json()["tip"]["height"]
    # XXX TODO:  Validate somehow?
    return latest


def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    # Connect to DB
    database = lib.get_db()

    grin_api_url = "http://" + CONFIG["grin_node"]["address"] + ":" + CONFIG["grin_node"]["api_port"]
    status_url = grin_api_url + "/v1/status"
    blocks_url = grin_api_url + "/v1/blocks/"
    check_interval = float(CONFIG[PROCESS]["check_interval"])

    last = get_current_height(status_url)
    while True:
        latest = get_current_height(status_url)
        for i in range(last + 1, latest + 1):
            last = latest
            url = blocks_url + str(i)
            r = requests.get(url)
            if not r.ok:
                LOGGER.error("Failed to get block info for block {}".format(last))
                continue
            response = requests.get(url).json()
            LOGGER.warn("New Block: {} at {}".format(response["header"]["hash"],
                                              response["header"]["height"]))
            try:
                new_block = Blocks(hash = response["header"]["hash"],
                                   version = response["header"]["version"],
                                   height = response["header"]["height"],
                                   previous = response["header"]["previous"],
                                   timestamp = response["header"]["timestamp"][:-1],
                                   output_root = response["header"]["output_root"],
                                   range_proof_root = response["header"]["range_proof_root"],
                                   kernel_root = response["header"]["kernel_root"],
                                   nonce = response["header"]["nonce"],
                                   total_difficulty = response["header"]["total_difficulty"],
                                   total_kernel_offset = response["header"]["total_kernel_offset"],
                                   state = "new")
                database.db.createDataObj(new_block)
            except Exception as e:
                LOGGER.error("Something went wrong: {}".format(e))
        sys.stdout.flush()
        sleep(check_interval)
    LOGGER.warn("=== Completed {}".format(PROCESS))


if __name__ == "__main__":
    main()
