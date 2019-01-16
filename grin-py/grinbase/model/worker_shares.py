#!/usr/bin/python3

import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Boolean, DateTime, asc, and_, func
from sqlalchemy.orm import relationship, load_only

from grinbase.dbaccess import database
from grinbase.model import Base

from grinbase.model.shares import Shares

# This table contains worker share information per block
#   Note the To-Many relationship with Shares

class Worker_shares(Base):
    __tablename__ = 'worker_shares'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    height = Column(BigInteger, primary_key=True, )
    timestamp = Column(DateTime, index=True)
    shares = relationship("Shares")
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return str(self.to_json())

    def __init__(self, height, user_id, timestamp):
        self.height = height
        self.user_id = user_id
        self.timestamp = timestamp

    def to_json(self, fields=None):
        share_data = []
        for rec in self.shares:
            share_data.append(rec.to_json())
        obj = { 'height': self.height,
                'user_id': self.user_id,
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

    def add_shares(self, edge_bits, difficulty, valid, invalid, stale):
        # First search existing shares to add to, else create new
        share_records = {}
        for rec in self.shares:
            share_records[rec.edge_bits] = rec
        if edge_bits not in share_records:
            rec = Shares(
                edge_bits = edge_bits,
                difficulty = difficulty,
                valid = valid,
                invalid = invalid,
                stale = stale,
            )
            self.shares.append(rec)
            return
        share_records[edge_bits].valid += valid
        share_records[edge_bits].invalid += invalid
        share_records[edge_bits].stale += stale
        
        

    # Get a list of all records in the table
    # XXX Please dont call this except in testing
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Worker_shares))

    # Get the height of the latest worker share record - so we know where to start from
    @classmethod
    def get_latest_height(cls, id=None):
        if id is None:
            return database.db.getSession().query(func.max(Worker_shares.height)).scalar()
        else:
            return database.db.getSession().query(Worker_shares.height).\
                                            filter(Worker_shares.user_id == id).\
                                            order_by(Worker_shares.height.desc()).\
                                            first()[0]

    # Get list of all worker share records by height and optionally range
    @classmethod
    def get_by_height(cls, height, range=None):
        if range is None:
            return list(database.db.getSession().query(Worker_shares).filter(Worker_shares.height == height))
        else:
            h_start = height-range-1
            h_end = height
            return list(database.db.getSession().query(Worker_shares).filter(and_(Worker_shares.height >= h_start, Worker_shares.height <= h_end)).order_by(Worker_shares.height))
            
    # Get all pool shares by height and user
    @classmethod
    def get_by_height_and_id(cls, height, id, range=None):
        print("height={}, id={}, range={}".format(height, id, range))
        if range is None:
            return list(database.db.getSession().query(Worker_shares).filter(and_(Worker_shares.height == height, Worker_shares.user_id == id))) #.one()
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Worker_shares).filter(and_(Worker_shares.height >= h_start, Worker_shares.height <= h_end, Worker_shares.user_id == id)).order_by(Worker_shares.height))
