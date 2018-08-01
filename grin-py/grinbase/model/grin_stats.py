import datetime
import uuid
import json

from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Float, asc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "pool statistics" table
#   Each entry contains stats for the block at height

class Grin_stats(Base):
    __tablename__ = 'grin_stats'
    timestamp = Column(DateTime, primary_key=True, nullable=False, index=True)
    height = Column(BigInteger, primary_key=True, nullable=False, unique=True, index=True)
    gps = Column(Float)
    difficulty = Column(Integer)
    total_utxoset_size = Column(BigInteger)
    total_transactions = Column(BigInteger)
    
    def __repr__(self):
        return "{} {} {} {} {} {}".format(
            self.timestamp.timestamp(),
            self.height,
            self.gps,
            self.difficulty,
            self.total_utxoset_size,
            self.total_transactions)

    def __init__(self, timestamp, height, gps, difficulty, total_utxoset_size, total_transactions):
        self.timestamp = datetime.datetime.utcnow()
        self.height = height
        self.gps = gps
        self.difficulty = difficulty
        self.total_utxoset_size = total_utxoset_size
        self.total_transactions = total_transactions

    def to_json(self, fields=None):
        obj = { 'timestamp': self.timestamp.timestamp(),
                 'height': self.height,
                 'gps': self.gps,
                 'difficulty': self.difficulty,
                 'total_utxoset_size': self.total_utxoset_size,
                 'total_transactions': self.total_transactions
              }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj

    # Get a list of all records in the table
    # XXX Please never call this except in testing
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Grin_stats))

    # Get the latest (n) record(s) in the db
    @classmethod
    def get_latest(cls, n=None):
        highest = database.db.getSession().query(func.max(Grin_stats.height)).scalar()
        if n == None:
            return database.db.getSession().query(Grin_stats).filter(Grin_stats.height == highest).first()
        else:
            return list(database.db.getSession().query(Grin_stats).filter(Grin_stats.height >= highest-n).order_by(asc(Grin_stats.height)))


    # Get record(s) by height and optional historical range
    @classmethod
    def get_by_height(cls, height, range=None):
        if range == None:
            return database.db.getSession().query(Grin_stats).filter(Grin_stats.height==height).first()
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Grin_stats).filter(and_(Grin_stats.height >= h_start, Grin_stats.height <= h_end)).order_by(asc(Grin_stats.height)))


    # Get stats records falling within requested time range
    @classmethod
    def get_by_time(cls, ts, range=None):
        if range == None:
            # XXX Get a range, sort, and give closest?
            return database.db.getSession().query(Grin_stats).filter(Grin_stats.timestamp<=ts).first()
        else:
            ts_start = ts-range
            ts_end = ts
            return list(database.db.getSession().query(Grin_stats).filter(and_(Grin_stats.timestamp >= ts_start, Grin_stats.timestamp <= ts_end)).order_by(asc(Grin_stats.height)))
