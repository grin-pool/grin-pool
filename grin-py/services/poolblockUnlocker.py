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
import db_api
import lib

PROCESS = "poolblockUnlocker"


def main():
    db = db_api.db_api()
    config = lib.get_config()
    logger = lib.get_logger(PROCESS)
    logger.warn("=== Starting {}".format(PROCESS))

    # Get the list of pool_blocks that are
    # old enough to unlock and
    # are not orphan blocks

    logger.debug(config.sections())

    # XXX TODO: The node may not be synced, may need to wait?

    grin_api_url = "http://" + config["grin_node"]["address"] + ":" + config["grin_node"]["api_port"]
    status_url = grin_api_url + "/v1/status"
    blocks_url = grin_api_url + "/v1/blocks/"
    block_locktime = int(config[PROCESS]["block_locktime"])
    block_expiretime = int(config[PROCESS]["block_expiretime"])

    response = requests.get(status_url)
    latest = int(response.json()["tip"]["height"])
    logger.debug("Latest: {}", format(latest))

    new_poolblocks = db.get_poolblocks_by_state('new')
    for (pb_hash, pb_height, pb_nonce, pb_actual_difficulty, pb_net_difficulty,
         pb_timestamp, pb_found_by, pb_state) in new_poolblocks:
        if pb_height < latest - block_expiretime:
            # Dont re-process very old blocks - protection against duplicate payouts.
            logger.debug("Processed expired pool block at height: {}".format(pb_height))
            db.set_poolblock_state("expired", int(pb_height))
            continue
        response = requests.get(blocks_url + str(pb_height)).json()
        # print("Response: {}".format(response))
        if int(response["header"]["nonce"]) != int(pb_nonce):
            logger.debug("Processed orphan pool block at height: {}".format(pb_height))
            db.set_poolblock_state("orphan", int(pb_height))
        else:
            if pb_height < (latest - block_locktime):
                logger.debug("Unlocking pool block at height: {}".format(pb_height))
                db.set_poolblock_state("unlocked", int(pb_height))
        sys.stdout.flush()

    db.set_last_run(PROCESS, str(time.time()))
    db.close()
    logger.warn("=== Completed {}".format(PROCESS))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
