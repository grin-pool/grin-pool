#!/usr/bin/python3

import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Boolean, DateTime, asc, and_, func
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base


# This table contains share information - one record per solution type per user per block

class Shares(Base):
    __tablename__ = 'shares'
    id = Column(BigInteger, primary_key=True)
    edge_bits = Column(Integer)
    difficulty = Column(BigInteger) # Shares actual difficulty as reported in grin log
    valid = Column(Integer)
    invalid = Column(Integer)
    stale = Column(Integer)
    parent_id = Column(BigInteger, ForeignKey('worker_shares.id'))

    def __repr__(self):
        return str(self.to_json())

    def __init__(self, edge_bits, difficulty, valid, invalid, stale):
        self.edge_bits = edge_bits
        self.difficulty = difficulty
        self.valid = valid
        self.invalid = invalid
        self.stale = stale

    def to_json(self, fields=None):
        obj = { 'edge_bits': self.edge_bits,
                'difficulty': self.difficulty,
                'valid': self.valid,
                'invalid': self.invalid,
                'stale': self.stale,
              }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj
