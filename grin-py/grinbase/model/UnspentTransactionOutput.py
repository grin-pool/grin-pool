import datetime

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Float
from sqlalchemy.orm import relationship

from grinbase.dbaccess import database
from grinbase.model import Base

#this is a user payment record

class UnspentTxOutput(Base):
    __tablename__ = 'pool_utxo'
    id = Column(String(36), primary_key=True, nullable=False)
    address = Column(String(1024), nullable=False)
    amount = Column(Float)

    def __repr__(self):
        return "{} {} {}".format(self.id, self.address, self.amount)

    def __init__(self, id, address, amount):
        self.id = id
        self.address = address
        self.amount = amount


    def updateAmount(self, amount):
        try:
            self.amount = amount
            database.db.getSession().commmit()
        except Exception as e:
            print("An error occured ", e)
            print(e.args)
            database.db.getSession().rollback()
            raise

    @classmethod
    def getAll(cls):
        return list(database.db.getSession().query(UnspentTxOutput))
