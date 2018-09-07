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
    last_try = Column(DateTime)
    last_success = Column(DateTime)
    total_amount = Column(Float)

    def __repr__(self):
        return "{} {} {} {} {} {} {}".format(
            self.id,
            self.address,
            self.amount,
            self.failure_count,
            self.last_try,
            self.last_success,
            self.total_amount)

    def __init__(self, id, address):
        self.id = id
        self.address = address
        self.amount = 0
        self.failure_count = 0
        self.last_try = datetime.datetime.utcfromtimestamp(0)
        self.last_success = datetime.datetime.utcfromtimestamp(0)
        self.total_amount = 0

    def to_json(self, fields=None):
        obj = {
                'id': self.id,
                'address': self.address,
                'amount': self.amount,
                'failure_count': self.failure_count,
                'last_try': self.last_try.timestamp(),
                'last_success': self.last_success.timestamp(),
                'total_amount': self.total_amount
        }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj

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

    # Get by address
    @classmethod
    def get_by_address(cls, address):
        full_addr = "http://" + address
        return database.db.getSession().query(Pool_utxo).filter(Pool_utxo.address==full_addr).first()

    # Get by id (no lock)
    @classmethod
    def get_by_id(cls, uid):
        return database.db.getSession().query(Pool_utxo).filter(Pool_utxo.id==uid).first()

    # Get a single record by id locked for update
    @classmethod
    def get_locked_by_id(cls, uid):
        return database.db.getSession().query(Pool_utxo).with_for_update().filter(Pool_utxo.id==uid).first()

    # Add creadit to a worker, create a new record if none exists
    @classmethod
    def credit_worker(cls, worker, amount):
        uid = Pool_utxo.loginToUUID(worker)
        worker_utxo = Pool_utxo.get_locked_by_id(uid)
        if worker_utxo is None:
            worker_utxo = Pool_utxo(id=uid, address=worker)
            database.db.createDataObj(worker_utxo)
        worker_utxo.amount += amount
        return worker_utxo
    
