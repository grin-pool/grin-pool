import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Float, asc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "Worker statistics" table
#   Each entry contains stats for a worker at the given block height
#   There will be at most one Worker_stats record per block height, and will be
#     None for the time when the miner is not active

class Worker_stats(Base):
    __tablename__ = 'worker_stats'
    timestamp = Column(DateTime, primary_key=True, nullable=False, index=True)
    height = Column(BigInteger, primary_key=True, nullable=False, unique=True, index=True)
    id = Column(String(36))
    gps = Column(Float)
    active_miners = Column(Integer)
    shares_processed = Column(Integer)  # this block only
    total_shares_processed = Column(BigInteger)
    total_grin_paid = Column(Float)
    balance = Column(Float)
    
    
    def __repr__(self):
        return "{} {} {} {} {} {} {} {}".format(
            self.timestamp,
            self.height,
            self.gps,
            self.active_miners,
            self.shares_processed.
            self.total_shares_processed,
            self.total_grin_paid,
            self.balance)

    def __init__(self, timestamp, height, gps, active_miners, shares_processed, total_shares_processed, total_grin_paid, balance):
        self.timestamp = timestamp
        self.height = height
        self.gps = gps
        self.active_miners = active_miners
        self.shares_processed = shares_processed
        self.total_shares_processed = total_shares_processed
        self.total_grin_paid = total_grin_paid
        self.balance = balance

    def to_json(self, fields=None):
        obj = {
                'timestamp': self.timestamp.timestamp(),
                'height': self.height,
                'gps': self.gps,
                'active_miners': self.active_miners,
                'shares_processed': self.shares_processed,
                'total_shares_processed': self.total_shares_processed,
                'balance': self.balance,
                'total_grin_paid': self.total_grin_paid }
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
        return list(database.db.getSession().query(Worker_stats))

    # Get record(s) by height
    @classmethod
    def get_by_height(cls, id, height, range=None):
        if range == None:
            return database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.height == height, Worker_stats.id == id).first())
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.height >= h_start, Worker_stats.height <= h_end, Worker_stats.id == id)).order_by(asc(Worker_stats.height)))

    # Get stats by timestamp
    @classmethod
    def get_by_time(cls, ts, range):
        if range == None:
            # XXX TODO: Test this
            return database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.timestamp <= ts, Worker_stats.id == id)).first()
        else:
            ts_start = ts-range
            ts_end = ts
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.timestamp >= ts_start, Worker_stats.timestamp <= ts_end, Worker_stats.id == id)).order_by(asc(Worker_stats.height)))
