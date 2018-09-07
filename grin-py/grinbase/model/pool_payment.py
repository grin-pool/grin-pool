import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

# This is the "payment" record table.  It keeps track of payments made to workers

class Pool_payment(Base):
    __tablename__ = 'pool_payment'
    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    address = Column(String(1024), nullable=False)
    amount = Column(Float)
    fee = Column(Float)
    failure_count = Column(Integer)
    invoked_by = Column(String(15))
    

    def __repr__(self):
        return "{} {} {} {} {} {} {}".format(
            self.id,
            self.timestamp,
            self.address,
            self.amount,
            self.fee,
            self.failure_count,
            self.invoked_by)

    def __init__(self, id, timestamp, address, amount, fee, failure_count=0, invoked_by="schedule"):
        self.id = id
        self.timestamp = timestamp
        self.address = address
        self.amount = amount
        self.fee = fee
        self.failure_count = failure_count
        self.invoked_by = invoked_by

    def to_json(self, fields=None):
        obj = {
                'id': self.id,
                'timestamp': self.timestamp,
                'address': self.address,
                'amount': self.amount,
                'fee': self.fee,
                'failure_count': self.failure_count,
                'invoked_by': self.invoked_by
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
        return list(database.db.getSession().query(Pool_payment))

    # Get by address
    @classmethod
    def get_by_address(cls, address):
        full_addr = "http://" + address
        return database.db.getSession().query(Pool_payment).filter(Pool_payment.address==full_addr).first()

    # Get by id (no lock)
    @classmethod
    def get_by_id(cls, uid):
        return database.db.getSession().query(Pool_payment).filter(Pool_payment.id==uid).first()

    # Get a single record by id locked for update
    @classmethod
    def get_locked_by_id(cls, uid):
        return database.db.getSession().query(Pool_payment).with_for_update().filter(Pool_payment.id==uid).first()
