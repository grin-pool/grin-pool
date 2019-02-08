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

# Verify our mysql chain against the grin network
#  Add missing blocks.
#  Mark orphan blocks.

import sys
import requests
import json
import time
import traceback
from datetime import datetime


from grinlib import lib
from grinlib import grin
from grinbase.model.blocks import Blocks

PROCESS = "blockValidator"
LOGGER = None
CONFIG = None

def main():
    global LOGGER
    global CONFIG

    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    
    # Connect to DB
    database = lib.get_db()

    validation_depth = int(CONFIG[PROCESS]["validation_depth"])

    latest = grin.get_current_height()
    last_block_record = Blocks.get_latest()
    if last_block_record == None:
        last_block_record_height = 0;
    else:
        last_block_record_height = last_block_record.height
    last = min(latest-validation_depth, last_block_record_height-validation_depth)  # start a reasonable distance back
    if last < 0:
        last = 0

    LOGGER.warn("Starting from block #{}".format(last))

    for i in range(last, latest+1):
        if i % 100 == 0:
            LOGGER.warn("Processing #{}".format(i))
        response = grin.blocking_get_block_by_height(i)
        assert(response is not None)
        assert(int(response["header"]["height"]) == i)
        #print("{}: {}".format(response["header"]["height"], response["header"]["hash"]))
        try:
            rec = Blocks.get_by_height(i)   # Get existing entry from the DB (if any)
            if rec is not None:
                # Test if we have an orphan thats not already marked
                # Dont update any block info in the orphan, just mark the state
                if rec.hash != response["header"]["hash"] and rec.state != "orphan":
                    LOGGER.warn("Found an orphan - height: {}, hash: {} vs {}".format(rec.height, rec.hash, response["header"]["hash"]))
                    rec.state = "orphan"
                    database.db.getSession().commit()
            else:
                # If it was not in the DB then we should add it now
                LOGGER.warn("Adding missing block - height: {}".format(response["header"]["height"]))
                missing_block = Blocks(hash = response["header"]["hash"],
                                   version = response["header"]["version"],
                                   height = response["header"]["height"],
                                   previous = response["header"]["previous"],
                                   timestamp = datetime.strptime(response["header"]["timestamp"][:-1], "%Y-%m-%dT%H:%M:%S+00:0"),
                                   output_root = response["header"]["output_root"],
                                   range_proof_root = response["header"]["range_proof_root"],
                                   kernel_root = response["header"]["kernel_root"],
                                   nonce = response["header"]["nonce"],
                                   edge_bits = response["header"]["edge_bits"],
                                   total_difficulty = response["header"]["total_difficulty"],
                                   secondary_scaling = response["header"]["secondary_scaling"],
                                   num_inputs = len(response["inputs"]),
                                   num_outputs = len(response["outputs"]),
                                   num_kernels = len(response["kernels"]),
                                   fee = sum(k["fee"] for k in response["kernels"]),
                                   lock_height = response["kernels"][0]["lock_height"] if len(response["kernels"]) > 0 else 0,
                                   total_kernel_offset = response["header"]["total_kernel_offset"],
                                   state = "missing")
                database.db.createDataObj(missing_block)
        except Exception as e:
            LOGGER.error("Something went wrong: {} - {}".format(e, traceback.print_stack()))
        sys.stdout.flush()
    # db.set_last_run(PROCESS, str(time.time()))
    database.db.getSession().commit()
    LOGGER.warn("=== Completed {}".format(PROCESS))



if __name__ == "__main__":
    main()
