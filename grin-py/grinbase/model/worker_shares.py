#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, asc, and_, func
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

#from grinlib import lib

# This table contains worker share information per block

class Worker_shares(Base):
    __tablename__ = 'worker_shares'
    id = Column(BigInteger, primary_key=True)
    height = Column(BigInteger, nullable=False, index=True)
    worker = Column(String(1024), index=True)
    timestamp = Column(DateTime, index=True)
    difficulty = Column(Integer)
    valid = Column(Integer)
    invalid = Column(Integer)

    def __repr__(self):
        return "{} {} {} {} {} {}".format(
            self.height,
            self.worker,
            self.timestamp,
            self.difficulty,
            self.valid,
            self.invalid)

    def __init__(self, height, worker, timestamp, difficulty, valid, invalid):
        self.height = height
        self.worker = worker
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.valid = valid
        self.invalid = invalid

    def to_json(self, fields=None):
        obj = { 'height': self.height,
                'worker': self.worker,
                'timestamp': self.timestamp.timestamp(),
                'difficulty': self.difficulty,
                'valid': self.valid,
                'invalid': self.invalid,
              }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj

    # Get a list of all records in the table
    # XXX Please dont call this except in testing
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Worker_shares))

    # Get the height of the latest worker share record - so we know where to start from
    @classmethod
    def get_latest_height(cls):
        return database.db.getSession().query(func.max(Worker_shares.height)).scalar()

    # Get list of all worker share records by height and optionally range
    @classmethod
    def get_by_height(cls, height, range=1):
        h_start = height-(range-1)
        h_end = height
        return list(database.db.getSession().query(Worker_shares).filter(and_(Worker_shares.height >= h_start, Worker_shares.height <= h_end)).order_by(Worker_shares.height))
            
    # Get all pool shares by height and user
    @classmethod
    def get_by_user_and_height(cls, user, height, range=1):
        h_start = height-(range-1)
        h_end = height
        return list(database.db.getSession().query(Worker_shares).filter(and_(Worker_shares.height >= h_start, Worker_shares.height <= h_end, getattr(Worker_shares, "worker").like("%"+user))).order_by(Worker_shares.height))
