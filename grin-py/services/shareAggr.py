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
import dateutil.parser
import time
import traceback
import json
import sys
import os
import atexit
import threading
import pika

from grinlib import lib
from grinlib import grin

from grinbase.model.blocks import Blocks
from grinbase.model.worker_shares import Worker_shares
from grinbase.model.shares import Shares
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.worker_stats import Worker_stats # XXX TODO: mark worker_stats record dirty if that users worker_shares record is updated


# so hard...
import pprint
pp = pprint.PrettyPrinter(indent=4)

PROCESS = "shareAggr"

# globals used by shareHandler callback
SHARE_EXPIRETIME = None


class Share:
    def __init__(self, timestamp, height, nonce, found_by, edge_bits=0, worker_difficulty=1, hash=None, share_difficulty=None, network_difficulty=None, is_solution=None, is_valid=False, invalid_reason="None"):
        self.timestamp = timestamp
        self.height = height
        self.edge_bits = edge_bits
        self.nonce = nonce
        self.found_by = found_by
        self.worker_difficulty = worker_difficulty
        self.hash = hash
        self.share_difficulty = share_difficulty
        self.network_difficulty = network_difficulty
        self.is_solution = is_solution
        self.is_valid = is_valid
        self.invalid_reason = invalid_reason

    def __repr__(self):
        return "timestamp={}, height={}, edge_bits={}, nonce={},  found_by={}, hash={}, is_valid={}, invalid_reason={}".format(
            self.timestamp,
            self.height,
            self.edge_bits,
            self.nonce,
            self.found_by,
            self.hash,
            self.is_valid,
            self.invalid_reason,
        )


    # Merge data from share into self
    def merge(self, share, sharetype):
        # Validation
        if self.height != share.height:
            self.is_valid = False 
            self.invalid_reason = "Worker share height mismatch: Expected {}, got {}".format(self.height, share.height)
        if self.nonce != share.nonce:
            self.is_valid = False
            self.invalid_reason = "Worker share nonce mismatch: Expected {}, got {}".format(self.nonce, share.nonce)
        # Merge
        if self.edge_bits == 0:
            self.edge_bits = share.edge_bits 
        if sharetype == "grinshare":
            if share.is_valid == True:
                self.is_valid = True
                self.invalid_reason = "None"
            else:
                self.is_valid = False
                self.invalid_reason = share.invalid_reason
        if self.found_by <= 1:
            self.found_by = share.found_by
        if self.found_by == 0:
            self.found_by = 1 # CANT have user_id 0 else we crash
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
        # rmq info for acking committed shares
        self.rmq_ack = {}

    # Add or merge a share
    def add(self, share, sharetype, rmq_channel, rmq_delivery_tag):
        # Hash by height, user_id, then nonce
        if share.height not in self.shares:
            self.LOGGER.warn("New Share Height: {}".format(share.height))
            self.shares[share.height] = {}
        if share.nonce not in self.shares[share.height]:
            # self.LOGGER.warn("New Share: {}".format(share.nonce))
            self.shares[share.height][share.nonce] = share
        else: # A version of this share already exists, merge them
            # self.LOGGER.warn("Mergeing share: {}".format(self.shares[share.height][share.nonce]))
            self.shares[share.height][share.nonce].merge(share, sharetype)
        # Record the message info so we can ack it when we commit
        if share.height not in self.rmq_ack:
            self.rmq_ack[share.height] = {}
        if rmq_channel not in self.rmq_ack[share.height]:
            self.rmq_ack[share.height][rmq_channel] = []
        self.rmq_ack[share.height][rmq_channel].append(rmq_delivery_tag)


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

    # For each worker with shares at height
    #   Create a worker_shares record + a shares record for each pow type submitted, and write it to the db
    def commit(self, height=None):
        global HEIGHT
        if height is None:
            block_heights = list(self.shares.keys())
            try:
                # Process all heights, except
                # Dont process shares from current block or newer
                block_heights = [h for h in block_heights if h < HEIGHT]
            except ValueError as e:
                pass
        else:
            block_heights = [height]

        #pp.pprint(self.shares)

        if len(block_heights) > 0:
            self.LOGGER.warn("Committing shares for blocks: {}".format(block_heights))
 
        for height in block_heights:
            if height not in self.shares or len(self.shares[height]) == 0:
                # XXX TODO: Only create filler record if no records already exist for this height
                self.LOGGER.warn("Processed 0 shares in block {} - Creating filler record".format(height))
                # Even if there are no shares in the pool at all for this block, we still need to create a filler record at this height
                filler_worker_shares_rec = Worker_shares(
                        height = height,
                        user_id = 1,
                        timestamp = datetime.utcnow(),
                    )
                database.db.createDataObj(filler_worker_shares_rec)
                return 
        
            # Sort the shares by worker and graph size
            # byWorker is multi-level structure:
            # 1) hash by worker id
            # 2) hash by graph size
            # 3) List of shares
            byWorker = {}
            for hash in self.shares[height]:
                share = self.shares[height][hash]
                # Sort shares by worker
                if share.found_by not in byWorker:
                    byWorker[share.found_by] = {}
                if share.edge_bits not in byWorker[share.found_by]:
                    byWorker[share.found_by][share.edge_bits] = []
                #print("XXX Adding share to workerShares: {}".format(share))
                byWorker[share.found_by][share.edge_bits].append(share)
                # Create Pool_blocks for full solution shares
                if share.is_solution:
                    self.addPoolBlock(share)

            #pp.pprint(byWorker)
            # Create/update a Worker_shares record for each user and commit to DB
            # XXX TODO: Bulk Insert - will be needed when the pool has hundredes or thousands of workers
            for worker in byWorker:
                if worker == 0:
                    continue
                workerShares = byWorker[worker]
                #print("workerShares for {} = {}".format(worker, workerShares))
                # Count them (just for logging)
                num_valid_shares = 0
                num_invalid_shares = 0
                num_stale_shares = 0
                for graph_size in workerShares:
                    for share in workerShares[graph_size]:
                        if share.is_valid:
                            num_valid_shares += 1
                        elif share.is_valid == False and share.invalid_reason == 'too late':
                            num_stale_shares += 1
                        elif share.is_valid == False:
                            num_invalid_shares += 1
                self.LOGGER.warn("Processed {} shares in block {} for user_id {}: Valid: {}, stale: {}, invalid: {}".format(len(workerShares), height, worker, num_valid_shares, num_stale_shares, num_invalid_shares))
                pp.pprint(workerShares)

# xxx

                # Get any existing record for this worker at this height
                worker_shares_rec = Worker_shares.get_by_height_and_id(height, worker)
                existing = True
                if worker_shares_rec is None or len(worker_shares_rec) == 0:
                    # No existing record, create it
                    self.LOGGER.warn("This is a new share record for worker: {}".format(worker))
                    worker_shares_rec = Worker_shares(
                            height = height,
                            user_id = worker,
                            timestamp = datetime.utcnow(),
                        )
                    database.db.createDataObj(worker_shares_rec)
                    existing = False
                else:
                    print("XXXXXXXXXXXXXXXXXXXXX")
                    pp.pprint(worker_shares_rec)
                    worker_shares_rec = worker_shares_rec[0]
                # Create/update Shares records - one per graph size mined in this block
                #pp.pprint(workerShares)
                for a_share_list in workerShares.values():
                    for a_share in a_share_list:
                        if a_share.edge_bits == 0:
                            # We dont actually know what size this share was since we
                            # only got the pools half.  Its invalid anyway, so just ignore
                            # for now. XXX TODO something better
                            continue
                        #print("a_share = {}".format(a_share))
                        edge_bits = a_share.edge_bits
                        difficulty = a_share.share_difficulty
                        valid = 0
                        stale = 0
                        invalid = 0
                        if share.is_valid:
                            valid = 1
                        elif share.is_valid == False and share.invalid_reason == 'too late':
                            stale = 1
                        else:
                            invalid = 1
                        worker_shares_rec.add_shares(a_share.edge_bits, a_share.share_difficulty, valid, invalid, stale)
                try:
                    database.db.getSession().commit()
                    # After we commit share data we need to ack the rmq messages and clear the committed shares
                    self.ack_and_clear(height)
                    # We added new worker share data, so if a Pool_stats record already exists at this height,
                    # we mark it dirty so it gets recalulated by thre shareValidator service
                    stats_rec = Pool_stats.get_by_height(height)
                    if stats_rec is not None:
                        stats_rec.dirty = True
                    # Commit any changes
                    if existing == True:
                        self.LOGGER.warn("XXX UPDATED worker share record: {}".format(worker_shares_rec))
                    else:
                        self.LOGGER.warn("XXX NEW worker share record: {}".format(worker_shares_rec))
                    database.db.getSession().commit()
                except Exception as e:
                    self.LOGGER.error("Failed to commit worker shares for {} at height {} - {}".format(worker, height, e))
    
    def ack_and_clear(self, height):
        shares = self.shares.pop(height, None)
        pp.pprint(shares)
        if shares is None:
            return
        rmq_ack = self.rmq_ack.pop(height, None)
        if rmq_ack is None:
            return
        print("RMQ ACK LIST: {}".format(rmq_ack))
        for channel, tags in rmq_ack.items():
            # Option 1, ack individual messages
            #for tag in tags:
            #    channel.basic_ack(delivery_tag = tag)
            # Option 2, bulk-ack up to the latest message we processed
            channel.basic_ack(delivery_tag=max(tags), multiple=True)
            # Option 3, (not implemented) make sure we have processed all the messages
            #  up to the latest message we processed, and if not, 
            #  do all the accounting necessary to bulk ack as much as possible

def share_handler(ch, method, properties, body):
    global LOGGER
    global SHARES
    global HEIGHT
    global GRINSHARE_HEIGHT
    global POOLSHARE_HEIGHT
    global SHARE_EXPIRETIME

    LOGGER.warn("= Starting ShareHandler")
    sys.stdout.flush()
    print("{}".format(body.decode("utf-8") ))
    sys.stdout.flush()
    content = json.loads(body.decode("utf-8"))
    LOGGER.warn("Processing new {} message".format(content["type"]))
    # LOGGER.warn("PUT message: {}".format(content))
    LOGGER.warn("Current Share -  Height: {} - Nonce: {}".format(content["height"], content["nonce"]))

    # Dont process very old shares
    if (HEIGHT - int(content["height"])) > SHARE_EXPIRETIME:
        ch.basic_ack(delivery_tag = method.delivery_tag)
        LOGGER.warn("Dropping expired share - Type: {}, Height: {}, Nonce: {}".format(content["type"], content["height"], content["nonce"]))
        return

    # create a Share instance
    if content["type"] == "poolshare":
        s_timestamp = dateutil.parser.parse(str(datetime.utcnow().year) + " " + content["log_timestamp"])
        s_height = int(content["height"])
        s_nonce = content["nonce"]
        s_difficulty = int(content["difficulty"])
        s_worker = int(content["worker"])
        new_share = Share(
                height = s_height, 
                nonce = s_nonce, 
                worker_difficulty = s_difficulty, 
                timestamp = s_timestamp, 
                found_by = s_worker,
            )
        SHARES.add(new_share, content["type"], ch, method.delivery_tag)
        POOLSHARE_HEIGHT = s_height
    elif content["type"] == "grinshare":
        s_timestamp = dateutil.parser.parse(content["log_timestamp"])
        try:
            s_hash = content["hash"]
        except KeyError:
            # invalid shares may not have a hash field
            s_hash = 0
        s_height = int(content["height"])
        # Special Case - round edge_bits up to our minimum C29, and C31
        s_edge_bits = int(content["edge_bits"])
        if(s_edge_bits < 29):
            s_edge_bits = 29
            s_valid = False
            s_error = "Invalid POW size"
        if(s_edge_bits == 30):
            s_edge_bits = 31
            s_valid = False
            s_error = "Invalid POW size"
        s_nonce = content["nonce"]
        try:
            s_share_difficulty = int(content["share_difficulty"])
            s_network_difficulty = int(content["net_difficulty"])
        except KeyError:
            s_share_difficulty = 0
            s_network_difficulty = 0
        try:
            s_error = content["error"]
            s_valid = False
        except KeyError:
            s_error = None
            s_valid = True
        s_worker = 1 # int(content["worker"])
        s_share_is_solution = int(s_share_difficulty) >= int(s_network_difficulty)
        new_share = Share(
                hash=s_hash, 
                height=s_height, 
                nonce=s_nonce, 
                edge_bits=s_edge_bits, 
                share_difficulty=s_share_difficulty, 
                network_difficulty=s_network_difficulty, 
                timestamp=s_timestamp, 
                found_by=s_worker, 
                is_solution=s_share_is_solution, 
                is_valid=s_valid, 
                invalid_reason=s_error
            )
        SHARES.add(new_share, content["type"], ch, method.delivery_tag)
        GRINSHARE_HEIGHT = s_height
    else:
        LOGGER.warn("Invalid message id: {}".format(content["id"]))
    sys.stdout.flush()

     
def ShareCommitScheduler(interval, database):
    global LOGGER
    global SHARES
    global HEIGHT
    global GRINSHARE_HEIGHT
    global POOLSHARE_HEIGHT
    database = lib.get_db()
    

    try:
        # XXX TODO:  enhance
        while True:
            bc_height = Blocks.get_latest().height # grin.blocking_get_current_height()
            LOGGER.warn("HEIGHT={}, POOLSHARE_HEIGHT={}, GRINSHARE_HEIGHT={}".format(HEIGHT, POOLSHARE_HEIGHT, GRINSHARE_HEIGHT))
            while (HEIGHT < POOLSHARE_HEIGHT and HEIGHT < GRINSHARE_HEIGHT) or (bc_height > HEIGHT):
                # Commit and purge current block share data if we are starting a new block
                LOGGER.warn("Commit shares for height: {}".format(HEIGHT))
                # time.sleep(5) # Give straggler shares a chance to come in
                SHARES.commit(HEIGHT)
                HEIGHT = HEIGHT + 1
            # Commit and purge all old share data (except current block) every 'interval' seconds
            try:
                SHARES.commit() # All except current block
            except Exception as e:
                LOGGER.error("Failed to commit: {}".format(e))
            time.sleep(interval)
    except Exception as e:
        LOGGER.error("Something went wrong: {}\n{}".format(e, traceback.format_exc().splitlines()))
        time.sleep(interval)
    lib.teardown_db()
    
def RmqConsumer(host):
    global LOGGER
    global RABBITMQ_USER
    global RABBITMQ_PASSWORD
    while True:
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=host,
                    credentials=credentials))
            channel = connection.channel()
            channel.basic_qos(prefetch_size=0, prefetch_count=0, all_channels=True)
            channel.basic_consume(share_handler,
                                  queue='grinshares',
                                  no_ack=False)
            channel.basic_consume(share_handler,
                                  queue='poolshares',
                                  no_ack=False)
            channel.start_consuming()
        except Exception as e:
            LOGGER.error("Something went wrong: {}\n{}".format(e, traceback.format_exc().splitlines()))
            sys.stdout.flush()
            time.sleep(10)

            
def main():
    global LOGGER
    global CONFIG
    global SHARES
    global HEIGHT
    global GRINSHARE_HEIGHT
    global POOLSHARE_HEIGHT
    global SHARE_EXPIRETIME
    global database
    global RABBITMQ_USER
    global RABBITMQ_PASSWORD
    CONFIG = lib.get_config()
    atexit.register(lib.teardown_db)

    GRINSHARE_HEIGHT = 0
    POOLSHARE_HEIGHT = 0

    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    SHARE_EXPIRETIME = int(CONFIG[PROCESS]["share_expire_time"])
    commit_interval = int(CONFIG[PROCESS]["commit_interval"])
    rmq_endpoints = json.loads(CONFIG[PROCESS]["rmq"])

    RABBITMQ_USER = os.environ["RABBITMQ_USER"]
    RABBITMQ_PASSWORD = os.environ["RABBITMQ_PASSWORD"]

    database = lib.get_db()
    HEIGHT = Worker_shares.get_latest_height()
    while HEIGHT is None:
        LOGGER.warn("Waiting on the first grin block...")
        time.sleep(5)
        latest_block = Blocks.get_latest()
        if latest_block is not None:
            HEIGHT = latest_block.height
        
    SHARES = WorkerShares(LOGGER)

    ##
    # Start a thread to commit shares 
    commit_thread = threading.Thread(target = ShareCommitScheduler, args = (commit_interval, database, ))
    commit_thread.start()

    ##
    # Start a pika consumer thread for each rabbit we want to consume from
    for rmq in rmq_endpoints:
        rmq_thread = threading.Thread(target = RmqConsumer, args = (rmq, ))
        rmq_thread.start()

if __name__ == "__main__":
    main()

