import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "user payment" table

class Pool_utxo(Base):
    __tablename__ = 'pool_utxo'
    id = Column(String(36), primary_key=True, nullable=False)
    address = Column(String(1024), nullable=False)
    amount = Column(Float)
    failure_count = Column(Integer)
    last_try = Column(String(32))
    last_success = Column(String(32))

    def __repr__(self):
        return "{} {} {} {} {} {}".format(self.id,
            self.address,
            self.amount,
            self.failure_count,
            self.last_try,
            self.last_success)

    def __init__(self, id, address, amount):
        self.id = id
        self.address = address
        self.amount = amount
        self.failure_count = 0
        self.last_try = now()
        self.last_success = now()

    # Get worker UUID from login string
    @classmethod
    def loginToUUID(cls, login):
        return str(uuid.uuid3(uuid.NAMESPACE_URL, str(login)))

    # Get a list of all records in the table
    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(Pool_utxo))

    # Get a list of all payable records
    @classmethod
    def getPayable(cls, minPayout):
        return list(database.db.getSession().query(Pool_utxo).filter(Pool_utxo.amount >= minPayout))

    # Get a single record by id locked for update
    @classmethod
    def get_locked_by_id(cls, uid):
        return database.db.getSession().query(Pool_utxo).with_for_update().filter_by(id=uid).first()

    # Add creadit to a worker, create a new record if none exists
    @classmethod
    def credit_worker(cls, worker, amount):
        uid = Pool_utxo.loginToUUID(worker)
        worker_utxo = Pool_utxo.get_locked_by_id(uid)
        if worker_utxo is None:
            worker_utxo = Pool_utxo(id=uid, amount=0, address=worker, failure_count=0, last_try=now(), last_success=now())
        worker_utxo.amount += amount
        return worker_utxo
    
