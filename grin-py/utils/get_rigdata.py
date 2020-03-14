#!/usr/bin/python3
import json
import sys
import os
import redis
import pickle


block = sys.argv[1]
user = sys.argv[2]

r = redis.Redis(
        host='35.197.25.81',
        # host='redis-master',
        # No username
        # No password
    )

redis_key = "rigdata.{}.{}".format(block, user)

if r.exists(redis_key):
    print("Found RigData")
#    rigdata_pickle = r.get(redis_key)
#    rigdata_json = pickle.loads(rigdata_pickle)
    rigdata_json = r.get(redis_key)
    print("RigData: height={}, userid={} - {}".format(block, user, rigdata_json))
else:
    print("RigData: height={}, userid={} - None")
