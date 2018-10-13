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

from datetime import datetime
import time
import traceback
import json
import sys
#from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import threading
import socketserver

from grinlib import lib
from grinlib import grin
from grinbase.model.worker_shares import Worker_shares
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.pool_stats import Pool_stats

PROCESS = "shareAggr"

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


# Accept shares from both pool and grin logs.
# Add or merge (validate) them into a hash table
# Write the data out as worker_shares records
# Also creates Pool_blocks records for shares that are full solutions
class WorkerShares:
    def __init__(self, LOGGER):
        self.LOGGER = LOGGER
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
        duplicate = lib.get_db().db.createDataObj_ignore_duplicates(new_pool_block)
        if duplicate:
            self.LOGGER.warn("Failed to add duplicate Pool Block: {}".format(new_pool_block.height))
        else:
            self.LOGGER.warn("Added Pool Block: {}".format(new_pool_block.height))

    # For each worker with shares
    #   Create a worker_shares record and write it to the db
    def commit(self, height):
        print("self.shares.keys(): {}".format(self.shares.keys()))
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
            lib.get_db().db.createDataObj_ignore_duplicates(filler_shares_rec)
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
            lib.get_db().db.createDataObj_ignore_duplicates(new_shares_rec)
            # We added new worker share data, so if a Pool_stats record already exists at this height, we mark it dirty so it gets recalulated
            stats_rec = Pool_stats.get_by_height(height)
            if stats_rec is not None:
                stats_rec.dirty = True
                lib.get_db().db.getSession().commit()
            #self.LOGGER.warn("New worker share record: {}".format(new_shares_rec))

    def clear(self, height=None):
        if height is None:
            self.shares = {}
        else:
            self.shares.pop(height, None)

class ThreadedTCPServer(ThreadingMixIn, socketserver.TCPServer):
    """Handle requests in a separate thread."""


class ShareHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global LOGGER
        global SHARES
        global HEIGHT
        global GRINSHARE_HEIGHT
        global POOLSHARE_HEIGHT

        print("Reading from rfile")
        sys.stdout.flush()
        while True:
            raw_content = self.rfile.readline().decode('utf8')
            print("{}".format(raw_content))
            sys.stdout.flush()
            content = json.loads(raw_content)
            LOGGER.warn("Processing new {} message".format(content["type"]))
            #LOGGER.warn("PUT message: {}".format(content))
    
            # If there are no existing shares (height is None) then we start at the first share height we got
            if HEIGHT is None:
                HEIGHT = content["height"]
    
            LOGGER.warn("Current Height: {}, Share Height: {} - {}".format(HEIGHT, content["height"], content["nonce"]))
    
            # create a Share instance
            if content["type"] == "poolshare":
                s_timestamp = datetime.strptime(str(datetime.utcnow().year) + " " + content["log_timestamp"], "%Y %b %d %H:%M:%S.%f")
                s_height = int(content["height"])
                s_nonce = content["nonce"]
                s_difficulty = int(content["difficulty"])
                s_worker = content["worker"]
                #print("log_timestamp: {}, height: {}, nonce: {}, difficulty: {}, worker: {}".format(s_timestamp, s_height, s_nonce, s_difficulty, s_worker))
                new_share = Share(height=s_height, nonce=s_nonce, worker_difficulty=s_difficulty, timestamp=s_timestamp, found_by=s_worker)
                SHARES.add(new_share)
                POOLSHARE_HEIGHT = s_height
            elif content["type"] == "grinshare":
                s_timestamp = datetime.strptime(str(datetime.utcnow().year) + " " + content["log_timestamp"], "%Y %b %d %H:%M:%S.%f")
                s_hash = content["hash"]
                s_height = int(content["height"])
                s_nonce = content["nonce"]
                s_share_difficulty = int(content["share_difficulty"])
                s_network_difficulty = int(content["net_difficulty"])
                s_worker = content["worker"]
                s_share_is_solution = int(s_share_difficulty) >= int(s_network_difficulty)
                new_share = Share(hash=s_hash, height=s_height, nonce=s_nonce, share_difficulty=s_share_difficulty, network_difficulty=s_network_difficulty, timestamp=s_timestamp, found_by=s_worker, is_solution=s_share_is_solution, is_valid=True)
                SHARES.add(new_share)
                GRINSHARE_HEIGHT = s_height
            else:
                LOGGER.warn("Invalid message id: {}".format(content["id"]))
    
         
#            LOGGER.warn("HEIGHT: {}, POOLSHARE_HEIGHT: {}, GRINSHARE_HEIGHT: {}".format(HEIGHT, POOLSHARE_HEIGHT, GRINSHARE_HEIGHT))
#            while HEIGHT < POOLSHARE_HEIGHT and HEIGHT < GRINSHARE_HEIGHT:
#                LOGGER.warn("Commit shares for height: {}".format(HEIGHT))
#                SHARES.commit(HEIGHT)
#                SHARES.clear(HEIGHT)
#                HEIGHT = HEIGHT + 1

def ShareCommitScheduler(interval=15):
    global LOGGER
    global SHARES
    global HEIGHT
    global GRINSHARE_HEIGHT
    global POOLSHARE_HEIGHT
    LOGGER.warn("HEIGHT: {}, POOLSHARE_HEIGHT: {}, GRINSHARE_HEIGHT: {}".format(HEIGHT, POOLSHARE_HEIGHT, GRINSHARE_HEIGHT))
    # XXX TODO:  enhance
    while True:
        bc_height = grin.blocking_get_current_height()
        while (HEIGHT < POOLSHARE_HEIGHT and HEIGHT < GRINSHARE_HEIGHT) or (bc_height > HEIGHT):
            LOGGER.warn("Commit shares for height: {}".format(HEIGHT))
            SHARES.commit(HEIGHT)
            SHARES.clear(HEIGHT)
            HEIGHT = HEIGHT + 1
        time.sleep(interval)
    
            
def main():
    global LOGGER
    global CONFIG
    global SHARES
    global HEIGHT
    global GRINSHARE_HEIGHT
    global POOLSHARE_HEIGHT
    CONFIG = lib.get_config()

    # XXX TODO: Put in config
    HOST = "0.0.0.0"
    PORT = 80
    GRINSHARE_HEIGHT = 0
    POOLSHARE_HEIGHT = 0

    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    database = lib.get_db()
    HEIGHT = Worker_shares.get_latest_height()
    if HEIGHT is None:
        HEIGHT = grin.blocking_get_current_height()
    SHARES = WorkerShares(LOGGER)


    #server = ThreadedHTTPServer((HOST, PORT), ShareHandler)
    #server = HTTPServer((HOST, PORT), ShareHandler)

#    server = socketserver.TCPServer((HOST, PORT), ShareHandler)
#    server.handle_request()
#    server.server_close()

    commit_thread = threading.Thread(target = ShareCommitScheduler, args = (15, ))
    commit_thread.start()
    server = ThreadedTCPServer((HOST, PORT), ShareHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
