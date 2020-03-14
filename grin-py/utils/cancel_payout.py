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

  
# Get pool
# Get username and amount
# Add amount to users account

import os
import sys
import getpass


sys.path.append("..")
from grinbase.constants.MysqlConstants import MysqlConstants
from grinbase.dbaccess import database
from sqlalchemy.sql import text
from grinbase.dbaccess.database import database_details
from grinbase.model.users import Users
from grinbase.model.pool_utxo import Pool_utxo
from grinbase.model.pool_payment import Pool_payment

MYSQL_ADDR = "mysql"

NANOGRIN = 1000000000

db_user = "root"
db_name = "pool"
db_host = None


def proceed_or_exit():
    proceed = "x"
    while proceed != "n" and proceed != "y":
        proceed = input("Proceed? (y/n): ")
        if proceed != "n" and proceed != "y":
            print("Invalid Input")
    if proceed != "y":
        print("Will not proceed")
        database.db.getSession().rollback()
        sys.exit(1)


# Disable "bracketed paste mode"
try:
    os.system('printf "\e[?2004l"')
except Exception as e:
    print("Failed to disable bracked paste mode: {}".format(e))


print(" ")
print("############# Cancel a payout #############")
print("## ")

db_password = getpass.getpass("MySQL Password: ")

db_host = MYSQL_ADDR
poolname = "Grin Pool"

# Connect to DB
try:
    connected = False
    while not connected:
        sql_check_read_only = text("""SHOW VARIABLES where variable_name="read_only";""")
        mysqlcontsraints = MysqlConstants(db_host, db_user, db_password, db_name)
        database.db = database_details(MYSQL_CONSTANTS=mysqlcontsraints)
        database.db.initialize()
        database.db.initializeSession()
        result = database.db.engine.execute(sql_check_read_only).first()
        if result[1] == "OFF":
            connected = True
        else:
            pass

except Exception as e:
    print(" ")
    print("Failed to connect to the database with:")
    print("  db_host: {}".format(db_host))
    print("  db_user: {}".format(db_user))
    print("  db_password: {}".format(db_password))
    print("  db_name: {}".format(db_name))
    print(" ")
    print("  Error: {}".format(e))
    sys.exit(1)

amount = 0
payout_id = int(input("payout id: "))
print("1) canceled")
print("2) expired")
new_state = input("Choose new payment state: ")
if new_state == "1":
    new_state = "canceled"
elif new_state == "2":
    new_state = "expired"
else:
    print("Invalid state choice")
    sys.exit(1)


# Get the payout record
payout_record = Pool_payment.get_by_id(payout_id)
print("{}".format(payout_record))
amount = payout_record.amount / float(NANOGRIN)

# Get the user id
user_id = payout_record.user_id
user_record = Users.get_by_id(user_id)
username = user_record.username
print("User: {}".format(username))

# Get the users UTXO record
user_utxo = Pool_utxo.get_by_userid(user_id)

# Print a report
print("Will update account for {} on {}".format(username, poolname))
print("Will cancel payout {} and add {} to users current balance of {} for a new balance of {}".format(payout_id, amount, float(user_utxo.amount)/NANOGRIN, float(user_utxo.amount)/NANOGRIN+amount))

# Confirm action
print("")
proceed_or_exit() 

# Do it
payout_record.state = new_state
user_utxo.amount += amount*NANOGRIN

# Sanity Check
print("")
print("Users updated balance: {}".format(float(user_utxo.amount)/NANOGRIN))

# Confirm action
print("")
proceed_or_exit() 

database.db.getSession().commit()
print("Done")
