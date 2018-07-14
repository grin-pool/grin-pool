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
import db_api
import lib


def get_current_height(url):
    response = requests.get(url)
    latest = response.json()["tip"]["height"]
    return latest


def main():
    db = db_api.db_api()
    config = lib.get_config()

    grin_api_url = "http://" + config["grin_node"]["address"] + ":" + config["grin_node"]["api_port"]
    status_url = grin_api_url + "/v1/status"
    blocks_url = grin_api_url + "/v1/blocks/"
    check_interval = float(config["blockwatcher"]["check_interval"])

    last = get_current_height(status_url)
    while True:
        latest = get_current_height(status_url)
        for i in range(last + 1, latest + 1):
            last = latest
            url = blocks_url + str(i)
            response = requests.get(url).json()
            print("New Block: {} at {}".format(response["header"]["hash"],
                                               response["header"]["height"]))
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
                db.add_blocks([data_block])
            except:
                pass
        sys.stdout.flush()
        sleep(check_interval)


if __name__ == "__main__":
    main()
