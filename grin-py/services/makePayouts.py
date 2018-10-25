#!/usr/bin/python3

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

import sys
import os
import time
import subprocess
from datetime import datetime
from random import randint
import socket

from grinlib import lib
from grinlib import grin
from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.pool_payment import Pool_payment

PROCESS = "makePayouts"
LOGGER = None
CONFIG = None

# pool_utxo <--- these are our user records.  A record of each pending payout (one per unique miner payout address)
# makePayouts.py gets the list of pool_utxo records with value greater than threshold and attepmts to make a payment.
#     * Future: Do multiple payouts in a single grin wallet tx
#     * updates pool_utxo with new total, timestamp of last payout, number of failed payout attempts

# XXX TODO:  Add maximum payout value to reduce the pools risk


def makePayout(address, amount):
    global LOGGER
    global CONFIG

    LOGGER.warn("Making Payout of: {} to: {}".format(address, amount))
    # Test a low-timeout connection before involving the wallet
    probe = testWalletPort(address)
    if probe == False:
        LOGGER.warn("Test Connection Failed: {} {}".format(address, amount))
        return 1 # failure status
    LOGGER.warn("Test Connection Ok: {} {}".format(address, amount))
    grin_api_url = grin.get_api_url()
    os.chdir(CONFIG[PROCESS]["wallet_dir"])
    send_cmd = [
        "/usr/local/bin/grin",
          "wallet",
            "--api_server_address", grin_api_url,
          "send",
            "--selection", "smallest",
            "--dest", str(address),
            str(amount)
    ]
    LOGGER.warn("Command: {}".format(send_cmd))
    try:
        output = subprocess.check_output(send_cmd, stderr=subprocess.STDOUT, shell=False)
        LOGGER.warn("Sent OK: {}".format(output))
        return 0
    except subprocess.CalledProcessError as exc:
        LOGGER.error("Send failed with rc {} and output {}".format(exc.returncode, exc.output))
        return 1 # exc.returncode
    except Exception as e:
        LOGGER.error("Send failed with error {}".format(str(e)))
        return 1

def testWalletPort(address):
    global LOGGER
    try:
        s = socket.socket()
        s.settimeout(2)
        addr = address.replace('http://', '')
        addr = addr.split(':')
        LOGGER.warn("Testing: {}, {}".format(addr[0], addr[1]))
        s.connect((addr[0], int(addr[1])))
        s.close()
    except Exception as e:
        LOGGER.error("Failed test connection: {}".format(str(e)))
        return False
    
    return True
        

def main():
    global LOGGER
    global CONFIG
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    # Connect to DB
    database = lib.get_db()

    wallet_dir = CONFIG[PROCESS]["wallet_dir"]
    minimum_payout = int(CONFIG[PROCESS]["minimum_payout"])
    os.chdir(wallet_dir)
    utxos = Pool_utxo.getPayable(minimum_payout)
    database.db.getSession().commit()
    # XXX TODO: Use the current balance, timestamp, the last_attempt timestamp, last_payout, and failed_attempts
    # XXX TODO: to filter and sort by order we want to make payment attempts
    for utxo in utxos:
        try:
            # Try less often for wallets that dont answer
            if utxo.amount < utxo.failure_count:
                if randint(0, 11) != 0:
                    continue
            LOGGER.warn("Trying to pay: {} {} {}".format(utxo.id, utxo.address, utxo.amount))
            # Lock just this current record for update
            locked_utxo = Pool_utxo.get_locked_by_id(utxo.id)
            # Save and Zero the balance
            original_balance = locked_utxo.amount
            locked_utxo.amount = 0
            # Savepoint changes - if we crash after sending coins but before commit we roll back to here.
            #   The pool audit service (coming soon) finds lost payouts and restores user balance
            database.db.getSession().begin_nested();
            # Attempt to make the payment
            timestamp = datetime.utcnow()
            status =  makePayout(locked_utxo.address, original_balance)
            LOGGER.warn("Payout status: {}".format(status))
            if status == 0:
                LOGGER.warn("Made payout for {} {} {} at {}".format(locked_utxo.id, locked_utxo.address, original_balance, timestamp))
                # Create a payment record
                payment_record = Pool_payment(locked_utxo.id, timestamp, locked_utxo.address, original_balance, 0, locked_utxo.failure_count, "schedule" )
                database.db.getSession().add(payment_record)
                # Update timestamp of last payout, number of failed payout attempts
                locked_utxo.amount = 0
                locked_utxo.failure_count = 0
                locked_utxo.last_try = timestamp
                locked_utxo.last_success = timestamp
                locked_utxo.total_amount += original_balance
                # Commit changes
                database.db.getSession().commit() 
            else:
                LOGGER.error("Failed to make payout: {} {} {}".format(locked_utxo.id, locked_utxo.address, original_balance))
                # Restore the users balance 
                locked_utxo.amount = original_balance
                # Update number of failed payout attempts
                if locked_utxo.failure_count is None:
                    locked_utxo.failure_count = 0
                locked_utxo.failure_count += 1
                locked_utxo.last_try = timestamp
                # Commit changes
                database.db.getSession().commit()
            database.db.getSession().commit()

        except Exception as e:
            LOGGER.error("Failed to process utxo: {} because {}".format(utxo.id, str(e)))
            database.db.getSession().rollback()
            sys.exit(1)

    LOGGER.warn("=== Completed {}".format(PROCESS))

if __name__ == "__main__":
    main()
