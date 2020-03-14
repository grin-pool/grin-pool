#!/usr/bion/python 

from grinbase.model.users import Users
from passlib.apps import custom_app_context as pwd_context
import sys

#print('sys.argv[1] is:', sys.argv[1])
hash = pwd_context.encrypt(sys.argv[1])
print(hash)
sys.stdout.flush()
