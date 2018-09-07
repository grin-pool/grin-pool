#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, asc, and_, func
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

#from grinlib import lib

# This table contains a record for each worker share accepted by the pool
# Note: Not all of these are valid shares, check for a matching grin_share to validate

class Pool_shares(Base):
    __tablename__ = 'pool_shares'
    height = Column(BigInteger, nullable=False, index=True)
    nonce = Column(String(20), primary_key=True, nullable=False)
    worker_difficulty = Column(Integer)
    timestamp = Column(DateTime, index=True)
    found_by = Column(String(1024), index=True)
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

    def to_json(self, fields=None):
        obj = { 'height': self.height,
                'nonce': self.nonce,
                'worker_difficulty': self.worker_difficulty,
                'timestamp': self.timestamp.timestamp(),
                'found_by': self.found_by,
                'validated': self.validated,
                'is_valid': self.is_valid,
                'invalid_reason': self.invalid_reason,
              }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj

    # Get number of records up to height
    @classmethod
    def count(cls, height, range=None, id=None):
        # id = lib.normalizeId(id)
        if range == None:
            if id == None:
                return database.db.getSession().query(Pool_shares).filter(Pool_shares.height == height).count()
            else:
                return database.db.getSession().query(Pool_shares).filter(Pool_shares.height == height).filter(getattr(Pool_shares, "found_by").like("%"+id)).count()
        else:
            h_start = height-(range-1)
            h_end = height
            if id == None:
                return database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height >= h_start, Pool_shares.height <= h_end)).count()
            else:
                return database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height >= h_start, Pool_shares.height <= h_end)).filter(getattr(Pool_shares, "found_by").like("%"+id)).count()

    # Get a list of all records in the table
    # XXX Please dont call this except in testing
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Pool_shares))

    # Get a list of all UNvalidated shares
    @classmethod
    def getUnvalidated(cls, height=0, range=None):
        if range is None:
            return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.validated == False, Pool_shares.height >= height)))
        else:
            return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.validated == False, Pool_shares.height <= height, Pool_shares.height >= height-range)))
 

    # Get a single record by nonce
    @classmethod
    def get_by_nonce(cls, nonce):
        return database.db.getSession().query(Pool_shares).filter(Pool_shares.nonce == nonce).first()

    # Get all pool shares by height
    @classmethod
    def get_by_height(cls, height, range=None):
        if range == None:
            return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height == height,  Pool_shares.is_valid == True)))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height >= h_start, Pool_shares.height <= h_end, Pool_shares.is_valid == True)).order_by(Pool_shares.height))
            
    # Get all pool shares by height and user
    @classmethod
    def get_by_user_and_height(cls, user, height, range=None):
        if range == None:
            return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height == height, getattr(Pool_shares, "found_by").like("%"+user))))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height >= h_start, Pool_shares.height <= h_end, getattr(Pool_shares, "found_by").like("%"+user))).order_by(Pool_shares.height))
            

    # Get all valid pool shares by height
    @classmethod
    def get_valid_by_height(cls, height, range=None):
        if range == None:
            return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height == height, Pool_shares.is_valid == True)).filter(Pool_shares.validated == True))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.height >= h_start, Pool_shares.height <= h_end)).filter(Pool_shares.validated == True).filter(Pool_shares.is_valid == True).order_by(Pool_shares.height))

    # Get count of pool shares by height
    @classmethod
    def get_count_by_height(cls, height):
        return database.db.getSession().query(Pool_shares).filter(Pool_shares.height == height).count()
    # XXX

    # Get all shares found by user in the past n minutes
    @classmethod
    def get_all_by_user_and_minutes(cls, user, minutes):
        since_timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
        return list(database.db.getSession().query(Pool_shares).filter(and_(getattr(Pool_shares, "found_by").like("%"+user), Pool_shares.timestamp >= since_timestamp)))

    # XXX DONT NEED THIS because we have get_by_height() above?
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
        records = list(database.db.getSession().query(Pool_shares).filter(and_(Pool_shares.timestamp >= ts_start, Pool_shares.timestamp <= ts_end, getattr(Pool_shares, "found_by").like("%"+user))).order_by(asc(Pool_shares.height)))
        return records

