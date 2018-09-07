#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, asc, and_, func
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This table contains a record for each worker share accepted by the pool
# Note: Not all of these are valid shares, check for a matching grin_share to validate

class Pool_blocks(Base):
    __tablename__ = 'pool_blocks'
    height = Column(BigInteger, primary_key=True, nullable=False, index=True)
    hash = Column(String(64))
    nonce = Column(String(20), nullable=False)
    actual_difficulty = Column(Integer)
    net_difficulty = Column(Integer)
    timestamp = Column(DateTime, nullable=False, index=True)
    found_by = Column(String(1024))
    state = Column(String(20))

    def __repr__(self):
        return "{} {} {} {} {} {} {} {}".format(
            self.hash,
            self.height,
            self.nonce,
            self.actual_difficulty,
            self.net_difficulty,
            self.timestamp,
            self.found_by,
            self.state)

    def __init__(self, hash, height, nonce, actual_difficulty, net_difficulty, timestamp, found_by, state):
        self.hash = hash
        self.height = height
        self.nonce = nonce
        self.actual_difficulty = actual_difficulty
        self.net_difficulty = net_difficulty
        self.timestamp = timestamp
        self.found_by = found_by
        self.state = state

    def to_json(self, fields=None):
        obj = { 'hash': self.hash,
                'height': self.height,
                'nonce': self.nonce,
                'actual_difficulty': self.actual_difficulty,
                'net_difficulty': self.net_difficulty,
                'timestamp': self.timestamp.timestamp(),
                'found_by': self.found_by,
                'state': self.state
              }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj

    # Get number of records up to height
    @classmethod
    def count(cls, height=None):
        if height == None:
            return database.db.getSession().query(func.count(Pool_blocks.height)).scalar()
        else:
            return database.db.getSession().query(Pool_blocks).filter(Pool_blocks.height <= height).statement.with_only_columns([func.count()]).order_by(None).scalar()

    # Get a list of all records in the table
    # XXX Please dont call this except in testing
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Pool_blocks))

    # Get a single record by nonce
    @classmethod
    def get_by_nonce(cls, nonce):
        return database.db.getSession().query(Pool_blocks).filter(Pool_blocks.nonce == nonce).first()

    # Get all new pool blocks
    @classmethod
    def get_all_new(cls):
        return list(database.db.getSession().query(Pool_blocks).filter(Pool_blocks.state == "new"))

    # Get all unlocked pool blocks
    @classmethod
    def get_all_unlocked(cls):
        return list(database.db.getSession().query(Pool_blocks).filter(Pool_blocks.state == "unlocked"))

    # Get the latest pool block record
    @classmethod
    def get_latest(cls, n=None):
        highest = database.db.getSession().query(func.max(Pool_blocks.height)).scalar()
        if n == None:
            return database.db.getSession().query(Pool_blocks).filter(Pool_blocks.height == highest).first()
        else:
            return list(database.db.getSession().query(Pool_blocks).filter(Pool_blocks.height >= highest-n).order_by(asc(Pool_blocks.height)))

    # Get record(s) by height
    @classmethod
    def get_by_height(cls, height, range=None):
        if range == None:
            return database.db.getSession().query(Pool_blocks).filter(Pool_blocks.height == height).first()
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_blocks).filter(and_(Pool_blocks.height >= h_start, Pool_blocks.height <= h_end)).order_by(asc(Pool_blocks.height)))

    # Get records falling within requested time range
    @classmethod
    def get_by_time(cls, ts, range):
        if range == None:
            # XXX TODO: Test this
            return database.db.getSession().query(Pool_blocks).filter(Pool_blocks.timestamp <= ts).first()
        else:
            ts_start = ts-range
            ts_end = ts
            return list(database.db.getSession().query(Pool_blocks).filter(and_(Pool_blocks.timestamp >= ts_start, Pool_blocks.timestamp <= ts_end)).order_by(asc(Pool_blocks.height)))
