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

import sys
import os
import time
import subprocess
import db_api
import lib

PROCESS = "makePayouts"

# pool_utxo <--- these are our user records.  A record of each pending payout (one per unique miner payout address)
# makePayouts.py gets the list of pool_utxo records with value greater than threshold and attepmts to make a payment.
#     * Bonus: Do all payouts in a single tx ?
#     * updates pool_utxo with new total, timestamp of last payout, number of failed payout attempts


def makePayout(utxo):
    (u_id, u_address, u_amount) = utxo
    send_cmd = [
        "/usr/local/bin/grin", "wallet", "send", "-s", "smallest", "-d",
        str(u_address),
        str(u_amount)
    ]
    ok = subprocess.call(send_cmd, stderr=subprocess.STDOUT, shell=False)
    return ok


def main():
    db = db_api.db_api()
    config = lib.get_config()
    logger = lib.get_logger(PROCESS)
    logger.warn("=== Starting {}".format(PROCESS))

    wallet_dir = config[PROCESS]["wallet_dir"]
    minimum_payout = int(config[PROCESS]["minimum_payout"])
    os.chdir(wallet_dir)
    utxos = db.get_utxo(minimum_payout)
    for utxo in utxos:
        (u_id, u_address, u_amount) = utxo
        logger.warn("Trying to pay: {} {} {}".format(u_id, u_address, u_amount))
        ok = makePayout(utxo)
        logger.warn("result: {}".format(ok))
        if ok == 0:
            logger.warn("Made payout - deleting utxo for {} {} {}".format(u_id, u_address, u_amount))
            db.remove_utxo(u_id)
        else:
            logger.error("Failed to make payout: {} {} {}".format(u_id, u_address, u_amount))
    db.set_last_run(PROCESS, str(time.time()))
    db.close()
    logger.warn("=== Completed {}".format(PROCESS))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
