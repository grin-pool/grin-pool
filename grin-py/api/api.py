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

from flask import Flask
from flask_restful import Resource, Api, reqparse

from grinbase.model.grin_stats import Grin_stats
from grinbase.model.blocks import Blocks
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_stats import Worker_stats

from grinlib import lib


app = Flask(__name__)
api = Api(app)


##
# -- Grin Network

# Stats
class GrinAPI_stats(Resource):
    def get(self, height, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if range == None:
            stat = Grin_stats.get_by_height(height)
            return stat.to_json(fields)
        else:
            stats = []
            for stat in Grin_stats.get_by_height(height, range):
                stats.append(stat.to_json(fields))
            return stats

api.add_resource(GrinAPI_stats,
        '/grin/stat/<int:height>',
        '/grin/stat/<int:height>/<string:fields>',
        '/grin/stats/<int:height>,<int:range>',
        '/grin/stats/<int:height>,<int:range>/<string:fields>')

# Blocks
class GrinAPI_blocks(Resource):
    def get(self, height, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if range == None:
            block = Blocks.get_by_height(height)
            return block.to_json(fields)
        else:
            blocks = []
            for block in Blocks.get_by_height(height, range):
                blocks.append(block.to_json(fields))
            return blocks

api.add_resource(GrinAPI_blocks,
        '/grin/block/<int:height>',
        '/grin/block/<int:height>/<string:fields>',
        '/grin/blocks/<int:height>,<int:range>',
        '/grin/blocks/<int:height>,<int:range>/<string:fields>')



##
# -- Pool

# Stats
class PoolAPI_stats(Resource):
    def get(self, height, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if range == None:
            stat = Pool_stats.get_by_height(height)
            return stat.to_json(fields)
        else:
            stats = []
            for stat in Pool_stats.get_by_height(height, range):
                stats.append(stat.to_json(fields))
            return stats

api.add_resource(PoolAPI_stats,
        '/pool/stat/<int:height>',
        '/pool/stat/<int:height>/<string:fields>',
        '/pool/stats/<int:height>,<int:range>',
        '/pool/stats/<int:height>,<int:range>/<string:fields>')

# Blocks
class PoolAPI_blocks(Resource):
    def get(self, height, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if range == None:
            block = Pool_blocks.get_by_height(height)
            if block == None:
                return {}
            else:
                return block.to_json(fields)
        else:
            blocks = []
            for block in Pool_blocks.get_by_height(height, range):
                blocks.append(block.to_json(fields))
            return blocks

api.add_resource(PoolAPI_blocks,
        '/pool/block/<int:height>',
        '/pool/block/<int:height>/<string:fields>',
        '/pool/blocks/<int:height>,<int:range>',
        '/pool/blocks/<int:height>,<int:range>/<string:fields>')



##
# -- Grin-Pool Workers

# Stats
class WorkerAPI_stats(Resource):
    def get(self, id, height, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if range == None:
            stat = Pool_workers.get_by_height(height)
            return stat.to_json(fields)
        else:
            stats = []
            for stat in Pool_workers.get_by_height(height, range):
                stats.append(stat.to_json(fields))
            return stats

api.add_resource(WorkerAPI_stats,
        '/worker/stat/<string:id>/<int:height>',
        '/worker/stat/<string:id>/<int:height>/<string:fields>',
        '/worker/stats/<string:id>/<int:s_height>,<int:e_height>',
        '/worker/stats/<string:id>/<int:s_height>,<int:e_height>/<string:fields>')

# Shares
class WorkerAPI_shares(Resource):
    def get(self, id, height, range=None, fields=None):
        if fields != None:
            fields = fields.split(',')
        return {'worker_shares':{'start': height, 'range': range, 'fields':fields}}

api.add_resource(WorkerAPI_shares,
        '/worker/share/<string:id>/<int:height>',
        '/worker/share/<string:id>/<int:height>/<string:fields>',
        '/worker/shares/<string:id>/<int:height>,<int:range>',
        '/worker/shares/<string:id>/<int:height>,<int:range>/<string:fields>')



# Start the API server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=13423)
