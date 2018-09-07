#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, asc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This table contains a record for each worker share accepted by the grin node

class Grin_shares(Base):
    __tablename__ = 'grin_shares'
    nonce = Column(String(20), primary_key=True, nullable=False)
    hash = Column(String(64))
    height = Column(BigInteger, nullable=False, index=True)
    actual_difficulty = Column(Integer)
    net_difficulty = Column(Integer)
    timestamp = Column(DateTime, index=True)
    found_by = Column(String(1024))
    is_solution = Column(Boolean)

    def __repr__(self):
        return "{} {} {} {} {} {} {} {}".format(
            self.hash,
            self.height,
            self.nonce,
            self.actual_difficulty,
            self.net_difficulty,
            self.timestamp,
            self.found_by,
            self.is_solution) 

    def __init__(self, hash, height, nonce, actual_difficulty, net_difficulty, timestamp, found_by, is_solution):
        self.hash = hash
        self.height = height
        self.nonce = nonce
        self.actual_difficulty = actual_difficulty
        self.net_difficulty = net_difficulty
        self.timestamp = timestamp
        self.found_by = found_by
        self.is_solution = is_solution

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Grin_shares))

    # Get a single record by nonce
    @classmethod
    def get_by_nonce(cls, nonce):
        return database.db.getSession().query(Grin_shares).filter(Grin_shares.nonce==nonce).first()

    # XXX

    # Get all shares found by user in the past n minutes
    @classmethod
    def get_all_by_user_and_minutes(cls, user, minutes):
        since_timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
        return list(database.db.getSession().query(Grin_shares).filter(and_(Grin_shares.found_by == user, Grin_shares.timestamp >= since_timestamp)))

    # Get stats records falling within requested range
    @classmethod
    def get_range_by_time(cls, ts_start, ts_end):
        records = list(database.db.getSession().query(Grin_shares).filter(and_(Grin_shares.timestamp >= ts_start, Grin_shares.timestamp <= ts_end)).order_by(asc(Grin_shares.height)))
        return records

    # Get stats records falling within requested range
    @classmethod
    def get_range_by_user_and_time(cls, user, ts_start, ts_end):
        records = list(database.db.getSession().query(Grin_shares).filter(and_(Grin_shares.timestamp >= ts_start, Grin_shares.timestamp <= ts_end, Grin_shares.found_by == user)).order_by(asc(Grin_shares.height)))
        return records
