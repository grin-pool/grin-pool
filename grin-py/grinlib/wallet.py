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

#
# Routines for working with the pool wallet
#

import os
import sys
import time
import requests
import json
from datetime import datetime
import pprint
pp = pprint.PrettyPrinter(indent=4)


from grinlib import lib
from grinlib import grin

from grinbase.model.pool_wallet import Pool_wallet

def get_wallet_auth():
    wallet_api_user = None
    wallet_api_key = None
    try:
        # Get K8s secret from container environment
        wallet_api_user = os.environ['WALLET_OWNER_API_USER']
        wallet_api_key = os.environ["WALLET_OWNER_API_PASSWORD"]
    except KeyError as e:
        error_msg = "Failed to get_wallet_auth: {}".format(str(e))
        lib.LOGGER.exception(error_msg)
    return (wallet_api_user, wallet_api_key)


def call_owner_api(data):
    method = json.loads(data)["method"]
    grin_owner_api_url = grin.get_owner_api_url()
    wallet_auth = get_wallet_auth()
    r = requests.post(
            headers={'content-type': 'application/json'},
            url=grin_owner_api_url,
            auth=wallet_auth,
            data=data,
        )
    if r.status_code >= 300 or r.status_code < 200:
        error_msg = "Error calling {}.  Code: {} Reason: {}".format(method, r.status_code, r.reason)
        lib.LOGGER.error(error_msg)
        raise Exception(error_msg)
    r_json = r.json()
    if "error" in r_json:
        code = r_json["error"]["code"]
        message = r_json["error"]["message"]
        error_msg = "Error calling {}.  Code: {} Reason: {}".format(method, code, message)
        lib.LOGGER.error(error_msg)
        raise Exception(error_msg)
    if "Err" in r_json["result"]:
        code = 0
        message = r_json["result"]["Err"]
        error_msg = "Error calling {}.  Code: {} Reason: {}".format(method, code, message)
        lib.LOGGER.error(error_msg)
        raise Exception(error_msg)
    return r_json


def retrieve_summary_info(minimum_confirmations=1, refresh=True):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "retrieve_summary_info",
        "params": [refresh, minimum_confirmations],
    })
    r_json = call_owner_api(data)
    return r_json["result"]["Ok"][1]


def retrieve_txs(tx_id=None, tx_slate_id=None, refresh=True):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "retrieve_txs",
        "params": [refresh, tx_id, tx_slate_id],
    })
    r_json = call_owner_api(data)
    return r_json["result"]["Ok"][1]


def retrieve_outputs(include_spent=False, tx_id=None, refresh=False):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "retrieve_outputs",
        "params": [include_spent, refresh, tx_id],
    })
    r_json = call_owner_api(data)
    return r_json["result"]["Ok"][1]

def outputs_to_map_by_height(data):
    outputs_map = {}
    for op in data:
        height = int(op["output"]["height"])
        outputs_map[height] = op
    return outputs_map


def cancel_tx(tx_id=None, tx_slate_id=None):
    # Test
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "cancel_tx",
        "params": [tx_id, tx_slate_id],
    })
    r_json = call_owner_api(data)
    #raise Exception("test error: before cancel_tx")
    return r_json["result"]["Ok"]
    

def check_repair(delete_unconfirmed=False):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "check_repair",
        "params": [delete_unconfirmed],
    })
    r_json = call_owner_api(data)
    return r_json["result"]["Ok"]


def finalize_tx(slate):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "finalize_tx",
        "params": [slate],
    })
    r_json = call_owner_api(data)
    # Test
    #raise Exception("test error: After finalize_tx")
    return r_json["result"]["Ok"]


def get_stored_tx():
    raise Exception("Not Yet Implemented")


def init_send_tx(args):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "init_send_tx",
        "params": [args],
    })
    r_json = call_owner_api(data)
    # Test
    #raise Exception("test error: after init_send_tx")
    return r_json["result"]["Ok"]


def issue_invoice_tx():
    raise Exception("Not Yet Implemented")


def post_tx(tx, fluff=False):
    # Test
    #raise Exception("Test error: before post_tx")
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "post_tx",
        "params": [tx, fluff],
    })
    r_json = call_owner_api(data)
    # Test
    #raise Exception("test error: after post_tx")
    return r_json["result"]["Ok"]


def process_invoice_tx():
    raise Exception("Not Yet Implemented")


def restore():
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "restore",
        "params": [],
    })
    r_json = call_owner_api(data)
    return r_json["result"]["Ok"]


def tx_lock_outputs(slate, participant_id=0):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tx_lock_outputs",
        "params": [slate, participant_id],
    })
    r_json = call_owner_api(data)
    # Test
    #raise Exception("test error: after tx_lock_outputs")
    return r_json["result"]["Ok"]


def verify_slate_messages(slate):
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "verify_slate_message",
        "params": [slate],
    })
    r_json = call_owner_api(data)
    return r_json["result"]["Ok"]
