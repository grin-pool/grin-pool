#!/usr/bin/env python
  
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

##
# Routines for making payments to miners
#

# Call flow for grin API V2 is the following:
# File send:
#     Sender: init_send_tx
#     Sender: tx_lock_outputs
#     Recipient: receive_tx
#     Sender: finalize_tx
#     Sender: post_tx
# 
# HTTP send:
#     Sender: init_send_tx with InitTxSendArgs (client receive it directly and finalization is made synchronously)


import sys
import os
import time
import json
import socket
import requests
import traceback
from datetime import datetime
from urllib.parse import urlparse


from grinlib import lib
from grinlib import grin
from grinlib import wallet
from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.pool_payment import Pool_payment

class PaymentError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
    def __str__(self):
        return repr(self.message)

def validateAddress(address, adderss_type, logger):
    logger.warn("validateAddress with {} {}".format(address, adderss_type))
    if adderss_type in ["http", "https"]:
        try:
            logger.warn("Validating http wallet address: {}".format(address))
            return urlparse(address).scheme in ['http', 'https']
        except Exception as e:
            logger.exception("Wallet http address is invalid: {}".format(str(e)))
        return False
    return True   # XXX TODO Validate keybase address

def testWalletPort(address, logger):
    try:
        logger.warn("testWalletPort: {}".format(address))
        s = socket.socket()
        s.settimeout(2)
        parsed = urlparse(address)
        if parsed.scheme == "http":
            addr = parsed.netloc
            port = 80
        else:
            addr = parsed.netloc
            port = 443
        if ":" in parsed.netloc:
            addr, port = parsed.netloc.split(':')
            port = int(port)
        logger.warn("Testing: {}, {}".format(addr, port))
        s.connect((addr, port))
        s.close()
    except Exception as e:
        logger.exception("Failed test connection: {}".format(str(e)))
        return False
    return True

# Get the users balance then call the wallet owner API to
# generate a payment tx slate.  Return that slate to the caller
def get_tx_slate(user_id, logger, database, method, invoked_by):

    # 1) Create a Slate
    slate = None
    try:
        locked_utxo = Pool_utxo.get_locked_by_userid(user_id)
        if locked_utxo is None or locked_utxo.amount < (1 * 1000000000):
            message = "Insufficient available balance for payout"
            logger.warn(message)
            raise PaymentError(400, message)
        amount = locked_utxo.amount
        # Generate a slate file
        try:
            args = {
                'src_acct_name': None,
                'amount': int(amount),
                'minimum_confirmations': 10,
                'max_outputs': 10,
                'num_change_outputs': 1,
                'selection_strategy_is_use_all': False,
                'message': "pool payment: slate: user_id={}".format(user_id),
                'target_slate_version': None,
                'send_args': None,
            }
            logger.warn("Requesting Payment slate from payment request api: {}".format(args))
            slate = wallet.init_send_tx(args)
        except Exception as e:
            logger.exception("Failed to get a payment slate: {}".format(str(e)))
            raise PaymentError(500, str(e))
    except PaymentError as e: # My own errors
        raise
    except Exception as e:
        logger.exception("Failed to get a payment slate: {}".format(str(e)))
        raise PaymentError(500, str(e))


    # 2) Create a payment record
    try:
        timestamp = datetime.utcnow()
        payment_record = Pool_payment(
                user_id = locked_utxo.user_id,
                timestamp = timestamp,
                height = slate["height"],
                address = slate["id"],
                amount = amount,
                method = method,
                fee = slate["fee"],
                failure_count = locked_utxo.failure_count,
                state = "sent",
                tx_data = json.dumps(slate),
                invoked_by = invoked_by,
            )
        database.db.getSession().add(payment_record)
        # Update the users utxo record
        locked_utxo.amount = int(slate["fee"]) * -1
        locked_utxo.last_try = timestamp
        locked_utxo.total_amount += amount
        database.db.getSession().commit()
    except Exception as e:
        logger.exception("Failed to create payment record: {}".format(str(e)))
        raise PaymentError(500, str(e))

    # 3) Lock the wallet outputs
    try:
        wallet.tx_lock_outputs(slate)
    except Exception as e:
        logger.exception("Failed to lock wallet outputs: {}".format(str(e)))
        raise PaymentError(500, str(e))

    # Return the slate
    return slate



# Cancel / Expire a tx and refund users coins
def cancel_tx_slate(tx_slate_id, new_state, logger, database):
    try:
        logger.warn("In cancel_tx_slate")
        # For tx sent via slate, tx_id is in the pool_payment.address field
        payment_rec = Pool_payment.get_by_address(tx_slate_id)
        if payment_rec is None:
            message = "Could not find any payment record for tx_slate_id {}".format(tx_slate_id)
            logger.warn(message)
            raise PaymentError(400, message)
        # Check if the wallet already has this marked as canceled
        wallet_rec = wallet.retrieve_txs(tx_slate_id=tx_slate_id)
        if len(wallet_rec) == 0:
            logger.warn("Wallet has no record of tx_slate_id: {}".format(tx_slate_id))
        else:
            logger.warn("XXX: wallet_rec = {}".format(wallet_rec))
            assert wallet_rec[0]["tx_slate_id"] == tx_slate_id, "Wallet returned incorrect tx data: {} vs {}".format(wallet_rec[0]["tx_slate_id"], tx_slate_id)
            if wallet_rec[0]["tx_type"] == "TxSentCancelled":
                logger.warn("Tx already marked canceled: {}".format(tx_slate_id))
            else:
                wallet.cancel_tx(tx_slate_id=tx_slate_id)
        # Mark payment record state as expired or canceled
        payment_rec.state = new_state
        # Credit back the user utxo amount
        locked_utxo = Pool_utxo.get_locked_by_userid(payment_rec.user_id)
        locked_utxo.amount = locked_utxo.amount + payment_rec.amount + payment_rec.fee
        locked_utxo.failure_count += payment_rec.failure_count + 1
        database.db.getSession().commit()
    except Exception as e:
        logger.exception("Unexpected Error in cancel_tx_slate: {}".format(str(e)))
        raise PaymentError(500, str(e))



# Submit a signed slate to the blockchain - finalize and post
def submit_tx_slate(user_id, slate, logger, database):
    if slate is None:
        message = "No slate data provided"
        logger.warn(message)
        raise PaymentError(400, message)
    try:
        slate_json = json.loads(slate.decode('utf-8'))
        tx_id = slate_json["id"]
    except Exception as e:
        message = "Invalid slate data provided"
        logger.warn(message)
        raise PaymentError(400, message)

    try:
        logger.warn("Running submit_slate: tx_id = {}".format(tx_id))
        # Record Keeping
        timestamp = datetime.utcnow()
        locked_utxo = Pool_utxo.get_locked_by_userid(user_id)
        locked_utxo.last_success = timestamp
        locked_utxo.failure_count = 0
        payment_rec = Pool_payment.get_by_address(tx_id)
        payment_rec.state = "posted"
        finalized_slate = wallet.finalize_tx(slate_json)
        payment_rec.tx_data = json.dumps(finalized_slate)
        database.db.getSession().commit()
    except Exception as e:
        logger.exception("Unexpected Error in submit_tx_slate")
        raise PaymentError(500, str(e))

    # Post the TX    
    try:
        wallet.post_tx(finalized_slate["tx"])
    except Exception as e:
        logger.exception("Failed to post payment: {}".format(repr(e)))
        raise PaymentError(500, str(e))




# Called from atomic_send()
def http_send(user_id, address, amount, logger, num_change_outputs=1):
    send_args = {
            'method': 'http',
            'dest': str(address),
            'finalize': True,
            'post_tx': False,
            'fluff': False,
        }
    args = {
            'src_acct_name': None,
            'amount': int(amount),
            'minimum_confirmations': 10,
            'max_outputs': 10,
            'num_change_outputs': int(num_change_outputs),
            'selection_strategy_is_use_all': False,
            'message': "pool payment: http: user_id={}".format(user_id),
            'target_slate_version': None,
            'send_args': send_args,
        }
    try:
        finalized_slate = wallet.init_send_tx(args)
    except Exception as e:
        logger.error("HTTP send failed with error {}".format(str(e)))
        if "is recipient listening" in str(e):
            raise PaymentError(400, "Could not connect to remote wallet listener (is recipient listening?)")
        else:
            raise PaymentError(500, str(e))
    logger.warn("Sent OK: user_id={} - address={} - amount {}".format(user_id, address, amount))
    return finalized_slate


# Called from atomic_send()
def keybase_send(user_id, address, amount, logger):
    send_args = {
            'method': 'keybase',
            'dest': str(address),
            'finalize': True,
            'post_tx': False,
            'fluff': False,
        }
    args = {
            'src_acct_name': None,
            'amount': int(amount),
            'minimum_confirmations': 10,
            'max_outputs': 10,
            'num_change_outputs': 1,
            'selection_strategy_is_use_all': False,
            'message': "pool payment: keybase: user_id={}".format(user_id),
            'target_slate_version': None,
            'send_args': send_args,
        }
    try:
        finalized_slate = wallet.init_send_tx(args)
    except Exception as e:
        logger.error("Keybase send failed with error {}".format(str(e)))
        raise PaymentError(500, str(e))
    logger.warn("Sent OK: user_id={} - address={} - amount {}".format(user_id, address, amount))
    return finalized_slate


# Atomic send used for http and keybase
def atomic_send(user_id, address, logger, database, method, invoked_by):
    # validate method
    if method not in ["http", "https", "keybase"]:
        message = "Invalid payment method requested"
        logger.warn(message)
        raise PaymentError(400, message)
    # Validate Address
    address = address.lstrip().rstrip()
    if address is None:
        message = "Wallet address is missing"
        logger.warn(message)
        raise PaymentError(400, message)
    if method == "http" or method == "https":
        if not address.startswith("http"):
            address = method + "://" + address
    valid = validateAddress(address, method, logger)
    if valid == False:
        message = "Wallet address is invalid: {}".format(address)
        logger.warn(message)
        raise PaymentError(400, message)
    if method == "http" or method == "https":
        probe = testWalletPort(address, logger)
        if probe == False:
            message = "Failed to establish connection with remote wallet listener at: {}".format(address)
            logger .warn(message)
            raise PaymentError(400, message)

    # Lock this utxo record for update and check for minimum balance
    amount = 0
    try:
        locked_utxo = Pool_utxo.get_locked_by_userid(user_id)
        if locked_utxo is None or locked_utxo.amount < (1 * 1000000000):
            message = "Insufficient available balance for payout"
            logger.warn(message)
            raise PaymentError(400, message)
        # Save the users current balance
        amount = locked_utxo.amount
    except PaymentError as e: # My own errors
        raise
    except Exception as e:
        logger.exception("Failed to get worker balance: {}".format(str(e)))
        raise PaymentError(500, str(e))

    # Call the synchronous send method
    # Subtract the balance from UTXO
    slate = None
    try:
        timestamp = datetime.utcnow()
        # Send the TX
        if method == "http" or method == "https":
            slate = http_send(user_id, address, amount, logger)
        elif method == "keybase":
            slate = keybase_send(user_id, address, amount, logger)
        # Create a payment record
        payment_rec = Pool_payment(
                user_id = locked_utxo.user_id,
                timestamp = timestamp,
                height = slate["height"],
                address = str(address),
                amount = locked_utxo.amount,
                method = method,
                fee = int(slate["fee"]),
                failure_count = locked_utxo.failure_count,
                state = "posted",
                tx_data = json.dumps(slate),
                invoked_by = invoked_by,
            )
        database.db.getSession().add(payment_rec)
        # Update the users utxo record
        locked_utxo.amount = int(slate["fee"]) * -1
        locked_utxo.last_try = timestamp
        locked_utxo.last_success = timestamp
        locked_utxo.total_amount += amount
        # Commit this
        database.db.getSession().commit()
    except PaymentError as e: # My own errors
        logger.exception("Failed to send tx".format(repr(e)))
        if slate is not None:
            wallet.cancel_tx(tx_slate_id=slate["id"])
        raise e
    except Exception as e: # All other (unexpected) errors
        logger.exception("Failed to create payment because {}".format(repr(e)))
        raise PaymentError(500, str(e))

    # Post the TX    
    try:
        logger.warn("Debug: Post the TX")
        wallet.post_tx(slate["tx"])
    except Exception as e: # All other (unexpected) errors
        # Tidy will handle the refund to utxo
        # Tidy will mark payment record expired
        # Tidy will call cancel_tx_slate to unlock the wallet outputs
        logger.exception("Failed to post payment because {}".format(repr(e)))
        raise PaymentError(500, str(e))
