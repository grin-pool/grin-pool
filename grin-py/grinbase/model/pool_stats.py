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
    timestamp = Column(DateTime, primary_key=True, nullable=False, index=True)
    height = Column(BigInteger, primary_key=True, nullable=False, unique=True, index=True)
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

    def to_json(self, fields=None):
        obj = { 
                'timestamp': self.timestamp.timestamp(),
                'height': self.height,
                'gps': self.gps,
                'active_miners': self.active_miners,
                'shares_processed': self.shares_processed,
                'total_shares_processed': self.total_shares_processed,
                'total_grin_paid': self.total_grin_paid,
                'total_blocks_found': self.total_blocks_found }
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
        return list(database.db.getSession().query(Pool_stats))

    # Get the latest record
    @classmethod
    def get_latest(cls, n=None):
        highest = database.db.getSession().query(func.max(Pool_stats.height)).scalar()
        if n == None:
            return database.db.getSession().query(Pool_stats).filter(Pool_stats.height == highest).first()
        else:
            return list(database.db.getSession().query(Pool_stats).filter(Pool_stats.height >= highest-n).order_by(asc(Pool_stats.height)))

    # Get record(s) by height
    @classmethod
    def get_by_height(cls, height, range=None):
        if range == None:
            return database.db.getSession().query(Pool_stats).filter(Pool_stats.height == height).first()
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_stats).filter(and_(Pool_stats.height >= h_start, Pool_stats.height <= h_end)).order_by(asc(Pool_stats.height)))

    # Get stats by timestamp
    @classmethod
    def get_by_time(cls, ts, range):
        if range == None:
            # XXX TODO: Test this
            return database.db.getSession().query(Pool_stats).filter(Pool_stats.timestamp <= ts).first()
        else:
            ts_start = ts-range
            ts_end = ts
            return list(database.db.getSession().query(Pool_stats).filter(and_(Pool_stats.timestamp >= ts_start, Pool_stats.timestamp <= ts_end)).order_by(asc(Pool_stats.height)))
