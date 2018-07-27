#!/usr/bin/python3

import datetime
import operator

from sqlalchemy import Column, Integer, String, BigInteger, SmallInteger, Boolean, DateTime, func, asc
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This table contains a record for each block as it is first seen by our pool

class Blocks(Base):
    __tablename__ = 'blocks'
    hash = Column(String(64))
    version = Column(SmallInteger)
    height = Column(BigInteger, primary_key=True, nullable=False)
    previous = Column(String(64))
    timestamp = Column(DateTime)
    output_root = Column(String(64))
    range_proof_root = Column(String(64))
    kernel_root = Column(String(64))
    nonce = Column(String(20), nullable=False)
    total_difficulty = Column(BigInteger)
    total_kernel_offset = Column(String(64))
    state = Column(String(64))

    def __repr__(self):
        return "{} {} {} {} {} {} {} {} {} {} {} {}".format(
            self.hash,
            self.version,
            self.height,
            self.previous,
            self.timestamp,
            self.output_root,
            self.range_proof_root,
            self.kernel_root,
            self.nonce,
            self.total_difficulty,
            self.total_kernel_offset,
            self.state) 

    def __init__(self, hash, version, height, previous, timestamp, output_root, range_proof_root, kernel_root, nonce, total_difficulty, total_kernel_offset, state):
            self.hash = hash
            self.version = version
            self.height = height
            self.previous = previous
            self.timestamp = timestamp
            self.output_root = output_root
            self.range_proof_root = range_proof_root
            self.kernel_root = kernel_root
            self.nonce = nonce
            self.total_difficulty = total_difficulty
            self.total_kernel_offset = total_kernel_offset
            self.state = state

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Blocks))

    # Get a single record by height
    @classmethod
    def get_by_height(cls, height):
        return database.db.getSession().query(Blocks).filter_by(height=height).first()

    # Get a single record by nonce
    @classmethod
    def get_by_nonce(cls, nonce):
        return database.db.getSession().query(Blocks).filter_by(nonce=nonce).first()

    # Get the last N block records and return as a list
    @classmethod
    def get_last_n(cls, n):
        highest = database.db.getSession().query(func.max(Blocks.height)).scalar()
        latest = list(database.db.getSession().query(Blocks).filter(Blocks.height >= highest-n).order_by(asc(Blocks.height)))
        return latest



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
