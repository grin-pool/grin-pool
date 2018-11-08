#!/usr/bin/python3

import datetime

from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, asc, and_, func
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This table contains worker share information per block
#   Note the To-Many relationship with Shares

class Worker_shares(Base):
    __tablename__ = 'worker_shares'
    id = Column(BigInteger, primary_key=True)
    height = Column(BigInteger, nullable=False, index=True)
    worker = Column(String(1024), index=True)
    timestamp = Column(DateTime, index=True)
    shares = relationship("Shares")

    def __repr__(self):
        return str(self.to_json())

    def __init__(self, height, worker, timestamp):
        self.height = height
        self.worker = worker
        self.timestamp = timestamp

    def to_json(self, fields=None):
        share_data = []
        for rec in self.shares:
            share_data.append(rec.to_json())
        obj = { 'height': self.height,
                'worker': self.worker,
                'timestamp': self.timestamp.timestamp(),
                'shares': share_data,
              }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj

    def num_shares(self):
        return self.num_valid() + self.num_invalid() + self.num_stale()

    def num_valid(self, edge_bits=None):
        if edge_bits is None:
            return sum([s.valid for s in self.shares])
        else:
            return sum([s.valid for s in self.shares if s.edge_bits == edge_bits])

    def num_invalid(self):
        return sum([s.invalid for s in self.shares])

    def num_stale(self):
        return sum([s.stale for s in self.shares])

    def sizes(self):
        return list(set([s.edge_bits for s in self.shares]))

    def num_shares_of_size(self, edge_bits):
        return sum([1 for s in self.shares if s == edge_bits])

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
    def get_by_height(cls, height, range=0):
        h_start = height-range
        h_end = height
        return list(database.db.getSession().query(Worker_shares).filter(and_(Worker_shares.height >= h_start, Worker_shares.height <= h_end)).order_by(Worker_shares.height))
            
    # Get all pool shares by height and user
    @classmethod
    def get_by_height_and_id(cls, height, id, range=0):
        print("height={}, id={}, range={}".format(height, id, range))
        h_start = height-range
        h_end = height
        return list(database.db.getSession().query(Worker_shares).filter(and_(Worker_shares.height >= h_start, Worker_shares.height <= h_end, getattr(Worker_shares, "worker").like("%"+id))).order_by(Worker_shares.height))
