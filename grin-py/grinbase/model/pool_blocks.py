#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This table contains a record for each worker share accepted by the pool
# Note: Not all of these are valid shares, check for a matching grin_share to validate

class Pool_blocks(Base):
    __tablename__ = 'pool_blocks'
    hash = Column(String(64))
    height = Column(BigInteger, primary_key=True, nullable=False)
    nonce = Column(String(20), nullable=False)
    actual_difficulty = Column(Integer)
    net_difficulty = Column(Integer)
    timestamp = Column(DateTime)
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

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Pool_blocks))

    # Get a single record by height
    @classmethod
    def get_by_height(cls, height):
        return database.db.getSession().query(Pool_blocks).filter_by(height=height).first()

    # Get a single record by nonce
    @classmethod
    def get_by_nonce(cls, nonce):
        return database.db.getSession().query(Pool_blocks).filter_by(nonce=nonce).first()

    # Get all new pool blocks
    @classmethod
    def get_all_new(cls):
        return list(database.db.getSession().query(Pool_blocks).filter_by(state="new"))

    # Get all unlocked pool blocks
    @classmethod
    def get_all_unlocked(cls):
        return list(database.db.getSession().query(Pool_blocks).filter_by(state="unlocked"))
