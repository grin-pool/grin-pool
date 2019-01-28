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

import sys
import os
import requests
import json
import subprocess
import argparse
import getpass
from datetime import datetime

def print_banner():
    print(" ")
    print("############# MWGrinPool Payout Request Script #############")
    print("## Started: {} ".format(datetime.now()))
    print("## ")

def print_footer():
    print("## ")
    print("## Complete: {} ".format(datetime.now()))
    print("############# MWGrinPool Payout Request Complete #############")
    print(" ")

##
# Get configuration - either from commandline or by prompting the user
parser = argparse.ArgumentParser()
parser.add_argument("--pool_user", help="Username on MWGrinPool")
parser.add_argument("--pool_pass", help="Password on MWGrinPool")
parser.add_argument("--wallet_pass", help="Your grin wallet password")
args = parser.parse_args()

print_banner()
prompted = False

if args.pool_user is None:
    username = input("   MWGrinPool Username: ")
    prompted = True
else:
    username = args.pool_user

if args.pool_pass is None:
    password = getpass.getpass("   MWGrinPool Password: ")
    prompted = True
else:
    password = args.pool_pass

if args.wallet_pass is None:
    wallet_pass = getpass.getpass("   Wallet Password: ")
    prompted = True
else:
    wallet_pass = args.wallet_pass


if prompted:
    print(" ")

## --------------------------------
# End of User Configuration section
## --------------------------------

mwURL = "https://api.mwgrinpool.com"
POOL_MINIMUM_PAYOUT = 0.25
tmpfile = "unsigned_slate.txt"

dont_clean = False

# Cleanup
if os.path.exists(tmpfile):
    # An unsigned slate file exists
    # XXX TODO: check if the response exists and if not offer to try to process it?
    os.remove(tmpfile)

##
# Find Grin Wallet Command
grin_cmd = "grin"
cwd = os.getcwd()
path = os.environ.get('PATH')
path = cwd + ":" + cwd + "/grin:" + path
for directory in path.split(":"):
    if os.path.isfile(directory + "/grin"):
        grin_cmd = directory + "/grin"

##
# Wallet Sanity Check
wallettest_cmd = [
    grin_cmd,
      "wallet",
        "-p", wallet_pass,
      "info",
]
try:
    sys.stdout.write("   ... Checking that your wallet works: ")
    sys.stdout.flush()
    output = subprocess.check_output(wallettest_cmd, stderr=subprocess.STDOUT, shell=False)
    # print("{}".format(output))  < --- this is success output
    print("Ok.")
except subprocess.CalledProcessError as exc:
    print("Failed")
    print(" ")
    print(" ")
    print("   *** Error: Wallet test failed with rc {} and output {}".format(exc.returncode, exc.output))
    print_footer()
    sys.exit(1)
except Exception as e:
    print("Failed")
    print(" ")
    print(" ")
    print("   *** Error: Wallet test failed with error {}".format(str(e)))
    print_footer()
    sys.exit(1)


##
# Get my pool user_id
get_user_id = mwURL + "/pool/users"
r = requests.get(
        url = get_user_id,
        auth = (username, password),
)
if r.status_code != 200:
    print(" ")
    print("   *** Failed to get your account information from MWGrinPool: {}".format(r.text))
    print_footer()
    sys.exit(1)
user_id = str(r.json()["id"])

##
# Get the users balance
sys.stdout.write('   ... Getting miner balance: ')
sys.stdout.flush()
get_user_balance = mwURL + "/worker/utxo/"+user_id
r = requests.get(
        url = get_user_balance,
        auth = (username, password),
)
if r.status_code != 200:
    print("Failed")
    print(" ")
    print(" ")
    print("   *** Failed to get your account balance: {}".format(r.text))
    print_footer()
    sys.exit(1)
if r.json() is None:
    balance_nanogrin = 0
else:
    balance_nanogrin = r.json()["amount"]
balance = balance_nanogrin / 1000000000.0
print("{} Grin".format(balance))


##
# Only continue if there are funds available
if balance <= POOL_MINIMUM_PAYOUT:
    print(" ")
    print("   *** Not enough funds available to request a payment.")
    print(" ")
    print("       Note: If you have recently attempted a payment request that did not complete, the pool will return your funds within 30 minutes.")
    print("       Please try again later.")
    print_footer()
    sys.exit(0)

##
# Get the initial tx slate and write it to a file
sys.stdout.write('   ... Getting payment slate: ')
sys.stdout.flush()
get_tx_slate_url = mwURL + "/pool/payment/get_tx_slate/"+user_id
r = requests.post(
        url = get_tx_slate_url,
        auth = (username, password),
)
if r.status_code != 200:
    print("Failed")
    print(" ")
    print(" ")
    print("Failed to get a payment slate.")
    print_footer()
    sys.exit(1)
f = open(tmpfile, "w")
f.write(r.text) 
f.flush()
f.close()
print("Ok.")

##
# Call the wallet CLI to receive and sign the slate
recv_cmd = [
    "grin",
      "wallet",
        "-p", wallet_pass,
      "receive",
        "-i", tmpfile,
]
try:
    sys.stdout.write("   ... Running the grin wallet receive command to sign the slate: ")
    #sys.stdout.write("   ... Debug: {} ".format(recv_cmd))
    sys.stdout.flush()
    output = subprocess.check_output(recv_cmd, stderr=subprocess.STDOUT, shell=False)
    # print("{}".format(output))  < --- this is success output
    if not dont_clean:
        os.remove(tmpfile)
    with open(tmpfile + '.response', 'r') as tx_slate_response:
        signed_tx_slate = tx_slate_response.read()
    print("Ok.")
except subprocess.CalledProcessError as exc:
    print("Failed")
    print(" ")
    print(" ")
    print("   *** Error: Signing slate failed with rc {} and output {}".format(exc.returncode, exc.output))
    print_footer()
    sys.exit(1)
except Exception as e:
    print("Failed")
    print(" ")
    print(" ")
    print("   *** Error: Wallet receive failed with error {}".format(str(e)))
    print_footer()
    sys.exit(1)


##
# Submit the signed slate back to MWGrinPool to be finalized and posted to the network
sys.stdout.write("   ... Submitting the signed slate back to GrinPool: ")
sys.stdout.flush()
submit_tx_slate_url = mwURL + "/pool/payment/submit_tx_slate/"+user_id
r = requests.post(
        url = submit_tx_slate_url,
        data = signed_tx_slate,
        auth = (username, password),
)
if r.status_code != 200:
    print("Failed")
    print(" ")
    print(" ")
    print("   *** Failed to submit signed slate - {}".format(r.text))
    print_footer()
    sys.exit(1)
if not dont_clean:
    os.remove(tmpfile+'.response')
print("Ok.")

print_footer()
sys.exit(0)
