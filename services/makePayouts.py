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

PROCESS="makePayouts"

# pool_utxo <--- these are our user records.  A record of each pending payout (one per unique miner payout address)
# makePayouts.py gets the list of pool_utxo records with value greater than threshold and attepmts to make a payment.
#     * Bonus: Do all payouts in a single tx ?
#     * updates pool_utxo with new total, timestamp of last payout, number of failed payout attempts

def makePayout(utxo):
    (u_id, u_address, u_amount) = utxo
    send_cmd = ["/grin/target/release/grin", "wallet", "send", "-s", "smallest", "-d", str(u_address), str(u_amount)]
    print("Sending Grin: ", send_cmd)
    ok = subprocess.call(send_cmd, stderr=subprocess.STDOUT, shell=False)
    print("ok result: ", ok)
    return ok

def main():
    db = db_api.db_api()
    config = lib.get_config()
    wallet_dir = config["makepayouts"]["wallet_dir"]
    minimum_payout = int(config["makepayouts"]["minimum_payout"])
    os.chdir(wallet_dir)
    utxos = db.get_utxo(minimum_payout)
    for utxo in utxos:
	(u_id, u_address, u_amount) = utxo
	ok = makePayout(utxo)
	if ok == 0:
	    db.remove_utxo(u_id)
	else:
	    print("Failed to make payout: ", u_id)
    db.set_last_run(PROCESS, str(time.time()))
    db.close()
    sys.stdout.flush()

if __name__ == "__main__":
    main()
