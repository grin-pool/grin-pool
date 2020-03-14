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
from grinbase.dbaccess.database import database_details
from sqlalchemy.sql import text
from grinbase.model.users import Users
from grinbase.model.pool_utxo import Pool_utxo

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
        sys.exit(1)


print(" ")
print("############# Credit a user account #############")
print("## ")

db_password = getpass.getpass("MySQL Password: ")

db_host = MYSQL_ADDR
poolname = "Grin Pool"

# Connect to DB
try:
    sql_check_read_only = text("""SHOW VARIABLES where variable_name="read_only";""")
    connected = False
    while not connected:
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

username = input("Account username: ")
amount = float(input("Ammount to credit: "))
debit_pool = "x"
while debit_pool != "n" and debit_pool != "y":
    debit_pool = input("Debit the pools account? (y/n): ")
    if debit_pool != "n" and debit_pool != "y":
        print("Invalid input")
    

# Get the user id
user_id = Users.get_id_by_username(username)
if user_id == 0:
    print("Could not find user: {} in the database".format(username))
    sys.exit(1)
#user_record = Users.get_by_id(user_id)
#print(user_record)

# Get the users UTXO record
user_utxo = Pool_utxo.get_by_userid(user_id)
# Get the pools UTXO if needed
if debit_pool == "y":
    pooladmin_utxo = Pool_utxo.get_by_userid(1)


# Print a report
print("Will update account for {} on {}".format(username, poolname))
print("Will add {} to users current balance of {} for a new balance of {}".format(amount, float(user_utxo.amount)/NANOGRIN, float(user_utxo.amount)/NANOGRIN+amount))
if debit_pool == "y":
    print("Will subtract {} from pool admin current balance of {} for a new balance of {}".format(amount, float(pooladmin_utxo.amount)/NANOGRIN, float(pooladmin_utxo.amount)/NANOGRIN-amount))

# Confirm action
print("")
proceed_or_exit() 

# Do it
user_utxo.amount += amount*NANOGRIN
if debit_pool == "y":
    pooladmin_utxo.amount -= amount*NANOGRIN

# Sanity Check
print("")
print("Users updated balance: {}".format(float(user_utxo.amount)/NANOGRIN))
if debit_pool == "y":
    print("Pools updated balance: {}".format(float(pooladmin_utxo.amount)/NANOGRIN))

# Confirm action
print("")
proceed_or_exit() 

database.db.getSession().commit()
print("Done")
