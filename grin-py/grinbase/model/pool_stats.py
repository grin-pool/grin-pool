import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Float, asc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "pool statistics" table
#   Each entry contains stats for the block at height

class Pool_stats(Base):
    __tablename__ = 'pool_stats'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    height = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    gps = Column(Float)
    active_miners = Column(Integer)
    shares_processed = Column(Integer) # this block only
    total_blocks_found = Column(Integer)
    total_shares_processed = Column(BigInteger) 
    total_grin_paid = Column(Float)
    
    
    def __repr__(self):
        return "{} {} {} {} {} {} {} {}".format(
            self.timestamp,
            self.height,
            self.gps,
            self.active_miners,
            self.shares_processed,
            self.total_shares_processed, 
            self.total_grin_paid, 
            self.total_blocks_found)

    def __init__(self, timestamp, height, gps, active_miners, shares_processed, total_shares_processed, total_grin_paid, total_blocks_found):
        self.timestamp = timestamp
        self.height = height
        self.gps = gps
        self.active_miners = active_miners
        self.shares_processed = shares_processed
        self.total_shares_processed = total_shares_processed
        self.total_grin_paid = total_grin_paid
        self.total_blocks_found = total_blocks_found

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Pool_stats))

    # Get the latest record
    @classmethod
    def get_latest(cls):
        highest = database.db.getSession().query(func.max(Pool_stats.height)).scalar()
        return database.db.getSession().query(Pool_stats).filter(Pool_stats.height==highest).first()

    # Get a single record by height
    @classmethod
    def get_by_height(cls, height):
        return database.db.getSession().query(Pool_stats).filter(Pool_stats.height==height).first()

    # Get the last N stats records and return as a list
    @classmethod
    def get_last_n(cls, n):
        highest = database.db.getSession().query(func.max(Pool_stats.height)).scalar()
        latest = list(database.db.getSession().query(Pool_stats).filter(Pool_stats.height >= highest-n).order_by(asc(Pool_stats.height)))
        return latest

    # Get stats records falling within requested range
    @classmethod
    def get_range(cls, ts_start, ts_end):
        records = list(database.db.getSession().query(Pool_stats).filter(and_(Pool_stats.timestamp >= ts_start, Pool_stats.timestamp <= ts_end)).order_by(asc(Pool_stats.height)))
        return records
