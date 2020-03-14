#!/usr/bin/python

from passlib.apps import custom_app_context as pwd_context
from passlib.handlers.sha2_crypt import sha256_crypt, sha512_crypt, _raw_sha2_crypt
import sys

rounds = int(sys.argv[3])
hashedPassword = _raw_sha2_crypt(sys.argv[1], sys.argv[2], rounds, True)
print(hashedPassword)
sys.stdout.flush()
