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

import json

from flask import Flask, request
from flask_restful import Resource, Api, reqparse

from grinbase.model.grin_stats import Grin_stats
from grinbase.model.blocks import Blocks
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.pool_shares import Pool_shares
from grinbase.model.worker_stats import Worker_stats
from grinbase.model.pool_utxo import Pool_utxo

from grinlib import lib
from grinlib import grin


app = Flask(__name__)
api = Api(app)


#################
# -- Grin Network

##
# Stats
class GrinAPI_stats(Resource):
    def get(self, height=0, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height == 0:
            height = grin.get_current_height()
        if range == None:
            stat = Grin_stats.get_by_height(height)
            if stat is None:
                return None
            return stat.to_json(fields)
        else:
            stats = []
            for stat in Grin_stats.get_by_height(height, range):
                stats.append(stat.to_json(fields))
            return stats

api.add_resource(GrinAPI_stats,
        '/grin/stat',
        '/grin/stat/<string:fields>',
        '/grin/stat/<int:height>',
        '/grin/stat/<int:height>/<string:fields>',
        '/grin/stats/<int:height>,<int:range>',
        '/grin/stats/<int:height>,<int:range>/<string:fields>')

##
# Blocks
class GrinAPI_blocks(Resource):
    def get(self, height=0, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height == 0:
            height = grin.get_current_height()
        if range == None:
            block = Blocks.get_by_height(height)
            if block is None:
                return None
            return block.to_json(fields)
        else:
            blocks = []
            for block in Blocks.get_by_height(height, range):
                blocks.append(block.to_json(fields))
            return blocks

api.add_resource(GrinAPI_blocks,
        '/grin/block',
        '/grin/block/<string:fields>',
        '/grin/block/<int:height>',
        '/grin/block/<int:height>/<string:fields>',
        '/grin/blocks/<int:height>,<int:range>',
        '/grin/blocks/<int:height>,<int:range>/<string:fields>')



#########
# -- Pool

##
# Stats
class PoolAPI_stats(Resource):
    def get(self, height=0, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height == 0:
            height = grin.get_current_height()
        if range == None:
            stat = Pool_stats.get_by_height(height)
            if stat is None:
                return None
            return stat.to_json(fields)
        else:
            stats = []
            for stat in Pool_stats.get_by_height(height, range):
                stats.append(stat.to_json(fields))
            return stats

api.add_resource(PoolAPI_stats,
        '/pool/stat',
        '/pool/stat/<string:fields>',
        '/pool/stat/<int:height>',
        '/pool/stat/<int:height>/<string:fields>',
        '/pool/stats/<int:height>,<int:range>',
        '/pool/stats/<int:height>,<int:range>/<string:fields>')

##
# Blocks
class PoolAPI_blocks(Resource):
    def get(self, height=0, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height == 0:
            height = Pool_blocks.get_latest().height
        if range == None:
            block = Pool_blocks.get_by_height(height)
            if block is None:
                return None
            else:
                return block.to_json(fields)
        else:
            blocks = []
            for block in Pool_blocks.get_by_height(height, range):
                blocks.append(block.to_json(fields))
            return blocks

api.add_resource(PoolAPI_blocks,
        '/pool/block',
        '/pool/block/<string:fields>',
        '/pool/block/<int:height>',
        '/pool/block/<int:height>/<string:fields>',
        '/pool/blocks/<int:height>,<int:range>',
        '/pool/blocks/<int:height>,<int:range>/<string:fields>')



######################
# -- Grin-Pool Workers

##
# Stats
class WorkerAPI_stats(Resource):
    def get(self, id=None, height=0, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height == 0:
            height = grin.get_current_height()
        stats = []
        if id == None:
            for stat in Worker_stats.get_by_height(height, range):
                stats.append(stat.to_json(fields))
            return stats
        else:
            if range == None:
                res = Worker_stats.get_by_height_and_id(id, height)
                if res is None:
                    return res
                return res.to_json(fields)
            else:
                for stat in Worker_stats.get_by_height_and_id(id, height, range):
                    stats.append(stat.to_json(fields))
                return stats

api.add_resource(WorkerAPI_stats,
        # All active workers
        '/worker/stats/<int:height>',
        '/worker/stats/<int:height>/<string:fields>',
        '/worker/stats/<int:height>,<int:range>',
        '/worker/stats/<int:height>,<int:range>/<string:fields>',
        # One specific worker
        '/worker/stat/<string:id>/<int:height>',
        '/worker/stat/<string:id>/<int:height>/<string:fields>',
        '/worker/stats/<string:id>/<int:height>,<int:range>',
        '/worker/stats/<string:id>/<int:height>,<int:range>/<string:fields>')

##
# Share
class WorkerAPI_share_count(Resource):
    def get(self, id=None, height=0, range=None):
        database = lib.get_db()
        print("id={} , height={}, range = {}".format(id,height,range))
        if range == 0:
            range = grin.get_current_height()
        if height == 0:
            height = grin.get_current_height()
        return Pool_shares.count(height, range, id)

api.add_resource(WorkerAPI_share_count,
        '/worker/shares/count',
        '/worker/shares/<int:height>/count',
        '/worker/shares/<int:height>,<int:range>/count',
        '/worker/shares/<string:id>/count',
        '/worker/shares/<string:id>/<int:height>/count',
        '/worker/shares/<string:id>/<int:height>,<int:range>/count')

class WorkerAPI_shares(Resource):
    def get(self, id=None, height=0, range=None, fields=None):
        database = lib.get_db()
        print("id={} , height={}, range = {}, fields = {}".format(id,height,range,fields))
        if height == 0:
            height = grin.get_current_height() + 1
        if fields != None:
            fields = fields.split(',')
        shares = []
        if id is None:
            for share in Pool_shares.get_by_height(height, range):
                shares.append(share.to_json(fields))
            return shares
        else:
            for share in Pool_shares.get_by_user_and_height(id, height, range):
                shares.append(share.to_json(fields))
            return shares
            

api.add_resource(WorkerAPI_shares,
        '/worker/shares/<string:id>',
        '/worker/shares/<string:id>/<string:fields>',
        '/worker/shares/<string:id>/<int:height>',
        '/worker/shares/<string:id>/<int:height>/<string:fields>',
        '/worker/shares/<string:id>/<int:height>,<int:range>',
        '/worker/shares/<string:id>/<int:height>,<int:range>/<string:fields>')


######################
# -- Worker Payments

##
# pool_utxo
class WorkerAPI_payments(Resource):
    def get(self, id=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        utxo = Pool_utxo.get_by_address(id)
        return utxo.to_json(fields)


api.add_resource(WorkerAPI_payments,
        '/worker/payment/<string:id>')


# Start the API server 
# XXX TODO:  Use a real webserver
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=13423)
