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
from grinlib import network
from grinbase.model.blocks import Blocks

PROCESS = "blockWatcher"
LOGGER = None
CONFIG = None

def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    # Connect to DB
    database = lib.get_db()

    check_interval = float(CONFIG[PROCESS]["check_interval"])

    last = network.get_current_height()
    while True:
        latest = network.get_current_height()
        for i in range(last + 1, latest + 1):
            last = latest
            response = network.get_block_by_height(i)
            if response == None:
                LOGGER.error("Failed to get block info for block {}".format(last))
                continue
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
