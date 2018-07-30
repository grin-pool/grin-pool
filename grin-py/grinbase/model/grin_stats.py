import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Float, asc, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "pool statistics" table
#   Each entry contains stats for the block at height

class Grin_stats(Base):
    __tablename__ = 'grin_stats'
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    height = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    gps = Column(Float)
    difficulty = Column(Integer)
    total_utxoset_size = Column(BigInteger)
    total_transactions = Column(BigInteger)
    
    
    def __repr__(self):
        return "{} {} {} {} {} {}".format(
            self.timestamp,
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

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Grin_stats))

    # Get the latest record
    @classmethod
    def get_latest(cls):
        highest = database.db.getSession().query(func.max(Grin_stats.height)).scalar()
        return database.db.getSession().query(Grin_stats).filter(Grin_stats.height==highest).first()


    # Get a single record by height
    @classmethod
    def get_by_height(cls, height):
        return database.db.getSession().query(Grin_stats).filter(Grin_stats.height==height).first()

    # Get the last N stats records and return as a list
    @classmethod
    def get_last_n(cls, n):
        highest = database.db.getSession().query(func.max(Grin_stats.height)).scalar()
        latest = list(database.db.getSession().query(Grin_stats).filter(Grin_stats.height >= highest-n).order_by(asc(Grin_stats.height)))
        return latest

    # Get stats records falling within requested height range
    @classmethod
    def get_range_by_height(cls, h_start, h_end):
        records = list(database.db.getSession().query(Grin_stats).filter(and_(Grin_stats.height >= h_start, Grin_stats.height <= h_end)).order_by(asc(Grin_stats.height)))
        return records

    # Get stats records falling within requested time range
    @classmethod
    def get_range_by_time(cls, ts_start, ts_end):
        records = list(database.db.getSession().query(Grin_stats).filter(and_(Grin_stats.timestamp >= ts_start, Grin_stats.timestamp <= ts_end)).order_by(asc(Grin_stats.height)))
        return records
