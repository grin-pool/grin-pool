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

#
# Routines for getting Grin Pool data
#

import sys
import time
import requests
import json

from grinlib import lib
from grinbase.model.pool_blocks import Pool_blocks

# Share graph rate
def calculate_graph_rate(difficulty, ts1, ts2, n):
    # gps = 42 * (diff/scale) / 60
    # XXX TODO:  Assumes cuckoo 30 for all blocks - Fixes for cuckatoos?
    scale = 29.0
    timedelta = (ts2 - ts1).total_seconds()
    if n == 0 or timedelta == 0:
      return 0
    gps = (42.0 * float(n)) / float(timedelta)
    return gps
