#!/usr/bin/python3
import os
import sys
import json
import time
import redis
from datetime import datetime
import requests


from grinbase.model.users import Users

from grinlib import lib
from grinlib import grin
from grinlib import pool

redis_userid_key = "userid."


r = redis.Redis(
    host='redis-master',
    port=6379)

database = lib.get_db()


for id in range(1, 9999):
    user_rec = Users.get_by_id(id)
    if user_rec is not None:
        redis_key = redis_userid_key + user_rec.username
        r.set(redis_key, user_rec.id)
        redis_key = redis_userid_key + user_rec.username.lower()
        r.set(redis_key, user_rec.id)

