#!/usr/bin/python3

import datetime
import operator

from sqlalchemy import Column, Integer, String, BigInteger, SmallInteger, Boolean, DateTime, func, asc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This table contains a record for each block as it is first seen by our pool

class Blocks(Base):
    __tablename__ = 'blocks'
    # id = Column(Integer, primary_key=True)
    height = Column(BigInteger, index=True, primary_key=True, autoincrement=False)
    hash = Column(String(64))
    version = Column(SmallInteger)
    previous = Column(String(64))
    timestamp = Column(DateTime, nullable=False, index=True)
    output_root = Column(String(64))
    range_proof_root = Column(String(64))
    kernel_root = Column(String(64))
    nonce = Column(String(20), nullable=False)
    edge_bits = Column(SmallInteger)
    total_difficulty = Column(BigInteger)
    secondary_scaling = Column(BigInteger)
    num_inputs = Column(Integer)
    num_outputs = Column(Integer)
    num_kernels = Column(Integer)
    fee = Column(BigInteger)
    lock_height = Column(BigInteger)
    total_kernel_offset = Column(String(64))
    state = Column(String(64))

    def __repr__(self):
        return "{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(
            self.hash,
            self.version,
            self.height,
            self.previous,
            self.timestamp,
            self.output_root,
            self.range_proof_root,
            self.kernel_root,
            self.nonce,
            self.edge_bits,
            self.total_difficulty,
            self.secondary_scaling,
            self.num_inputs,
            self.num_outputs,
            self.num_kernels,
            self.fee,
            self.lock_height,
            self.total_kernel_offset,
            self.state) 

    def __init__(self, hash, version, height, previous, timestamp, output_root, range_proof_root, kernel_root, nonce, edge_bits, total_difficulty, secondary_scaling, num_inputs, num_outputs, num_kernels, fee, lock_height, total_kernel_offset, state):
            self.hash = hash
            self.version = version
            self.height = height
            self.previous = previous
            self.timestamp = timestamp
            self.output_root = output_root
            self.range_proof_root = range_proof_root
            self.kernel_root = kernel_root
            self.nonce = nonce
            self.edge_bits = edge_bits
            self.total_difficulty = total_difficulty
            self.secondary_scaling = secondary_scaling
            self.num_inputs = num_inputs
            self.num_outputs = num_outputs
            self.num_kernels = num_kernels
            self.fee = fee
            self.lock_height = lock_height
            self.total_kernel_offset = total_kernel_offset
            self.state = state

    def to_json(self, fields=None):
        obj = { 'hash': self.hash,
                'version': self.version,
                'height': self.height,
                'previous': self.previous,
                'timestamp': self.timestamp.timestamp(),
                'output_root': self.output_root,
                'range_proof_root': self.range_proof_root,
                'kernel_root': self.kernel_root,
                'nonce': self.nonce,
                'edge_bits': self.edge_bits,
                'total_difficulty': self.total_difficulty,
                'secondary_scaling': self.secondary_scaling,
                'num_inputs': self.num_inputs,
                'num_outputs': self.num_outputs,
                'num_kernels': self.num_kernels,
                'fee': self.fee,
                'lock_height': self.lock_height,
                'total_kernel_offset': self.total_kernel_offset,
                'state': self.state
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
        return list(database.db.getSession().query(Blocks))

    # Get the count of the number of blocks we have
    @classmethod
    def count(cls):
        return database.db.getSession().query(func.count(Blocks.height)).scalar()
    # Get the first block we have thats > 0
    @classmethod
    def get_earliest(cls):
        lowest = database.db.getSession().query(func.min(Blocks.height)).scalar()
        return database.db.getSession().query(Blocks).filter(Blocks.height == lowest).first()

    # Get a single record by nonce
    @classmethod
    def get_by_nonce(cls, nonce):
        return database.db.getSession().query(Blocks).filter(Blocks.nonce == nonce).first()

    # Get the latest block record
    @classmethod
    def get_latest(cls, n=None):
        highest = database.db.getSession().query(func.max(Blocks.height)).scalar()
        if n == None:
            return database.db.getSession().query(Blocks).filter(Blocks.height == highest).first()
        else:
            return list(database.db.getSession().query(Blocks).filter(Blocks.height >= highest-n).order_by(asc(Blocks.height)))

    # Get record(s) by height and range
    @classmethod
    def get_by_height(cls, height, range=None):
        if range == None:
            return database.db.getSession().query(Blocks).filter(Blocks.height == height).first()
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Blocks).filter(and_(Blocks.height >= h_start, Blocks.height <= h_end)).order_by(asc(Blocks.height)))

    # Get stats records falling within requested range
    @classmethod
    def get_by_time(cls, ts, range=None):
        if range == None:
            # XXX TODO: Test this
            return database.db.getSession().query(Blocks).filter(Blocks.timestamp <= ts).first()
        else:
            ts_start = ts-range
            ts_end = ts
            return list(database.db.getSession().query(Blocks).filter(and_(Blocks.timestamp >= ts_start, Blocks.timestamp <= ts_end)).order_by(asc(Blocks.height)))



# def main():
#     PROCESS = "GrinPoolBaseModelBlockTest"
#     from grinlib import lib
#     config = lib.get_config()
#     logger = lib.get_logger(PROCESS)
#     logger.error("test")
#     database = lib.get_db()
# 
# 
# if __name__ == "__main__":
#     main()
