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

# Check for earliest "dirty" stats and re-calcualte from there up to current height

import sys
import requests
import json
import time

from grinlib import lib
from grinlib import grin
from grinlib import grinstats
from grinlib import poolstats
from grinlib import workerstats

from grinbase.model.grin_stats import Grin_stats
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.worker_stats import Worker_stats

PROCESS = "statsValidator"
LOGGER = None
CONFIG = None

def main():
    global LOGGER
    global CONFIG

    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    database = lib.get_db()
    LOGGER.warn("=== Starting {}".format(PROCESS))
    
    check_interval = float(CONFIG[PROCESS]["check_interval"])
    max_rebuild_depth = float(CONFIG[PROCESS]["max_rebuild_depth"])
    avg_over_range_grin = int(CONFIG["grinStats"]["avg_over_range"])
    avg_over_range_pool = int(CONFIG["poolStats"]["avg_over_range"])
    avg_over_range_worker = int(CONFIG["workerStats"]["avg_over_range"])

    current_height = grin.blocking_get_current_height()
    rebuild_height = current_height - max_rebuild_depth

    while True:
        # Check for dirty worker stats
        dirty = Worker_stats.get_first_dirty(rebuild_height)
        while dirty is not None:
            LOGGER.warn("Recalculating Worker Stats for {} from {}".format(dirty.height, avg_over_range_worker))
            end_height = workerstats.recalculate(dirty.height, avg_over_range_worker)
            LOGGER.warn("Finished Recalculating Worker Stats for {} - {}".format(dirty.height, end_height))
            dirty = Worker_stats.get_first_dirty()
        # Check for dirty pool stats
        dirty = Pool_stats.get_first_dirty(rebuild_height)
        if dirty is not None:
            LOGGER.warn("Recalculating Pool Stats from {}".format(dirty.height))
            end_height = poolstats.recalculate(dirty.height, avg_over_range_pool)
            LOGGER.warn("Finished Recalculating Pool Stats: {} - {}".format(dirty.height, end_height))
# Grin blocks and therefore grin stats cant be dirty
#        # Check for dirty grin stats
#        dirty = Grin_stats.get_first_dirty()
#        if dirty is not None:
#            LOGGER.warn("Recalculating Grin Stats from {}".format(dirty.height))
#            end_height = grinstats.recalculate(dirty.height, avg_over_range_grin)
#            LOGGER.warn("Finished Recalculating Grin Stats: {} - {}".format(dirty.height, end_height))

        sys.stdout.flush()
        time.sleep(check_interval)

    LOGGER.warn("=== Completed {}".format(PROCESS))


if __name__ == "__main__":
    main()
