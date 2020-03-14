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

#
# This script should audit:
# 1) individual payouts - if there is a failure in the database or makePayouts.py script it should be detected and fixed here
# 2) overall pool payouts vs pool blocks found - if the pool pays out more than it has found in blocks an alarm should be raised
# 3) xxx add more
#

import os
import sys
import time
import requests
import traceback
import json


from grinlib import lib
from grinlib import wallet
from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.pool_payment import Pool_payment
from grinbase.model.pool_audit import Pool_audit
from grinbase.model.pool_credits import Pool_credits


# NOTE:  All calculations are in nanogrin

PROCESS = "auditor"
LOGGER = None
CONFIG = None

def main():
    global LOGGER
    global CONFIG
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)

    while True:
        try:
            LOGGER.warn("=== Starting {}".format(PROCESS))

            # Connect to DB
            database = lib.get_db()

            # Get the prebious audit record to find its height
            previous_audit_record = Pool_audit.getLatest()
            if previous_audit_record is None:
                previous_audit_record = Pool_audit()
                database.db.createDataObj(previous_audit_record)

            # Create new pool audit record
            audit_record = Pool_audit()

            summary_info = wallet.retrieve_summary_info(refresh=True)

            # Set the height by wallet
            audit_record.height = int(summary_info["last_confirmed_height"])
            # Set pool bock count
            audit_record.pool_blocks_count = Pool_blocks.count(audit_record.height) - Pool_blocks.count(previous_audit_record.height)
            # Audit pools liability vs equity
            audit_record.equity = int(summary_info["amount_currently_spendable"]) + int(summary_info["amount_awaiting_confirmation"])
            audit_record.liability = Pool_utxo.get_liability()
            audit_record.balance = audit_record.equity - audit_record.liability
    
            # Add payouts value
            payments_made = Pool_payment.get_by_height(audit_record.height, audit_record.height-previous_audit_record.height)
            audit_record.payouts = sum([payment.amount for payment in payments_made])
            # Add payments value
            pool_credits = Pool_credits.get_by_height(audit_record.height, audit_record.height-previous_audit_record.height)
            total_credits = 0
            if pool_credits is not None:
                for credit in pool_credits:
                    credits_this_block = sum(credit.credits.values())
                    total_credits += credits_this_block
                    print("credits_this_block: {}, total_credits: {}".format(credits_this_block, total_credits))
                audit_record.payments = total_credits
            else:
                audit_record.payments = 0

            # Add and Commit the audit record
            #LOGGER.warn("Create Audit Record: {}".format(json.dumps(audit_record)))
            database.db.createDataObj(audit_record)

            LOGGER.warn("=== Completed {}".format(PROCESS))
        except Exception as e:
            lib.teardown_db()
            LOGGER.exception("Something went wrong: {} ".format(traceback.format_exc()))

        time.sleep(999)


if __name__ == "__main__":
    main()

