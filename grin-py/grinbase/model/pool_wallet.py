from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, BigInteger, DateTime, JSON, DateTime # String, DateTime, func, ForeignKey, Boolean, and_
# from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "pool wa;;et data" table

# Note:  All denominations are in nanogrin

class Pool_wallet(Base):
    __tablename__ = 'pool_wallet'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)    # When this record was created
    chain_height = Column(BigInteger)   # Height of blockchain
    # Walet Data
    height = Column(BigInteger, index=True)    # Height of wallet information
    immature = Column(BigInteger) # Coinbase total value waiting for lock height (immature coinbases)
    total = Column(BigInteger)    # Total amount in the wallet
    awaiting_confirmation = Column(BigInteger) # Amount awaiting confirmation
    currently_spendable = Column(BigInteger)   # Amount currently spendable
    txs = Column(JSON)            # All txs in the wallet since previous record
    outputs = Column(JSON)        # All wallet outputs since previous record
#    latest_tx = Column(Integer)   # The latest tx id included in this record (wallet tx does not include height)

    def __repr__(self):
        return self.to_json()

    def __init__(self):
        self.timestamp = datetime.utcnow()
        self.chain_height = 0
        self.height = 0
        self.immature = 0
        self.total = 0
        self.awaiting_confirmation = 0
        self.currently_spendable = 0
        self.txs = {}
        self.outputs = {}
#        self.latest_tx = 0
 

    def to_json(self, fields=None):
        obj = {
                'id': self.id,
                'timestamp': self.timestamp.timestamp(),
                'chain_height': self.height,
                'height': self.height,
                'immature': self.immature,
                'total': self.total,
                'awaiting_confirmation': self.awaiting_confirmation,
                'currently_spendable': self.currently_spendable,
                'txs': self.txs,
                'outputs': self.outputs,
#                'latest_tx': self.latest_tx,
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
        return list(database.db.getSession().query(Pool_wallet))

    # Get wallet data record
    @classmethod
    def getLatest(cls):
        return database.db.getSession().query(Pool_wallet).order_by(Pool_wallet.id.desc()).first()
