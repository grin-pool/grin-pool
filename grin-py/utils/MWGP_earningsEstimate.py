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

# ------------------------------------------------------------------------

###
# Estmate MWGrinPool earnings from historic data
# Input: --days, --c29gps, --c31gps

# Algorithm:
#   Get a list of the blocks found by MWGrinPool within the requested block range
#   For each pool-found-block:
#       Calculate the theoritical rewards for a user with provided GPS
#   Generate a graph

import os
import sys
import argparse
from datetime import datetime, timedelta

try:
    import requests
except Exception as e:
    print("Error:  This script requires the 'requests' module, please run `pip3 install requests`")
Graph = True
try:
    import plotly
    import plotly.graph_objs as go
except Exception as e:
    Graph = False

mwURL = "https://api.mwgrinpool.com"
NanoGrin = 1.0/1000000000.0
SecondsInDay = float(60*60*24)
PPLNGSeconds = float(60*60*4)

def print_header():
    print(" ")
    print("############# MWGrinPool Average Daily Earnings #############")
    print("## ")
    if Graph == False:
        print("   WARNING: ")
        print("     This script requires the 'plotly' module to produce a graph")
        print("     Please run: `pip3 install plotly`")
        print("     (running in text mode)")
        print(" ")

def print_footer(rewardTotal, c29gps, c31gps, numDays, startTS, endTS):
    print("  ")
    print("  ")
    print("   Report for {} days - from: {} to: {}".format(numDays, startTS.strftime("%m-%d-%y %H:%M"), endTS.strftime("%m-%d-%y %H:%M")))
    print("   Mining C29 at {}gps, C31 at {}gps".format(c29gps, c31gps))
    print(" ")
    print("   Total Rewards: {} Grin".format(rewardTotal))
    print("   Avg Daily Reward = {} Grin".format(rewardTotal/NumDays))
    print(" ")

def epoch_to_dt(epoch):
    return datetime.fromtimestamp(epoch)

parser = argparse.ArgumentParser()
parser.add_argument("--days", help="Number of days to average over")
parser.add_argument("--c29gps", help="Miners C29 Graphs/second")
parser.add_argument("--c31gps", help="Miners C31 Graphs/second")
parser.add_argument("--debug", help="Print lots of debug info")
args = parser.parse_args()


print_header()

if args.days is None:
    NumDays = float(input("   Number of days to average over: "))
else:
    NumDays = float(args.days)

if NumDays > 62:
    print(" ")
    print("   -- Error: Please limit your query to 60 days to prevent excess load on our pool API")
    print(" ")
    sys.exit(1)

if args.c29gps is None:
    C29Gps = float(input("   Miners C29 Graphs/second: "))
else:
    C29Gps = float(args.c29gps)

if args.c31gps is None:
    C31Gps = float(input("   Miners C31 Graphs/second: "))
else:
    C31Gps = float(args.c31gps)

if args.debug is None:
    debug = False

EndTS = datetime.now()
startTS = EndTS - timedelta(days=NumDays)


# Get a list of the pool-found-blocks within the range
poolblocksURL = mwURL + "/pool/blocks/0,1440/timestamp,height"
poolblocksJSON = requests.get(url = poolblocksURL).json()
poolblocks = [block['height'] for block in poolblocksJSON if(block['timestamp'] >= startTS.timestamp() and block['timestamp'] <= EndTS.timestamp())]
poolblocks.sort()
debug and print("Pool Blocks found in range: {}".format(poolblocks))

print(" ")
print("   Getting Mining Data: ")
rewardTotal = 0
x = [startTS]
y = [0]
debug and print("Start Time: {} - {}".format(startTS, startTS.timestamp()))
debug and print("End Time:   {} - {}".format(EndTS, EndTS.timestamp()))
debug or sys.stdout.write("   ")
sys.stdout.flush()
for blockHeight in poolblocks:
    # For each pool block, get some information:
    #   Secondary Scale Value
    #   Any TX fees included in the block reward
    grinBlockURL = mwURL + "/grin/block/{}/timestamp,height,secondary_scaling,fee".format(blockHeight)
    grinblockJSON = requests.get(url = grinBlockURL).json()
    #   Pool GPS at that block height
    poolGpsURL = mwURL + "/pool/stat/{}/gps".format(blockHeight)
    poolGpsJSON = requests.get(url = poolGpsURL).json()
    #   Calculate theoretical miners reward
    scale = (2**(1+31-24)*31)/float(max(29, grinblockJSON['secondary_scaling']))
    minerValue = C29Gps + C31Gps*scale
    poolValue = 0
    for gps in poolGpsJSON['gps']:
        if gps['edge_bits'] == 29:
            poolValue += gps['gps']
        else:
            poolValue += gps['gps']*scale
    debug and print("Miner value: {}, pool value: {}".format(minerValue, poolValue))
    fullMinersReward = (minerValue/poolValue)*(60+grinblockJSON['fee']*NanoGrin)
    tsNow = datetime.fromtimestamp(grinblockJSON['timestamp'])
    timedelta = tsNow - startTS
    # Check if we get the full reward or not
    if(timedelta.total_seconds() < PPLNGSeconds):
        minersReward = fullMinersReward * (timedelta.total_seconds()/PPLNGSeconds)
    else:
        minersReward = fullMinersReward
    debug and print("   + Miners reward for {} block {}: {}".format(datetime.fromtimestamp(grinblockJSON['timestamp']).strftime('%c'), blockHeight, minersReward))
    rewardTotal += minersReward
    # Graph
    x.append(tsNow)
    timedelta = tsNow - startTS
    debug and print("timedelta = {}".format(timedelta))
    daysSinceStartTS = float(timedelta.total_seconds())/float(SecondsInDay)
    debug and print("daysSinceStartTS = {}".format(daysSinceStartTS))
    y.append(rewardTotal/daysSinceStartTS)
    debug and print(" ")
    debug or sys.stdout.write(".")
    sys.stdout.flush()

x.append(EndTS)
y.append(rewardTotal/NumDays)
print_footer(rewardTotal, C29Gps, C31Gps, NumDays, startTS, EndTS)

if Graph == True:
    print("Generating graph...")
    graphName = "Avg Daily Reward: {} Grin".format(round(rewardTotal/NumDays, 2))
    graphData = [go.Scatter(x=x, y=y, name=graphName)]
    graphLayout = go.Layout(
        title=go.layout.Title(text=graphName),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text='Time',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#008000'
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text='Grin',
                font=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#008000'
                )
            )
        ),
    )
    graphFigure = go.Figure(data=graphData, layout=graphLayout)
    graph_name = "estimate-{}days.html".format(NumDays)
    plotly.offline.plot(graphFigure, filename=graph_name)
