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

import os
import json
import time
import requests
from datetime import datetime
from datetime import timedelta

from grinlib import lib
from grinlib import grin
from grinlib import payments
from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.pool_payment import Pool_payment

PROCESS = "tidyWallet"
LOGGER = None
CONFIG = None

# Get K8s secret from container environment
wallet_api_user = os.environ['WALLET_OWNER_API_USER']
wallet_api_key = os.environ["WALLET_OWNER_API_PASSWORD"]

def retrieve_txs(tx=None, refresh=False):
    global LOGGER
    grin_owner_api_url = grin.get_owner_api_url()
    GET_TX_URL = grin_owner_api_url + "/v1/wallet/owner/retrieve_txs"
    tx_id = None
    try:
        if tx is not None:
            tx_id = json.loads(tx)["id"]
    except json.decoder.JSONDecodeError as e:
        print("tx data is: {}".format(tx))
        LOGGER.error("Failed to get tx_id: {}".format(repr(e)))
        return None
    second_arg = False
    if refresh == True:
        GET_TX_URL += "?refresh"
        second_arg = True
    if tx_id is not None:
        if second_arg == True:
            GET_TX_URL += "&"
        else:
            GET_TX_URL += "?"
        GET_TX_URL += "tx_id=" + tx_id
    r = requests.get(
            url=GET_TX_URL,
            auth=(wallet_api_user, wallet_api_key)
        )
    print(r.status_code)
    print(len(r.json()))
    return r

def retrieve_outputs():
    grin_owner_api_url = grin.get_owner_api_url()
    GET_OP_URL = grin_owner_api_url + "/v1/wallet/owner/retrieve_outputs"
    r = requests.get(
            url=GET_OP_URL,
            auth=(wallet_api_user, wallet_api_key)
        )
    print(r.status_code)
    print(len(r.json()))
    return r

# Cacnel an old UNPOSTED tx (users time to return it expired)
def cancel_expired_tx(database, grin_owner_api_url, tx_timeout):
    global LOGGER
    global CONFIG
    LOGGER.warn("Running cancel_expired_tx ---")
    # XXX TODO: Update to query the db first, then get single tx from the wallet
    r = retrieve_txs()
    for tx in r.json()[1]:
        if tx["tx_type"] == "TxSent" and tx["confirmed"] == False:
            payment_rec = Pool_payment.get_by_address(tx["tx_slate_id"])
            if payment_rec is not None and payment_rec.state == "sent":
                dts = tx["creation_ts"][0:-5]
                dt = datetime.strptime(dts, "%Y-%m-%dT%H:%M:%S.%f")
                if (datetime.utcnow() - dt) > tx_timeout:
                    print(tx["tx_slate_id"])
                    try:
                        payments.cancel_tx_slate(
                                tx_id = payment_rec.address, # XXX TODO: Change this to use payment_rec.tx_data.tx_id
                                logger = LOGGER,
                                database = database,
                                wallet_auth = (wallet_api_user, wallet_api_key),
                            )
                    except Exception as e:
                        LOGGER.warn("Failed to cancel expired transaction: {}".format(repr(e)))

# Re-post a posted tx
def repost_tx(database, grin_owner_api_url, tx_timeout):
    global LOGGER
    global CONFIG
    LOGGER.warn("Running repost_tx ---")

    pending_txs = Pool_payment.get_by_state("posted")
    for payment_rec in pending_txs:
        if payment_rec.tx_data is None:
            continue
  
        r = retrieve_txs(payment_rec.tx_data)
        if r is None:
            continue
        for tx in r.json()[1]:
            if tx["tx_type"] == "TxSent" and tx["confirmed"] == False:
                if payment_rec.state == "posted":
                    dts = tx["creation_ts"][0:-5]
                    dt = datetime.strptime(dts, "%Y-%m-%dT%H:%M:%S.%f")
                    if (datetime.utcnow() - dt) > tx_timeout:
                        try:
                            tx_id = json.loads(payment_rec.tx_data)["id"]
                            LOGGER.warn("Re-posting tx: {}".format(tx_id))
                            payments.post_tx(
                                    tx_slate = payment_rec.tx_data,
                                    logger = LOGGER,
                                    wallet_auth = (wallet_api_user, wallet_api_key),
                                )
                        except Exception as e:
                            LOGGER.warn("Failed to repost unconfirmed transaction: {}".format(repr(e)))

# control the number of wallet outputs
def update_outputs_count(grin_owner_api_url, target_output_count):
    global LOGGER
    LOGGER.warn("Running update_outputs_count() ---")
    current_height = grin.blocking_get_current_height()
    r = retrieve_outputs()  
    #LOGGER.warn("Wallet outputs are {}".format(r.json()))
    # Itr through the list of outputs and count the ones that could be consolidated (the spendable outputs)
    outputs = r.json()[1]
    count = 0
    for output in outputs:
        output = output[0]
        if output["status"] == 'Unspent' and output["lock_height"] < current_height:
            count = count + 1
    LOGGER.warn("Wallet has {} spendable outputs".format(count))
    min_count = target_output_count - (target_output_count/2)
    max_count = target_output_count + (target_output_count*2)
    if (count < min_count) or (count > max_count):
        LOGGER.warn("Setting number of wallet outputs to {}".format(count))
        try:
            payments.tidy_outputs(
                    target_output_count,
                    logger = LOGGER,
                    wallet_auth = (wallet_api_user, wallet_api_key),
                    )
        except Exception as e:
            LOGGER.warn("Failed to set number of wallet outputs: {}".format(repr(e)))


def main():
    global LOGGER
    global CONFIG
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    database = lib.get_db()
    grin_owner_api_url = grin.get_owner_api_url()

    # Get Config values
    tx_expire_seconds = int(CONFIG[PROCESS]["tx_expire_seconds"])
    tx_repost_seconds = int(CONFIG[PROCESS]["tx_repost_seconds"])
    tx_expire_delta = timedelta(seconds=tx_expire_seconds)
    tx_repost_delta = timedelta(seconds=tx_expire_seconds)
    target_output_count = 100 # XXX TODO GET FROM CONFIG

    ##
    # Run a few tidy algorithms

    # 1) Run tidys
    # Cancel any "sent" (but nt posted) transactions older than the timeout
    try:
        cancel_expired_tx(database, grin_owner_api_url, tx_expire_delta)
    except Exception as e:
        LOGGER.error("Failed to cancel_expired_tx(): {}".format(repr(e)))
    # Repost any "posted" (but not mined) transactions older than the timeout
    try:
        repost_tx(database, grin_owner_api_url, tx_repost_delta)
    except Exception as e:
        LOGGER.error("Failed to repost_tx(): {}".format(repr(e)))


    # 2) Set UTXO 
    # If there are too many, or too few outputs in the wallet, re-output
    try:
        update_outputs_count(grin_owner_api_url, target_output_count)
    except Exception as e:
        LOGGER.error("Failed to update_outputs_count(): {}".format(repr(e)))

    LOGGER.warn("=== Completed {}".format(PROCESS))

if __name__ == "__main__":
    main()
