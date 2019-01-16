#!/usr/bin/python3

import sys
import os

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError

from grinbase.model.users import Users

from grinlib import lib
from grinlib import grin

PROCESS = "dbInit"

def main():
    CONFIG = lib.get_config()
    LOGGER = lib.get_logger(PROCESS)
    LOGGER.warn("=== Starting {}".format(PROCESS))

    # Get DB Config
    db_address = CONFIG["db"]["address"]
    db_port = CONFIG["db"]["port"]
    db_user = CONFIG["db"]["user"]
    db_password = os.environ['MYSQL_ROOT_PASSWORD']
    db_name = CONFIG["db"]["db_name"]
    LOGGER.warn("Got Config: db_address: {}, db_port: {}, db_user: {}, db_password: {}, db_name: {}".format(db_address, db_port, db_user, db_password, db_name))

    # Create the DB if it does not already exist
    mysql_engine_string = "mysql+pymysql://{user}:{password}@{host}:{port}".format(
        user = db_user,
        password = db_password,
        host = db_address,
        port = db_port)
    sys.stdout.flush()


    # Create db if needed
    tmp_engine = create_engine(mysql_engine_string)
    conn = tmp_engine.connect()
    conn.execute("commit")
    conn.execute("CREATE DATABASE IF NOT EXISTS {};".format(db_name))
    conn.close()
    LOGGER.warn("Created db: {}".format(db_name))

    # Connect to the DB
    mysql_string = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}".format(
            user = db_user,
            passwd = db_password,
            host = db_address,
            db_name = db_name,
            port = db_port)
    engine = create_engine(
            mysql_string,
            echo=False,
            pool_recycle=3600,
            isolation_level="READ_COMMITTED",
            max_overflow=125,
            pool_size=32
        )
    LOGGER.warn("Get Engine")

    # Create Special Users
    database = lib.get_db()

    ##
    # Admin
    LOGGER.warn("Validate Admin user account")
    try:
        admin_user = os.environ["GRIN_POOL_ADMIN_USER"]
        admin_pass = os.environ["GRIN_POOL_ADMIN_PASSWORD"]
    except KeyError:
        LOGGER.error("We dont have Admin account info, failed...")
        sys.exit(1)
    # Create the account
    user = Users.get_by_id(1)
    if user is not None:
        database.db.deleteDataObj(user)
    user = Users(
            id = 1,
            username = admin_user,
            password = admin_pass,
        )
    database.db.createDataObj(user)

if __name__ == "__main__":
    main()
