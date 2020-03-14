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

# Update all existing usernames with rigid delimiter "/" to "."


import sys
import traceback

from grinbase.dbaccess import database
from grinbase.model.users import Users
import redis

from grinlib import lib
from grinlib import pool

PROCESS = "usernameUpdate"
LOGGER = None
CONFIG = None

# XXX
COMMIT = False

def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    ##
    # Update user records in MySQL and REDIS
    database = lib.get_db()
    database.db.initializeSession()

    redisdb = lib.get_redis_db()
    redis_userid_key = "userid."

    id = 1
    try:
        while True:
            thisuser = Users.get_by_id(id)
            if thisuser is None:
                if id > 2358:
                    LOGGER.warn("last id = {}".format(id))
                    break
                id = id + 1 
                continue
            if thisuser.username == "bjg62hj8byyksphuw95vqc3f74.lionm1":
                orig_username = thisuser.username
                thisuser.username = "bjg62hj8byyksphuw95vqc3f74__lionm1"
                LOGGER.warn("Updated: {} to {}".format(orig_username, thisuser.username))
            if thisuser.username == "vova5310@gmail.com_d1":
                orig_username = thisuser.username
                thisuser.username = "vova5310@gmail_com__d1"
                LOGGER.warn("Updated: {} to {}".format(orig_username, thisuser.username))
            if thisuser.username == "rootalex020@gmail.com":
                orig_username = thisuser.username
                thisuser.username = "rootalex020@gmail__com"
                LOGGER.warn("Updated: {} to {}".format(orig_username, thisuser.username))
            if "." in thisuser.username:
                orig_username = thisuser.username
                # Update mysql
                thisuser.username = thisuser.username.replace(".", "_")
                # Update redis
                redis_key = redis_userid_key + orig_username
                COMMIT and redisdb.delete(redis_key)
                redis_key = redis_userid_key + thisuser.username
                COMMIT and redisdb.set(redis_key, id)
                LOGGER.warn("Updated: {} to {}".format(orig_username, thisuser.username))
            id = id + 1 
    except Exception as e:  # AssertionError as e:
        LOGGER.error("Something went wrong: {} - {}".format(e, traceback.print_stack()))
    
    COMMIT or LOGGER.warn("XXX No Commit - Edit for final run")
    COMMIT and database.db.getSession().commit()
    LOGGER.warn("=== Completed {}".format(PROCESS))


    
    

if __name__ == "__main__":
    main()
