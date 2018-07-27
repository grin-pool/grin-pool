#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime
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
        return database.db.getSession().query(Pool_shares).filter_by(nonce=nonce).first()

    # Get all valid pool shares by height
    @classmethod
    def get_valid_by_height(cls, height):
        return list(database.db.getSession().query(Pool_shares).filter_by(height=height).filter_by(is_valid=True).filter_by(validated=True))

    # XXX

    # Get all shares found by user in the past n minutes
    @classmethod
    def get_all_by_user_and_minutes(cls, user, minutes):
        since_timestamp = 0 # now() - minutes
        return list(database.db.getSession().query(Pool_shares).filter_by(found_by=user).filter_by(timestamp>since_timestamp))
