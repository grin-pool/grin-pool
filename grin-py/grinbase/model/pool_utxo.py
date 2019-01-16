from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, BigInteger, Boolean, and_
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "user balance and payout" table

class Pool_utxo(Base):
    __tablename__ = 'pool_utxo'
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(1024))
    method = Column(String(64))
    locked = Column(Boolean)
    amount = Column(BigInteger)
    failure_count = Column(Integer)
    last_try = Column(DateTime)
    last_success = Column(DateTime)
    total_amount = Column(BigInteger)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return self.to_json()

    def __init__(self, user_id, address=None, method=None):
        self.user_id = user_id
        self.address = address
        self.method = method
        self.locked = False
        self.amount = 0
        self.failure_count = 0
        self.last_try = datetime.utcfromtimestamp(0)
        self.last_success = datetime.utcfromtimestamp(0)
        self.total_amount = 0

    def to_json(self, fields=None):
        obj = {
                'id': self.id,
                'address': self.address,
                'method': self.method,
                'locked': self.locked,
                'amount': self.amount,
                'failure_count': self.failure_count,
                'last_try': self.last_try.timestamp(),
                'last_success': self.last_success.timestamp(),
                'total_amount': self.total_amount,
                'user_id': self.user_id,
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
        return list(database.db.getSession().query(Pool_utxo))

    # Get a list of all payable records
    @classmethod
    def getPayable(cls, minPayout):
        return list(database.db.getSession().query(Pool_utxo).filter(and_(Pool_utxo.amount >= minPayout,Pool_utxo.locked == False,Pool_utxo.address != None,Pool_utxo.method != None)))

    # Get by address
    @classmethod
    def get_by_address(cls, address):
        full_addr = "http://" + address
        return database.db.getSession().query(Pool_utxo).filter(Pool_utxo.address==full_addr).first()

    # Get by user_id
    @classmethod
    def get_by_userid(cls, user_id):
        return database.db.getSession().query(Pool_utxo).filter(Pool_utxo.user_id==user_id).first()

    # Get a single record by user_id locked for update
    @classmethod
    def get_locked_by_userid(cls, user_id):
        return database.db.getSession().query(Pool_utxo).with_for_update().filter(Pool_utxo.user_id==user_id).first()

    # Add creadit to a worker, create a new record if none exists
    @classmethod
    def credit_worker(cls, user_id, amount):
        worker_utxo = Pool_utxo.get_locked_by_userid(int(user_id))
        if worker_utxo is None:
            worker_utxo = Pool_utxo(user_id=user_id)
            database.db.createDataObj(worker_utxo)
        worker_utxo.amount += amount
        return worker_utxo
    
    # Update fields in the record
    @classmethod
    def update_field(cls, user_id, field, value):
        worker_utxo = Pool_utxo.get_by_userid(int(user_id))
        if worker_utxo is None:
            return False
        try:
            setattr(worker_utxo, field, value)
            database.db.getSession().commit()
        except:
            return False
        return True
        
    
