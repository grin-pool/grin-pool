#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, asc, and_, func
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This table contains a record for each worker share accepted by the pool
# Note: Not all of these are valid shares, check for a matching grin_share to validate

class Pool_shares(Base):
    __tablename__ = 'pool_shares'
    height = Column(BigInteger, nullable=False)
    nonce = Column(String(20), primary_key=True, nullable=False)
    worker_difficulty = Column(Integer)
    timestamp = Column(DateTime)
    found_by = Column(String(1024))
    validated = Column(Boolean)
    is_valid = Column(Boolean)
    invalid_reason = Column(String(1024))

    def __repr__(self):
        return "{} {} {} {} {} {} {} {}".format(
            self.height,
            self.nonce,
            self.worker_difficulty,
            self.timestamp,
            self.found_by,
            self.validated,
            self.is_valid, 
            self.invalid_reason)

    def __init__(self, height, nonce, worker_difficulty, timestamp, found_by, validated, is_valid, invalid_reason):
        self.height = height
        self.nonce = nonce
        self.worker_difficulty = worker_difficulty
        self.timestamp = timestamp
        self.found_by = found_by
        self.validated = validated
        self.is_valid = is_valid
        self.invalid_reason = invalid_reason

    # Get number of records
    @classmethod
    def count(cls):
        q = database.db.getSession().query(func.count(Pool_shares.nonce)).scalar()
        cnt = int(q)

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Pool_shares))

    # Get a list of all UNvalidated shares
    @classmethod
    def getUnvalidated(cls):
        return list(database.db.getSession().query(Pool_shares).filter(Pool_shares.validated == False))

    # Get a single record by nonce
    @classmethod
    def get_by_nonce(cls, nonce):
        return database.db.getSession().query(Pool_shares).filter(Pool_shares.nonce == nonce).first()

    # Get all valid pool shares by height
    @classmethod
    def get_valid_by_height(cls, height):
        return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height == height, Pool_shares.is_valid == True)).filter(Pool_shares.validated == True))

    # Get count of pool shares by height
    @classmethod
    def get_count_by_height(cls, height):
        return database.db.getSession().query(Pool_shares).filter(Pool_shares.height == height).count()
    # XXX

    # Get all shares found by user in the past n minutes
    @classmethod
    def get_all_by_user_and_minutes(cls, user, minutes):
        since_timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
        return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.found_by == user, Pool_shares.timestamp >= since_timestamp)))

    # Get stats records falling within requested range
    @classmethod
    def get_range_by_height(cls, h_start, h_end):
        records = list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height >= h_start, Pool_shares.height <= h_end)).order_by(asc(Pool_shares.height)))
        return records

    # Get stats records falling within requested range
    @classmethod
    def get_range_by_time(cls, ts_start, ts_end):
        records = list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.timestamp >= ts_start, Pool_shares.timestamp <= ts_end)).order_by(asc(Pool_shares.height)))
        return records

    # Get stats records falling within requested range
    @classmethod
    def get_range_by_user_and_time(cls, user, ts_start, ts_end):
        records = list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.timestamp >= ts_start, Pool_shares.timestamp <= ts_end, Pool_shares.found_by == user)).order_by(asc(Pool_shares.height)))
        return records

