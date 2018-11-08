#!/usr/bin/python3

import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Float, BigInteger, Boolean, DateTime, asc, and_, func
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base


# This table contains Estimated Graph Rate information

class Gps(Base):
    __tablename__ = 'gps'
    id = Column(BigInteger, primary_key=True)
    edge_bits = Column(Integer)
    gps = Column(Float)
    grin_stats_id = Column(BigInteger, ForeignKey('grin_stats.height'))
    pool_stats_id = Column(BigInteger, ForeignKey('pool_stats.height'))
    worker_stats_id = Column(Integer, ForeignKey('worker_stats.id'))

    def __repr__(self):
        return str(self.to_json())

    def __init__(self, edge_bits, gps):
        self.edge_bits = edge_bits
        self.gps = gps

    def to_json(self, fields=None):
        obj = { 'edge_bits': self.edge_bits,
                'gps': self.gps,
              }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj
