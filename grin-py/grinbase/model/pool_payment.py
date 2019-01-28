import datetime
import sys
import json

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, func, and_, ForeignKey, Text
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "payment" record table.  It keeps track of payments made to users

class Pool_payment(Base):
    __tablename__ = 'pool_payment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    height = Column(BigInteger, nullable=False, index=True)
    address = Column(String(1024))
    amount = Column(BigInteger)
    method = Column(String(64))
    fee = Column(BigInteger)
    failure_count = Column(Integer)
    invoked_by = Column(String(16))
    state = Column(String(16))
    tx_data = Column(Text(100000))
    user_id = Column(Integer, ForeignKey('users.id'))
    

    def __repr__(self):
        return self.to_json()

    def __init__(self, user_id, timestamp, height, address, amount, method, fee, tx_data, failure_count=0, state="new", invoked_by="schedule"):
        self.timestamp = timestamp
        self.height = height
        self.user_id = user_id
        self.address = address
        self.amount = amount
        self.method = method
        self.fee = fee
        self.failure_count = failure_count
        self.state = state
        self.tx_data = str(tx_data)
        self.invoked_by = invoked_by

    def to_json(self, fields=None):
        # Extract txid from tx_data
        try:
            tx_data_json = json.loads(self.tx_data)
            txid = tx_data_json['id']
        except Exception as e:
            print("XXX Extract TXID from payemnt record: {}".format(repr(e)))
            sys.stdout.flush()
            txid = self.address
        obj = {
                'id': self.id,
                'timestamp': self.timestamp.timestamp(),
                'height': self.height,
                'user_id': self.user_id,
                'address': self.address,
                'amount': self.amount,
                'method': self.method,
                'fee': self.fee,
                'failure_count': self.failure_count,
                'state': self.state,
                'invoked_by': self.invoked_by,
                'txid': txid,
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
        return list(database.db.getSession().query(Pool_payment))

    # Get by state
    @classmethod
    def get_by_state(cls, state):
        return list(database.db.getSession().query(Pool_payment).filter(Pool_payment.state==state).all())

    # Get by address
    @classmethod
    def get_by_address(cls, address):
        rec = database.db.getSession().query(Pool_payment).filter(Pool_payment.address==address).first()
        if rec is None:
            full_addr = "http://" + address
            rec = database.db.getSession().query(Pool_payment).filter(Pool_payment.address==full_addr).first()
        return rec

    # Get all payment records by height for a single worker
    @classmethod
    def get_by_userid_and_height(cls, user_id, height, range=None):
        if range is None:
            return list(database.db.getSession().query(Pool_payment).filter(and_(Pool_payment.user_id==user_id, Pool_payment.height==height)))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_payment).filter(and_(Pool_payment.user_id==user_id, Pool_payment.height >= h_start, Pool_payment.height <= h_end)))


    # Get all payment records by height got all workers
    @classmethod
    def get_by_height(cls, height, range=None):
        if range is None:
            return list(database.db.getSession().query(Pool_payment).filter(Pool_payment.height==height))
        else:
            h_start = height-(range-1)
            h_end = height
            return list(database.db.getSession().query(Pool_payment).filter(and_(Pool_payment.height >= h_start, Pool_payment.height <= h_end)))

    # Get payment records by timestamp
    @classmethod
    def get_by_userid_and_time(cls, user_id, ts, range):
        ts_start = ts-range
        ts_end = ts
        return list(database.db.getSession().query(Pool_payment).filter(and_(Pool_payment.timestamp >= ts_start, Pool_payment.timestamp <= ts_end, Pool_payment.user_id == user_id)).order_by(asc(Pool_payment.timestamp)))


    # Get latest payment records by user_id (no lock)
    @classmethod
    def get_latest_by_userid(cls, user_id, range=None):
        if range is None:
            return database.db.getSession().query(Pool_payment).filter(Pool_payment.user_id==user_id).order_by(Pool_payment.height.desc()).first()
        else:
            return list(database.db.getSession().query(Pool_payment).filter(Pool_payment.user_id==user_id).order_by(Pool_payment.height.desc()).limit(range).all())
