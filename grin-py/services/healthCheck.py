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

# This service provides high-level health checks for various components and services

import sys
import socket
import requests
import json

from flask import Flask, request, Response
from flask_restful import Resource, Api, reqparse

from grinlib import lib
from grinlib import grin

PROCESS = "healthCheck"

# XXX TODO: Move to / get from  config
CACHE_TIME = 30
PORT = 32050
STRATUM_HOST = "stratum"
STRATUM_PORT = 3333
GRIN_API_URL = "http://grin:13413"
GRINPOOL_API_URL = "http://api.mwgrinpool.com:13423"
GRINMINT_API_URL = "http://api.grinmint.com"

# GLOBALS
STRATUM_CONN = None
KEEPALIVE_MSG = '{"id":"0","jsonrpc":"2.0","method":"keepalive"}\n'.encode()




app = Flask(__name__)
api = Api(app)

##
# Stratum
class Stratum_health(Resource):
    def get(self):
        global LOGGER
        global STRATUM_CONN
        global STRATUM_HOST
        global STRATUM_PORT
        if STRATUM_CONN is None:
            try:
                STRATUM_CONN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                STRATUM_CONN.settimeout(5)
                STRATUM_CONN.connect((STRATUM_HOST, STRATUM_PORT))
            except Exception as e:
                LOGGER.error("Failed to connect to stratum server: {}:{}, {}".format(STRATUM_HOST, STRATUM_PORT, e))
                STRATUM_CONN = None
        if self.check_keepalive():
            LOGGER.warn("Reporting health: ok")
            return Response("{'status':'ok'}", status=200, mimetype='application/json')
        else:
            LOGGER.warn("Reporting health: failed")
            return Response("{'status':'failed'}", status=503, mimetype='application/json')

    def check_keepalive(self):
        global STRATUM_CONN
        global LOGGER
        try:
            STRATUM_CONN.send(KEEPALIVE_MSG)
            data = STRATUM_CONN.recv(999999)
        except Exception as e:
            LOGGER.error("Failed to send keepalive to stratum connection: {}".format(e))
            STRATUM_CONN = None
            return False
        return True


##
# webui
class Webui_health(Resource):
    def get(self):
        # XXX TODO: Write this code
        return Response("{'status':'ok'}", status=200, mimetype='application/json')



##
# Grin
class Grin_health(Resource):
    def get(self):
        grin_height = self.get_grin_height()
        pool_height = self.get_grinpool_height()
        mint_height = self.get_grinmint_height()
        print("grin_height={}, pool_height={}, mint_height={}".format(grin_height, pool_height, mint_height))
        sys.stdout.flush()
        if (grin_height >= (pool_height - 5)) and (grin_height >= (mint_height - 5)):
            return Response("{'status':'ok'}", status=200, mimetype='application/json')
        else:
            return Response("{'status':'failed'}", status=503, mimetype='application/json')
            
    # Get the current height of the "local" grin node
    def get_grin_height(self):
        status_url = GRIN_API_URL + "/v1/status"
        latest = 0
        try:
            response = requests.get(status_url)
            latest = response.json()["tip"]["height"]
        except:
            pass
        return int(latest)

    # Get the height from the pools API
    def get_grinpool_height(self):
        url = GRINPOOL_API_URL + "/grin/block/height"
        latest = 0
        try:
            response = requests.get(url)
            latest = response.json()["height"]
        except:
            pass
        return int(latest)

    # Get the height from GrinMint Pool API
    def get_grinmint_height(sef):
        url = GRINMINT_API_URL + "/v1/networkStats"
        latest = 0
        try:
            response = requests.get(url)
            latest = response.json()["height"]
        except:
            pass
        return int(latest)
        





api.add_resource(Stratum_health, '/health/stratum')
api.add_resource(Webui_health, '/health/webui')
api.add_resource(Grin_health, '/health/grin')


def main():
    global PORT
    global LOGGER
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))
    app.run(debug=True, host='0.0.0.0', port=PORT)
    LOGGER.warn("=== Completed {}".format(PROCESS))

if __name__ == "__main__":
    main()
