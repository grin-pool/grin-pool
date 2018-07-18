import datetime

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

    # Add to the current amount
    def addAmount(self, amount):
        try:
            self.amount += amount
            database.db.getSession().commmit()
        except Exception as e:
            print("An error occured ", e)
            print(e.args)
            database.db.getSession().rollback()
            raise

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
