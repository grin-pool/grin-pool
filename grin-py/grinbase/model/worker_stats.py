import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Float, asc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "Worker statistics" table
#   Each entry contains stats for a worker at the given block height
#   There will be at most one Worker_stats record per block height, and will be
#     none for the time when the miner is not active

class Worker_stats(Base):
    __tablename__ = 'worker_stats'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    height = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    gps = Column(Float)
    active_miners = Column(Integer)
    shares_processed = Column(Integer)  # this block only
    total_shares_processed = Column(BigInteger)
    
    
    def __repr__(self):
        return "{} {} {} {} {} {}".format(
            self.timestamp,
            self.height,
            self.gps,
            self.active_miners,
            self.shares_processed.
            self.total_shares_processed)

    def __init__(self, timestamp, height, gps, active_miners, shares_processed, total_shares_processed):
        self.timestamp = timestamp
        self.height = height
        self.gps = gps
        self.active_miners = active_miners
        self.shares_processed = shares_processed
        self.total_shares_processed = total_shares_processed

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Worker_stats))

    # Get a single record by height
    @classmethod
    def get_by_height(cls, height):
        return database.db.getSession().query(Worker_stats).filter(Worker_stats.height==height).first()

    # Get the last N stats records and return as a list
    @classmethod
    def get_last_n(cls, n):
        highest = database.db.getSession().query(func.max(Worker_stats.height)).scalar()
        latest = list(database.db.getSession().query(Worker_stats).filter(Worker_stats.height >= highest-n).order_by(asc(Worker_stats.height)))
        return latest

    # Get stats records falling within requested range
    @classmethod
    def get_range(cls, ts_start, ts_end):
        records = list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.timestamp >= ts_start, Worker_stats.timestamp <= ts_end)).order_by(asc(Worker_stats.height)))
        return record
