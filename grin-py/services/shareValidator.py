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

# shareValidator.py
#   For each pool_share not yet validated:
#     Verify it against the grin_share (does it exist?)
#       if not, mark it as invalid
#     get the share difficulty from grin_share table
#     Verify that the difficulty meets requirements,
#     If everything is ok, mark pool_shares record validated and valid

# shareValidator.py validates pool_share:
#        Check if a matching grin_share exists.  If not, this share was rejected and is invalid
#        Check grin_share.actual_difficulty >= pool_share.worker_difficulty or mark invalid
#        Check nonce and timestamp against grin_share for added sanity

import sys
import requests
import json
import time
import db_api
import lib

PROCESS = "shareValidator"

def main():
    db = db_api.db_api()
    logger = lib.get_logger(PROCESS)
    logger.warn("=== Starting {}".format(PROCESS))

    new_poolshares = db.get_unvalidated_poolshares()
    for pool_share in new_poolshares:
        invalid_reason = "NULL"
        ok = True
        (ps_height, ps_nonce, ps_worker_difficulty, ps_timestamp, ps_found_by,
         ps_validated, ps_is_valid, ps_invalid_reason) = pool_share
        grin_share = db.get_grin_share_by_nonce(ps_nonce)
        if grin_share == None:
            ok = False
            invalid_reason = "no grin_share"
            # continue # Check again later
        else:
            (gs_hash, gs_height, gs_nonce, gs_actual_difficulty,
             gs_net_difficulty, gs_timestamp, gs_found_by,
             gs_is_solution) = grin_share
            if ps_nonce != gs_nonce:
                ok = False
                invalid_reason = "nonce mismatch"
            if ps_worker_difficulty > gs_actual_difficulty:
                ok = False
                invalid_reason = "low difficulty"
        # Update record
        logger.warn("Share {}, {} is {} because {}".format(ps_height, ps_nonce, ok,
                                                     invalid_reason))
        db.set_poolshare_validation(ok, invalid_reason, ps_nonce)

    db.set_last_run(PROCESS, str(time.time()))
    db.close()
    logger.warn("=== Completed {}".format(PROCESS))


if __name__ == "__main__":
    main()
