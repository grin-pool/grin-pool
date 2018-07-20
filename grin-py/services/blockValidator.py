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
import lib

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

    grin_api_url = "http://" + CONFIG["grin_node"]["address"] + ":" + CONFIG["grin_node"]["api_port"]
    status_url = grin_api_url + "/v1/status"
    blocks_url = grin_api_url + "/v1/blocks/"
    validation_depth = int(CONFIG[PROCESS]["validation_depth"])

    response = requests.get(status_url)
    latest = int(response.json()["tip"]["height"])
    last = latest - validation_depth  # start a reasonable distance back
    LOGGER.warn("Starting from block #{}".format(last))
    #    last = 0
    for i in range(last, latest):
        url = blocks_url + str(i)
        response = requests.get(url).json()
        # print("{}: {}".format(response["header"]["height"], response["header"]["hash"]))
        try:
            rec = Blocks.get_by_height([i])
            if rec is not None:
                #print("Got block {} at height {}".format(r[0], r[2]))
                if rec.hash != response["header"]["hash"]:
                    LOGGER.warn("Found an orphan - height: {}, hash: {} vs {}".format(rec.height, rec.hash, response["header"]["hash"]))
                    rec.state = "orphan"
                    db.set_block_state("orphan")
            else:
                LOGGER.warn("Adding missing block - height: {}".format(response["header"]["height"]))
                # XXX TODO:  Probably want to mark it as "missing" so we know it was filled in after the fact?
                missing_block = Blocks(hash=response["header"]["hash"],
                                       version=response["header"]["version"],
                                       height = response["header"]["height"],
                                       previous = response["header"]["previous"],
                                       timestamp = response["header"]["timestamp"][:-1],
                                       output_root = response["header"]["output_root"],
                                       range_proof_root = response["header"]["range_proof_root"],
                                       kernel_root = response["header"]["kernel_root"],
                                       nonce = response["header"]["nonce"],
                                       total_difficulty = response["header"]["total_difficulty"],
                                       total_kernel_offset = response["header"]["total_kernel_offset"] )
                database.db.createDataObj(missing_block)
        except Exception as e:
            # XXX TODO: Something more ?
            LOGGER.error("Something went wrong: {}".format(e))
        sys.stdout.flush()
    # db.set_last_run(PROCESS, str(time.time()))
    # db.close()
    database.db.getSession().commit()


if __name__ == "__main__":
    main()
