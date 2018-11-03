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
from flask_cors import CORS

from grinbase.model.grin_stats import Grin_stats
from grinbase.model.blocks import Blocks
from grinbase.model.pool_stats import Pool_stats
from grinbase.model.pool_blocks import Pool_blocks
from grinbase.model.worker_stats import Worker_stats
from grinbase.model.worker_shares import Worker_shares
from grinbase.model.gps import Gps
from grinbase.model.shares import Shares
from grinbase.model.pool_utxo import Pool_utxo

from grinlib import lib
from grinlib import grin

# so hard...
import pprint
pp = pprint.PrettyPrinter(indent=4)


app = Flask(__name__)
CORS(app)
api = Api(app)


#################
# -- Grin Network

##
# Stats
class GrinAPI_stats(Resource):
    def get(self, height=None, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height is None or height == 0:
            stats = Grin_stats.get_latest(range)
        else:
            stats = Grin_stats.get_by_height(height, range)
        pp.pprint(stats)
        
        if range == None:
            if stats is None:
                return None
            return stats.to_json(fields)
        else:
            st = []
            for stat in stats:
                st.append(stat.to_json(fields))
            return st

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
    def get(self, height=None, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height is None or height == 0:
            blocks = Blocks.get_latest(range)
        else:
            blocks = Blocks.get_by_height(height, range)
        if range == None:
            if blocks is None:
                return None
            return blocks.to_json(fields)
        else:
            bl = []
            for block in blocks:
                bl.append(block.to_json(fields))
            return bl

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
# Blocks
class PoolAPI_blocks(Resource):
    def get(self, height=None, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height is None or height == 0:
            blocks = Pool_blocks.get_latest(range)
        else:
            blocks = Pool_blocks.get_by_height(height, range)
        if range == None:
            if blocks is None:
                return None
            return blocks.to_json(fields)
        else:
            bl = []
            for block in blocks:
                bl.append(block.to_json(fields))
            return bl

api.add_resource(PoolAPI_blocks,
        '/pool/block',
        '/pool/block/<string:fields>',
        '/pool/block/<int:height>',
        '/pool/block/<int:height>/<string:fields>',
        '/pool/blocks/<int:height>,<int:range>',
        '/pool/blocks/<int:height>,<int:range>/<string:fields>',
)

class PoolAPI_blocksCount(Resource):
    def get(self, height=None):
        database = lib.get_db()
        count = Pool_blocks.count(height)
        return count

api.add_resource(PoolAPI_blocksCount,
        '/pool/blocks/count',
        '/pool/blocks/count/<int:height>',
)


##
# Stats
class PoolAPI_stats(Resource):
    def get(self, height=None, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height is None or height == 0:
            stats = Pool_stats.get_latest(range)
        else:
            stats = Pool_stats.get_by_height(height, range)
        if range == None:
            if stats is None:
                return None
            return stats.to_json(fields)
        else:
            st = []
            for stat in stats:
                st.append(stat.to_json(fields))
            return st

api.add_resource(PoolAPI_stats,
        '/pool/stat',
        '/pool/stat/<string:fields>',
        '/pool/stat/<int:height>',
        '/pool/stat/<int:height>/<string:fields>',
        '/pool/stats/<int:height>,<int:range>',
        '/pool/stats/<int:height>,<int:range>/<string:fields>')


##
# Shares
class PoolAPI_shareCount(Resource):
    def get(self, height=None, range=None):
        database = lib.get_db()
        # Totals across all workers are stored in the Pool_stats record
        if range is None:
            if height is None:
                height = 0
            pool_st_rec = Pool_stats.get_by_height(height)
            if pool_st_rec is None:
                count = 0
            else:
                count = pool_st_rec.total_shares_processed
            return  { "height": height,
                       "count": count,
                     }
        else:
            counts = []
            pool_st_recs = Pool_stats.get_by_height(height, range)
            for st_rec in pool_st_recs:
                rec = { "height": st_rec.height,
                        "count": st_rec.total_shares_processed,
                      }
                counts.append(rec)
            return counts

api.add_resource(PoolAPI_shareCount,                                                              
        '/pool/share/count',                                                                      
        '/pool/share/count/<int:height>',
        '/pool/share/counts/<int:height>,<int:range>',
)


######################
# -- Grin-Pool Workers

##
# Stats
class WorkerAPI_stats(Resource):
    def get(self, id=None, height=0, range=None, fields=None):
        database = lib.get_db()
        fields = lib.fields_to_list(fields)
        if height == 0:
            height = Blocks.get_latest().height
        stats = []
        if id is None:
            for stat in Worker_stats.get_by_height(height, range):
                print("YYY: {}".format(stats))
                stats.append(stat.to_json(fields))
            return stats
        else:
            if range is None:
                res = Worker_stats.get_by_height_and_id(id, height)
                if res is None:
                    return "[]".to_json()
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

class WorkerAPI_shares(Resource):
    def get(self, id=None, height=0, range=0, fields=None):
        database = lib.get_db()
        print("id={} , height={}, range={}, fields={}".format(id,height,range,fields))
        fields = lib.fields_to_list(fields)
        if height == 0:
            height = Blocks.get_latest().height
        shares_records = []
        if id is None:
            for shares in Worker_shares.get_by_height(height, range):
                shares_records.append(shares.to_json(fields))
            return shares_records
        else:
            if range is None:
                worker_sh_recs = Worker_shares.get_by_height_and_id(height, id)
                print("worker_sh_recs = {}".format(worker_sh_recs))
                if res is None:
                    return "[]".to_json()
                return res.to_json(fields)
            else:
                for share in Worker_shares.get_by_height_and_id(height, id, range):
                    shares_records.append(share.to_json(fields))
                return shares_records

api.add_resource(WorkerAPI_shares,
        # All active workers
        '/worker/shares/<int:height>',
        '/worker/shares/<int:height>/<string:fields>',
        '/worker/shares/<int:height>,<int:range>',
        '/worker/shares/<int:height>,<int:range>/<string:fields>',
        # One specific worker
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
