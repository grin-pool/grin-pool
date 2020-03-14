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


# Performance Notes:
#   Testing shows that this can process about 150 messages / second
#   MySQL seems to max out at about 180 commits / second 
#   so thats 9000 messages (users) at full capacity


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
import redis
import re

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

# Name of this service
PROCESS = "shareAggr"

# Debung messages get printed?
debug = True

# Which RMQ servers to conect to. local cluster "rmq" by default
RMQ = "rmq"

# globals used by poolblock records
POOLBLOCK_MUTEX = threading.Lock()

# globals used by per-block per user aggrreagated rig shares records (stored in mysql)
SHARE_EXPIRETIME = 60*4 # ~4 hours (# blocks)
REDIS_SHAREDATA_KEY = "sharedata"
REDIS_SHAREDATA_EXPIRETIME = 60*60 # 1 hour
SHARES_MUTEX = threading.Lock()

# globals used by individual rig-data records (stored in redis)
REDIS_RIGDATA_KEY = "rigdata"
REDIS_RIGDATA_CACHE_EXPIRETIME = 60*60 # 1 hour
REDIS_RIGDATA_EXPIRETIME = 60*60*24*15 # 15 days
RIGDATA_GROUPSIZE = 5.0
RIGDATA_MUTEX = threading.Lock()
RIGDATA = {}

# Example share message:  {29: Shares { edge_bits: 29, accepted: 7, rejected: 0, stale: 0 }}
SHARE_RE = re.compile('{ edge_bits: (\d+), accepted: (\d+), rejected: (\d+), stale: (\d+) }')

# Add a Pool_block (for full solutions)
def addPoolBlock(logger, timestamp, height, hash, found_by, serverid):
    global POOLBLOCK_MUTEX
    POOLBLOCK_MUTEX.acquire()
    database = lib.get_db()
    try:
        logger.warn("Adding A PoolBlock: Timestamp: {}, ServerID: {}, Height: {}, Hash: {}".format(timestamp, serverid, height, hash))
        state = "new"
        this_block = Blocks.get_by_height(height)
        while this_block is None:
            this_block = Blocks.get_by_height(height) 
            time.sleep(1)
        nonce = this_block.nonce
        actual_difficulty = grin.difficulty(this_block.hash, this_block.edge_bits, this_block.secondary_scaling)
        net_difficulty = grin.get_network_difficulty(height)
        # Create the DB record
        new_pool_block = Pool_blocks(
                hash=hash, 
                height=height, 
                nonce=nonce, 
                actual_difficulty=actual_difficulty, 
                net_difficulty=net_difficulty, 
                timestamp=timestamp, 
                found_by=found_by, 
                state=state
            )
        duplicate = lib.get_db().db.createDataObj_ignore_duplicates(new_pool_block)
        if duplicate:
            logger.warn("Failed to add duplicate Pool Block: {}".format(height))
        else:
            logger.warn("Added Pool Block: {}".format(height))
    finally:
        POOLBLOCK_MUTEX.release()


# Accept a workers share record, add it to all the data structures we want
def addWorkerShares(logger, channel, delivery_tag, timestamp, height, worker, workerid, rig_id, agent, difficulty, shares_data):
    global debug
    global SHARES_MUTEX
    global SHARE_RE
    global REDIS_SHAREDATA_KEY
    global REDIS_SHAREDATA_EXPIRETIME
    global RIGDATA_MUTEX
    global REDIS_RIGDATA_KEY
    global RIGDATA_GROUPSIZE
    global REDIS_RIGDATA_CACHE_EXPIRETIME
    logger.warn("New Worker Shares: Height: {}, Worker: {}, RigID: {}, Agent: {}, Difficulty: {}, SharesData: {}".format(height, worker, rig_id, agent, difficulty, shares_data))
    # Parse the sharedata
    # TEST: shares_data = "{29: Shares { edge_bits: 29, accepted: 7, rejected: 0, stale: 0 }, 31: Shares { edge_bits: 31, accepted: 4, rejected: 0, stale: 0 }}"
    all_shares = SHARE_RE.findall(shares_data)
    #logger.warn("addWorkerShares processing all_shares: {}".format(all_shares))

    # God Damn REDIS - Convert all keys to strings
    worker = str(worker)
    rig_id = str(rig_id)
    workerid = str(workerid)

    for shares in all_shares:
        debug and logger.warn("shares: {}".format(shares))
        edge_bits, accepted, rejected, stale = shares
        # Adjust for minimum share difficulty
        accepted = int(accepted) * difficulty
        rejected = int(rejected) * difficulty
        stale    = int(stale)    * difficulty
        logger.warn("New Worker Shares: Difficulty: {}, Accepted: {}, Rejected: {}, Stale: {}".format(difficulty, accepted, rejected, stale))

        ##
        # Add the data to Aggregated counts of *all rigs* for this worker
        SHARES_MUTEX.acquire()
        try:
            redisdb = lib.get_redis_db()
            redis_key = "{}-{}".format(REDIS_SHAREDATA_KEY, height) 
            # Check for exisintg redis record
            sharedata = redisdb.get(redis_key)
            if sharedata is None:
                # Create a new record
                sharedata = { "timestamp": str(timestamp) }
            else:
                # Load existing record
                sharedata = json.loads(sharedata.decode())
            # Merge in this shares data
            if worker not in sharedata:
                sharedata[worker] = {}
            if edge_bits not in sharedata[worker]:
                sharedata[worker][edge_bits] = { 'difficulty': 1, 'accepted': 0, 'rejected': 0, 'stale': 0 }
            sharedata[worker][edge_bits]['accepted'] += accepted
            sharedata[worker][edge_bits]['rejected'] += rejected
            sharedata[worker][edge_bits]['stale'] += stale
            # Write the record to REDIS
            logger.debug("Write to REDIS: {} - {}".format(redis_key, sharedata))
            redisdb.set(redis_key, json.dumps(sharedata), ex=REDIS_SHAREDATA_EXPIRETIME)
            # Debug
            logger.debug("Adding to sharedata cache: {}[{}][{}] = {}".format(redis_key, worker, edge_bits, sharedata[worker][edge_bits]))
        finally:
            SHARES_MUTEX.release()

        ##
        # Add the *individual rig* share data for each worker (into redis cache record)
        RIGDATA_MUTEX.acquire()
        group_height = int((height - height % RIGDATA_GROUPSIZE) + RIGDATA_GROUPSIZE)
        try:
            redisdb = lib.get_redis_db()
            redis_key = "{}-{}".format(REDIS_RIGDATA_KEY, group_height)
            # Check for exisintg redis record
            rigdata = redisdb.get(redis_key)
            if rigdata is None:
                # Create a new record
                rigdata = {}
            else:
                # Load existing record
                rigdata = json.loads(rigdata.decode())
                logger.debug("Existing rigdata cache record: {}".format(rigdata))
            if worker not in rigdata:
                rigdata[worker] = {}
            if rig_id not in rigdata[worker]:
                rigdata[worker][rig_id] = {}
            if workerid not in rigdata[worker][rig_id]:
                rigdata[worker][rig_id][workerid] = {}
            if edge_bits not in rigdata[worker][rig_id][workerid]:
                logger.debug("New rigdata cache record: height {}  group_height {} worker_id {}".format(height, group_height, worker))
                rigdata[worker][rig_id][workerid][edge_bits] = {'difficulty': 1, 'agent': agent, 'accepted': 0, 'rejected': 0, 'stale': 0 }
            rigdata[worker][rig_id][workerid][edge_bits]['accepted'] += accepted
            rigdata[worker][rig_id][workerid][edge_bits]['rejected'] += rejected
            rigdata[worker][rig_id][workerid][edge_bits]['stale'] += stale
            # Write the record to REDIS
            logger.debug("Write to REDIS: {} - {}".format(redis_key, rigdata))
            redisdb.set(redis_key, json.dumps(rigdata), ex=REDIS_RIGDATA_CACHE_EXPIRETIME)
            logger.debug("Adding to rigdata cache:  {}[{}][{}][{}][{}] = {}".format(redis_key, group_height, worker, rig_id, workerid, edge_bits, rigdata[worker][rig_id][workerid][edge_bits]))
        finally:
            RIGDATA_MUTEX.release()


def share_handler(ch, method, properties, body):
    global LOGGER
    global SHARE_EXPIRETIME

    content = json.loads(body.decode())

    # Debug
    LOGGER.warn("= Starting share_handler")
    LOGGER.warn("Current Share -  Height: {} - Type: {}".format(content["height"], content["type"]))

#    # Dont process very old messages
#    if (HEIGHT - int(content["height"])) > SHARE_EXPIRETIME:
#        ch.basic_ack(delivery_tag = method.delivery_tag)
#        LOGGER.error("Dropping expired {} - Height: {}".format(content["type"], content["height"]))
#        return

    # Process worker shares message
    if content["type"] == "share":
        # LOGGER.warn("Timestamp String: {}".format(content["log_timestamp"]))
        s_timestamp = dateutil.parser.parse(str(content["log_timestamp"]))
        s_height = int(content["height"])
        s_difficulty = int(content["difficulty"])
        s_worker = int(content["worker"])
        if s_worker == 0:
            s_worker = 1
        try:
            s_workerid = content["workerid"]
        except Exception as e:
            s_workerid = "default"
        try:
            s_rigid = content["rigid"]
        except Exception as e:
            s_rigid = "0"
        try:
            s_agent = content["agent"]
        except Exception as e:
            s_agent = "unknown"
        s_sharedata = content["sharedata"]
        addWorkerShares(LOGGER, ch, method.delivery_tag, s_timestamp, s_height, s_worker, s_workerid, s_rigid, s_agent, s_difficulty, s_sharedata)
    else:
        LOGGER.warn("Invalid message type: {}".format(content["type"]))

    # Ack the RMQ message
    ch.basic_ack(delivery_tag=method.delivery_tag)   

    # Debug
    LOGGER.warn("= Completed share_handler")
    sys.stdout.flush()


def poolblock_handler(ch, method, properties, body):
    global LOGGER
    global SHARE_EXPIRETIME

    content = json.loads(body.decode())

    # Debug
    LOGGER.warn("= Starting poolblock_handler")
    LOGGER.warn("Current Share -  Height: {} - Type: {}".format(content["height"], content["type"]))

    if content["type"] == "poolblocks":

        # Add the pool block to the database
        s_timestamp = dateutil.parser.parse(str(content["log_timestamp"]))
        s_height = int(content["height"])
        s_hash = content["hash"]
        s_worker =  1 # grin log does not know, credit Pool Admin
        serverid = content["serverid"]
        addPoolBlock(LOGGER, s_timestamp, s_height, s_hash, s_worker, serverid)
    else:
        LOGGER.warn("Invalid message type: {}".format(content["type"]))

    # Ack the RMQ message
    ch.basic_ack(delivery_tag=method.delivery_tag)   

    # Debug
    LOGGER.warn("= Completed poolblock_handler")
    sys.stdout.flush()
    
     
def RmqConsumer(host):
    global LOGGER
    global RABBITMQ_USER
    global RABBITMQ_PASSWORD
    while True:
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                            host=host,
                            credentials=credentials
                        )
                )
            channel = connection.channel()
            channel.basic_qos(
                    prefetch_size=0,
                    prefetch_count=0,
                    global_qos=True
                )
            # Consume pool block records
            channel.basic_consume(
                    queue='poolblocks',
                    on_message_callback=poolblock_handler,
                    auto_ack=False
                )
            # Consume worker shares records
            channel.basic_consume(
                    queue='shares',
                    on_message_callback=share_handler,
                    auto_ack=False
                )
            channel.start_consuming()
        except Exception as e:
            LOGGER.exception("Something went wrong: {}".format(traceback.format_exc()))
            sys.stdout.flush()
            time.sleep(10)

def ShareCommitScheduler(max_lag, commit_interval, logger):
    global SHARES_MUTEX
    while True:
        try:
            database = lib.get_db()
            latest_block = Blocks.get_latest()
            while latest_block is None:
                logger.warn("Waiting for first block")
                time.sleep(10)
                latest_block = Blocks.get_latest()
            chain_height = latest_block.height
            SHARES_MUTEX.acquire()
            try:
                logger.warn("= Begin ShareCommitScheduler")
                # Itterate over each sharedata key in redis
                redisdb = lib.get_redis_db()
                redis_key = "{}-*".format(REDIS_SHAREDATA_KEY) 
                keys = []
                for key in redisdb.scan_iter(match=redis_key, count=100):
                    keys.append(key.decode())
                for key in sorted(keys):
                    share_height = int(key.split("-")[1])
                    if share_height < chain_height - max_lag:
                        # Commit this record
                        logger.warn("-- ShareCommitScheduler processing record at height: {}".format(share_height))
                        redis_sharedata = redisdb.get(key)
                        redis_sharedata = json.loads(redis_sharedata.decode())
                        ts_str = redis_sharedata.pop("timestamp", str(datetime.utcnow()))
                        ts = datetime.strptime(ts_str.split(".")[0], '%Y-%m-%d %H:%M:%S')
                        for worker, worker_shares in redis_sharedata.items():
                            # Get any existing record
                            worker_shares_rec = Worker_shares.get_by_height_and_id(share_height, worker)
                            if worker_shares_rec is None:
                                # No existing record for this worker at this height, create it
                                logger.warn("New share record for worker {} at height {}".format(worker, share_height))
                                worker_shares_rec = Worker_shares(
                                        height = share_height,
                                        user_id = worker,
                                        timestamp = ts,
                                    )
                                database.db.createDataObj(worker_shares_rec)
                            else:
                                logger.warn("Add to existing record for worker {} at height {}".format(worker, share_height))
                            for edge_bits, shares_count in worker_shares.items():
                                worker_shares_rec.add_shares(
                                        edge_bits,
                                        shares_count["difficulty"],
                                        shares_count["accepted"],
                                        shares_count["rejected"],
                                        shares_count["stale"]
                                    )
                                # Debug
                                logger.warn("Worker Shares: {}".format(worker_shares_rec))
                        # We wrote this record to mysql, so remove the redis cache
                        database.db.getSession().commit()
                        redisdb.delete(key)
                # Write fillter record if needed
                share_height = Worker_shares.get_latest_height()
                if share_height is None:
                    share_height = grin.blocking_get_current_height()
                share_height = share_height + 1
                while share_height < (chain_height - max_lag):
                    logger.warn("Processed 0 shares in block {} - Creating filler record".format(share_height))
                    filler_worker_shares_rec = Worker_shares(
                            height = share_height,
                            user_id = 1, # Pool User
                            timestamp = datetime.utcnow(),
                        )
                    database.db.createDataObj(filler_worker_shares_rec)
                    share_height += 1
            finally:
                database.db.getSession().commit()
                SHARES_MUTEX.release()
                lib.teardown_db()
                logger.warn("= End ShareCommitScheduler")
            time.sleep(commit_interval)
        except Exception as e:
            lib.teardown_db()
            logger.exception("Something went wrong: {} ".format(traceback.format_exc()))
            time.sleep(10)
            
def RigDataCommitScheduler(max_lag, commit_interval, logger):
    global RIGDATA_MUTEX
    global RIGDATA_GROUPSIZE
    global REDIS_RIGDATA_KEY
    global REDIS_RIGDATA_EXPIRETIME
    while True:
        try:
            database = lib.get_db()
            latest_block = Blocks.get_latest()
            while latest_block is None:
                logger.warn("Cant get latest block from database")
                time.sleep(10)
                latest_block = Blocks.get_latest()
            chain_height = latest_block.height
            lib.teardown_db()
            RIGDATA_MUTEX.acquire()
            try:
                logger.warn("= Begin RigDataCommitScheduler")
                # Itterate over each rigdata cache key in redis
                redisdb = lib.get_redis_db()
                redis_key = "{}-*".format(REDIS_RIGDATA_KEY)
                keys = []
                for key in redisdb.scan_iter(match=redis_key, count=100):
                    keys.append(key.decode())
                for key in sorted(keys):
                    share_height = int(key.split("-")[1])
                    if share_height < chain_height - RIGDATA_GROUPSIZE - max_lag:
                        # Commit this set of rigdata records
                        logger.warn("-- RigDataCommitScheduler processing record at height: {}".format(share_height))
                        redis_cached_rigdata = redisdb.get(key)
                        redis_cached_rigdata = json.loads(redis_cached_rigdata.decode())
                        for user, rigdata in redis_cached_rigdata.items():
                            redis_key = "{}.{}.{}".format(REDIS_RIGDATA_KEY, share_height, user)
                            if redisdb.exists(redis_key):
                                # XXX TODO
                                logger.warn("XXX TODO: DUPLICATE RIGDATA WORKER KEY - MERGE ???")
                            else:
                                redisdb.set(redis_key, json.dumps(rigdata), ex=REDIS_RIGDATA_EXPIRETIME)
                        # Wrote this rigdata to REDIS, so remove the cache record now
                        redisdb.delete(key)
            finally:
                RIGDATA_MUTEX.release()
                logger.warn("= End RigDataCommitScheduler")
            time.sleep(commit_interval)
        except Exception as e:
            logger.exception("Something went wrong: {}".format(traceback.format_exc()))
            time.sleep(10)
            
def main():
    global LOGGER
    global CONFIG
    global SHARE_EXPIRETIME
    global RABBITMQ_USER
    global RABBITMQ_PASSWORD
    global RMQ
    CONFIG = lib.get_config()

    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    SHARE_EXPIRETIME = int(CONFIG[PROCESS]["share_expire_time"])
    COMMIT_INTERVAL = int(CONFIG[PROCESS]["commit_interval"])
    SHAREDATA_COMMIT_LAG = 3 # Allow shares to lag up to max_lag behind the blockchain before filler record is created
    RIGDATA_COMMIT_LAG = 3   # Allow rigdata to lag up to max_lag behind the blockchain before creating the record

    RABBITMQ_USER = os.environ["RABBITMQ_USER"]
    RABBITMQ_PASSWORD = os.environ["RABBITMQ_PASSWORD"]

    try:
       RMQ = os.environ["RMQ"]
    except KeyError as e:
       RMQ = "rmq"
       LOGGER.warn("Cant determine RMQ servsers, default to {}".format(RMQ))

    ##
    # Start a thread to commit share records
    commit_thread = threading.Thread(target = ShareCommitScheduler, args = (SHAREDATA_COMMIT_LAG, COMMIT_INTERVAL, LOGGER,))
    commit_thread.start()

    ## 
    rigdata_thread = threading.Thread(target = RigDataCommitScheduler, args = (RIGDATA_COMMIT_LAG, COMMIT_INTERVAL, LOGGER,))
    rigdata_thread.start()

    ##
    # Start a pika consumer thread for each rabbit we want to consume from
    for rmq in RMQ.split():
        try:
            LOGGER.warn("Connecting to RMQ server: {}".format(rmq))
            rmq_thread = threading.Thread(target = RmqConsumer, args = (rmq, ))
            rmq_thread.start()
        except Exception as e:
            logger.error("Failed to connect to RMQ: {} - {}".format(rmq, e))

if __name__ == "__main__":
    main()

