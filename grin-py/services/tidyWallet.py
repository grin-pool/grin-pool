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
import traceback
from datetime import datetime
from datetime import timedelta

from grinlib import lib
from grinlib import grin
from grinlib import payments
from grinlib import wallet
from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.pool_payment import Pool_payment

PROCESS = "tidyWallet"
LOGGER = None
CONFIG = None

# Cancel an old UNPOSTED tx (users time to return it expired)
def cancel_expired_tx(database, grin_owner_api_url, tx_timeout):
    global LOGGER
    global CONFIG
    LOGGER.warn("Running cancel_expired_tx ---")

    sent_txs = Pool_payment.get_by_state("sent")
    for tx in sent_txs:
        tx_data = json.loads(tx.tx_data)
        if (datetime.utcnow() - tx.timestamp) > tx_timeout:
            # This is a timed-out tx
            try:
                payments.cancel_tx_slate(
                        tx_slate_id = tx_data["id"],
                        new_state = "expired",
                        logger = LOGGER,
                        database = database,
                    )
            except Exception as e:
                LOGGER.warn("Failed to cancel expired transaction: {}".format(repr(e)))

# Cancel any tx the wallet has rejected and marked as canceled
#def cancel_canceled_tx()
#    XXX TODO
#    Check the wallet status of each tx for the previous 1440 blocks
#    Get the list from query of pool_payment for state=confirmed
#    If any of them are marked "Canceled" in the wallet, mark the pool_payment 
#    record as "canceled" and refund to the workers balance

# Mark confirmed payments as confirmed
def confirm_tx(database, grin_owner_api_url):
    global LOGGER
    global CONFIG
    LOGGER.warn("Running confirm_tx ---")

    posted_txs = Pool_payment.get_by_state("posted")
    for payment_rec in posted_txs:
        # print("processing payment_rec: {}".format(payment_rec))
        if payment_rec.tx_data is None:
            LOGGER.warn("Skipping confirmation check on payment record {} - no tx data".format(payment_rec.id))
            continue
        try:
            tx_slate = json.loads(payment_rec.tx_data)
            tx_id = tx_slate["id"]
        except Exception as e:
            LOGGER.warn("Skipping confirmation check on payment record {} - invalid tx_data: {}".format(payment_rec.id, str(e)))
            continue
        try:
            txs = wallet.retrieve_txs(tx_slate_id=tx_id)
        except Exception as e:
            LOGGER.warn("Skipping confirmation check on payment record {} - Failed to retrieve from wallet: {}".format(payment_rec.id, str(e)))
            continue
        
        try:
            # Result of retrieve_txs is an array even if we request a spcific one
            for tx in txs:
                if tx["tx_type"] == "TxSent" and tx["confirmed"] == True:
                    LOGGER.warn("Confirmed tx: {}".format(tx_id))
                    payment_rec.state = "confirmed"
                    database.db.getSession().commit()
        except Exception as e:
            LOGGER.warn("Failed to confirm payment record {}: tx {}: {}".format(payment_rec.id, tx_id, str(e)))
            continue

    
            

# Re-post a posted tx
def repost_tx(database, grin_owner_api_url, tx_timeout_delta):
    global LOGGER
    global CONFIG
    LOGGER.warn("Running repost_tx ---")

    pending_txs = Pool_payment.get_by_state_and_agelimit("posted", tx_timeout_delta)
    for payment_rec in pending_txs:
        LOGGER.warn("processing payment_rec: {}".format(payment_rec))
        if payment_rec.tx_data is None:
            LOGGER.warn("Skipping repost check on payment record {} - no tx data".format(payment_rec.id))
            continue
        try:
            tx_slate = json.loads(payment_rec.tx_data)
            tx_id = tx_slate["id"]
        except Exception as e:
            LOGGER.warn("Skipping repost on payment record {} - invalid tx_data: {}".format(payment_rec.id, str(e)))
            continue
        try:
            txs = wallet.retrieve_txs(tx_slate_id=tx_id)
        except Exception as e:
            LOGGER.warn("Skipping repost on payment record {} - Failed to retrieve from wallet: {}".format(payment_rec.id, str(e)))
            continue
        
        try:
            # Result of retrieve_txs is an array even if we request a spcific one
            for tx in txs:
                print("tx data: {}".format(tx))
                if tx["tx_type"] == "TxSent" and tx["confirmed"] == False:
                    LOGGER.warn("Re-posting tx: {}".format(tx_id))
                    res = wallet.post_tx(tx_slate["tx"])
                    print("XXX repost result = {}".format(res))
        except Exception as e:
            LOGGER.warn("Failed to re-post payment record {}: tx {}: {}".format(payment_rec.id, tx_id, str(e)))
            continue



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

    ##
    # Run a few tidy algorithms

    # Marked confirmed payments
    try:
        confirm_tx(database, grin_owner_api_url)
    except Exception as e:
        LOGGER.exception("Failed to confirm_tx(): {}".format(repr(e)))

    # Cancel any "sent" (but nt posted) transactions older than the timeout
    try:
        cancel_expired_tx(database, grin_owner_api_url, tx_expire_delta)
    except Exception as e:
        LOGGER.exception("Failed to cancel_expired_tx(): {}".format(repr(e)))

    # Repost any "posted" (but not mined) transactions older than the timeout
    try:
        repost_tx(database, grin_owner_api_url, tx_repost_delta)
    except Exception as e:
        LOGGER.exception("Failed to repost_tx(): {}".format(repr(e)))

    # Run wallet check
    try:
        # XXX TODO
        pass
    except Exception as e:
        LOGGER.exception("Failed to run wallet check: {}".format(repr(e)))

    # Cancel any tx the wallet found to be canceled
    # XXX TODO


    LOGGER.warn("=== Completed {}".format(PROCESS))

if __name__ == "__main__":
    main()
