from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, BigInteger, DateTime, JSON, DateTime, String, and_ # func, ForeignKey, Boolean
# from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "pool redits" table

class Pool_credits(Base):
    __tablename__ = 'pool_credits'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)        # When this record was created
    height = Column(BigInteger, index=True) # Height of blockchain when credit is applied
    poolblock_height = Column(BigInteger, index=True) # Height of poolblock this credit is for
    # Data
    credits = Column(JSON)

    def __repr__(self):
        return self.to_json()

    def __init__(self, height, poolblock_height, credits_map):
        self.timestamp = datetime.utcnow()
        self.height = height
        self.poolblock_height = poolblock_height
        self.credits = credits_map
 

    def to_json(self, fields=None):
        obj = {
                'id': self.id,
                'timestamp': self.timestamp.timestamp(),
                'height': self.height,
                'poolblock_height': self.poolblock_height,
                'credits': self.credits,
        }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Pool_credits))

    # Get latest credits record
    @classmethod
    def getLatest(cls):
        return database.db.getSession().query(Pool_credits).order_by(Pool_credits.height.desc()).first()

    # Get all credits records by blockchain height
    @classmethod
    def get_by_height(cls, height, range=None):
        if range is None:
            return list(database.db.getSession().query(Pool_credits).filter(Pool_credits.height==height))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_credits).filter(and_(Pool_credits.height >= h_start, Pool_credits.height <= h_end)))

    # Get all credits records by poolblock height
    @classmethod
    def get_by_poolblock_height(cls, height, range=None):
        if range is None:
            return list(database.db.getSession().query(Pool_credits).filter(Pool_credits.poolblock_height==height))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_credits).filter(and_(Pool_credits.poolblock_height >= h_start, Pool_credits.poolblock_height <= h_end)))
