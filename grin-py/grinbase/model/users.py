from datetime import datetime
import uuid
from passlib.hash import pbkdf2_sha256
from passlib.apps import custom_app_context as pwd_context

from sqlalchemy import Column, Integer, String, DateTime, func, and_, ForeignKey, Text
from sqlalchemy.orm import relationship

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from grinbase.dbaccess import database
from grinbase.model import Base

from grinbase.model.pool_utxo import Pool_utxo


# This is the "user account" table

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index = True, unique=True)
    password_hash = Column(String(128))
    email = Column(String(255))
    settings = Column(Text(10000))
    extra1 = Column(String(255))
    extra2 = Column(String(255))
    extra3 = Column(String(255))
    utxo = relationship("Pool_utxo")
    shares = relationship("Worker_shares")
    stats = relationship("Worker_stats")
    payments = relationship("Pool_payment")

    def __repr__(self):
        return str(self.to_json())

    def __init__(self, username, password, id=None, email=None):
        if id is not None:
            self.id = id
        self.username = username
        self.hash_password(password)

    def to_json(self, fields=None):
        obj = {
                'id': self.id,
                'username': self.username,
                'password_hash': self.password_hash,
                #'email': self.email,
        }
        # Filter by field(s)
        if fields != None:
            for k in list(obj.keys()):
                if k not in fields:
                    del obj[k]
        return obj

    @classmethod
    def get_by_id(cls, id):
        return database.db.getSession().query(Users).filter(Users.id == id).one_or_none()

    @classmethod
    def check_username_exists(cls, username):
        if username is None:
            return False
        username = username.lower()
        count = database.db.getSession().query(Users).filter(Users.username == username).count()
        print("COUNT={}".format(count))
        return count != 0

    @classmethod
    def get_id_by_username(cls, username):
        if username is None:
            return 0
        username = username.lower()
        try:
            user = database.db.getSession().query(Users).filter(Users.username == username).one_or_none()
        except:
            return 0
        return user.id

    @classmethod
    def get(cls, username, password):
        if username is None or password is None:
            return None
        username = username.lower()
        # Get user with that name and then test the password against it
        try:
            user = database.db.getSession().query(Users).filter(Users.username == username).one_or_none()
            # Attempt to verify with the provided password
            if pwd_context.verify(password, user.password_hash):
                return user
        except:
            return None
        return None

    @classmethod
    def create(cls, username, password):
        if username is None or password is None:
            return None
        username = username.lower()
        try:
            user_rec = Users(username, password)
            database.db.createDataObj(user_rec)
            # Create the users utxo record
            pool_utxo = Pool_utxo(user_rec.id)
            database.db.createDataObj(pool_utxo)
            return user_rec
        except:
            # XXX TODO: Log err
            return None

    # Instance Methods
    def get_id(self):
        return self.id.encode('utf-8')

    def hash_password(self, password):
        #self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        #return self.password_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, key, expiration = 600):
        s = Serializer(key, expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(secret, token):
        s = Serializer(secret)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = Users.get_by_id(data['id'])
        return user
