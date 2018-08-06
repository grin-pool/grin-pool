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

# Add a grin network stats record ~per block

import sys
import requests
import json
from time import sleep

from grinlib import lib
from grinlib import grin
from grinbase.model.blocks import Blocks
from grinbase.model.grin_stats import Grin_stats

PROCESS = "grinStats"
LOGGER = None
CONFIG = None

def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    # Connect to DB
    database = lib.get_db()

    check_interval = float(CONFIG[PROCESS]["check_interval"])
    avg_over_range = int(CONFIG[PROCESS]["avg_over_range"])

    # Find the height of the latest stats record
    last_height = 0
    latest_stat = Grin_stats.get_latest()
    if latest_stat == None:
        # Special case for new pool startup
        seed_stat = Grin_stats(height=0, timestamp=0, gps=0, difficulty=0, total_utxoset_size=0, total_transactions=0)
        database.db.createDataObj(seed_stat)
    else:
        last_height = latest_stat.height
    LOGGER.warn("Starting at block height: {}".format(last_height))

    # Generate status records - one per grin block
    while True:
        latest = grin.get_current_height()
        while latest > last_height:
            try:
                # Get the most recent blocks from which to generate the stats
                previous = Grin_stats.get_by_height(last_height)
                recent_blocks = Blocks.get_by_height(last_height, avg_over_range)
                if len(recent_blocks) < 3:
                    # We dont have at least 3 of these blocks in the DB
                    last_height = last_height+1
                    continue
                height = last_height + 1# recent_blocks[-1].height
                timestamp = recent_blocks[-1].timestamp
                difficulty = recent_blocks[-1].total_difficulty - recent_blocks[-2].total_difficulty
                gps = lib.calculate_graph_rate(difficulty, recent_blocks[0].timestamp, recent_blocks[-1].timestamp, avg_over_range)
                total_utxoset_size = 0
                total_transactions = 0
                if previous is not None:
                    total_utxoset_size = previous.total_utxoset_size + 1 # XXX TODO: Track this
                    total_transactions = previous.total_transactions + 2 # XXX TODO: Track this
                new_stats = Grin_stats(
                                   height = height,
                                   timestamp = timestamp,
                                   gps = gps,
                                   difficulty = difficulty,
                                   total_utxoset_size = total_utxoset_size,
                                   total_transactions = total_transactions,
                )
                LOGGER.warn("Added GrinStats for block: {} - {} {} {} {}".format(height, gps, difficulty, total_utxoset_size, total_transactions))
                database.db.createDataObj(new_stats)
                last_height = last_height + 1
            except Exception as e:
                LOGGER.error("Something went wrong: {}".format(e))
        sys.stdout.flush()
        sleep(check_interval)
    LOGGER.warn("=== Completed {}".format(PROCESS))


if __name__ == "__main__":
    main()
