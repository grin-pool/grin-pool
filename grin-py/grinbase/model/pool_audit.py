from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, BigInteger, DateTime, JSON, DateTime # String, DateTime, func, ForeignKey, Boolean, and_
# from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "pool audit data" table

class Pool_audit(Base):
    __tablename__ = 'pool_audit'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)        # When this record was created
    height = Column(BigInteger, index=True) # Height of blockchain
    # Data
    pool_blocks_count = Column(Integer) # Number of pool blocks found since the last audit record height (includes orphans)
    payments = Column(BigInteger)  # Summ of rewards credited to miners since last audit record height
    payouts = Column(BigInteger)   # Summ of all payouts since last audit record
    liability = Column(BigInteger) # Amount owed to miners
    equity = Column(BigInteger)    # Amount in the wallet 
    balance = Column(BigInteger)   # equity - liability

    def __repr__(self):
        return self.to_json()

    def __init__(self):
        self.timestamp = datetime.utcnow()
        self.height = 0
        self.pool_blocks_count = 0
        self.payments = 0
        self.liability = 0
        self.equity = 0
        self.balance = 0
        self.payouts = 0
 

    def to_json(self, fields=None):
        obj = {
                'id': self.id,
                'timestamp': self.timestamp.timestamp(),
                'height': self.height,
                'blocks_count': self.pool_blocks_count,
                'payments': self.payments,
                'payouts': self.payouts,
                'liability': self.liability,
                'equity': self.equity,
                'balance': self.balance,
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
        return list(database.db.getSession().query(Pool_audit))

    # Get latest audit record
    @classmethod
    def getLatest(cls):
        return database.db.getSession().query(Pool_audit).order_by(Pool_audit.height.desc()).first()
