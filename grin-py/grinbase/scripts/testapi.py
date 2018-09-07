#!/usr/bin/env python3

import requests
import json
import datetime
import time

#WORKER = "192.168.1.100:13415"
#WORKER = "192.168.2.225:13415"


print("Grin Network")

# Get the latest grin block
while True:
    latest = json.loads(requests.get("http://192.168.2.224:13423/grin/block").content.decode('utf-8'))
    if latest != None:
        break
# print("Latest: {}".format(latest))
# Get the previous grin block
prev_height = int(latest["height"]) - 1
previous = json.loads(requests.get("http://192.168.2.224:13423/grin/block/{}".format(prev_height)).content.decode('utf-8'))
# print("Previous: {}".format(previous))
# Get the latest grin stats
#stats = json.loads(requests.get("http://grin-pool.us:13423/grin/stat").content.decode('utf-8'))
stats = json.loads(requests.get("http://192.168.2.224:13423/grin/stats/0,5".format(prev_height)).content.decode('utf-8'))
stats = sorted(stats, key=lambda k: int(k['height']))[-1]


#print("Stats: {}".format(stats))

# Calculate seconds since last block found
seconds = int(datetime.datetime.now().timestamp()) - int(float(latest["timestamp"]))

print("Graph Rate: {} g/sec".format(stats["gps"]))
print("Block Found: {} seconds ago".format(seconds))
print("Difficulty: {}".format(stats["difficulty"]))
print("Chain Height: {}".format(latest["height"]))
print("Rewards: {}".format("60"))
print("Latest Hash: {}".format(latest["hash"][:8]))

# -------------
print("")

print("Grin-Pool.us")
# Get the latest pool block
latest_pool = json.loads(requests.get("http://192.168.2.224:13423/pool/block").content.decode('utf-8'))
#print("Latest Pool: {}".format(latest_pool))
#pool_stats = json.loads(requests.get("http://grin-pool.us:13423/pool/stat").content.decode('utf-8'))
pool_stats = json.loads(requests.get("http://192.168.2.224:13423/pool/stats/0,5").content.decode('utf-8'))
pool_stats = sorted(pool_stats, key=lambda k: int(k['height']))[-1]
#print("Latest Pool stat: {}".format(pool_stats))

seconds = int(datetime.datetime.now().timestamp()) - int(float(latest_pool["timestamp"]))

active_miners = json.loads(requests.get("http://192.168.2.224:13423/worker/stats/{},2/worker".format(pool_stats["height"])).content.decode('utf-8'))
active_miners = list(set([d['worker'] for d in active_miners]))
#active_miners = json.loads(requests.get("http://grin-pool.us:13423/worker/stats/{}/worker".format(pool_stats["height"])).content.decode('utf-8'))
#active_miners = set(active_miners)
    

print("Active Miners: {}".format(len(active_miners)))
print("Graph Rate: {} g/sec".format(pool_stats["gps"]))
print("Block Found: {} seconds ago".format(seconds))
print("Found Every: {} seconds (est)".format(int(float(stats["gps"])/float(pool_stats["gps"])*60)))
print("Blocks Found: {}".format(pool_stats["total_blocks_found"]))

# ----------------

print("")
print("Worker Stats:  {}".format(active_miners))

for miner_j in sorted(active_miners):
    miner = miner_j.split('/')[2]
    print("miner = {}".format(miner))
    worker_stats = json.loads(requests.get("http://192.168.2.224:13423/worker/stats/{}/0,5".format(miner)).content.decode('utf-8'))
    worker_stats = sorted(worker_stats, key=lambda k: int(k['height']))[-1]
#    print("worker_stats = {}".format(worker_stats))
    worker_shares = json.loads(requests.get("http://192.168.2.224:13423/worker/shares/{}/0,20".format(miner)).content.decode('utf-8'))
    worker_shares = sorted(worker_shares, key=lambda k: int(k['timestamp']))
#    print("worker_shares = {}".format(worker_shares))

    share_seconds = 0
    if len(worker_shares) == 0:
        share_seconds = -1
    else:
        share_seconds = int(datetime.datetime.now().timestamp()) - int(float(worker_shares[-1]["timestamp"]))
#        print("share: {}".format(worker_shares[-1]))
    
    worker_payment_info = json.loads(requests.get("http://192.168.2.224:13423/worker/payment/{}".format(miner)).content.decode('utf-8'))

    print("Graph Rate: {} g/sec".format(worker_stats["gps"]))
    print("Share Found: {} seconds ago".format(share_seconds))
    print("Balance: {} grin".format(worker_stats["balance"]))
    print("Last Paid: {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(worker_payment_info["last_success"]))))
    print("Total Paid: {}".format(worker_stats["total_grin_paid"]))
    print("-------------------------------")

