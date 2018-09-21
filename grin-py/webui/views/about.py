from datetime import datetime
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen # python 3 syntax
import requests
import time
import json
import sys
import traceback 

from flask import Flask, Blueprint, render_template, request, session, make_response, flash, url_for, redirect
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField
from flask import Flask, Blueprint, render_template, request, session, make_response

about_profile = Blueprint('about_profile'
                           , __name__
                           , template_folder='templates'
                           , static_folder='static'
                           )

@about_profile.route('/about')
def about_template():
  try:



  except Exception as e:
    print("FAILED - {}".format(e))
    traceback.print_exc(file=sys.stdout)
    time.sleep(1)
    pass

  return render_template('about/about.html')

