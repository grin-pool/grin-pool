#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This table contains a record for each worker share accepted by the grin node

class Grin_shares(Base):
    __tablename__ = 'grin_shares'
    hash = Column(String(64))
    height = Column(BigInteger, nullable=False)
    nonce = Column(String(20), primary_key=True, nullable=False)
    actual_difficulty = Column(Integer)
    net_difficulty = Column(Integer)
    timestamp = Column(DateTime)
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
        return database.db.getSession().query(Grin_shares).filter_by(nonce=nonce).first()
