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

# Audit history of paid blocks to see if we paid out for orphans

import sys
import requests
import json
import time

from grinlib import lib
from grinlib import grin
from grinbase.model.pool_blocks import Pool_blocks

PROCESS = "auditPoolblocks"
LOGGER = None
CONFIG = None

def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    # Connect to DB
    database = lib.get_db()

    # Get the list of pool_blocks that have been paid
    paid_poolblocks = Pool_blocks.get_all_paid()
    print("Number of paid_poolblocks: {}".format(len(paid_poolblocks)))
    sys.stdout.flush()
 
    for pb in paid_poolblocks:
        # Get the blockchain data for this block
        response = grin.get_block_by_height(pb.height)
        if response == None:
            LOGGER.error("Failed to get block {}".format(pb.height))
            continue
        if int(response["header"]["nonce"]) != int(pb.nonce):
            print("")
            sys.stdout.flush()
            LOGGER.warn("Processed orphan pool block at height: {}".format(pb.height))
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
            
    
if __name__ == "__main__":
    main()
