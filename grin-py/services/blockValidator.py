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
import db_api
import lib

PROCESS = "blockValidator"


def main():
    db = db_api.db_api()
    config = lib.get_config()
    logger = lib.get_logger(PROCESS)
    logger.warn("=== Starting {}".format(PROCESS))

    grin_api_url = "http://" + config["grin_node"]["address"] + ":" + config["grin_node"]["api_port"]
    status_url = grin_api_url + "/v1/status"
    blocks_url = grin_api_url + "/v1/blocks/"
    validation_depth = int(config[PROCESS]["validation_depth"])

    response = requests.get(status_url)
    latest = int(response.json()["tip"]["height"])
    last = latest - validation_depth  # start a reasonable distance back
    logger.warn("Starting from block #{}".format(last))
    #    last = 0
    for i in range(last, latest):
        url = blocks_url + str(i)
        response = requests.get(url).json()
        # print("{}: {}".format(response["header"]["height"], response["header"]["hash"]))
        data_block = (response["header"]["hash"],
                      response["header"]["version"],
                      response["header"]["height"],
                      response["header"]["previous"],
                      response["header"]["timestamp"][:-1],
                      response["header"]["output_root"],
                      response["header"]["range_proof_root"],
                      response["header"]["kernel_root"],
                      response["header"]["nonce"],
                      response["header"]["total_difficulty"],
                      response["header"]["total_kernel_offset"])

        try:
            rec = db.get_blocks_by_height([i])
            if len(rec) > 0:
                r = rec[0]
                #print("Got block {} at height {}".format(r[0], r[2]))
                if r[0] != response["header"]["hash"]:
                    logger.warn("Found an orphan - height: {}, hash: {} vs {}".format(r[2], r[0], response["header"]["hash"]))
                    db.set_block_state("orphan", int(i))
            else:
                logger.warn("Adding missing block - height: {}".format(response["header"]["height"]))
                # XXX TODO:  Probably want to mark it as "missing" so we know it was filled in after the fact?
                db.add_blocks([data_block], True)
        except:
            # XXX TODO: Something
            pass
        sys.stdout.flush()
    db.set_last_run(PROCESS, str(time.time()))
    db.close()


if __name__ == "__main__":
    main()
