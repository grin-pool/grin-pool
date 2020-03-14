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
import requests
import traceback
from datetime import datetime

from flask import Flask, request, jsonify, url_for, g
from flask_login import login_required, LoginManager
from flask_restful import Resource, Api, reqparse
from flask_httpauth import HTTPBasicAuth

from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.pool_payment import Pool_payment
from grinbase.model.users import Users

from grinlib import lib
from grinlib import grin
from grinlib import payments

# so hard...
#import pprint
#pp = pprint.PrettyPrinter(indent=4)

PROCESS = "paymentapi"

# XXX TODO: Get From config
MINIMUM_PAYOUT = 0

# Get K8s secret from container environment
payment_api_port = os.environ['PAYMENT_API_PORT']
wallet_api_user = os.environ['WALLET_OWNER_API_USER']
wallet_api_key = os.environ["WALLET_OWNER_API_PASSWORD"]
admin_user = os.environ["GRIN_POOL_ADMIN_USER"]
admin_pass = os.environ["GRIN_POOL_ADMIN_PASSWORD"]
app_secret_key = "xxxxyyyyyzzzzz" # os.environ["APP_SECRET_KEY"]

app = Flask(__name__)
app.secret_key = app_secret_key
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
auth = HTTPBasicAuth()
database = lib.get_db()
LOGGER = lib.get_logger(PROCESS)

@app.before_request
def pre_request():
    global database
    database.db.initializeSession()

@app.teardown_request
def teardn_request(response):
    global database
    database.db.destroySession()
    return response

@auth.verify_password
def verify_password(username, password):
    # Only the pool admin user is allowed to call this API
    if username == admin_user and password == admin_pass:
        g.user = username
        return True
    return False

##
# Payment REQUESTs
class PoolAPI_paymentrequest(Resource):
    @auth.login_required
    def post(self, id, function, address=None):
        try:
            LOGGER = lib.get_logger(PROCESS)
            LOGGER.warn("In PoolAPI_paymentrequest POST: {} - {}".format(id, function))
    
            # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            #LOGGER.warn("Payment requests are disabled")
            #response = jsonify({ 'message': 'Payouts are temporarily disabled' })
            #response.status_code = 400
            #return response
            # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    
            # Connect to DB
            try:
                database = lib.get_db()
            except Exception as e:
                LOGGER.exception("Failed to connect to the db: {}".format(e))
                response = jsonify({ 'message': "Something went wrong, please contact pool admin" })
                response.status_code = 500
                return response
    
    
            grin_owner_api_url = grin.get_owner_api_url()
            # Verify the users balance then call the wallet owner API to
            # generate a payment tx slate.  Return that slate to the caller
            if function == "get_tx_slate":
                ##
                # Offline Phase 1) issue_send_tx
                # Generate the send transaction slate
                try:
                    payment_slate = payments.get_tx_slate(
                            user_id = id,
                            logger = LOGGER,
                            database = database,
                            method = "api_paymentrequest",
                            invoked_by = "request",
                        )
                except payments.PaymentError as e:
                    # System Error Logging
                    LOGGER.exception("Failed to get a payment slate: {}".format(repr(e)))
                    # User Error Reporting
                    if e.code == 400:
                        response = jsonify({ 'message': e.message })
                    else:
                        response = jsonify({ 'message': "Something went wrong, please contact pool admin" })
                    response.status_code = e.code
                    return response
                return(payment_slate)
    
            elif function == "submit_tx_slate":
                ##
                # Offline Phase 2) finalize_tx
                # Submit the signed slate to be finalized
                try:
                    requestdata = request.data
                except AttributeError as e:
                    # System Error Logging
                    LOGGER.exception("Failed to submit a payment slate, missing slate data in request: {}".format(str(e)))
                    # User Error Reporting
                    response = jsonify({ 'message': 'Request is missing signed slate data' })
                    response.status_code = 400
                    return response
                try:
                    payments.submit_tx_slate(
                            user_id = id,
                            slate = requestdata,
                            logger = LOGGER,
                            database = database,
                        )
                    LOGGER.warn("submit_tx_slate completed Ok")
                    response = jsonify({'message': 'ok'})
                    response.status_code = 200
                    return response
                except payments.PaymentError as e:
                    # System Error Logging
                    LOGGER.exception("Failed to submit a payment slate: {}".format(repr(e)))
                    # User Error Reporting
                    if e.code == 400:
                        response = jsonify({ 'message': e.message })
                    else:
                        LOGGER.error("XXX")
                        response = jsonify({ 'message': "Something went wrong, please contact pool admin" })
                    response.status_code = e.code
                    LOGGER.error("YYY")
                    return response
    
            elif function in ["http", "https", "keybase"]:
                ##
                # Online http or Offline keybase
                # Instruct the wallet to pay via method
                # Add prefix if needed
                if function == "keybase":
                    message = "keybase payouts are disabled"
                    LOGGER.warn(message)
                    response = jsonify({ 'message': message })
                    response.status_code = 400
                    return response
                try:
                    LOGGER.warn("Request json: {}".format(request.json))
                    arg_data = ""
                    if request.json is not None:
                        arg_data = "?"
                        if "poloniex" in address: # Fuck, ugly - https://github.com/mimblewimble/grin/issues/2700
                            arg_data += "currency=" + request.json["currency"] + \
                                        "&command=" + request.json["command"] + \
                                        "&id=" + request.json["id"]
                        else:
                            for arg, val in request.json.items():
                                arg_data += arg + "=" + val + "&"
                            arg_data = arg_data[0:-1]
                    LOGGER.warn("sending to address: {}".format(address + arg_data))
                    payments.atomic_send(
                             user_id = id,
                             address = address + arg_data,
                             logger = LOGGER,
                             database = database,
                             method = function,
                             invoked_by = "request",
                         )
                    return "ok"
                except payments.PaymentError as e:
                    # System Error Logging
                    LOGGER.exception("Failed to complete {} tx: {}".format(function, repr(e)))
                    # User Error Reporting
                    if e.code == 400:
                        response = jsonify({ 'message': e.message })
                    else:
                        response = jsonify({ 'message': "Something went wrong, please contact pool admin" })
                    response.status_code = e.code
                    return response
        except Exception as e:
            LOGGER.exception(" Unexpected Exception: {}".format(repr(e)))
            response = jsonify({ 'message': "Something went wrong, please contact pool admin" })
            response.status_code = 500
            return response
            
api.add_resource(PoolAPI_paymentrequest,
        '/pool/payment/<string:function>/<int:id>',
        '/pool/payment/<string:function>/<int:id>/<path:address>',
)


# Start the API server 
# XXX TODO:  Use a real webserver
if __name__ == '__main__':
    debug = False
    try:
        floonet = os.environ["NET_FLAG"]
        if floonet == "--floonet":
            debug = True
    except Exception as e:
        pass
    app.run(debug=debug, host='0.0.0.0', port=payment_api_port)

