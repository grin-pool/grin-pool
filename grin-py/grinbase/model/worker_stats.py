import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Float, asc, desc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "Worker statistics" table
#   Each entry contains stats for a worker at the given block height
#   There will be at most one Worker_stats record per block height, and will be
#     None for the time when the miner is not active

class Worker_stats(Base):
    __tablename__ = 'worker_stats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, primary_key=True, nullable=False, index=True)
    height = Column(BigInteger, primary_key=True, nullable=False, index=True)
    worker = Column(String(1024))
    gps = Column(Float)
    shares_processed = Column(Integer)  # this block only
    total_shares_processed = Column(BigInteger)
    grin_paid = Column(Float)   
    total_grin_paid = Column(Float)
    balance = Column(Float)
    
    
    def __repr__(self):
        return "{} {} {} {} {} {} {} {} {}".format(
            self.id,
            self.timestamp,
            self.height,
            self.worker,
            self.gps,
            self.shares_processed,
            self.total_shares_processed,
            self.grin_paid,
            self.total_grin_paid,
            self.balance)

    def __init__(self, id, timestamp, height, worker, gps, shares_processed, total_shares_processed, grin_paid, total_grin_paid, balance):
        self.id = id
        self.timestamp = timestamp
        self.height = height
        self.worker = worker
        self.gps = gps
        self.shares_processed = shares_processed
        self.total_shares_processed = total_shares_processed
        self.total_grin_paid = total_grin_paid
        self.grin_paid = grin_paid
        self.balance = balance

    def to_json(self, fields=None):
        obj = {
                'timestamp': self.timestamp.timestamp(),
                'height': self.height,
                'worker': self.worker,
                'gps': self.gps,
                'shares_processed': self.shares_processed,
                'total_shares_processed': self.total_shares_processed,
                'grin_paid': self.grin_paid,
                'total_grin_paid': self.total_grin_paid,
                'balance': self.balance
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

    # Get the most recent stats record
    @classmethod
    def get_last(cls):
        last_height = database.db.getSession().query(func.max(Worker_stats.height)).scalar()
        if last_height is None:
            return None
        return database.db.getSession().query(Worker_stats).filter(Worker_stats.height == last_height).first()

    # Get the most recent stats record for specified worker
    @classmethod
    def get_last_by_id(cls, id):
        last_rec = database.db.getSession().query(Worker_stats).filter(Worker_stats.worker == "http://"+id).order_by(Worker_stats.id.desc()).first()
        if last_rec is None:
            return None
        print("XXXXX last_rec = {}".format(last_rec))
        last_height = last_rec.height
        return database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.height == last_height, Worker_stats.worker == "http://"+id)).one_or_none()

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
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.height == height, Worker_stats.worker == "http://"+id)))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.height >= h_start, Worker_stats.height <= h_end, Worker_stats.worker == "http://"+id)).order_by(asc(Worker_stats.height)))

    # Get stats by timestamp
    @classmethod
    def get_by_time(cls, id, ts, range):
        if range == None:
            # XXX TODO: Test this
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.timestamp <= ts, Worker_stats.worker == "http://"+id)))
        else:
            ts_start = ts-range
            ts_end = ts
            return list(database.db.getSession().query(Worker_stats).filter(and_(Worker_stats.timestamp >= ts_start, Worker_stats.timestamp <= ts_end, Worker_stats.worker == "http://"+id)).order_by(asc(Worker_stats.height)))
