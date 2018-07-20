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

# Checks blocks found by the pool to see if they are ready to be unlocked and made available for payout.
#

import sys
import requests
import json
import time

from grinlib import lib
from grinbase.model.pool_blocks import Pool_blocks

PROCESS = "poolblockUnlocker"
LOGGER = None
CONFIG = None

def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    # Connect to DB
    database = lib.get_db()

    # Get the list of pool_blocks that are
    # old enough to unlock and
    # are not orphan blocks

    # XXX TODO: The node may not be synced, may need to wait?
    #  move this functionality to the lib

    grin_api_url = "http://" + CONFIG["grin_node"]["address"] + ":" + CONFIG["grin_node"]["api_port"]
    status_url = grin_api_url + "/v1/status"
    blocks_url = grin_api_url + "/v1/blocks/"
    block_locktime = int(CONFIG[PROCESS]["block_locktime"])
    block_expiretime = int(CONFIG[PROCESS]["block_expiretime"])
    LOGGER.warn("using locktime: {}, expiretime: {}".format(block_locktime, block_expiretime))

    response = requests.get(status_url)
    latest = int(response.json()["tip"]["height"])
    LOGGER.warn("Latest: {}".format(latest))

    new_poolblocks = Pool_blocks.get_all_new()
    for pb in new_poolblocks:
        if pb.height < (latest - block_expiretime):
            # Dont re-process very old blocks - protection against duplicate payouts.
            LOGGER.warn("Processed expired pool block at height: {}".format(pb.height))
            pb.state = "expired"
            continue
        # XXX TODO: More robust request handling
        response = requests.get(blocks_url + str(pb.height)).json()
        # print("Response: {}".format(response))
        if int(response["header"]["nonce"]) != int(pb.nonce):
            LOGGER.warn("Processed orphan pool block at height: {}".format(pb.height))
            pb.state = "orphan"
        else:
            if pb.height < (latest - block_locktime):
                LOGGER.warn("Unlocking pool block at height: {}".format(pb.height))
                pb.state = "unlocked"
        sys.stdout.flush()

    # db.set_last_run(PROCESS, str(time.time()))
    database.db.getSession().commit()
    LOGGER.warn("=== Completed {}".format(PROCESS))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
