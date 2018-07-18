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

# Database Schema and API

import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import uuid
import lib


class db_api:
    TABLES = {}
    TABLES['blocks'] = ("CREATE TABLE `blocks` ("
                        "  `hash` varchar(64) NOT NULL,"
                        "  `version` smallint NOT NULL,"
                        "  `height` bigint NOT NULL,"
                        "  `previous` varchar(64) NOT NULL,"
                        "  `timestamp` DATETIME NOT NULL,"
                        "  `output_root` varchar(64) NOT NULL,"
                        "  `range_proof_root` varchar(64) NOT NULL,"
                        "  `kernel_root` varchar(64) NOT NULL,"
                        "  `nonce` varchar(20) NOT NULL,"
                        "  `total_difficulty` bigint NOT NULL,"
                        "  `total_kernel_offset` varchar(64) NOT NULL,"
                        "  `state` varchar(64) NOT NULL,"
                        "  PRIMARY KEY (`height`), UNIQUE KEY `hash` (`hash`)"
                        ") ENGINE=InnoDB")
    TABLES['pool_blocks'] = (
        "CREATE TABLE `pool_blocks` ("
        "  `hash` varchar(64) NOT NULL,"
        "  `height` bigint NOT NULL,"
        "  `nonce` varchar(20) NOT NULL,"
        "  `actual_difficulty` bigint NOT NULL,"
        "  `net_difficulty` bigint NOT NULL,"
        "  `timestamp` DATETIME NOT NULL,"
        "  `found_by` varchar(1024) NOT NULL,"
        #	"  `reward` smallint NOT NULL," <--- ADD THIS TODO XXX
        "  `state` varchar(20) NOT NULL,"
        "  PRIMARY KEY (`height`), UNIQUE KEY `nonce` (`nonce`)"
        ") ENGINE=InnoDB")
    TABLES['pool_shares'] = ("CREATE TABLE `pool_shares` ("
                             "  `height` bigint NOT NULL,"
                             "  `nonce` varchar(20) NOT NULL,"
                             "  `worker_difficulty` bigint NOT NULL,"
                             "  `timestamp` DATETIME NOT NULL,"
                             "  `found_by` varchar(1024) NOT NULL,"
                             "  `validated` boolean NOT NULL,"
                             "  `is_valid` boolean,"
                             "  `invalid_reason` varchar(1024),"
                             "  PRIMARY KEY (`nonce`)"
                             ") ENGINE=InnoDB")
    TABLES['grin_shares'] = ("CREATE TABLE `grin_shares` ("
                             "  `hash` varchar(64) NOT NULL,"
                             "  `height` bigint NOT NULL,"
                             "  `nonce` varchar(20) NOT NULL,"
                             "  `actual_difficulty` bigint NOT NULL,"
                             "  `net_difficulty` bigint NOT NULL,"
                             "  `timestamp` DATETIME NOT NULL,"
                             "  `found_by` varchar(1024) NOT NULL,"
                             "  `is_solution` boolean NOT NULL,"
                             "  PRIMARY KEY (`nonce`)"
                             ") ENGINE=InnoDB")
    TABLES['payments'] = ("CREATE TABLE `payments` ("
                          "  `id` bigint NOT NULL AUTO_INCREMENT,"
                          "  `height` bigint NOT NULL,"
                          "  `address` varchar(1024) NOT NULL,"
                          "  `reward` FLOAT NOT NULL,"
                          "  PRIMARY KEY (`id`)"
                          ") ENGINE=InnoDB")
    TABLES['last_run'] = ("CREATE TABLE `last_run` ("
                          "  `process` varchar(64) NOT NULL,"
                          "  `timestamp` varchar(1024) NOT NULL,"
                          "  PRIMARY KEY (`process`)"
                          ") ENGINE=InnoDB")
    TABLES['pool_utxo'] = ("CREATE TABLE `pool_utxo` ("
                           "  `id` CHAR(36) NOT NULL,"
                           "  `address` varchar(1024) NOT NULL,"
                           "  `amount` FLOAT NOT NULL,"
                           "  PRIMARY KEY (`id`)"
                           ") ENGINE=InnoDB")

    def __init__(self):
        config = lib.get_config()
        my_host = config["db"]["address"]
        my_port = config["db"]["port"]
        my_user = config["db"]["user"]
        my_pass = config["db"]["password"]
        my_dbname = config["db"]["db_name"]
        # Connect to mysql server
        try:
            self.cnx = mysql.connector.connect(
                host=my_host, port=my_port, user=my_user, password=my_pass)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            print(err)
            exit(1)
        # Open DB, create if needed
        try:
            cursor = self.cnx.cursor()
            self.cnx.database = my_dbname
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database(cursor)
                self.cnx.database = my_dbname
            else:
                print(err)
                exit(1)
        # Ensure all schema is created
        self.create_tables(cursor)
        # Init complete
        self.cnx.commit()

    def close(self):
        self.cnx.close()

    def create_database(self, cursor):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(
                    my_dbname))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    def create_tables(self, cursor):
        for name, ddl in self.TABLES.items():
            try:
                print("Creating table {}: ".format(name))
                cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

    #
    # Add Blocks to the database
    SQL_add_block = (
        "INSERT INTO blocks "
        "(hash, version, height, previous, timestamp, output_root, range_proof_root, kernel_root, nonce, total_difficulty, total_kernel_offset, state) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    def add_blocks(self, blocks, ignore_dup=False):
        cursor = self.cnx.cursor()
        for block in blocks:
            block = block + ("new", )
            try:
                cursor.execute(self.SQL_add_block, block)
            except mysql.connector.IntegrityError:
                if not ignore_dup:
                    raise
        cursor.close()
        self.cnx.commit()

    #
    # Read Blocks from the database
    SQL_get_blocks_by_height = (
        "SELECT hash, version, height, previous, timestamp, output_root, range_proof_root, kernel_root, nonce, total_difficulty, total_kernel_offset, state FROM blocks "
        "WHERE height IN (%s)")

    def get_blocks_by_height(self, requested):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_get_blocks_by_height, requested)
        for (bhash, version, height, previous, timestamp, output_root,
             range_proof_root, kernel_root, nonce, total_difficulty,
             total_kernel_offset, state) in cursor:
            res = (bhash, version, height, previous, timestamp, output_root,
                   range_proof_root, kernel_root, nonce, total_difficulty,
                   total_kernel_offset, state)
            result.append(res)
        cursor.close()
        self.cnx.commit()
        return result

    #
    # Update Blocks
    SQL_set_block_state = ("UPDATE blocks "
                           "SET state = (%s) "
                           "WHERE height = (%s)")

    def set_block_state(self, state, requested):
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_set_block_state, (
            state,
            requested,
        ))
        self.cnx.commit()
        cursor.close()

    #
    # Add PoolBlocks to the database
    SQL_add_poolblock = (
        "INSERT INTO pool_blocks "
        "(hash, height, nonce, actual_difficulty, net_difficulty, timestamp, found_by, state) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

    def add_poolblocks(self, poolblocks, ignore_dup=False):
        cursor = self.cnx.cursor()
        for poolblock in poolblocks:
            poolblock = poolblock + ("new", )
            try:
                cursor.execute(self.SQL_add_poolblock, poolblock)
            except mysql.connector.IntegrityError:
                if not ignore_dup:
                    raise
        cursor.close()
        self.cnx.commit()

    #
    # Read PoolBlocks from the database
    SQL_get_poolblocks_by_height = (
        "SELECT hash, height, nonce, actual_difficulty, net_difficulty, timestamp, found_by, state FROM pool_blocks "
        "WHERE height IN (%s)")

    def get_poolblocks_by_height(self, requested):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_get_poolblocks_by_height, requested)
        for (hash, height, nonce, actual_difficulty, net_difficulty, timestamp,
             found_by, state) in cursor:
            res = (hash, height, nonce, actual_difficulty, net_difficulty,
                   timestamp, found_by, state)
            result.append(res)
        cursor.close()
        self.cnx.commit()
        return result

    SQL_get_poolblocks_by_state = (
        "SELECT hash, height, nonce, actual_difficulty, net_difficulty, timestamp, found_by, state FROM pool_blocks "
        "WHERE state LIKE (%s)")

    def get_poolblocks_by_state(self, requested):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_get_poolblocks_by_state, (requested, ))
        for (hash, height, nonce, actual_difficulty, net_difficulty, timestamp,
             found_by, state) in cursor:
            res = (hash, height, nonce, actual_difficulty, net_difficulty,
                   timestamp, found_by, state)
            result.append(res)
        cursor.close()
        self.cnx.commit()
        return result

    #
    # Update PoolBlocks
    SQL_set_poolblock_state = ("UPDATE pool_blocks "
                               "SET state = (%s) "
                               "WHERE height = (%s)")

    def set_poolblock_state(self, state, requested):
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_set_poolblock_state, (
            state,
            requested,
        ))
        self.cnx.commit()
        cursor.close()

    #
    # Add Pool-Reported Shares to the database
    SQL_add_poolshares = (
        "INSERT INTO pool_shares "
        "(height, nonce, worker_difficulty, timestamp, found_by, validated, is_valid, invalid_reason) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

    def add_poolshares(self, shares, ignore_dup=False):
        # A few default values
        cursor = self.cnx.cursor()
        invalid_reason = "NULL"
        is_valid = "NULL"
        validated = "False"
        for share in shares:
            share = share + (
                validated,
                is_valid,
                invalid_reason,
            )
            try:
                cursor.execute(self.SQL_add_poolshares, share)
            except mysql.connector.IntegrityError:
                if not ignore_dup:
                    raise
        cursor.close()
        self.cnx.commit()

    #
    # Get all pool shares not yet [in]validated
    SQL_get_unvalidated_poolshares = (
        "SELECT height, nonce, worker_difficulty, timestamp, found_by, validated, is_valid, invalid_reason "
        "FROM pool_shares "
        "WHERE validated = False ")

    def get_unvalidated_poolshares(self):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_get_unvalidated_poolshares)
        for (height, nonce, worker_difficulty, timestamp, found_by, validated,
             is_valid, invalid_reason) in cursor:
            res = (
                height,
                nonce,
                worker_difficulty,
                timestamp,
                found_by,
                validated,
                is_valid,
                invalid_reason,
            )
            result.append(res)
        cursor.close()
        self.cnx.commit()
        return result

    #
    # [In]Validate a PoolShare
    SQL_set_poolshare_validation = ("UPDATE pool_shares "
                                    "SET validated = True, "
                                    "    is_valid = (%s), "
                                    "    invalid_reason = (%s) "
                                    "WHERE nonce = %s")

    def set_poolshare_validation(self, is_valid, invalid_reason, nonce):
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_set_poolshare_validation,
                       (is_valid, invalid_reason, nonce))
        self.cnx.commit()
        cursor.close()

    #
    # Get valid pool shares by height
    SQL_get_valid_poolshares_by_height = (
        "SELECT height, nonce, worker_difficulty, timestamp, found_by, validated, is_valid, invalid_reason "
        "FROM pool_shares "
        "WHERE validated = True "
        "AND is_valid = True "
        "AND height = %s "
        "ORDER BY height")

    def get_valid_poolshares_by_height(self, requested):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_get_valid_poolshares_by_height, (requested, ))
        for (height, nonce, worker_difficulty, timestamp, found_by, validated,
             is_valid, invalid_reason) in cursor:
            res = (
                height,
                nonce,
                worker_difficulty,
                timestamp,
                found_by,
                validated,
                is_valid,
                invalid_reason,
            )
            result.append(res)
        cursor.close()
        self.cnx.commit()
        return result

    #
    # Remove Pool-Reported Shares from the database
    SQL_remove_poolshares_to_height = ("DELETE FROM pool_shares "
                                       "WHERE height <= %s")

    def remove_poolshares_to_height(self, requested):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_remove_poolshares_to_height, (requested, ))
        cursor.close()
        self.cnx.commit()
        return result

    #
    # Add Grin-Reported Shares to the database
    SQL_add_grinshares = (
        "INSERT INTO grin_shares "
        "(hash, height, nonce, actual_difficulty, net_difficulty, timestamp, found_by, is_solution) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

    def add_grinshares(self, shares, ignore_dup=False):
        cursor = self.cnx.cursor()
        for share in shares:
            try:
                cursor.execute(self.SQL_add_grinshares, share)
            except mysql.connector.IntegrityError:
                if not ignore_dup:
                    raise
        cursor.close()
        self.cnx.commit()

    #
    # Read Grin-Reported Shares from the database
    SQL_get_grinshares_by_nonce = ("SELECT * FROM grin_shares "
                                   "WHERE nonce IN (%s)")

    def get_grin_share_by_nonce(self, requested):
        result = None
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_get_grinshares_by_nonce, (requested, ))
        for (hash, height, nonce, actual_difficulty, net_difficulty, timestamp,
             found_by, is_solution) in cursor:
            res = (hash, height, nonce, actual_difficulty, net_difficulty,
                   timestamp, found_by, is_solution)
            result = res
        cursor.close()
        self.cnx.commit()
        return result

    #
    # Remove Grin-Reported Shares from the database
    SQL_remove_grinshares_to_height = ("DELETE FROM grin_shares "
                                       "WHERE height <= %s")

    def remove_grinshares_to_height(self, requested):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_remove_grinshares_to_height, (requested, ))
        cursor.close()
        self.cnx.commit()
        return result

    #
    # Set "last run" timestamp
    SQL_set_last_run = ("INSERT INTO last_run "
                        "VALUES (%s, %s) "
                        "ON DUPLICATE KEY UPDATE timestamp=%s")

    def set_last_run(self, pr, ts):
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_set_last_run, (
            pr,
            ts,
            ts,
        ))
        cursor.close()
        self.cnx.commit()

    #
    # Create payment record for a worker
    SQL_create_payments = ("INSERT INTO payments "
                           "(height, address, reward)"
                           "VALUES (%s, %s, %s)")

    def create_payments(self, height, address, reward):
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_create_payments, (
            height,
            address,
            reward,
        ))
        cursor.close()
        self.cnx.commit()

    #
    # Get all pending payment records
    SQL_get_payments = ("SELECT * FROM payments " "ORDER BY id ")

    def get_payments(self):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_get_payments, )
        for (p_id, height, address, amount) in cursor:
            res = (
                p_id,
                height,
                address,
                amount,
            )
            result.append(res)
        cursor.close()
        self.cnx.commit()
        return result

    #
    # Delete payment records from the database
    SQL_remove_payment = ("DELETE FROM payments " "WHERE id = %s")

    def remove_payment(self, requested):
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_remove_payment, (requested, ))
        cursor.close()
        self.cnx.commit()

    #
    # Create or Add to worker UTXO
    SQL_create_or_add_utxo = ("INSERT INTO pool_utxo "
                              "(id, address, amount)"
                              "VALUES (%s, %s, %s) "
                              "ON DUPLICATE KEY UPDATE amount=amount+%s")

    def create_or_add_utxo(self, address, amount):
        p_id = str(uuid.uuid3(uuid.NAMESPACE_URL, str(address)))
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_create_or_add_utxo, (
            p_id,
            address,
            amount,
            amount,
        ))
        cursor.close()
        self.cnx.commit()

    #
    # Get UTXO records from the DB
    SQL_get_utxo = ("SELECT * FROM pool_utxo "
                    "WHERE amount >= %s "
                    "ORDER BY amount ")

    def get_utxo(self, requested):
        result = []
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_get_utxo, (requested, ))
        for (u_id, u_address, u_amount) in cursor:
            res = (u_id, u_address, u_amount)
            result.append(res)
        cursor.close()
        self.cnx.commit()
        return result

    #
    # Delete utxo records from the database
    SQL_remove_utxo = ("DELETE FROM pool_utxo " "WHERE id = %s")

    def remove_utxo(self, requested):
        cursor = self.cnx.cursor()
        cursor.execute(self.SQL_remove_utxo, (requested, ))
        cursor.close()
        self.cnx.commit()


# ----------------
# Random helper functions - move this to lib.py
def to_sqltimestamp(s_timestamp):
    year = str(datetime.today().year)
    tm = datetime.strptime(s_timestamp, '%b %d %H:%M:%S.%f')
    sql_timestamp = year + "-" + tm.strftime("%m-%d %H:%M:%S")
    return sql_timestamp
