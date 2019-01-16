import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Boolean, asc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "pool statistics" table
#   Each entry contains stats for the block at height

class Pool_stats(Base):
    __tablename__ = 'pool_stats'
    height = Column(BigInteger, primary_key=True, index=True, autoincrement=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    active_miners = Column(BigInteger)
    shares_processed = Column(Integer) # this block only
    total_blocks_found = Column(Integer) 
    total_shares_processed = Column(BigInteger) 
    dirty = Column(Boolean, index=True)
    gps = relationship("Gps")
    
    def __repr__(self):
        return str(self.to_json())

    def __init__(self, timestamp, height, active_miners, shares_processed, total_shares_processed, total_blocks_found, dirty=False):
        self.timestamp = timestamp
        self.height = height
        self.active_miners = active_miners
        self.shares_processed = shares_processed
        self.total_shares_processed = total_shares_processed
        self.total_blocks_found = total_blocks_found
        self.dirty = dirty

    def to_json(self, fields=None):
        gps_data =  []
        for rec in self.gps:
            gps_data.append(rec.to_json())
        obj = { 
                'timestamp': self.timestamp.timestamp(),
                'height': self.height,
                'active_miners': self.active_miners,
                'shares_processed': self.shares_processed,
                'total_shares_processed': self.total_shares_processed,
                'total_blocks_found': self.total_blocks_found,
                'dirty': self.dirty,
                'gps': gps_data,
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
        if height == 0:
            height = database.db.getSession().query(func.max(Pool_stats.height)).scalar()
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


    # Get the earliest dirty stat
    @classmethod
    def get_first_dirty(cls, from_height=0):
        return database.db.getSession().query(Pool_stats).filter(and_(Pool_stats.dirty == True, Pool_stats.height >= from_height)).order_by(asc(Pool_stats.height)).first()

    # Mark a record dirty by height
    @classmethod
    def mark_dirty(cls, height):
        rec = Pool_stats.get_by_height(height)
        if rec is None:
            return False
        rec.dirty = True
        database.db.getSession().commit()
        return True

