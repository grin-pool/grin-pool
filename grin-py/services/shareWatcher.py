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

# Watches the pool logs and adds the records for pool shares:
#   pool log -> pool_shares: height, nonce, *user_address*, *expected_difficulty*

import sys
import subprocess
from threading import Thread
import re
import glob
from datetime import datetime
import time
import traceback

from grinlib import lib
from grinbase.model.worker_shares import Worker_shares
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.pool_stats import Pool_stats

PROCESS = "shareWatcher"

# XXX TODO: Move to config
DIFFICULTY = 29


class Share:
    def __init__(self, timestamp, height, nonce, found_by, worker_difficulty=1, hash=None, share_difficulty=None, network_difficulty=None, is_solution=None, is_valid=False, invalid_reason="None"):
        self.timestamp = timestamp
        self.height = height
        self.nonce = nonce
        self.found_by = found_by
        self.worker_difficulty = worker_difficulty
        self.hash = hash
        self.share_difficulty = share_difficulty
        self.network_difficulty = network_difficulty
        self.is_solution = is_solution
        self.is_valid = is_valid
        self.invalid_reason = invalid_reason

    # Merge data from share into self
    def merge(self, share):
        # Validation
        if self.height != share.height:
            self.is_valid = False 
            self.invalid_reason = "Worker share height mismatch: Expected {}, got {}".format(self.height, share.height)
        if self.nonce != share.nonce:
            self.is_valid = False
            self.invalid_reason = "Worker share nonce mismatch: Expected {}, got {}".format(self.nonce, share.nonce)
        # Merge
        if share.is_valid == True:
            self.is_valid = True
        if self.found_by == "GrinPool":
            self.found_by = share.found_by
        if self.worker_difficulty > share.worker_difficulty:
            self.worker_difficulty = share.worker_difficulty
        if self.hash is None:
            self.hash = share.hash
        if self.share_difficulty is None:
            self.share_difficulty = share.share_difficulty
        if self.network_difficulty is None:
            self.network_difficulty = share.network_difficulty
        if self.is_solution is None:
            self.is_solution = share.is_solution


# Consumes log messages, extracts pool shares, provides itr to consume
class PoolShareItr:
    def __init__(self, sourceItr):
        self.source = sourceItr
        self.poolShareRegex = r'^(.+) WARN .+ Got share at height (\d+) with nonce (\d+) with difficulty (\d+) from worker (.+)$'

    def __iter__(self):
        return self

    def __next__(self):
        for msg in self.source:
            try:
                if 'Got share at height' in msg:
                    match = re.search(self.poolShareRegex, msg)
                    if match and match.group(0):
                        # We found a pool share log message, parse it and return a pool share object
                        s_timestamp = datetime.strptime(str(datetime.utcnow().year) + " " + match.group(1), "%Y %b %d %H:%M:%S.%f")
                        s_height = int(match.group(2))
                        s_nonce = match.group(3)
                        s_difficulty = int(match.group(4))
                        s_worker = match.group(5)
                        # Create a new record
                        new_share = Share(height=s_height, nonce=s_nonce, worker_difficulty=s_difficulty, timestamp=s_timestamp, found_by=s_worker)
                        # LOGGER.warn("New PoolShare: {}".format(new_share.nonce))
                        return new_share
            except Exception as e:
                pass
        raise StopIteration


# Consumes log messages, extracts grin shares, provides itr to consume
class GrinShareItr:
    def __init__(self, sourceItr):
        self.source = sourceItr
        self.poolShareRegex = r'^(.+) INFO .+ Got share for block: hash (.+), height (\d+), nonce (\d+), difficulty (\d+)/(\d+), submitted by (.+)$'

    def __iter__(self):
        return self

    def __next__(self):
        for msg in self.source:
            try:
                if "Got share for block:" in msg:
                    match = re.search(self.poolShareRegex, msg)
                    if match and match.group(0):
                        # We found a grin share log message, parse it and return a grin share object
                        s_timestamp = datetime.strptime(str(datetime.utcnow().year) + " " + match.group(1), "%Y %b %d %H:%M:%S.%f")
                        s_hash = match.group(2)
                        s_height = int(match.group(3))
                        s_nonce = match.group(4)
                        s_share_difficulty = int(match.group(5))
                        s_network_difficulty = int(match.group(6))
                        s_worker = match.group(7)
                        if s_share_difficulty >= s_network_difficulty:
                            share_is_solution = True
                        else:
                            share_is_solution = False
                        # Create a new record
                        new_share = Share(hash=s_hash, height=s_height, nonce=s_nonce, share_difficulty=s_share_difficulty, network_difficulty=s_network_difficulty, timestamp=s_timestamp, found_by=s_worker, is_solution=share_is_solution, is_valid=True)
                        # LOGGER.warn("New GrinShare: {}".format(new_share.nonce))
                        return new_share
            except Exception as e:
                pass
        raise StopIteration

# Accept shares from both pool and grin logs.
# Add or merge (validate) them into a hash table
# Write the data out as worker_shares records
# Also creates Pool_blocks records for shares that are full solutions
class WorkerShares:
    def __init__(self, LOGGER, db):
        self.LOGGER = LOGGER
        self.db = db
        # shares is a 2-level hash table:
        # 1) block height
        # 2) share nonce
        self.shares = {}

    # Add or merge a share
    def add(self, share):
        # Hash by height, worker, then nonce
        if share.height not in self.shares:
            self.LOGGER.warn("New Share Height: {}".format(share.height))
            self.shares[share.height] = {}
        if share.nonce not in self.shares[share.height]:
            # self.LOGGER.warn("New Share: {}".format(share.nonce))
            self.shares[share.height][share.nonce] = share
        else: # A version of this share already exists, merge them
            # self.LOGGER.warn("Mergeing share: {}".format(self.shares[share.height][share.nonce]))
            self.shares[share.height][share.nonce].merge(share)

    # Add a Pool_block (for full solutions)
    def addPoolBlock(self, share):
        if share.is_valid == False:
            return
        new_pool_block = Pool_blocks(hash=share.hash, height=share.height, nonce=share.nonce, actual_difficulty=share.share_difficulty, net_difficulty=share.network_difficulty, timestamp=share.timestamp, found_by=share.found_by, state="new")
        duplicate = self.db.createDataObj_ignore_duplicates(new_pool_block)
        if duplicate:
            self.LOGGER.warn("Failed to add duplicate Pool Block: {}".format(new_pool_block.height))
        else:
            self.LOGGER.warn("Added Pool Block: {}".format(new_pool_block.height))

    # For each worker with shares
    #   Create a worker_shares record and write it to the db
    def commit(self, height):
        if height not in self.shares or len(self.shares[height]) == 0:
            self.LOGGER.warn("Processed 0 shares in block {} - Creatiing filler record".format(height))
            # Even if there are no shares in the pool at all for this block, we still need to create a filler record at this height
            filler_shares_rec = Worker_shares(
                    height = height,
                    worker = "GrinPool",
                    timestamp = datetime.utcnow(),
                    difficulty = DIFFICULTY,
                    valid = 0,
                    invalid = 0
                )
            self.db.createDataObj_ignore_duplicates(filler_shares_rec)
            return
        
        byWorker = {}
        for nonce in self.shares[height]:
            share = self.shares[height][nonce]
            # Sort shares by worker
            if share.found_by not in byWorker:
                byWorker[share.found_by] = []
            byWorker[share.found_by].append(share)
            # Create Pool_blocks for full solution shares
            if share.is_solution:
                self.addPoolBlock(share)

        # Create a Worker_shares record for each user and commit to DB
        # XXX TODO: Bulk Insert - will be needed when the pool has hundredes or thousands of workers
        for worker in byWorker:
            workerShares = byWorker[worker]
# Not possible?
#            if len(workerShares) == 0:
#                continue
            self.LOGGER.warn("Processed {} shares in block {} for worker {}".format(len(workerShares), height, worker))
            valid_list = [share.is_valid for share in workerShares]
            # self.LOGGER.warn("xxx:  {}".format(valid_list))
            num_valid = sum([int(share.is_valid) for share in workerShares])
            new_shares_rec = Worker_shares(
                    height = height,
                    worker = worker,
                    timestamp = datetime.utcnow(),
                    difficulty = DIFFICULTY,
                    valid = num_valid,
                    invalid = len(workerShares) - num_valid
                )
            self.db.createDataObj_ignore_duplicates(new_shares_rec)
            # We added new worker share data, so if a Pool_stats record already exists at this height, we mark it dirty so it gets recalulated
            stats_rec = Pool_stats.get_by_height(height)
            if stats_rec is not None:
                stats_rec.dirty = True
                database.db.getSession().commit()
            self.LOGGER.warn("New worker share record: {}".format(new_shares_rec))

    def clear(self, height=None):
        if height is None:
            self.shares = {}
        else:
            self.shares.pop(height, None)


class ShareWatcher:
    def __init__(self, CONFIG, LOGGER):
        self.POOL_LOG = CONFIG["stratum"]["log_dir"] + "/" + CONFIG["stratum"]["log_filename"]
        self.GRIN_LOG = CONFIG["grin_node"]["log_dir"] + "/" + CONFIG["grin_node"]["log_filename"]
        self.LOGGER = LOGGER
        self.database = lib.get_db()
        self.shares = WorkerShares(LOGGER, self.database.db)
        
    def processNewLogs(self):
        self.LOGGER.warn("Processing new logs from: {}".format(self.POOL_LOG))
        self.LOGGER.warn("Processing new logs from: {}".format(self.GRIN_LOG))
        # Get poolShares from the pool log
        poolLogItr = lib.PopenItr(['tail', '-F', self.POOL_LOG])
        poolShareItr = PoolShareItr(poolLogItr)
        # Get grinShares from the grin log
        grinLogItr = lib.PopenItr(['tail', '-F', self.GRIN_LOG])
        grinShareItr = GrinShareItr(grinLogItr)

        poolShare = next(poolShareItr)
        grinShare = next(grinShareItr)
        # height = min(grinShare.height, poolShare.height)
        height = Worker_shares.get_latest_height()
        # XXX TODO: Do I get 0 if no records exist?  None?  Something else?

        LOGGER.warn("Started {} at height: {}, with grin:{}, pool:{} ".format(PROCESS, height, grinShare.height, poolShare.height))

        while True:
            try:
                while grinShare.height == height and poolShare.height == height:
                    # Get the next share for each
                    poolShare = next(poolShareItr)
                    self.shares.add(poolShare)
                    grinShare = next(grinShareItr)
                    self.shares.add(grinShare)

                while poolShare.height == height:
                    poolShare = next(poolShareItr)
                    self.shares.add(poolShare)

                while grinShare.height == height:
                    grinShare = next(grinShareItr)
                    self.shares.add(grinShare)

                self.shares.commit(height)
                self.shares.clear(height)
                height = height + 1
                #LOGGER.getLogger(__name__).flush()

            except Exception as e:
                LOGGER.error("Something went wrong: {}".format(e))
                raise e


def main():
    global LOGGER
    global CONFIG
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)

    shareWatcher = ShareWatcher(CONFIG, LOGGER)
    shareWatcher.processNewLogs()


if __name__ == "__main__":
    main()
