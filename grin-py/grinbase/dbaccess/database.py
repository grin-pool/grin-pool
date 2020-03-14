import threading
import traceback

from sqlalchemy import *
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import IntegrityError

import grinbase
from grinbase.model import initialize_sql

db = None

class database_details:
    def __init__(self, MYSQL_CONSTANTS, user=None):
        self.db = MYSQL_CONSTANTS.mysql_db
        self.session = {}
        self.engine = None

        self.mysql_engine_string = "mysql+pymysql://{user}:{passwd}@{host}".format(
            user=MYSQL_CONSTANTS.mysql_user if user is None else user,
            passwd=MYSQL_CONSTANTS.mysql_passwd,
            host=MYSQL_CONSTANTS.mysql_host)

        # Create db if needed
        tmp_engine = create_engine(self.mysql_engine_string)
        
        # Query for existing databases
        existing_databases = tmp_engine.execute("SHOW DATABASES;")
        # Results are a list of single item tuples, so unpack each tuple
        existing_databases = [d[0] for d in existing_databases]
        
        # Create database if not exists
        if MYSQL_CONSTANTS.mysql_db not in existing_databases:
            tmp_engine.execute("CREATE DATABASE {0}".format(MYSQL_CONSTANTS.mysql_db))
            print("Created database {0}".format(MYSQL_CONSTANTS.mysql_db))

        # Connect to the DB
        self.mysql_string = "mysql+pymysql://{user}:{passwd}@{host}/{db_name}".format(
            user=MYSQL_CONSTANTS.mysql_user if user is None else user,
            passwd=MYSQL_CONSTANTS.mysql_passwd,
            host=MYSQL_CONSTANTS.mysql_host,
            db_name=MYSQL_CONSTANTS.mysql_db)
        self.engine = create_engine(
            self.mysql_string,
            echo=False,
            pool_recycle=3600,
            isolation_level="READ_COMMITTED",
            max_overflow=125,
            pool_size=32
        )

    def getSession(self):
        return self.session[threading.get_ident()]

    def initialize(self):
        initialize_sql(self.engine)
        self.session[threading.get_ident()] = scoped_session(grinbase.model.session_factory)

    def initializeSession(self):
        self.session[threading.get_ident()]  = scoped_session(grinbase.model.session_factory)

    def destroySession(self):
        self.session[threading.get_ident()].expunge_all()
        self.session[threading.get_ident()].close()
        self.session[threading.get_ident()].remove()

    def deleteDataObj(self, obj):
        try:
            self.session[threading.get_ident()].delete(obj)
            self.session[threading.get_ident()].commit()
            self.session[threading.get_ident()].flush()
        except Exception as e:
            print("An error occured ", e)
            print(e.args)
            traceback.print_exc()
            self.session[threading.get_ident()].rollback()
            raise e

    def createDataObj(self, obj):
        try:
            self.session[threading.get_ident()].add(obj)
            self.session[threading.get_ident()].commit()
            self.session[threading.get_ident()].flush()
        except Exception as e:
            print("An error occured ", e)
            print(e.args)
            traceback.print_exc()
            self.session[threading.get_ident()].rollback()
            raise e

    def createFromList(self, list):
        try:
            self.session[threading.get_ident()].bulk_save_objects(list)
            self.session[threading.get_ident()].commit()
            self.session[threading.get_ident()].flush()
        except Exception as e:
            print("An error occured ", e)
            print(e.args)
            traceback.print_exc()
            self.session[threading.get_ident()].rollback()
            raise e

    def createDataObj_ignore_duplicates(self, obj):
        try:
            self.session[threading.get_ident()].add(obj)
            self.session[threading.get_ident()].commit()
            self.session[threading.get_ident()].flush()
            return False
        except IntegrityError as e:
            self.session[threading.get_ident()].rollback()
            return True

