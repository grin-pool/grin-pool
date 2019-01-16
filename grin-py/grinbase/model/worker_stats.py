import datetime
import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, BigInteger, Boolean, asc, desc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "Worker statistics" table
#   Each entry contains stats for a worker at the given block height
#   There will be at most one Worker_stats record per block height per worker, and will be
#     None for the blocks when the worker is not active

class Worker_stats(Base):
    __tablename__ = 'worker_stats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    height = Column(BigInteger, nullable=False, index=True)
    valid_shares = Column(Integer)  # this block only
    invalid_shares = Column(Integer)  # this block only
    stale_shares = Column(Integer)  # this block only
    total_valid_shares = Column(BigInteger) # Running total all blocks
    total_invalid_shares = Column(BigInteger) # Running total all blocks
    total_stale_shares = Column(BigInteger) # Running total all blocks
    dirty = Column(Boolean, index=True)
    gps = relationship("Gps")
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return str(self.to_json())

    def __init__(self, timestamp, height, user_id, valid_shares=0, invalid_shares=0, stale_shares=0, total_valid_shares=0, total_invalid_shares=0, total_stale_shares=0, dirty=False):
        self.timestamp = timestamp
        self.height = height
        self.user_id = user_id
        self.valid_shares = valid_shares
        self.invalid_shares = invalid_shares
        self.stale_shares = stale_shares
        self.total_valid_shares = total_valid_shares
        self.total_invalid_shares = total_invalid_shares
        self.total_stale_shares = total_stale_shares
        self.dirty = dirty

    def to_json(self, fields=None):
        gps_data =  []
        #print("XXXXX self.gps = {}".format(self.gps))
        for rec in self.gps:
            gps_data.append(rec.to_json())
        obj = {
                'timestamp': self.timestamp.timestamp(),
                'height': self.height,
                'user_id': self.user_id,
                'valid_shares': self.valid_shares,
                'invalid_shares': self.invalid_shares,
                'stale_shares': self.stale_shares,
                'total_valid_shares': self.total_valid_shares,
                'total_invalid_shares': self.total_invalid_shares,
                'total_stale_shares': self.total_stale_shares,
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
        return list(database.db.getSession().query(Worker_stats))

    # Get the most recent stats record (any worker)
    @classmethod
    def get_latest(cls):
        last_height = database.db.getSession().query(func.max(Worker_stats.height)).scalar()
        if last_height is None:
            return None
        return database.db.getSession().query(Worker_stats).filter(Worker_stats.height == last_height).first()

    # Get the most recent stats record for specified worker
    @classmethod
    def get_latest_by_id(cls, id):
        return database.db.getSession().query(Worker_stats).filter(Worker_stats.user_id == id).order_by(Worker_stats.id.desc()).first()


    # Get record(s) by height for all pool workers
    @classmethod
    def get_by_height(cls, height, range=None):
        if range == None:
            return list(database.db.getSession().query(Worker_stats).filter(Worker_stats.height == height))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.height >= h_start, Worker_stats.height <= h_end)).order_by(asc(Worker_stats.height)))

    # Get record(s) by height for a single worker id
    @classmethod
    def get_by_height_and_id(cls, id, height, range=None):
        if range == None:
            return database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.height == height, Worker_stats.user_id == id)).one_or_none()
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.height >= h_start, Worker_stats.height <= h_end, Worker_stats.user_id == id)).order_by(asc(Worker_stats.height)))

    # Get stats by timestamp
    @classmethod
    def get_by_time(cls, id, ts, range):
        if range == None:
            # XXX TODO: Test this
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.timestamp <= ts, Worker_stats.user_id == id)))
        else:
            ts_start = ts-range
            ts_end = ts
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.timestamp >= ts_start, Worker_stats.timestamp <= ts_end, Worker_stats.user_id == id)).order_by(asc(Worker_stats.height)))

    # Get the earliest dirty stat
    @classmethod
    def get_first_dirty(cls, from_height=0):
        return database.db.getSession().query(Worker_stats).filter(Worker_stats.dirty == True).filter(Worker_stats.height >= from_height).first()

