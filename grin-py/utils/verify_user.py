#!/usr/bin/python
  
# Given a username and plaintext password,
#  authenticate against the db user records

import sys
from grinbase.model.users import Users
from grinlib import lib


# User to authenticate
username = sys.argv[1]
password = sys.argv[2]

# Initialize a db connection
database = lib.get_db()

# Lookup / authenticate
theUserRecord = Users.get(username, password)

# Print the results
if theUserRecord is None:
    print("Failed to find or autenticate user: {}".format(username))
else:
    print("Success, {} has id {}".format(username, theUserRecord.id))

